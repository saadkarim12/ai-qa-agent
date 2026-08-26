"""Application configuration — single source of truth for all settings.

Reads from environment variables with sensible defaults for local dev.
Production values come from Azure Key Vault / environment injection.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All configuration flows through here. Never read os.environ directly."""

    # --- Application ---
    app_name: str = "ai-qa-agent"
    app_env: str = Field(default="development", description="development | staging | production")
    debug: bool = False
    api_prefix: str = "/v1"
    cors_origins: list[str] = ["http://localhost:3000"]

    # --- Database (PostgreSQL 16 with RLS) ---
    database_url: str = Field(
        default="postgresql+asyncpg://qaagent:qaagent@localhost:5432/qaagent",
        description="Async PostgreSQL connection string",
    )
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_echo: bool = False

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Azure Blob Storage ---
    azure_storage_connection_string: str = ""
    azure_storage_container: str = "documents"
    azure_evidence_container: str = "evidence"

    # --- Model Gateway (LLM) ---
    anthropic_api_key: str = ""
    default_model: str = "claude-sonnet-4-20250514"
    model_max_tokens: int = 4096
    model_temperature: float = 0.0  # Deterministic extraction

    # --- Temporal ---
    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "ai-qa-agent"
    temporal_task_queue: str = "document-ingestion"

    # --- Security ---
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    model_config = {"env_prefix": "QA_", "env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    """Cached singleton — settings are immutable after startup."""
    return Settings()
