"""Layer 3 - the pipeline.

    document -> [Layer 1] Requirement[] -> TestPlan

TestPlan carries all five HLD 4.3 outputs: strategy, test cases with steps and
expected results, coverage map, prioritised execution plan, and test data
requirements.

Layer 2 is not built yet, so tests are written in business language rather than
bound to real page elements. That is stated in the strategy's limitations
rather than left for someone to discover during execution.
"""

from typing import List, Optional

from layer1.contracts import Requirement, RequirementSet
from layer1.pipeline import extract_requirements
from layer3.contracts import TestPlan, TestStrategy
from layer3.coverage import build_coverage
from layer3.design import TestDesigner
from layer3.binder import bind
from layer3.risk import FORMULA, UNAVAILABLE, WEIGHTS, build_execution_plan, score_tests


def build_strategy(
    document_name: str, requirements: List[Requirement], plan_warnings: List[str],
    bound: bool = False,
) -> TestStrategy:
    workflows = sorted({r.workflow for r in requirements})
    unclear = [r for r in requirements if r.ambiguity_flags]
    inferred = [r for r in requirements if r.source.value == "discovered"]

    limitations = [
        "Tests are bound to page elements discovered by Layer 2. A locator that "
        "drifts should be healed from the element's fallback chain, not rewritten "
        "by hand."
        if bound else
        "Tests are written in business language. They are not yet bound to page "
        "elements, so they are not directly executable until Layer 2 supplies "
        "the application map.",
        "Coverage is measured against the requirements found in this document only. "
        "It says nothing about parts of the application the document does not describe.",
        "Defect-likelihood weights are starting priors, not measured yield. They "
        "become evidence-based once executed runs report outcomes.",
    ]
    if unclear:
        limitations.append(
            "%d of %d requirements carry ambiguity flags; those marked for "
            "clarification have no test until the wording is resolved."
            % (len(unclear), len(requirements))
        )
    doc_workflows = {r.workflow.lower() for r in requirements if r.source.value != "discovered"}
    disc_workflows = {r.workflow.lower() for r in requirements if r.source.value == "discovered"}
    if doc_workflows and disc_workflows:
        limitations.append(
            "Workflow names from the document and from discovery are not merged. "
            "The same area may appear twice under different names (for example "
            "'Customer Login' and 'Sign in'), so per-workflow counts can be split. "
            "Merging them automatically risks combining two genuinely different "
            "areas, so it is left visible rather than guessed."
        )
    if inferred:
        limitations.append(
            "%d requirements are inferred rather than customer-confirmed and are "
            "counted separately in coverage (BR-03)." % len(inferred)
        )

    return TestStrategy(
        document_name=document_name,
        scope_summary=(
            "Functional black-box test plan derived from %d requirements across "
            "%d workflow(s) in %s." % (len(requirements), len(workflows), document_name)
        ),
        workflows_in_scope=workflows,
        categories_used=[
            "positive", "negative", "boundary", "required_field",
            "permission", "precondition", "clarification",
        ],
        risk_approach=(
            "Risk-based ordering. Every test is scored deterministically and ranked; "
            "the score's terms are published with each test so the order can be "
            "challenged and corrected."
        ),
        scoring_formula=FORMULA,
        scoring_weights=dict(WEIGHTS),
        unavailable_signals=list(UNAVAILABLE),
        assumptions=[
            "A test environment is available with data that can be created and destroyed.",
            "Accounts can be provisioned for each actor named in the requirements.",
            "Testing is authorised against the supplied environment (BRD 19).",
        ],
        exclusions=[
            "Performance, security, accessibility and mobile testing (later phases).",
            "Source-code analysis - this is black-box only (BRD 30.1).",
            "Anything the supplied document does not describe.",
        ],
        limitations=limitations + plan_warnings,
        entry_criteria=[
            "Requirements ingested and reviewed.",
            "Clarification items resolved, or consciously accepted as untested.",
            "Test data fixtures provisioned.",
        ],
        exit_criteria=[
            "All P1 and P2 tests executed.",
            "No unresolved Critical failure.",
            "Coverage and any untested areas reported honestly.",
        ],
    )


def build_test_plan(
    requirement_set: RequirementSet,
    budget_minutes: Optional[int] = None,
    app_map=None,
    discovered: Optional[List[Requirement]] = None,
) -> TestPlan:
    """Requirement[] (+ optionally what Layer 2 discovered) -> the full Layer 3 output.

    Document requirements and discovered behaviour are the same contract, so
    they are simply concatenated and one pipeline runs (HLD 3.4). Where an
    application map is supplied, tests are then bound to real locators.
    """
    requirements = list(requirement_set.requirements) + list(discovered or [])
    designer = TestDesigner()
    tests, test_data = designer.design(requirements)
    score_tests(tests, requirements)

    binding_counts = None
    if app_map is not None and tests:
        binding_counts = bind(tests, app_map)

    coverage = build_coverage(requirements, tests)
    plan = build_execution_plan(tests, budget_minutes)

    warnings: List[str] = []
    if not requirements:
        warnings.append("No requirements were extracted, so no tests could be designed.")
    if coverage.uncovered_refs:
        warnings.append(
            "%d requirement(s) produced no test: %s"
            % (len(coverage.uncovered_refs), ", ".join(coverage.uncovered_refs[:5]))
        )
    if coverage.unclear_refs:
        warnings.append(
            "%d requirement(s) are too ambiguous to test and need clarification: %s"
            % (len(coverage.unclear_refs), ", ".join(coverage.unclear_refs[:5]))
        )
    if binding_counts is not None:
        warnings.append(
            "binding: %d test(s) fully bound to page elements, %d partially, %d unbound"
            % (binding_counts["bound"], binding_counts["partially_bound"],
               binding_counts["unbound"])
        )
    if plan.deferred_tests:
        warnings.append(
            "%d test(s) fall outside the %s-minute budget and are deferred."
            % (plan.deferred_tests, budget_minutes)
        )

    return TestPlan(
        strategy=build_strategy(
            requirement_set.document_name, requirements, list(requirement_set.warnings),
            bound=binding_counts is not None,
        ),
        test_cases=tests,
        coverage=coverage,
        execution_plan=plan,
        test_data=test_data,
        generator="rules",
        warnings=warnings,
    )


def plan_from_document(
    path: str, use_llm: bool = False, budget_minutes: Optional[int] = None
) -> TestPlan:
    """Document only: a file in, a full test plan out (unbound)."""
    return build_test_plan(extract_requirements(path, use_llm=use_llm), budget_minutes)


def plan_from_document_and_app(
    path: Optional[str] = None,
    url: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    budget_minutes: Optional[int] = None,
    use_llm: bool = False,
    probe_paths: Optional[List[str]] = None,
    max_pages: int = 25,
):
    """The full chain: document and/or live application -> one bound test plan.

    Either input may be omitted. With only a document you get a readable plan;
    with only a URL you get a plan from discovered behaviour alone; with both,
    the document says what *should* happen and the crawl says what the
    application *does*, which is where the interesting gaps live.
    """
    from layer1.contracts import RequirementSet

    requirement_set = (
        extract_requirements(path, use_llm=use_llm) if path
        else RequirementSet(document_name=url or "application", document_kind="none",
                            extractor="rules")
    )

    app_map = None
    discovered: List[Requirement] = []
    if url:
        from layer2.pipeline import discover
        app_map, discovered = discover(
            url, username, password,
            max_pages=max_pages,
            entry_paths=["/"] + list(probe_paths or []),
        )

    plan = build_test_plan(
        requirement_set, budget_minutes=budget_minutes,
        app_map=app_map, discovered=discovered,
    )
    return plan, app_map
