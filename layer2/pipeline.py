"""Layer 2 - the pipeline.

    URL (+ optional credentials) -> ApplicationMap + Requirement[] (discovered)

The second output is the important one: discovery emits the same `Requirement`
contract Layer 1 does, so both ingestion strategies converge on one model and a
single pipeline runs from there (HLD 3.4).
"""

from typing import List, Optional, Tuple

from layer1.contracts import Requirement
from layer2.auth import FormLogin, IAuthAdapter, NoAuth
from layer2.contracts import ApplicationMap, CrawlBudget
from layer2.crawler import crawl
from layer2.infer import infer_journeys, infer_requirements


def discover(
    base_url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    login_path: str = "/login",
    max_pages: int = 40,
    max_depth: int = 4,
    entry_paths: Optional[List[str]] = None,
    scope_deny: Optional[List[str]] = None,
    allow_destructive: bool = False,
) -> Tuple[ApplicationMap, List[Requirement]]:
    """Crawl an application and return what it is, plus what it appears to do."""
    auth: IAuthAdapter = (
        FormLogin(login_path, username, password) if username and password else NoAuth()
    )
    budget = CrawlBudget(
        max_pages=max_pages, max_depth=max_depth, allow_destructive=allow_destructive
    )
    amap = crawl(
        base_url, budget=budget, auth=auth,
        entry_paths=entry_paths, scope_deny=scope_deny,
    )
    amap.journeys = infer_journeys(amap)
    return amap, infer_requirements(amap)
