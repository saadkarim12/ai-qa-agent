"""Layer 1 - Requirements Intelligence (HLD 4.1).

Converts customer context (Jira exports, user-story documents, specifications,
spreadsheets) into a normalised, traceable, schema-validated Requirement[].
"""

from layer1.contracts import Requirement, RequirementSet, Risk, Source
from layer1.pipeline import extract_requirements

__all__ = ["Requirement", "RequirementSet", "Risk", "Source", "extract_requirements"]
