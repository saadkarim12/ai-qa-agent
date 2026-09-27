"""The shapes that move through the generator.

`DraftSet` / `DraftCase` are what the model is allowed to write. They leave out
everything the code knows better: test IDs, the story reference, status. So
the model cannot misnumber tests or claim a test has already passed.

`TestCase` is a finished row: the draft plus the fields the code fills in,
plus any issues the checker found.
"""

from typing import List

from pydantic import BaseModel, ConfigDict, Field

try:  # Python 3.8+
    from typing import Literal
except ImportError:  # pragma: no cover
    from typing_extensions import Literal

Category = Literal[
    "positive", "negative", "boundary", "required-field", "permission",
    "navigation", "state-transition", "security", "ui",
]
Derivation = Literal["stated", "derived"]
Risk = Literal["Critical", "High", "Medium", "Low"]
Priority = Literal["P1", "P2", "P3", "P4"]


class TestDatum(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="What the value is for, e.g. username")
    value: str = Field(description="The literal value, or a <placeholder> when it is not given")


class DraftCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objective: str = Field(description="What this test validates, in one line")
    derivation: Derivation = Field(
        description="stated: the story asks for this directly. derived: follows from the "
                    "story's feature (negative, validation, security...) but is not written in it")
    category: Category
    preconditions: List[str]
    steps: List[str] = Field(description="One action per step, each starting with an action verb")
    test_data: List[TestDatum]
    expected_result: str
    risk: Risk
    priority: Priority
    evidence_requirements: List[str]


class DraftSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    area_code: str = Field(description="Short upper-case code for the feature, e.g. LOGIN, CART")
    cases: List[DraftCase]


class TestCase(BaseModel):
    """A finished row: BRD 12.2 columns plus Test Data."""

    model_config = ConfigDict(extra="forbid")

    test_id: str
    story_id: str
    source: str
    objective: str
    preconditions: List[str]
    steps: List[str]
    test_data: List[TestDatum]
    expected_result: str
    risk: Risk
    priority: Priority
    evidence_requirements: List[str]
    status: str = "Draft"
    category: Category
    derivation: Derivation
    issues: List[str] = Field(default_factory=list)
