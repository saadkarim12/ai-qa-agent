"""Layer 3 - Test Intelligence: output contracts.

HLD 4.3 defines this layer's outputs as:

    Test Strategy, TestCase[] with steps and expected results, coverage map,
    prioritised execution plan, test data requirements.

Each is a validated model here. Two principles carried forward from Layer 1:

  * ADR-012 - every number in these models is produced by arithmetic, not by a
    model. `score_breakdown` carries the working so a customer can be shown
    exactly why a test ranked where it did.
  * BR-03 - coverage distinguishes requirements confirmed by the customer from
    behaviour that was merely inferred. A coverage figure that blends the two
    is a misleading figure.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from layer1.contracts import Risk


class TestCategory(str, Enum):
    """BRD 12.1 test categories, plus the two this layer needs to be honest."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    BOUNDARY = "boundary"
    REQUIRED_FIELD = "required_field"
    PERMISSION = "permission"
    PRECONDITION = "precondition"
    NAVIGATION = "navigation"
    STATE_TRANSITION = "state_transition"
    # Emitted instead of guessing when the requirement is too vague to test.
    CLARIFICATION = "clarification"


class Priority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class TestStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    index: int
    action: str = Field(description="What the tester or runner does")
    expected: Optional[str] = Field(default=None, description="Observable check at this step")
    # Filled in by Layer 3's binder when Layer 2 has supplied an application
    # map. Until then a step is business language a human can follow but a
    # runner cannot execute.
    target_path: Optional[str] = Field(default=None, description="Page this step acts on")
    locator: Optional[str] = Field(default=None, description="Preferred locator from the chain")


class TestDataRequirement(BaseModel):
    """What must exist before a test can run (HLD 4.3 Test Data Service)."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str
    fields: List[str] = Field(default_factory=list)
    sensitivity: str = Field(default="synthetic", description="synthetic | masked | pii-free")
    used_by: List[str] = Field(default_factory=list, description="Test case ids")


class TestCase(BaseModel):
    """One executable test intention. Steps are business-level until Layer 2
    supplies real selectors - see `binding`."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    category: TestCategory
    actor: str
    workflow: str
    preconditions: List[str] = Field(default_factory=list)
    steps: List[TestStep]
    expected_result: str
    # Traceability back through Layer 1 to the source document (BR-02).
    requirement_refs: List[str] = Field(default_factory=list)
    risk: Risk
    priority: Priority
    score: float = Field(ge=0.0, le=100.0)
    score_breakdown: Dict[str, float] = Field(
        default_factory=dict, description="The arithmetic behind `score`, term by term"
    )
    test_data_ids: List[str] = Field(default_factory=list)
    estimated_seconds: int = Field(default=60)
    needs_clarification: bool = False
    clarification_reasons: List[str] = Field(default_factory=list)
    binding: str = Field(
        default="business-language",
        description="business-language | partially-bound | bound",
    )
    page_path: Optional[str] = Field(default=None, description="Page the test acts on")
    executor_type: str = "ui"
    status: str = "Draft"


class PlannedTest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int
    test_id: str
    title: str
    score: float
    priority: Priority
    estimated_seconds: int
    cumulative_seconds: int
    selected: bool = Field(description="False when it falls outside the run budget")


class ExecutionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    budget_minutes: Optional[int] = None
    total_tests: int
    selected_tests: int
    deferred_tests: int
    estimated_total_seconds: int
    estimated_selected_seconds: int
    order: List[PlannedTest] = Field(default_factory=list)


class WorkflowCoverage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow: str
    requirements: int
    requirements_covered: int
    tests: int
    coverage_pct: float


class CoverageMap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirements_total: int
    requirements_covered: int
    coverage_pct: float
    # BR-03: never blend confirmed requirements with inferred behaviour.
    confirmed_requirements: int
    inferred_requirements: int
    by_workflow: List[WorkflowCoverage] = Field(default_factory=list)
    by_category: Dict[str, int] = Field(default_factory=dict)
    uncovered_refs: List[str] = Field(default_factory=list)
    unclear_refs: List[str] = Field(
        default_factory=list, description="Covered only by a clarification request"
    )


class TestStrategy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_name: str
    scope_summary: str
    workflows_in_scope: List[str] = Field(default_factory=list)
    categories_used: List[str] = Field(default_factory=list)
    risk_approach: str
    scoring_formula: str
    scoring_weights: Dict[str, float] = Field(default_factory=dict)
    unavailable_signals: List[str] = Field(
        default_factory=list,
        description="Scoring terms that are zero because the layer that feeds them is not built",
    )
    assumptions: List[str] = Field(default_factory=list)
    exclusions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    entry_criteria: List[str] = Field(default_factory=list)
    exit_criteria: List[str] = Field(default_factory=list)


class TestPlan(BaseModel):
    """Everything Layer 3 produces for one document."""

    model_config = ConfigDict(extra="forbid")

    strategy: TestStrategy
    test_cases: List[TestCase] = Field(default_factory=list)
    coverage: CoverageMap
    execution_plan: ExecutionPlan
    test_data: List[TestDataRequirement] = Field(default_factory=list)
    generator: str = Field(default="rules", description="rules | rules+llm")
    warnings: List[str] = Field(default_factory=list)

    @property
    def stats(self) -> dict:
        by_cat: Dict[str, int] = {}
        by_pri: Dict[str, int] = {}
        for t in self.test_cases:
            by_cat[t.category.value] = by_cat.get(t.category.value, 0) + 1
            by_pri[t.priority.value] = by_pri.get(t.priority.value, 0) + 1
        return {
            "total": len(self.test_cases),
            "by_category": by_cat,
            "by_priority": by_pri,
            "needs_clarification": sum(1 for t in self.test_cases if t.needs_clarification),
            "coverage_pct": self.coverage.coverage_pct,
            "estimated_minutes": round(self.execution_plan.estimated_selected_seconds / 60, 1),
        }
