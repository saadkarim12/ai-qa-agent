"""Deterministic checks for what the model could not have known.

The model is told to stay grounded; this module checks that it did. Nothing
here is AI: every rule is a text comparison against the story and the user's
examples for the same site. A flagged case is kept and shown with its issue,
because deleting it would hide the problem from the reviewer.

Issues come in two kinds:
  grounding - a literal that isn't in the story or examples (possible hallucination)
  format    - something Playwright or a reviewer will stumble over
"""

import re
from typing import List

from tcgen.models import TestCase
from tcgen.prompt import STEP_VERBS

_PLACEHOLDER = re.compile(r"^<[^<>]+>$")
_QUOTED = re.compile(r'"([^"\n]{4,})"|“([^”\n]{4,})”')
_URL = re.compile(r"https?://[^\s`)>\]\"',]+")
_BACKTICK = re.compile(r"`([^`]+)`")

GROUNDING = "grounding"
FORMAT = "format"

# Standard attack inputs. They make no claim about the application - they are
# inputs whose expected outcome is "rejected safely" - so they cannot be a
# hallucination about it. The user's own examples include the SQL one.
_GENERIC_ATTACK = re.compile(
    r"('\s*or\s*'?1'?\s*=\s*'?1|\bor\s+1\s*=\s*1|<\s*script|javascript:|onerror\s*=|"
    r"\.\./|;\s*drop\s+table|union\s+select|\$\{|\{\{)",
    re.IGNORECASE,
)


# A bare number is a boundary input (0, -1, 101), not a claim about the application.
_NUMBER = re.compile(r"^[+-]?\d+(?:[.,]\d+)?$")

# Keyboard keys a step may press. Naming one says nothing about the application.
_KEYS = {
    "enter", "return", "tab", "escape", "esc", "space", "backspace", "delete",
    "arrowup", "arrowdown", "arrowleft", "arrowright", "home", "end", "pageup",
    "pagedown", "shift", "control", "ctrl", "alt", "meta", "cmd", "shift+tab",
}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def _in(needle: str, corpus: str) -> bool:
    """Case-insensitive, so a deliberate variant such as STANDARD_USER (a
    case-sensitivity test built from the example's standard_user) is grounded."""
    return _norm(needle).lower() in corpus.lower()


def _url_grounded(url: str, corpus: str, site: str) -> bool:
    """A URL is grounded if it appears as given, or if it is the story's own
    site plus a path that appears in the input (examples often mention a page
    by its path, e.g. '/cart.html')."""
    url = url.rstrip("/.,")
    if _in(url, corpus) or _in(url + "/", corpus):
        return True
    m = re.match(r"^(https?://[^/]+)(/.*)?$", url)
    s = re.match(r"^(https?://[^/]+)", (site or "").strip())
    if not (m and s):
        return False
    same_site = m.group(1).lower().replace("www.", "") == s.group(1).lower().replace("www.", "")
    path = (m.group(2) or "/").split("?")[0]
    return same_site and (path in ("", "/") or _in(path, corpus))


def check_case(case: TestCase, corpus: str, seen_objectives: set,
               site_url: str = "") -> List[str]:
    """Return human-readable issues, each prefixed with its kind."""
    issues: List[str] = []
    corpus_n = _norm(corpus)

    for datum in case.test_data:
        # Models sometimes wrap a value in backticks to make surrounding spaces
        # visible (a whitespace-padding test); the value itself is inside.
        value = datum.value.strip().strip("`").strip()
        if (not value or _PLACEHOLDER.match(value) or _GENERIC_ATTACK.search(value)
                or _NUMBER.match(value)):
            continue
        if _URL.fullmatch(value) and _url_grounded(value, corpus_n, site_url):
            continue
        if not _in(value, corpus_n):
            issues.append("%s: test data %s = `%s` is not in the story or the examples"
                          % (GROUNDING, datum.name, value))

    # Literals written into steps must also be accounted for.
    for step in case.steps:
        for literal in _BACKTICK.findall(step):
            literal = literal.strip()
            if (_PLACEHOLDER.match(literal) or _GENERIC_ATTACK.search(literal)
                    or _NUMBER.match(literal) or literal.lower() in _KEYS
                    or _in(literal, corpus_n)):
                continue
            if any(literal == d.value.strip() for d in case.test_data):
                continue  # already reported against test data, if at all
            issues.append("%s: step uses `%s`, which is not in the story or the examples"
                          % (GROUNDING, literal))

    text_fields = case.steps + [case.expected_result, case.objective] + case.preconditions
    for field in text_fields:
        for a, b in _QUOTED.findall(field):
            quoted = a or b
            if not _in(quoted, corpus_n):
                issues.append('%s: quotes "%s" as exact on-screen text, but it is not in the '
                              "story or the examples" % (GROUNDING, quoted))
        for url in _URL.findall(field):
            if not _url_grounded(url, corpus_n, site_url):
                issues.append("%s: URL %s is not in the story or the examples" % (GROUNDING, url))

    for i, step in enumerate(case.steps, start=1):
        first = step.strip().split(" ", 1)[0].rstrip(":,.")
        if first not in STEP_VERBS:
            issues.append("%s: step %d starts with '%s', not a recognised action verb"
                          % (FORMAT, i, first))
    if not case.steps:
        issues.append("%s: no steps" % FORMAT)

    key = _norm(case.objective).lower()
    if key in seen_objectives:
        issues.append("%s: repeats the objective of an earlier test case" % FORMAT)
    seen_objectives.add(key)

    # De-duplicate while keeping order (one bad value can appear in two places).
    return list(dict.fromkeys(issues))


def check_set(cases: List[TestCase], corpus: str, site_url: str = "") -> List[str]:
    """Annotate each case in place; return set-level issues."""
    seen: set = set()
    for case in cases:
        case.issues = check_case(case, corpus, seen, site_url)
    problems: List[str] = []
    if cases and not any(c.derivation == "stated" for c in cases):
        problems.append("%s: no test case covers the story's stated behaviour" % FORMAT)
    return problems


def grounding_issue_count(cases: List[TestCase]) -> int:
    """Distinct problems: one invented value used in five test cases is one
    thing the model made up, not five."""
    return len({i for c in cases for i in c.issues if i.startswith(GROUNDING)})
