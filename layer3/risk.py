"""Layer 3 - deterministic risk scoring and execution ordering.

HLD 4.3 specifies the shape of the formula:

    score = w1*criticality + w2*change_impact + w3*failure_history
          + w4*coverage_gap + w5*recency_decay

Three of those terms need layers that do not exist yet: change_impact needs
source control (Layer 6), failure_history and recency_decay need executed runs
(Layer 4). Rather than quietly inventing values for them, the weights are
redistributed across the signals we genuinely have, and the missing ones are
declared in the strategy so nobody mistakes this for the full model.

Every number here is arithmetic. `score_breakdown` on each test carries the
per-term contribution so the ordering can be explained to a customer, argued
with, and corrected (ADR-012).
"""

from typing import Dict, List

from layer1.contracts import Requirement, Risk
from layer3.contracts import (
    ExecutionPlan,
    PlannedTest,
    Priority,
    TestCase,
    TestCategory,
)

WEIGHTS: Dict[str, float] = {
    "criticality": 0.50,       # how bad is it if this is broken
    "defect_likelihood": 0.30,  # how often this kind of test finds a real break
    "coverage_gap": 0.20,       # how thin the safety net is around it
}

# Extraction confidence is deliberately NOT a scoring term. An earlier revision
# scored `1 - confidence`, which ranked well-written requirements *lower* than
# badly-written ones - the opposite of useful. Confidence is reported on each
# requirement as metadata; it does not drive execution order.

UNAVAILABLE = [
    "change_impact - needs source-control history (Layer 6)",
    "failure_history - needs executed runs (Layer 4)",
    "recency_decay - needs run history (Layer 4)",
]

FORMULA = (
    "score = 100 x (0.50*criticality + 0.30*defect_likelihood + 0.20*coverage_gap)"
)

_CRITICALITY = {Risk.CRITICAL: 1.0, Risk.HIGH: 0.75, Risk.MEDIUM: 0.45, Risk.LOW: 0.20}

# How often each kind of test historically finds a real defect. These are
# starting priors, to be replaced by measured yield once Layer 4 reports
# outcomes - which is the point at which this stops being guesswork.
_DEFECT_LIKELIHOOD = {
    TestCategory.BOUNDARY: 0.95,
    TestCategory.NEGATIVE: 0.90,
    TestCategory.PERMISSION: 0.90,
    TestCategory.REQUIRED_FIELD: 0.85,
    TestCategory.PRECONDITION: 0.70,
    TestCategory.STATE_TRANSITION: 0.65,
    TestCategory.POSITIVE: 0.50,
    TestCategory.NAVIGATION: 0.45,
    TestCategory.CLARIFICATION: 0.0,
}

_BANDS = ((70.0, Priority.P1), (55.0, Priority.P2), (40.0, Priority.P3))


def score_tests(tests: List[TestCase], requirements: List[Requirement]) -> List[TestCase]:
    """Assign score, breakdown and priority to every test. Mutates in place."""
    # A requirement covered by one test is a thinner safety net than one
    # covered by five, so a thin requirement lifts its tests up the order.
    tests_per_ref: Dict[str, int] = {}
    for t in tests:
        for ref in t.requirement_refs:
            tests_per_ref[ref] = tests_per_ref.get(ref, 0) + 1

    for t in tests:
        covering = max((tests_per_ref.get(r, 1) for r in t.requirement_refs), default=1)

        criticality = _CRITICALITY.get(t.risk, 0.45)
        likelihood = _DEFECT_LIKELIHOOD.get(t.category, 0.5)
        coverage_gap = 1.0 / float(covering)

        breakdown = {
            "criticality": round(100 * WEIGHTS["criticality"] * criticality, 1),
            "defect_likelihood": round(100 * WEIGHTS["defect_likelihood"] * likelihood, 1),
            "coverage_gap": round(100 * WEIGHTS["coverage_gap"] * coverage_gap, 1),
        }
        total = round(sum(breakdown.values()), 1)

        t.score = min(100.0, max(0.0, total))
        t.score_breakdown = breakdown
        t.priority = _band(t.score)
        if t.category is not TestCategory.CLARIFICATION:
            t.status = "Ready"
    return tests


def _band(score: float) -> Priority:
    for threshold, priority in _BANDS:
        if score >= threshold:
            return priority
    return Priority.P4


def build_execution_plan(tests: List[TestCase], budget_minutes: int = None) -> ExecutionPlan:
    """Order by score, then fit to the run budget.

    Clarification items are never scheduled: they are questions for a human,
    not tests. They keep their score so their urgency is visible.
    """
    runnable = [t for t in tests if t.category is not TestCategory.CLARIFICATION]
    ordered = sorted(runnable, key=lambda t: (-t.score, t.id))

    budget_seconds = budget_minutes * 60 if budget_minutes else None
    cumulative = 0
    selected_seconds = 0
    rows: List[PlannedTest] = []

    for i, t in enumerate(ordered, start=1):
        cumulative += t.estimated_seconds
        fits = budget_seconds is None or cumulative <= budget_seconds
        if fits:
            selected_seconds = cumulative
        rows.append(PlannedTest(
            rank=i,
            test_id=t.id,
            title=t.title,
            score=t.score,
            priority=t.priority,
            estimated_seconds=t.estimated_seconds,
            cumulative_seconds=cumulative,
            selected=fits,
        ))

    return ExecutionPlan(
        budget_minutes=budget_minutes,
        total_tests=len(rows),
        selected_tests=sum(1 for r in rows if r.selected),
        deferred_tests=sum(1 for r in rows if not r.selected),
        estimated_total_seconds=cumulative,
        estimated_selected_seconds=selected_seconds,
        order=rows,
    )
