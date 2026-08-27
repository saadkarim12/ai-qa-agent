"""Layer 2 - Black Box Intelligence: output contracts.

HLD 4.2 defines this layer's output as:

    Application Map (pages, routes, navigation graph), interactive element
    inventory, journey candidates, state-transition model, discovered
    behaviour assertions with confidence.

Two things carried through from the other layers:

  * BR-03 - everything discovered here is `source = discovered`. It is
    observed behaviour, never a confirmed requirement, and the type system
    keeps the two apart.
  * HLD 10.3 - every element carries a *chain* of locator candidates in
    preference order (role/label -> test-id -> css -> structural), so Layer 4
    can heal a broken locator by walking down the chain instead of guessing.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ElementKind(str, Enum):
    LINK = "link"
    BUTTON = "button"
    INPUT = "input"
    SELECT = "select"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SUBMIT = "submit"
    TABLE = "table"
    OTHER = "other"


class SafetyVerdict(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"


class Locator(BaseModel):
    """One way of finding an element, and how much we trust it."""

    model_config = ConfigDict(extra="forbid")

    strategy: str = Field(description="role_label | test_id | css | structural")
    value: str
    preference: int = Field(description="0 is most preferred")


class Element(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: ElementKind
    name: str = Field(description="Accessible name: label, text or placeholder")
    locators: List[Locator] = Field(default_factory=list)
    input_type: Optional[str] = None
    required: bool = False
    options: List[str] = Field(default_factory=list)
    destructive: bool = False
    safety: SafetyVerdict = SafetyVerdict.ALLOW
    safety_reason: Optional[str] = None

    @property
    def best_locator(self) -> Optional[str]:
        return self.locators[0].value if self.locators else None


class Form(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    action: str
    method: str = "get"
    fields: List[Element] = Field(default_factory=list)
    submit: Optional[Element] = None

    @property
    def required_fields(self) -> List[Element]:
        return [f for f in self.fields if f.required]


class Page(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str
    path: str
    title: str
    status: int = 200
    signature: str = Field(description="Structural fingerprint - dedupes parameterised routes")
    requires_auth: bool = False
    access_denied: bool = False
    forms: List[Form] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list, description="Outgoing in-scope paths")
    elements: List[Element] = Field(default_factory=list)
    headings: List[str] = Field(default_factory=list)
    tables: int = 0
    blocked_actions: List[str] = Field(default_factory=list)


class Transition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_path: str
    to_path: str
    via: str = Field(description="The element that causes the transition")


class Journey(BaseModel):
    """A plausible end-to-end path a real user would take."""

    model_config = ConfigDict(extra="forbid")

    name: str
    paths: List[str]
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)


class ApplicationMap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base_url: str
    pages: List[Page] = Field(default_factory=list)
    transitions: List[Transition] = Field(default_factory=list)
    journeys: List[Journey] = Field(default_factory=list)
    authenticated: bool = False
    pages_visited: int = 0
    pages_skipped: int = 0
    blocked_actions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    @property
    def stats(self) -> dict:
        forms = sum(len(p.forms) for p in self.pages)
        return {
            "pages": len(self.pages),
            "forms": forms,
            "elements": sum(len(p.elements) for p in self.pages),
            "journeys": len(self.journeys),
            "transitions": len(self.transitions),
            "auth_required_pages": sum(1 for p in self.pages if p.requires_auth),
            "blocked_actions": len(self.blocked_actions),
        }


class CrawlBudget(BaseModel):
    """HLD 5.2 - every discovery run is bounded before it starts."""

    model_config = ConfigDict(extra="forbid")

    max_pages: int = 40
    max_depth: int = 4
    page_timeout_ms: int = 8000
    politeness_ms: int = 120
    allow_destructive: bool = Field(
        default=False,
        description="C-04: destructive actions are disabled unless explicitly enabled",
    )
