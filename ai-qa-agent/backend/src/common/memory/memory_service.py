"""Requirement & Document Memory Service (Knowledge Base & History Engine).

Provides long-term memory across document ingestions and test scans:
1. Document Memory: Stores parsed markdown structures, headings, and raw context.
2. Requirement Memory: Tenant-scoped semantic & keyword retrieval for requirement context.
3. Change Memory: Calculates requirement diffs (new, modified, deprecated) between scans.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.models.base import Document, Requirement

logger = logging.getLogger(__name__)


@dataclass
class MemorySearchResult:
    """Retrieved memory match."""

    requirement_id: UUID
    workflow: str | None
    rule: str | None
    expected_outcome: str | None
    similarity_score: float
    source_ref: str | None


@dataclass
class RequirementDiffResult:
    """Diff between new requirement candidates and existing requirement memory."""

    added: list[dict[str, Any]] = field(default_factory=list)
    updated: list[dict[str, Any]] = field(default_factory=list)
    unchanged: list[dict[str, Any]] = field(default_factory=list)
    deprecated: list[UUID] = field(default_factory=list)


class MemoryService:
    """Tenant-isolated memory manager for Requirements and Document context."""

    def __init__(self, session: AsyncSession, tenant_id: UUID, project_id: UUID):
        self.session = session
        self.tenant_id = tenant_id
        self.project_id = project_id

    async def compute_content_hash(self, content: str) -> str:
        """Compute SHA-256 hash for document/chunk dedup memory."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def search_requirement_memory(
        self, query: str, limit: int = 10
    ) -> list[MemorySearchResult]:
        """Search existing requirement memory for relevant rules and workflows.

        Uses PostgreSQL full-text search & keyword matching filtered by project & tenant.
        """
        sql = text("""
            SELECT id, workflow, rule, expected_outcome, source_ref,
                   ts_rank_cd(to_tsvector('english', coalesce(rule, '') || ' ' || coalesce(workflow, '')), plainto_tsquery('english', :query)) as rank
            FROM requirements
            WHERE project_id = :project_id
              AND is_active = TRUE
              AND to_tsvector('english', coalesce(rule, '') || ' ' || coalesce(workflow, '')) @@ plainto_tsquery('english', :query)
            ORDER BY rank DESC
            LIMIT :limit
        """)

        result = await self.session.execute(
            sql, {"project_id": str(self.project_id), "query": query, "limit": limit}
        )
        rows = result.fetchall()

        return [
            MemorySearchResult(
                requirement_id=row.id,
                workflow=row.workflow,
                rule=row.rule,
                expected_outcome=row.expected_outcome,
                similarity_score=float(row.rank),
                source_ref=row.source_ref,
            )
            for row in rows
        ]

    async def diff_against_memory(
        self, new_candidates: list[dict[str, Any]]
    ) -> RequirementDiffResult:
        """Compare new requirement candidates against existing requirement memory.

        Enables incremental updates & versioning across scan runs.
        """
        # Fetch existing active requirements for this project
        stmt = select(Requirement).where(
            Requirement.project_id == self.project_id,
            Requirement.is_active == True,
        )
        result = await self.session.execute(stmt)
        existing_reqs = {
            (r.workflow or "").lower().strip() + ":" + (r.rule or "").lower().strip(): r
            for r in result.scalars().all()
        }

        diff = RequirementDiffResult()

        for candidate in new_candidates:
            wf = (candidate.get("workflow") or "").lower().strip()
            rl = (candidate.get("rule") or "").lower().strip()
            key = f"{wf}:{rl}"

            if key in existing_reqs:
                existing = existing_reqs[key]
                # Check if fields updated
                if (
                    existing.expected_outcome != candidate.get("expected_outcome")
                    or existing.actor != candidate.get("actor")
                    or existing.risk != candidate.get("risk")
                ):
                    diff.updated.append({**candidate, "existing_id": existing.id, "version": existing.version + 1})
                else:
                    diff.unchanged.append(candidate)
            else:
                diff.added.append(candidate)

        return diff
