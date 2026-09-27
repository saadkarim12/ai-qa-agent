"""The user's example stories and test cases, loaded for the prompt and the checker."""

import json
import os
from functools import lru_cache
from typing import List, Optional

from tcgen.models import DraftSet

_PATH = os.path.join(os.path.dirname(__file__), "fewshot", "exemplars.json")


@lru_cache(maxsize=1)
def _load() -> dict:
    with open(_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def exemplars() -> List[dict]:
    """[{story: {...}, area_code, cases: [...]}], validated against the schema."""
    out = []
    for ex in _load()["exemplars"]:
        DraftSet(area_code=ex["area_code"], cases=ex["cases"])  # fail loudly if the file drifts
        out.append(ex)
    return out


def example_text_for_site(site_url: str, exemplar_list: Optional[List[dict]] = None) -> str:
    """Everything the user supplied for this site, as one searchable string.

    This is the grounding corpus: the spreadsheet rows verbatim (including the
    Actual Result text someone observed by running the site) plus the converted
    exemplars and the documented corrections. Examples for a *different* site
    contribute nothing, so saucedemo's accounts can never leak into tests for
    another application.
    """
    data = _load()
    pool = exemplar_list if exemplar_list is not None else data["exemplars"]
    same_site = [ex for ex in pool
                 if _origin(ex["story"]["site_url"]) == _origin(site_url or "")]
    if not same_site:
        return ""
    # Only the rows behind the examples actually in play. In a leave-one-out
    # evaluation the held-out story's rows are the answer key; letting them
    # into the corpus would pass values the model could only know from memory.
    parts: List[str] = []
    in_play = {ex["story"]["id"] for ex in same_site}
    for ex in same_site:
        for sheet in ex.get("raw_sheets", []):
            for row in data["raw_rows"].get(sheet, []):
                parts.append(" | ".join(row))
    for c in data.get("_corrections", []):
        if c.get("applies_to") in in_play:
            parts.append(c["text"])
    for ex in same_site:
        parts.append(ex["story"]["text"])
        parts.append(json.dumps(ex["cases"], ensure_ascii=False))
    return "\n".join(parts)


def _origin(url: str) -> str:
    url = (url or "").strip().lower().rstrip("/")
    for prefix in ("https://", "http://"):
        if url.startswith(prefix):
            url = url[len(prefix):]
    return url.split("/")[0].replace("www.", "")
