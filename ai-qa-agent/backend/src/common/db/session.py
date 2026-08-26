"""Database session management with tenant-scoped RLS.

Every query goes through here. The tenant context is set as a PostgreSQL
session variable, and RLS policies enforce isolation at the database level.
This is the backstop — even if the application layer has a bug, RLS prevents
cross-tenant data access (HLD §7.6, QA-07).
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from src.common.config.settings import get_settings


def _create_engine():
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        echo=settings.db_echo,
        pool_pre_ping=True,  # Detect stale connections
    )


engine = _create_engine()
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_tenant_session(tenant_id: UUID) -> AsyncGenerator[AsyncSession, None]:
    """Create a session with tenant context set for RLS enforcement.

    This is the ONLY way to get a database session in the application.
    The tenant_id is set as a PostgreSQL session variable that RLS policies
    reference. Handlers cannot construct a query without going through this.

    Usage:
        async with get_tenant_session(tenant_id) as session:
            result = await session.execute(select(Requirement))
            # RLS automatically filters to this tenant's data
    """
    async with async_session_factory() as session:
        # Set the tenant context for this session — RLS policies use this
        await session.execute(
            text("SET LOCAL app.current_tenant = :tenant_id"),
            {"tenant_id": str(tenant_id)},
        )
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_system_session() -> AsyncGenerator[AsyncSession, None]:
    """Session without tenant scoping — for system-level operations only.

    Use sparingly: tenant onboarding, migrations, health checks.
    RLS policies still apply but with no tenant set, so tenant-scoped
    tables return zero rows (safe by default).
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
