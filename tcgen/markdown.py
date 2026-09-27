"""Test cases as a markdown file, and back again.

The markdown is the hand-off to the Playwright layer, so it has to be
machine-readable as well as readable. The conventions are fixed:

  * one table per user story, always with the COLUMNS below, in that order
  * multi-value cells use <br> between items (a markdown cell cannot hold a newline)
  * steps are numbered "1. ", "2. " ...
  * test data is "name = `value`"; a value in <angle brackets> is a placeholder to fill in
  * Source is "US-n · stated (category)" or "US-n · derived (category)"

`parse_markdown` reads the file back. The tests round-trip every case through
it, which is the guarantee the next layer can rely on.
"""

import datetime
import re
from typing import List, Optional

from tcgen.models import TestCase, TestDatum
from tcgen.stories import Story

COLUMNS = [
    "Test ID", "Source", "Objective", "Preconditions", "Steps", "Test Data",
    "Expected Result", "Risk", "Priority", "Evidence Requirements", "Status",
]
_SOURCE = re.compile(r"^(US-\d+)\s*·\s*(stated|derived)\s*\(([^)]+)\)$")
_DATUM = re.compile(r"^(.+?)\s*=\s*`(.*)`$")
_STEP_NO = re.compile(r"^\d+\.\s*")


def _cell(text: str) -> str:
    return (text or "").replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").strip()


def _join(items: List[str]) -> str:
    return "<br>".join(_cell(i) for i in items if i and i.strip())


def source_label(case: TestCase) -> str:
    return "%s · %s (%s)" % (case.story_id, case.derivation, case.category)


def render_markdown(stories: List[Story], cases: List[TestCase],
                    model: Optional[str] = None, generated: Optional[str] = None) -> str:
    when = generated or datetime.datetime.now().strftime("%d %b %Y %H:%M")
    sites = sorted({s.site_url for s in stories if s.site_url})
    out: List[str] = ["# Test Cases", ""]
    if sites:
        out.append("- **Site:** %s" % ", ".join(sites))
    out.append("- **Generated:** %s" % when)
    if model:
        out.append("- **Model:** %s" % model)
    out.append("- **Stories:** %d · **Test cases:** %d" % (len(stories), len(cases)))
    out.append("- **Status:** every test case is Draft until a QA engineer reviews it")
    out.append("")

    for story in stories:
        rows = [c for c in cases if c.story_id == story.id]
        out.append("## %s — %s" % (story.id, story.title))
        out.append("")
        for line in story.text.splitlines():
            out.append("> %s" % line if line.strip() else ">")
        out.append("")
        if not rows:
            out.append("_No test cases were generated for this story._")
            out.append("")
            continue
        out.append("| " + " | ".join(COLUMNS) + " |")
        out.append("|" + "---|" * len(COLUMNS))
        for c in rows:
            steps = ["%d. %s" % (i, s) for i, s in enumerate(c.steps, start=1)]
            data = ["%s = `%s`" % (d.name, d.value) for d in c.test_data]
            out.append("| " + " | ".join([
                _cell(c.test_id), _cell(source_label(c)), _cell(c.objective),
                _join(c.preconditions), _join(steps), _join(data) or "—",
                _cell(c.expected_result), c.risk, c.priority,
                _join(c.evidence_requirements), c.status,
            ]) + " |")
        out.append("")
        flagged = [c for c in rows if c.issues]
        if flagged:
            out.append("**Check before running**")
            out.append("")
            for c in flagged:
                for issue in c.issues:
                    out.append("- %s — %s" % (c.test_id, issue))
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def _split_row(line: str) -> List[str]:
    """Split a table row on unescaped pipes."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    cells, buf, i = [], [], 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            buf.append(body[i + 1])
            i += 2
            continue
        if ch == "|":
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def _items(cell: str) -> List[str]:
    if cell in ("", "—"):
        return []
    return [p.strip() for p in cell.split("<br>") if p.strip()]


def parse_markdown(text: str) -> List[TestCase]:
    """Read test cases back out of a file produced by render_markdown."""
    cases: List[TestCase] = []
    in_table = False
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            in_table = False
            continue
        cells = _split_row(line)
        if cells == COLUMNS:
            in_table = True
            continue
        if not in_table or all(set(c) <= set("-: ") for c in cells):
            continue
        if len(cells) != len(COLUMNS):
            raise ValueError("Row has %d cells, expected %d: %s"
                             % (len(cells), len(COLUMNS), line[:80]))
        row = dict(zip(COLUMNS, cells))
        m = _SOURCE.match(row["Source"])
        if not m:
            raise ValueError("Unrecognised Source value: %r" % row["Source"])
        data = []
        for item in _items(row["Test Data"]):
            dm = _DATUM.match(item)
            if not dm:
                raise ValueError("Unrecognised test data item: %r" % item)
            data.append(TestDatum(name=dm.group(1).strip(), value=dm.group(2)))
        cases.append(TestCase(
            test_id=row["Test ID"],
            story_id=m.group(1), derivation=m.group(2), category=m.group(3),
            source=row["Source"],
            objective=row["Objective"],
            preconditions=_items(row["Preconditions"]),
            steps=[_STEP_NO.sub("", s) for s in _items(row["Steps"])],
            test_data=data,
            expected_result=row["Expected Result"],
            risk=row["Risk"], priority=row["Priority"],
            evidence_requirements=_items(row["Evidence Requirements"]),
            status=row["Status"],
        ))
    return cases
