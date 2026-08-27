"""Layer 1 — Requirements Intelligence: the output contract.

HLD 4.1 defines the output of this layer as:

    Requirement[] records with {actor, workflow, rule, precondition,
    expected_outcome, risk, source, source_ref, confidence, ambiguity_flags}

This module IS that contract. Two rules from the HLD are enforced here rather
than left to convention:

  * BR-03 / C-06 - `source` is a typed enum, so a discovered behaviour can
    never be rendered as a confirmed requirement. It is a type-level
    distinction, not a naming convention.
  * ADR-005 - every extractor returns objects validated against this schema.
    Nothing downstream ever parses free text.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Risk(str, Enum):
    """Business/technical risk of the requirement (BRD 10.1)."""

    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Source(str, Enum):
    """Where the requirement came from (BRD 10.1, BR-02).

    JIRA and DOCUMENT are customer-confirmed. DISCOVERED is inferred by the
    agent from observed behaviour and must never be presented as confirmed.
    """

    JIRA = "jira"
    DOCUMENT = "document"
    DISCOVERED = "discovered"


class Requirement(BaseModel):
    """One normalised, traceable requirement. The unit of Layer 1's output."""

    # extra="forbid" stops an LLM from inventing fields into the contract.
    model_config = ConfigDict(extra="forbid", use_enum_values=False)

    actor: str = Field(description="Who performs the action, e.g. 'Registered User'")
    workflow: str = Field(description="Business workflow, e.g. 'Checkout'")
    rule: str = Field(description="The testable requirement statement")
    precondition: Optional[str] = Field(
        default=None, description="What must be true before the rule applies"
    )
    expected_outcome: str = Field(description="Observable behaviour that proves the rule holds")
    risk: Risk = Field(default=Risk.MEDIUM)
    source: Source = Field(description="jira | document | discovered")
    source_ref: str = Field(description="Traceability pointer, e.g. 'PROJ-1423' or 'stories.md#US-004'")
    confidence: float = Field(ge=0.0, le=1.0, description="Extraction confidence. NOT evidence (BR-09).")
    ambiguity_flags: List[str] = Field(
        default_factory=list,
        description="Why this requirement is vague, contradictory or untestable",
    )

    @field_validator("actor", "workflow", "rule", "expected_outcome")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("must not be empty")
        return v

    @field_validator("precondition")
    @classmethod
    def _blank_precondition_is_none(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        return v or None

    @property
    def is_confirmed(self) -> bool:
        """BR-03: only customer-supplied sources are confirmed requirements."""
        return self.source in (Source.JIRA, Source.DOCUMENT)

    @property
    def is_ambiguous(self) -> bool:
        return bool(self.ambiguity_flags)


class RequirementSet(BaseModel):
    """Layer 1's full output for one ingested document, plus provenance."""

    model_config = ConfigDict(extra="forbid")

    document_name: str
    document_kind: str
    extractor: str = Field(description="rules | llm | llm+rules")
    requirements: List[Requirement] = Field(default_factory=list)
    warnings: List[str] = Field(
        default_factory=list,
        description="Partial-failure surface: unparsed pages, skipped blocks (HLD 4.1)",
    )
    extraction_methods: List[str] = Field(
        default_factory=list,
        description="Per-requirement origin ('rules' | 'llm'), aligned to `requirements` by index. "
                    "Kept at set level so the Requirement contract stays exactly the HLD fields.",
    )

    @property
    def stats(self) -> dict:
        reqs = self.requirements
        by_risk = {r.value: 0 for r in Risk}
        by_source = {s.value: 0 for s in Source}
        for r in reqs:
            by_risk[r.risk.value] += 1
            by_source[r.source.value] += 1
        avg_conf = round(sum(r.confidence for r in reqs) / len(reqs), 2) if reqs else 0.0
        methods = {}
        for m in self.extraction_methods:
            methods[m] = methods.get(m, 0) + 1
        return {
            "total": len(reqs),
            "by_method": methods,
            "by_risk": by_risk,
            "by_source": by_source,
            "ambiguous": sum(1 for r in reqs if r.is_ambiguous),
            "confirmed": sum(1 for r in reqs if r.is_confirmed),
            "avg_confidence": avg_conf,
        }
