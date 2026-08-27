"""Layer 3 - coverage mapping.

Coverage is the number a customer will quote back at you, so it has to be
honest in two specific ways:

  * BR-03 - requirements the customer confirmed are counted separately from
    behaviour that was merely inferred. A blended figure overstates certainty.
  * A requirement 'covered' only by a request for clarification is not covered.
    It is counted, reported and listed separately.
"""

from typing import Dict, List

from layer1.contracts import Requirement, Source
from layer3.contracts import CoverageMap, TestCase, TestCategory, WorkflowCoverage


def build_coverage(requirements: List[Requirement], tests: List[TestCase]) -> CoverageMap:
    real_cover: Dict[str, int] = {}
    unclear_only: Dict[str, bool] = {}
    by_category: Dict[str, int] = {}

    for t in tests:
        by_category[t.category.value] = by_category.get(t.category.value, 0) + 1
        for ref in t.requirement_refs:
            if t.category is TestCategory.CLARIFICATION:
                unclear_only.setdefault(ref, True)
            else:
                real_cover[ref] = real_cover.get(ref, 0) + 1
                unclear_only[ref] = False

    total = len(requirements)
    covered = sum(1 for r in requirements if real_cover.get(r.source_ref, 0) > 0)

    workflows: Dict[str, Dict[str, int]] = {}
    for r in requirements:
        w = workflows.setdefault(r.workflow, {"requirements": 0, "covered": 0, "tests": 0})
        w["requirements"] += 1
        if real_cover.get(r.source_ref, 0) > 0:
            w["covered"] += 1
        w["tests"] += real_cover.get(r.source_ref, 0)

    return CoverageMap(
        requirements_total=total,
        requirements_covered=covered,
        coverage_pct=round(100.0 * covered / total, 1) if total else 0.0,
        confirmed_requirements=sum(
            1 for r in requirements if r.source in (Source.JIRA, Source.DOCUMENT)
        ),
        inferred_requirements=sum(1 for r in requirements if r.source is Source.DISCOVERED),
        by_workflow=[
            WorkflowCoverage(
                workflow=name,
                requirements=v["requirements"],
                requirements_covered=v["covered"],
                tests=v["tests"],
                coverage_pct=round(100.0 * v["covered"] / v["requirements"], 1)
                if v["requirements"] else 0.0,
            )
            for name, v in sorted(workflows.items())
        ],
        by_category=by_category,
        uncovered_refs=[
            r.source_ref for r in requirements
            if real_cover.get(r.source_ref, 0) == 0 and not unclear_only.get(r.source_ref)
        ],
        unclear_refs=[
            r.source_ref for r in requirements if unclear_only.get(r.source_ref)
        ],
    )
