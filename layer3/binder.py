"""Layer 3 - binding tests to the real application.

Without Layer 2, a test step says "Go to Customer Login" - readable by a human,
useless to a runner. With an Application Map, the same step can name the page
and the locator to use.

Binding is a *match*, not a guess. A step is bound only when the page and the
element are actually found in the map; anything unmatched keeps its business
language and the test is reported as partially bound. Silently attaching a
plausible-looking selector would produce tests that fail for reasons that have
nothing to do with the product.

Locators come from the element's chain in preference order (HLD 10.3), so the
most robust available strategy is chosen and the rest remain as fallbacks.
"""

import re
from typing import Dict, List, Optional, Tuple

from layer2.contracts import ApplicationMap, Element, ElementKind, Page
from layer3.contracts import TestCase

_DISCOVERED_REF = re.compile(r"^discovered:(?P<path>/[^#]*)")
_STOP = {"the", "a", "an", "of", "and", "for", "to", "my", "page", "view", "screen"}


def _tokens(text: str) -> set:
    return {t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if t and t not in _STOP}


def _page_index(amap: ApplicationMap) -> Tuple[Dict[str, Page], List[Tuple[set, Page]]]:
    by_path = {p.path: p for p in amap.pages}
    fuzzy = []
    for p in amap.pages:
        keys = _tokens(p.path) | _tokens(p.title)
        for h in p.headings[:2]:
            keys |= _tokens(h)
        fuzzy.append((keys, p))
    return by_path, fuzzy


def _match_page(test: TestCase, by_path, fuzzy) -> Optional[Page]:
    # 1. A discovered requirement already names its page - exact, no guessing.
    for ref in test.requirement_refs:
        m = _DISCOVERED_REF.match(ref)
        if m and m.group("path") in by_path:
            return by_path[m.group("path")]

    # 2. Otherwise match the workflow name against page titles and headings.
    wanted = _tokens(test.workflow)
    if not wanted:
        return None
    best, best_score = None, 0.0
    for keys, page in fuzzy:
        overlap = len(wanted & keys)
        if not overlap:
            continue
        score = overlap / float(len(wanted))
        if score > best_score:
            best, best_score = page, score
    return best if best_score >= 0.5 else None


def _find_element(page: Page, text: str) -> Optional[Element]:
    """Pick the element a step's wording most plausibly refers to."""
    wanted = _tokens(text)
    if not wanted:
        return None
    best, best_score = None, 0.0
    for el in page.elements:
        name_tokens = _tokens(el.name)
        if not name_tokens:
            continue
        overlap = len(wanted & name_tokens)
        if not overlap:
            continue
        score = overlap / float(len(name_tokens))
        # Prefer something you can act on over a passing mention.
        if el.kind in (ElementKind.SUBMIT, ElementKind.BUTTON, ElementKind.INPUT,
                       ElementKind.SELECT, ElementKind.LINK):
            score += 0.25
        if score > best_score:
            best, best_score = el, score
    return best if best_score >= 0.4 else None


def bind(tests: List[TestCase], amap: ApplicationMap) -> Dict[str, int]:
    """Attach page paths and locators where the map supports it."""
    by_path, fuzzy = _page_index(amap)
    counts = {"bound": 0, "partially_bound": 0, "unbound": 0, "steps_bound": 0}

    for test in tests:
        page = _match_page(test, by_path, fuzzy)
        if page is None:
            counts["unbound"] += 1
            continue

        test.page_path = page.path
        submit = next(
            (f.submit for f in page.forms if f.submit and f.submit.best_locator), None
        )
        bound_steps = 0

        for step in test.steps:
            action = step.action
            low = action.lower()

            if low.startswith("go to"):
                step.target_path = page.path
                step.locator = page.url
                bound_steps += 1
                continue
            if low.startswith("observe"):
                step.target_path = page.path
                continue
            if low.startswith("sign in as"):
                login = by_path.get("/login")
                if login and login.forms:
                    step.target_path = login.path
                    step.locator = (login.forms[0].submit.best_locator
                                    if login.forms[0].submit else None)
                    bound_steps += 1
                continue

            element = _find_element(page, action)
            if element is None and submit is not None:
                element = submit
            if element is not None and element.best_locator:
                step.target_path = page.path
                step.locator = element.best_locator
                bound_steps += 1

        actionable = [s for s in test.steps if not s.action.lower().startswith("observe")]
        if actionable and bound_steps == len(actionable):
            test.binding = "bound"
            counts["bound"] += 1
        elif bound_steps:
            test.binding = "partially-bound"
            counts["partially_bound"] += 1
        else:
            counts["unbound"] += 1
        counts["steps_bound"] += bound_steps

    return counts
