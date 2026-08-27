"""Layer 2 - the Safety Governor.

ADR-011: this sits *below* the agent and is deterministic. No prompt, no model
and no clever reasoning can talk its way past it, because there is no model
involved - it is a deny-list applied to the element before anything is clicked.

The crawler drives a live customer system with real credentials. The cost of a
false negative here is a deleted customer account, so the classifier is
deliberately blunt and errs towards blocking.
"""

import re
from typing import Optional, Tuple

# Irreversible whatever the element is: a link that deletes is still a delete.
_ALWAYS = [
    (r"\b(delete|remove|erase|destroy|purge|wipe)\b", "deletes data"),
    (r"\b(close|terminate)\s+(account|subscription|membership|policy)\b", "closes an account"),
    (r"\b(deactivate|disable)\s+(account|user)\b", "deactivates an account"),
    (r"\breset\s+(all|everything|factory)\b", "resets state"),
    (r"\b(revoke|unpublish|suspend)\b", "removes access or content"),
    (r"\bbulk\s+\w+\b", "bulk action"),
    (r"\bsign\s*out|log\s*out|sign\s*off\b", "ends the crawl session"),
]

# Unsafe to *submit*, but safe to *navigate to*. Following a "Transfer" link
# opens the form, which is exactly what discovery needs; pressing "Send
# transfer" moves real money. The distinction is the element kind, so the
# crawler can explore a payments area without transacting in it.
_ACTION_ONLY = [
    (r"\b(pay|purchase|buy|checkout|subscribe)\b", "may take payment"),
    (r"\b(transfer|withdraw|remit|send)\b", "may move money"),
    (r"\b(place|confirm|submit)\s+(order|payment|transfer)\b", "may move money"),
    (r"\b(cancel)\s+(order|subscription|booking)\b", "cancels a commitment"),
]

_NAVIGATION_KINDS = {"link"}

_DANGER_ATTRS = re.compile(r"\b(danger|destructive|delete|remove|warning)\b", re.IGNORECASE)


def classify(
    name: str, css_class: str = "", href: str = "", kind: str = "button"
) -> Tuple[bool, Optional[str]]:
    """Return (is_destructive, reason) for this element."""
    blob = " ".join(x for x in (name, css_class, href) if x).lower()
    for pattern, reason in _ALWAYS:
        if re.search(pattern, blob):
            return True, reason
    if kind not in _NAVIGATION_KINDS:
        for pattern, reason in _ACTION_ONLY:
            if re.search(pattern, blob):
                return True, reason
        if _DANGER_ATTRS.search(css_class or ""):
            return True, "styled as a destructive action"
    return False, None


def is_blocked(
    name: str, css_class: str = "", href: str = "",
    kind: str = "button", allow_destructive: bool = False,
) -> Tuple[bool, Optional[str]]:
    """Whether the crawler may interact with this element.

    `allow_destructive` does not make an action safe; it records that an
    operator explicitly accepted the risk for this environment (C-04).
    """
    destructive, reason = classify(name, css_class, href, kind)
    if not destructive:
        return False, None
    if allow_destructive:
        return False, "destructive but explicitly permitted for this environment"
    return True, reason
