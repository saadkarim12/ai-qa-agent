"""Hybrid Requirement Extractor (Rule-Based + Claude 3.5 LLM).

Combines deterministic rule extraction with Claude LLM reasoning:
1. Structured tables & explicit bullet lists extracted via rules ($0 cost, 100% deterministic).
2. Unstructured narrative prose enriched via Claude LLM for deep business rules & subtle ambiguity rationale.
3. Automatically falls back to 100% rule extraction if LLM is unavailable (offline demo mode).
"""

from __future__ import annotations

import logging
from typing import Any, Optional
from pydantic import BaseModel, Field

from src.document_ingestion.parsers.base import ParsedChunk
from src.document_ingestion.extraction.rule_extractor import (
    ExtractedRequirementCandidate,
    RuleBasedRequirementExtractor,
)
from src.model_gateway.gateway import ModelGateway

logger = logging.getLogger(__name__)


class LLMRequirementItem(BaseModel):
    actor: str = Field(description="Actor or user role (e.g. Registered User, Admin)")
    workflow: str = Field(description="Workflow name (e.g. Authentication, Billing, Role Management)")
    rule: str = Field(description="Concise functional requirement statement")
    precondition: Optional[str] = Field(default=None, description="Preconditions required before step")
    expected_outcome: str = Field(description="Expected system behavior")
    risk: str = Field(default="medium", description="critical | high | medium | low")
    ambiguity_explanation: Optional[str] = Field(default=None, description="Detailed explanation if requirement is ambiguous or untestable")



class LLMExtractionSchema(BaseModel):
    requirements: list[LLMRequirementItem]


class HybridRequirementExtractor:
    """Combines Rule-based parsing with Model Gateway LLM enrichment."""

    def __init__(self, model_gateway: ModelGateway | None = None):
        self.rule_extractor = RuleBasedRequirementExtractor()
        self.gateway = model_gateway or ModelGateway()

    async def extract(
        self, chunks: list[ParsedChunk], source_name: str
    ) -> list[ExtractedRequirementCandidate]:
        """Run hybrid extraction pipeline over document chunks."""
        # 1. Deterministic Rule Extraction
        rule_candidates = self.rule_extractor.extract_from_chunks(chunks, source_name)

        # 2. If ModelGateway is available, process narrative chunks via Claude
        llm_candidates: list[ExtractedRequirementCandidate] = []
        if self.gateway.is_available:
            narrative_chunks = [c for c in chunks if c.chunk_type in ("text", "markdown") and len(c.content) > 100]
            for chunk in narrative_chunks[:5]:  # Limit for speed & cost
                prompt = (
                    f"Analyze this software document section and extract testable functional requirements:\n\n"
                    f"Document: {source_name}\n"
                    f"Section: {chunk.section_title or 'General'}\n"
                    f"Content:\n{chunk.content[:2000]}\n"
                )
                res = await self.gateway.extract_structured(prompt, LLMExtractionSchema)
                if res and res.requirements:
                    for item in res.requirements:
                        flags = []
                        if item.ambiguity_explanation:
                            flags.append(f"llm_ambiguity:{item.ambiguity_explanation}")
                        if not item.precondition:
                            flags.append("missing_precondition")

                        llm_candidates.append(
                            ExtractedRequirementCandidate(
                                actor=item.actor,
                                workflow=item.workflow or chunk.section_title or "General",
                                rule=item.rule,
                                precondition=item.precondition,
                                expected_outcome=item.expected_outcome,
                                description=f"{item.rule} -> {item.expected_outcome}",
                                risk=item.risk.lower(),
                                confidence=0.92,  # High LLM confidence
                                ambiguity_flags=flags,
                                source_ref=f"{source_name}#{chunk.section_title or 'Section'}",
                                extraction_method="hybrid_llm",
                            )
                        )

        # 3. Deduplicate and merge candidates
        merged = self._merge_candidates(rule_candidates, llm_candidates)
        return merged

    def _merge_candidates(
        self,
        rule_reqs: list[ExtractedRequirementCandidate],
        llm_reqs: list[ExtractedRequirementCandidate],
    ) -> list[ExtractedRequirementCandidate]:
        """Merge rule and LLM candidates, preferring structured table data."""
        seen_keys = set()
        final_list: list[ExtractedRequirementCandidate] = []

        # Keep all rule reqs from tables (structured data)
        for r in rule_reqs:
            key = f"{(r.workflow or '').lower()}:{(r.rule or '').lower()[:40]}"
            seen_keys.add(key)
            final_list.append(r)

        # Add LLM reqs if not duplicate
        for r in llm_reqs:
            key = f"{(r.workflow or '').lower()}:{(r.rule or '').lower()[:40]}"
            if key not in seen_keys:
                seen_keys.add(key)
                final_list.append(r)

        return final_list
