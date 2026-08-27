"""Layer 3 tests.

The rules path is the whole product here, so the tests cover what it promises:
the five HLD 4.3 outputs, honest coverage, and arithmetic anyone can re-check.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layer1.contracts import Requirement, Risk, Source
from layer3.contracts import TestCategory
from layer3.design import TestDesigner
from layer3.pipeline import build_test_plan, plan_from_document
from layer3.risk import WEIGHTS, build_execution_plan, score_tests
from layer1.pipeline import extract_requirements

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA = os.path.join(ROOT, "sample_data", "qa")
STORIES_MD = os.path.join(QA, "01_happy_path_stories.md")
STORIES_PDF = os.path.join(QA, "18_stories.pdf")
VAGUE = os.path.join(QA, "02_ambiguous_requirements.md")


def _req(**over):
    base = dict(
        actor="Registered Customer", workflow="Login",
        rule="The customer submits a valid password",
        expected_outcome="The dashboard is displayed",
        risk=Risk.CRITICAL, source=Source.DOCUMENT, source_ref="US-1/AC1", confidence=0.95,
    )
    base.update(over)
    return Requirement(**base)


def _design(reqs):
    cases, data = TestDesigner().design(reqs)
    score_tests(cases, reqs)
    return cases, data


# --- generation ------------------------------------------------------------

def test_every_clear_requirement_gets_a_positive_test():
    cases, _ = _design([_req()])
    assert any(c.category is TestCategory.POSITIVE for c in cases)


def test_a_stated_threshold_produces_boundary_tests():
    cases, _ = _design([_req(rule="The password must be at least 12 characters")])
    boundary = [c for c in cases if c.category is TestCategory.BOUNDARY]
    assert len(boundary) == 2
    titles = " ".join(c.title for c in boundary)
    assert "12" in titles and "11" in titles


def test_written_numbers_are_understood():
    cases, _ = _design([_req(rule="The customer submits a wrong password five times")])
    assert any("5 times" in c.title for c in cases if c.category is TestCategory.BOUNDARY)


def test_an_already_negative_rule_is_not_negated_again():
    """'submits an email that is not registered' must not become 'not unregistered'."""
    cases, _ = _design([_req(rule="The customer submits an email that is not registered")])
    assert not [c for c in cases if c.category is TestCategory.NEGATIVE]


def test_negation_is_named_not_generic():
    cases, _ = _design([_req(rule="The customer submits a valid password")])
    neg = [c for c in cases if c.category is TestCategory.NEGATIVE]
    assert len(neg) == 1
    assert "invalid" in neg[0].title


def test_a_precondition_produces_an_unmet_precondition_test():
    cases, _ = _design([_req(precondition="the account is active")])
    assert any(c.category is TestCategory.PRECONDITION for c in cases)


def test_permission_wording_produces_a_role_test():
    cases, _ = _design([_req(
        actor="Administrator", workflow="Audit",
        rule="They open /admin", expected_outcome="The audit log is displayed")])
    assert any(c.category is TestCategory.PERMISSION for c in cases)


def test_vague_requirement_yields_a_question_not_a_guessed_test():
    """The core honesty rule: never invent an expected result."""
    cases, _ = _design([_req(
        rule="The system should handle errors appropriately",
        expected_outcome="The system should handle errors appropriately",
        ambiguity_flags=["unspecified behaviour 'handle' - what happens is not stated",
                         "non-committal modality - no mandatory obligation stated"])])
    assert len(cases) == 1
    assert cases[0].category is TestCategory.CLARIFICATION
    assert cases[0].needs_clarification
    assert cases[0].clarification_reasons
    assert cases[0].status == "Blocked"


def test_every_test_traces_back_to_a_requirement():
    cases, _ = _design(extract_requirements(STORIES_MD, use_llm=False).requirements)
    assert cases
    assert all(c.requirement_refs for c in cases)


def test_test_data_requirements_are_derived_and_linked():
    cases, data = _design([_req(rule="The customer submits a valid card", workflow="Checkout")])
    assert data
    payment = [d for d in data if d.id == "TD-PAYMENT"]
    assert payment and payment[0].used_by


# --- scoring ---------------------------------------------------------------

def test_weights_sum_to_one():
    assert round(sum(WEIGHTS.values()), 6) == 1.0


def test_breakdown_sums_to_the_score():
    cases, _ = _design(extract_requirements(STORIES_MD, use_llm=False).requirements)
    for c in cases:
        if c.category is TestCategory.CLARIFICATION:
            continue
        assert round(sum(c.score_breakdown.values()), 1) == pytest.approx(c.score, abs=0.15)


def test_critical_outranks_low_all_else_equal():
    crit, _ = _design([_req(risk=Risk.CRITICAL, source_ref="A")])
    low, _ = _design([_req(risk=Risk.LOW, source_ref="B")])
    assert crit[0].score > low[0].score


def test_confidence_does_not_lower_a_score():
    """An earlier revision ranked well-written requirements lower. It must not recur."""
    high, _ = _design([_req(confidence=0.99, source_ref="A")])
    low, _ = _design([_req(confidence=0.30, source_ref="B")])
    assert high[0].score == low[0].score


# --- plan ------------------------------------------------------------------

def test_budget_defers_the_lowest_ranked_tests():
    plan = plan_from_document(STORIES_MD, budget_minutes=5)
    ex = plan.execution_plan
    assert ex.selected_tests < ex.total_tests
    assert ex.estimated_selected_seconds <= 5 * 60
    selected = [r for r in ex.order if r.selected]
    deferred = [r for r in ex.order if not r.selected]
    assert min(r.score for r in selected) >= max(r.score for r in deferred)


def test_plan_is_ordered_by_score():
    plan = plan_from_document(STORIES_MD)
    scores = [r.score for r in plan.execution_plan.order]
    assert scores == sorted(scores, reverse=True)


def test_clarifications_are_never_scheduled():
    plan = plan_from_document(VAGUE)
    scheduled = {r.test_id for r in plan.execution_plan.order}
    for t in plan.test_cases:
        if t.category is TestCategory.CLARIFICATION:
            assert t.id not in scheduled


# --- coverage --------------------------------------------------------------

def test_clarification_only_requirement_is_not_counted_as_covered():
    plan = plan_from_document(VAGUE)
    assert plan.coverage.unclear_refs
    assert plan.coverage.coverage_pct < 50.0


def test_clear_document_reaches_full_coverage():
    plan = plan_from_document(STORIES_MD)
    assert plan.coverage.coverage_pct == 100.0
    assert plan.coverage.uncovered_refs == []


def test_confirmed_and_inferred_are_counted_separately():
    plan = plan_from_document(STORIES_MD)
    c = plan.coverage
    assert c.confirmed_requirements == c.requirements_total
    assert c.inferred_requirements == 0


# --- end to end ------------------------------------------------------------

def test_pdf_and_markdown_produce_the_same_plan():
    """The PDF structure parser must not change the outcome."""
    md = plan_from_document(STORIES_MD)
    pdf = plan_from_document(STORIES_PDF)
    assert md.stats["total"] == pdf.stats["total"]
    assert md.coverage.coverage_pct == pdf.coverage.coverage_pct
    assert [t.title for t in md.test_cases] == [t.title for t in pdf.test_cases]


def test_plan_is_deterministic():
    a = plan_from_document(STORIES_MD, budget_minutes=10)
    b = plan_from_document(STORIES_MD, budget_minutes=10)
    assert a.model_dump() == b.model_dump()


def test_plan_uses_no_model():
    assert plan_from_document(STORIES_MD).generator == "rules"


def test_strategy_declares_what_it_cannot_score():
    st = plan_from_document(STORIES_MD).strategy
    assert st.unavailable_signals
    assert any("failure_history" in u for u in st.unavailable_signals)
    assert any("not yet bound to page elements" in l for l in st.limitations)


def test_empty_document_produces_an_empty_plan_not_a_crash():
    plan = plan_from_document(os.path.join(QA, "06_empty.md"))
    assert plan.test_cases == []
    assert plan.coverage.coverage_pct == 0.0
    assert any("No requirements" in w for w in plan.warnings)


# --- Layer 2 -> Layer 3 integration ----------------------------------------

def test_discovered_and_document_requirements_merge_into_one_plan(crawled):
    """HLD 3.4: two ingestion strategies, one Behaviour Model, one pipeline."""
    amap, discovered = crawled
    rs = extract_requirements(STORIES_PDF, use_llm=False)
    plan = build_test_plan(rs, budget_minutes=20, app_map=amap, discovered=discovered)

    assert plan.coverage.requirements_total == len(rs.requirements) + len(discovered)
    assert plan.coverage.confirmed_requirements == len(rs.requirements)
    assert plan.coverage.inferred_requirements == len(discovered)
    assert plan.stats["total"] > len(rs.requirements)


def test_binding_attaches_real_locators(crawled):
    amap, discovered = crawled
    rs = extract_requirements(STORIES_PDF, use_llm=False)
    plan = build_test_plan(rs, app_map=amap, discovered=discovered)

    bound = [t for t in plan.test_cases if t.binding == "bound"]
    assert bound, "expected at least some tests to bind to real elements"
    step = next(s for t in bound for s in t.steps if s.locator)
    assert step.target_path
    assert step.locator


def test_unbound_tests_keep_business_language_rather_than_a_guessed_selector(crawled):
    """A plausible-looking wrong selector is worse than an honest gap."""
    amap, discovered = crawled
    rs = extract_requirements(STORIES_MD, use_llm=False)
    plan = build_test_plan(rs, app_map=amap, discovered=discovered)

    for t in plan.test_cases:
        if t.binding == "business-language":
            assert all(s.locator is None for s in t.steps)


def test_without_an_application_map_nothing_is_bound():
    plan = plan_from_document(STORIES_MD)
    assert all(t.binding == "business-language" for t in plan.test_cases)
    assert all(s.locator is None for t in plan.test_cases for s in t.steps)


def test_strategy_limitation_changes_once_tests_are_bound(crawled):
    amap, discovered = crawled
    rs = extract_requirements(STORIES_MD, use_llm=False)
    unbound = build_test_plan(rs)
    bound = build_test_plan(rs, app_map=amap, discovered=discovered)

    assert any("not yet bound" in l for l in unbound.strategy.limitations)
    assert not any("not yet bound" in l for l in bound.strategy.limitations)


def test_binding_counts_are_reported(crawled):
    amap, discovered = crawled
    rs = extract_requirements(STORIES_MD, use_llm=False)
    plan = build_test_plan(rs, app_map=amap, discovered=discovered)
    assert any(w.startswith("binding:") for w in plan.warnings)
