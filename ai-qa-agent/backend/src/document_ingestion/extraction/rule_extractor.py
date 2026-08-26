"""Rule-Based Requirement Extractor.

Performs deterministic, rule-based extraction on parsed document chunks:
1. Column-mapping for structured tables (Actor, Precondition, Steps, Expected Result, Risk).
2. Pattern extraction for Given/When/Then & bulleted functional rules.
3. Ambiguity detection (flags missing preconditions, vague words: "should", "etc.", "appropriate").
4. Risk & Confidence scoring.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from src.document_ingestion.parsers.base import ParsedChunk


@dataclass
class ExtractedRequirementCandidate:
    """A requirement candidate extracted by rules before persistence."""

    actor: str | None = None
    workflow: str | None = None
    rule: str | None = None
    precondition: str | None = None
    expected_outcome: str | None = None
    description: str | None = None
    risk: str = "medium"  # critical | high | medium | low
    confidence: float = 0.80  # 0.00 to 1.00
    ambiguity_flags: list[str] = field(default_factory=list)
    source_ref: str | None = None
    extraction_method: str = "rule"


class RuleBasedRequirementExtractor:
    """Deterministic requirement extractor operating on document chunks."""

    # Keywords flagging ambiguous or untestable requirements
    AMBIGUITY_KEYWORDS = [
        "should",
        "etc",
        "and so on",
        "appropriate",
        "as needed",
        "possibly",
        "tbd",
        "to be decided",
        "fast",
        "user-friendly",
    ]

    # Keyword mapping for risk scoring
    RISK_KEYWORDS = {
        "critical": ["payment", "auth", "security", "delete", "destroy", "critical", "login", "admin", "p0"],
        "high": ["checkout", "permission", "role", "create", "update", "high", "p1"],
        "medium": ["filter", "search", "export", "view", "medium", "p2"],
        "low": ["color", "theme", "footer", "ui", "alignment", "low", "p3"],
    }

    def extract_from_chunks(
        self, chunks: list[ParsedChunk], source_name: str
    ) -> list[ExtractedRequirementCandidate]:
        """Extract requirements from all document chunks using rules."""
        candidates: list[ExtractedRequirementCandidate] = []

        for chunk in chunks:
            if chunk.chunk_type == "table" and chunk.table_data:
                table_reqs = self._extract_from_table(chunk.table_data, source_name, chunk.section_title)
                candidates.extend(table_reqs)

            elif chunk.content:
                text_reqs = self._extract_from_text(chunk.content, source_name, chunk.section_title)
                candidates.extend(text_reqs)

        return candidates

    def _extract_from_table(
        self, table_rows: list[dict[str, str]], source_name: str, section_title: str | None
    ) -> list[ExtractedRequirementCandidate]:
        """Extract requirements from structured table rows (e.g. Excel / Word tables)."""
        results: list[ExtractedRequirementCandidate] = []

        for idx, row in enumerate(table_rows, start=1):
            # Map column names dynamically
            actor = self._find_column_value(row, ["user", "actor", "role", "user(s)"])
            precondition = self._find_column_value(row, ["precondition", "pre-condition", "prerequisite"])
            steps = self._find_column_value(row, ["step(s)", "steps", "action", "procedure"])
            expected = self._find_column_value(row, ["expected_output", "expected_result", "expected", "outcome"])
            desc = self._find_column_value(row, ["test_case_description", "description", "requirement", "rule", "objective"])
            tc_id = self._find_column_value(row, ["test_case_id", "req_id", "id"])

            workflow = section_title or "General Workflow"

            if desc or expected or steps:
                rule_text = desc or steps or "Validated behavior"
                candidate = ExtractedRequirementCandidate(
                    actor=actor or "Authorized User",
                    workflow=workflow,
                    rule=rule_text,
                    precondition=precondition,
                    expected_outcome=expected,
                    description=f"Steps: {steps}" if steps else desc,
                    source_ref=f"{source_name}#{tc_id or f'Row-{idx}'}",
                    extraction_method="rule",
                )
                self._enrich_risk_and_ambiguity(candidate)
                results.append(candidate)

        return results

    def _extract_from_text(
        self, text: str, source_name: str, section_title: str | None
    ) -> list[ExtractedRequirementCandidate]:
        """Extract requirements from markdown text using Given/When/Then & bullet rules."""
        results: list[ExtractedRequirementCandidate] = []
        workflow = section_title or "Functional Requirement"

        # Pattern 1: Given / When / Then scenarios
        gwt_pattern = re.compile(
            r"given\s+(.*?)\s+when\s+(.*?)\s+then\s+(.*?)(?=\n\n|given|\Z)",
            re.IGNORECASE | re.DOTALL,
        )

        for match in gwt_pattern.finditer(text):
            given_clause, when_clause, then_clause = match.groups()
            candidate = ExtractedRequirementCandidate(
                actor="System User",
                workflow=workflow,
                rule=f"When {when_clause.strip()}",
                precondition=f"Given {given_clause.strip()}",
                expected_outcome=f"Then {then_clause.strip()}",
                description=match.group(0).strip(),
                source_ref=f"{source_name}#{workflow}",
                extraction_method="rule",
            )
            self._enrich_risk_and_ambiguity(candidate)
            results.append(candidate)

        # Pattern 2: Bullet points stating system requirements ("The system must...", "User can...")
        bullet_pattern = re.compile(r"^[•\*\-\d+\.]\s+(.*(?:must|shall|should|can|will).*)$", re.MULTILINE | re.IGNORECASE)

        for match in bullet_pattern.finditer(text):
            statement = match.group(1).strip()
            if len(statement) > 15:
                candidate = ExtractedRequirementCandidate(
                    actor="User",
                    workflow=workflow,
                    rule=statement,
                    expected_outcome="System enforces stated requirement",
                    description=statement,
                    source_ref=f"{source_name}#{workflow}",
                    extraction_method="rule",
                )
                self._enrich_risk_and_ambiguity(candidate)
                results.append(candidate)

        return results

    def _find_column_value(self, row: dict[str, str], possible_keys: list[str]) -> str | None:
        """Find row value matching any possible column key."""
        for k in possible_keys:
            if k in row and row[k]:
                return row[k].strip()
        # Fallback to key substring match
        for key, val in row.items():
            for p in possible_keys:
                if p in key and val:
                    return val.strip()
        return None

    def _enrich_risk_and_ambiguity(self, candidate: ExtractedRequirementCandidate) -> None:
        """Calculate risk rating and flag ambiguity issues."""
        combined_text = f"{candidate.workflow} {candidate.rule} {candidate.expected_outcome or ''}".lower()

        # Risk assignment
        assigned_risk = "medium"
        for level, keywords in self.RISK_KEYWORDS.items():
            if any(kw in combined_text for kw in keywords):
                assigned_risk = level
                break
        candidate.risk = assigned_risk

        # Ambiguity detection
        flags = []
        if not candidate.precondition:
            flags.append("missing_precondition")
        if not candidate.expected_outcome or len(candidate.expected_outcome) < 5:
            flags.append("vague_expected_outcome")

        for kw in self.AMBIGUITY_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", combined_text):
                flags.append(f"ambiguous_term:{kw}")

        candidate.ambiguity_flags = flags

        # Confidence calculation (rule-based score)
        base_confidence = 0.85
        if "missing_precondition" in flags:
            base_confidence -= 0.10
        if "vague_expected_outcome" in flags:
            base_confidence -= 0.15
        if any(f.startswith("ambiguous_term") for f in flags):
            base_confidence -= 0.10

        candidate.confidence = round(max(0.30, base_confidence), 2)
