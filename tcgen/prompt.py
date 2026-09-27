"""What the model is told.

The examples do most of the teaching (format, depth, tone). The system prompt
exists mainly to draw the line between what the model may state and what it
must leave as a placeholder, because that line is what "not hallucinated" means
here: every literal in a test case should be traceable to the story or to the
user's own examples for the same site.
"""

import json
from typing import List

from tcgen.examples import _origin
from tcgen.stories import Story

STEP_VERBS = (
    "Navigate", "Enter", "Clear", "Click", "Select", "Check", "Uncheck", "Hover",
    "Scroll", "Press", "Upload", "Wait", "Leave", "Refresh", "Log", "Open", "Verify",
)

SYSTEM = """You write black-box test cases for a web application from a user story.

A QA engineer reviews your test cases and Playwright then executes them, so every fact in them has to be checkable against the story or the examples you are given. Where you don't know something, leave a placeholder instead of filling the gap from memory.

What to cover
- Every behaviour the story asks for. Mark these derivation "stated".
- Cases that follow from the same feature although the story doesn't spell them out: invalid and missing input, boundaries, access and permissions, security abuse of the same inputs, state changes the feature implies. Mark these "derived". Write the cases a careful tester would write for this story. Don't pad, don't repeat a scenario, and don't test other features.

Grounding
- You may recognise the website. Don't use anything you know about it from outside this conversation: account names, product names, page paths, button labels or on-screen messages. If the story and the examples don't give it, use a placeholder or describe it.
- Test data: use a literal value only if it appears in the story or in the examples for the same site. Otherwise use a descriptive placeholder in angle brackets, such as <valid username>. Example data belongs to its own site; never reuse it for a different site.
- Don't quote exact on-screen text (error messages, labels, headings) unless that exact text appears in the story or the examples. Describe the expected behaviour instead, the way the examples do ("an appropriate error message is displayed").
- Don't invent URLs. Use only URLs that appear in the story or in the examples for this site.
- Name UI elements the way the story or the examples name them; otherwise describe them by purpose ("the button that adds the product to the cart"). Only put text in backticks if it appears in the story or the examples, or it is a placeholder.
- Generic attack inputs such as an SQL injection string are fine for security cases; they say nothing about the application.
- Don't write an actual result. That is recorded when the test runs.

Format
- Steps: one action each, starting with one of these verbs: %s. Put literal values in backticks.
- Preconditions describe the state before step 1. Test data lists every literal value the steps use.
- Risk is the business impact if this behaviour is broken. Priority is execution order, P1 first.
- area_code is a short upper-case code for the feature, such as LOGIN, CART or CHECKOUT.""" % ", ".join(STEP_VERBS)


def render_story(story_id: str, text: str, site_url: str) -> str:
    return "Site URL: %s\nStory %s:\n%s" % (site_url or "(not given)", story_id, text.strip())


def build_messages(story: Story, exemplars: List[dict]) -> List[dict]:
    """Examples as prior turns, then the target story.

    The last example turn carries a cache breakpoint: the system prompt and the
    examples are identical on every call, so after the first request they are
    read from cache at a tenth of the input price.
    """
    messages: List[dict] = []
    for i, ex in enumerate(exemplars):
        s = ex["story"]
        messages.append({"role": "user",
                         "content": render_story(s["id"], s["text"], s["site_url"])})
        answer = json.dumps({"area_code": ex["area_code"], "cases": ex["cases"]},
                            ensure_ascii=False, indent=1)
        block = {"type": "text", "text": answer}
        if i == len(exemplars) - 1:
            block["cache_control"] = {"type": "ephemeral"}
        messages.append({"role": "assistant", "content": [block]})

    request = render_story(story.id, story.text, story.site_url or "")
    example_sites = {_origin(ex["story"]["site_url"]) for ex in exemplars}
    if story.site_url and _origin(story.site_url) not in example_sites:
        request += ("\n\nThis story is for a different site from the examples, so none of "
                    "the example test data, URLs or on-screen text applies to it.")
    elif not story.site_url:
        request += "\n\nNo site URL was given, so don't assume the example site."
    messages.append({"role": "user", "content": request})
    return messages
