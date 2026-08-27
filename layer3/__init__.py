"""Layer 3 - Test Intelligence (HLD 4.3).

Turns Layer 1's Requirement[] into a test strategy, test cases with steps and
expected results, a coverage map, a prioritised execution plan and test data
requirements. Deterministic and offline.
"""

from layer3.contracts import TestCase, TestPlan, TestStrategy
from layer3.pipeline import build_test_plan, plan_from_document

__all__ = ["TestCase", "TestPlan", "TestStrategy", "build_test_plan", "plan_from_document"]
