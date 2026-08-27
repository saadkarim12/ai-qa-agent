"""Layer 2 - Black Box Intelligence (HLD 4.2).

Discovers what an application is and does from the outside: crawls the
permitted URL space, inventories interactive elements, infers journeys, and
emits discovered behaviour as `Requirement` records tagged source='discovered'.
No source-code access (C-01, BRD 30.1).
"""

from layer2.contracts import ApplicationMap, CrawlBudget, Page
from layer2.pipeline import discover

__all__ = ["ApplicationMap", "CrawlBudget", "Page", "discover"]
