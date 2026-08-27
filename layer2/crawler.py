"""Layer 2 - crawl coordination.

A breadth-first walk of the permitted URL space under a hard budget (HLD 4.2).
Three properties matter more than coverage:

  * Bounded. max_pages, max_depth and a per-page timeout are set before the
    crawl starts, so a link farm cannot run the bill up (HLD 5.2).
  * Polite. A delay between requests, because scanning must never degrade the
    customer's own environment (T-10, AR-06).
  * Deduplicated by page *signature*, not URL, so /orders/1 and /orders/2 count
    once and parameterised routes do not explode the frontier (HLD 4.2).

Nothing here clicks anything. Discovery navigates and reads; it does not
submit forms or press action buttons, so the Safety Governor's verdicts are
recorded for later layers rather than tested by trial.
"""

import time
from typing import List, Optional, Set, Tuple
from urllib.parse import urljoin

from layer2.analyse import EXTRACT_JS, analyse
from layer2.auth import IAuthAdapter, NoAuth
from layer2.contracts import ApplicationMap, CrawlBudget, Page, Transition


def crawl(
    base_url: str,
    budget: Optional[CrawlBudget] = None,
    auth: Optional[IAuthAdapter] = None,
    entry_paths: Optional[List[str]] = None,
    scope_deny: Optional[List[str]] = None,
) -> ApplicationMap:
    from playwright.sync_api import sync_playwright

    budget = budget or CrawlBudget()
    auth = auth or NoAuth()
    deny = [d.lower() for d in (scope_deny or [])]
    base = base_url.rstrip("/")

    amap = ApplicationMap(base_url=base)
    seen_paths: Set[str] = set()
    seen_signatures: Set[str] = set()
    transitions: List[Transition] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        page.set_default_timeout(budget.page_timeout_ms)

        if auth.name != "none":
            try:
                amap.authenticated = auth.authenticate(page, base)
                if not amap.authenticated:
                    amap.warnings.append(
                        "authentication with the %s adapter did not succeed; "
                        "only public pages were crawled" % auth.name)
            except Exception as exc:  # noqa: BLE001
                amap.warnings.append("authentication failed: %s" % exc)

        frontier: List[Tuple[str, int, Optional[str]]] = [
            (p, 0, None) for p in (entry_paths or ["/"])
        ]

        while frontier and len(amap.pages) < budget.max_pages:
            path, depth, came_from = frontier.pop(0)
            if path in seen_paths or depth > budget.max_depth:
                continue
            seen_paths.add(path)

            if any(d in path.lower() for d in deny):
                amap.pages_skipped += 1
                amap.warnings.append("skipped %s (excluded by scope_deny)" % path)
                continue

            url = urljoin(base + "/", path.lstrip("/"))
            try:
                response = page.goto(url, wait_until="domcontentloaded",
                                     timeout=budget.page_timeout_ms)
                status = response.status if response else 0
                data = page.evaluate(EXTRACT_JS)
            except Exception as exc:  # noqa: BLE001 - one bad page must not end the crawl
                amap.warnings.append("%s could not be loaded: %s" % (path, str(exc)[:110]))
                amap.pages_skipped += 1
                continue

            analysed: Page = analyse(page.url, status, data, budget.allow_destructive)
            amap.pages_visited += 1

            if analysed.signature in seen_signatures:
                # Same structure, different data - one representative is enough.
                amap.pages_skipped += 1
            else:
                seen_signatures.add(analysed.signature)
                amap.pages.append(analysed)
                for action in analysed.blocked_actions:
                    entry = "%s: %s" % (analysed.path, action)
                    if entry not in amap.blocked_actions:
                        amap.blocked_actions.append(entry)

            if came_from:
                transitions.append(Transition(from_path=came_from, to_path=analysed.path,
                                              via="link"))

            for link in analysed.links:
                if link not in seen_paths:
                    frontier.append((link, depth + 1, analysed.path))

            if budget.politeness_ms:
                time.sleep(budget.politeness_ms / 1000.0)

        if frontier:
            amap.warnings.append(
                "crawl budget reached (%d pages); %d path(s) left unexplored"
                % (budget.max_pages, len({f[0] for f in frontier} - seen_paths)))

        browser.close()

    amap.transitions = transitions
    return amap
