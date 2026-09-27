"""User stories in, checked test cases and a markdown file out.

All stories run at the same time, and every test case is reported through
`on_event` the moment it is complete, so a page can show results within a few
seconds rather than after the slowest story has finished.

Events (plain dicts, JSON-serialisable):
  {"type": "stories", "stories": [...]}                       once, first
  {"type": "case", "story_id", "n", "case": {...}}            each case as written
  {"type": "story_done", "story_id", "count", "seconds"}
  {"type": "story_error", "story_id", "error"}
Final IDs (TC-AREA-NNN) are assigned once everything has finished, in story
order, so numbering never depends on which story happened to finish first.
"""

import re
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from tcgen import examples as ex_mod
from tcgen.guard import check_case, check_set, grounding_issue_count
from tcgen.llm import DEFAULT_MODEL, MODELS, ModelError, Usage, draft
from tcgen.markdown import render_markdown, source_label
from tcgen.models import DraftCase, DraftSet, TestCase
from tcgen.prompt import build_messages
from tcgen.stories import Story, parse_stories

MAX_STORIES = 10
MAX_CHARS = 20000
MAX_PARALLEL = 6

Event = Callable[[dict], None]


@dataclass
class Result:
    stories: List[Story]
    cases: List[TestCase]
    markdown: str
    usage: Usage
    errors: Dict[str, str] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    @property
    def grounding_issues(self) -> int:
        return grounding_issue_count(self.cases)


def _area(code: str) -> str:
    code = re.sub(r"[^A-Z0-9]+", "", (code or "").upper())[:12]
    return code or "TC"


def corpus_for(story: Story, exemplars: Optional[List[dict]] = None) -> str:
    """Everything a test case for this story may legitimately quote."""
    return (story.text + "\n" + (story.site_url or "") + "\n"
            + ex_mod.example_text_for_site(story.site_url or "", exemplars))


def _as_case(story: Story, d: DraftCase, test_id: str) -> TestCase:
    case = TestCase(test_id=test_id, story_id=story.id, source="", status="Draft",
                    **d.model_dump())
    case.source = source_label(case)
    return case


def finalise(story: Story, drafted: DraftSet, counters: Dict[str, int],
             exemplars: Optional[List[dict]] = None) -> List[TestCase]:
    """Number, label and check one story's draft."""
    area = _area(drafted.area_code)
    out: List[TestCase] = []
    for d in drafted.cases:
        counters[area] = counters.get(area, 0) + 1
        out.append(_as_case(story, d, "TC-%s-%03d" % (area, counters[area])))
    check_set(out, corpus_for(story, exemplars), story.site_url or "")
    return out


def validate_input(text: str) -> List[Story]:
    if len(text or "") > MAX_CHARS:
        raise ModelError("That's more than %d characters. Split it into smaller batches."
                         % MAX_CHARS)
    stories = parse_stories(text)
    if not stories:
        raise ModelError("No user story found. Paste at least one story, for example: "
                         "'As a registered user, I want to log in, so that I can access "
                         "the application.'")
    if len(stories) > MAX_STORIES:
        raise ModelError("Found %d stories; the limit per run is %d."
                         % (len(stories), MAX_STORIES))
    return stories


def generate(text: str, site_url: Optional[str], client, model_key: str = DEFAULT_MODEL,
             exemplars: Optional[List[dict]] = None,
             on_event: Optional[Event] = None) -> Result:
    emit: Event = on_event or (lambda e: None)
    if model_key not in MODELS:
        raise ModelError("Unknown model '%s'." % model_key)
    validate_input(text)
    stories = parse_stories(text, site_url)
    if client is None:
        raise ModelError("The AI model isn't set up on this server: ANTHROPIC_API_KEY is "
                         "missing.")

    shots = exemplars if exemplars is not None else ex_mod.exemplars()
    emit({"type": "stories",
          "stories": [dict(s.__dict__) for s in stories]})

    total = Usage(model=MODELS[model_key]["id"])
    drafts: Dict[str, DraftSet] = {}
    errors: Dict[str, str] = {}
    lock = threading.Lock()

    def run(story: Story) -> None:
        corpus = corpus_for(story, shots)
        seen: set = set()
        counter = [0]

        def on_case(d: DraftCase) -> None:
            counter[0] += 1
            live = _as_case(story, d, "#%d" % counter[0])
            live.issues = check_case(live, corpus, seen, story.site_url or "")
            emit({"type": "case", "story_id": story.id, "n": counter[0],
                  "case": live.model_dump()})

        try:
            drafted, usage = draft(client, model_key, build_messages(story, shots), on_case)
        except ModelError as exc:
            with lock:
                errors[story.id] = str(exc)
            emit({"type": "story_error", "story_id": story.id, "error": str(exc)})
            return
        with lock:
            drafts[story.id] = drafted
            total.add(usage)
            total.model = usage.model  # reports a fallback model if one answered
        emit({"type": "story_done", "story_id": story.id, "count": len(drafted.cases),
              "seconds": usage.seconds})

    # Every story at once: the wait is the slowest story, not the sum of them.
    with ThreadPoolExecutor(max_workers=min(MAX_PARALLEL, len(stories))) as pool:
        list(pool.map(run, stories))

    counters: Dict[str, int] = {}
    cases: List[TestCase] = []
    notes: List[str] = []
    for story in stories:
        if story.id in drafts:
            cases.extend(finalise(story, drafts[story.id], counters, shots))
            if not story.site_url:
                notes.append("%s has no site URL, so every URL and value in its test cases "
                             "must come from the story itself." % story.id)

    return Result(stories=stories, cases=cases,
                  markdown=render_markdown(stories, cases, model=total.model),
                  usage=total, errors=errors, notes=notes)
