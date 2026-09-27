"""Split pasted text into individual user stories.

People paste stories in whatever shape they have them. The rules here are
deliberately simple and match the user's own examples: an optional
"Site URL:" line, an optional "User Story N — Title" heading, then the
"As a / I want / So that" lines. A second "As a" starts a new story.
"""

import re
from dataclasses import dataclass
from typing import List, Optional

_SITE = re.compile(r"^\s*site\s*url\s*:\s*(\S+)", re.IGNORECASE)
_HEADING = re.compile(r"^\s*(?:user\s*story|story|us)\s*[#-]?\s*(\d+)\b\s*[—:\-–]*\s*(.*)$",
                      re.IGNORECASE)
_AS_A = re.compile(r"^\s*as\s+an?\b", re.IGNORECASE)
_WANT = re.compile(r"\bi\s+want\s+(?:to\s+)?(.+?)[.\n]*$", re.IGNORECASE | re.MULTILINE)
_URL = re.compile(r"https?://[^\s)>\]]+")


@dataclass
class Story:
    id: str
    title: str
    text: str
    site_url: Optional[str]


def _title_from(text: str) -> str:
    m = _WANT.search(text)
    if not m:
        first = text.strip().splitlines()[0] if text.strip() else "Story"
        return first[:60]
    words = m.group(1).strip().rstrip(".").split()
    return " ".join(words[:8]).capitalize()


def parse_stories(text: str, site_url: Optional[str] = None) -> List[Story]:
    """Return one Story per user story found. Never returns an empty story."""
    blocks: List[dict] = []
    current: Optional[dict] = None
    site = (site_url or "").strip() or None

    def start(title: str = "") -> dict:
        block = {"lines": [], "title": title, "site": site}
        blocks.append(block)
        return block

    for line in (text or "").splitlines():
        m_site = _SITE.match(line)
        if m_site:
            site = m_site.group(1).strip()
            if current is not None and not any(l.strip() for l in current["lines"]):
                current["site"] = site
            continue

        m_head = _HEADING.match(line)
        if m_head:
            current = start(m_head.group(2).strip())
            current["lines"].append(line.strip())
            continue

        if _AS_A.match(line):
            has_as_a = current is not None and any(_AS_A.match(l) for l in current["lines"])
            if current is None or has_as_a:
                current = start()
        if current is None:
            if not line.strip():
                continue
            current = start()
        current["lines"].append(line.rstrip())

    stories: List[Story] = []
    for block in blocks:
        body = "\n".join(block["lines"]).strip()
        if not body:
            continue
        story_site = block["site"]
        if not story_site:
            found = _URL.search(body)
            story_site = found.group(0) if found else None
        n = len(stories) + 1
        stories.append(Story(
            id="US-%d" % n,
            title=block["title"] or _title_from(body),
            text=body,
            site_url=story_site,
        ))
    return stories
