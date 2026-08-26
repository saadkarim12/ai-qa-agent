"""SQLAlchemy base model and mixins for all domain entities.

Every tenant-scoped table uses TenantScopedMixin, which adds the tenant_id
column and is the target for RLS policies. This is structural enforcement
of multi-tenancy — you can't accidentally create a table without it.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    ForeignKey,
    Numeric,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    declared_attr,
    relationship,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    type_annotation_map = {
        dict: JSONB,
        list: JSONB,
        uuid.UUID: PG_UUID(as_uuid=True),
    }


class TimestampMixin:
    """Adds created_at and updated_at to any model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TenantScopedMixin:
    """Adds tenant_id — the column that RLS policies filter on.

    Every table that stores tenant data MUST use this mixin.
    The RLS policy checks: tenant_id = current_setting('app.current_tenant')
    """

    @declared_attr
    def tenant_id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("tenants.id"),
            nullable=False,
            index=True,
        )


class VersionedMixin:
    """Optimistic concurrency + change tracking between scans."""

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


# =============================================================================
# Domain Models
# =============================================================================


class Tenant(Base, TimestampMixin):
    """Top-level isolation boundary. One per customer organisation."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="active", nullable=False
    )  # active | suspended | archived
    tier: Mapped[str] = mapped_column(
        String(20), default="standard", nullable=False
    )  # standard | enterprise | private
    region: Mapped[str | None] = mapped_column(String(50))
    data_residency: Mapped[str | None] = mapped_column(String(50))
    retention_days: Mapped[int] = mapped_column(Integer, default=90)
    quotas: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    projects: Mapped[list["Project"]] = relationship(back_populates="tenant")


class Project(Base, TenantScopedMixin, TimestampMixin):
    """A QA engagement for one application. Belongs to exactly one tenant."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    application_url: Mapped[str | None] = mapped_column(Text)
    environment_type: Mapped[str] = mapped_column(
        String(20), default="staging"
    )  # development | staging | production
    status: Mapped[str] = mapped_column(
        String(20), default="active"
    )  # active | paused | archived
    default_profile_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True))

    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="projects")
    requirements: Mapped[list["Requirement"]] = relationship(back_populates="project")
    documents: Mapped[list["Document"]] = relationship(back_populates="project")


class Document(Base, TenantScopedMixin, TimestampMixin):
    """An uploaded document being processed through the ingestion pipeline."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Azure Blob path: tenant/{id}/project/{id}/documents/{id}/{filename}
    content_hash: Mapped[str] = mapped_column(String(64))  # SHA-256

    # Pipeline status
    status: Mapped[str] = mapped_column(
        String(20), default="uploaded"
    )  # uploaded | processing | completed | failed
    total_pages: Mapped[int | None] = mapped_column(Integer)
    processed_pages: Mapped[int] = mapped_column(Integer, default=0)
    requirements_extracted: Mapped[int] = mapped_column(Integer, default=0)
    parse_warnings: Mapped[list] = mapped_column(JSONB, default=list)
    parse_errors: Mapped[list] = mapped_column(JSONB, default=list)
    workflow_id: Mapped[str | None] = mapped_column(String(255))  # Temporal workflow ID

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="documents")


class Requirement(Base, TenantScopedMixin, TimestampMixin, VersionedMixin):
    """A single testable requirement extracted from customer context.

    This is the core output of Layer 1 and the input to everything downstream.
    The schema matches HLD §4.1 and BRD §10.1 exactly.
    """

    __tablename__ = "requirements"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True
    )

    # --- Source traceability (BR-02, BR-03) ---
    source: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # jira | document | discovered
    source_ref: Mapped[str | None] = mapped_column(
        Text
    )  # Jira key, document page, discovery URL
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("documents.id")
    )

    # --- Requirement content (BRD §10.1) ---
    actor: Mapped[str | None] = mapped_column(Text)
    workflow: Mapped[str | None] = mapped_column(Text)
    rule: Mapped[str | None] = mapped_column(Text)
    precondition: Mapped[str | None] = mapped_column(Text)
    expected_outcome: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)  # Full text if unstructured

    # --- Classification ---
    risk: Mapped[str | None] = mapped_column(
        String(10)
    )  # critical | high | medium | low
    confidence: Mapped[float] = mapped_column(
        Numeric(3, 2), default=0.0
    )  # 0.00–1.00
    ambiguity_flags: Mapped[list] = mapped_column(JSONB, default=list)

    # --- Extraction metadata ---
    extraction_method: Mapped[str] = mapped_column(
        String(20), default="rule"
    )  # rule | llm | hybrid
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="requirements")


class AuditEvent(Base, TenantScopedMixin):
    """Append-only audit log. Every significant action is recorded here.

    This is the audit spine the HLD references — non-negotiable for enterprise.
    """

    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    actor_type: Mapped[str] = mapped_column(String(20))  # user | agent | system
    actor_id: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False)
    before_state: Mapped[dict | None] = mapped_column(JSONB)
    after_state: Mapped[dict | None] = mapped_column(JSONB)
    correlation_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
