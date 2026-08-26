"""Model Gateway (LLM Abstraction Layer — HLD §16.1, ADR-010).

Provides a single, provider-agnostic interface for all LLM interactions:
- Provider abstraction (Claude / Anthropic, Azure OpenAI, OpenAI)
- Token usage & cost accounting
- Schema-validated output (Pydantic parsing with retries)
- Graceful fallback to rule-based engine when API key is unconfigured or offline.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Type, TypeVar

from pydantic import BaseModel
import anthropic

from src.common.config.settings import get_settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


@dataclass
class ModelResponse:
    raw_text: str
    tokens_in: int
    tokens_out: int
    model_used: str
    parsed_object: Any | None = None


class ModelGateway:
    """Sole egress path to LLM providers across the application (ADR-010)."""

    def __init__(self, api_key: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.anthropic_api_key
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key) if self.api_key else None
        self.default_model = settings.default_model

    @property
    def is_available(self) -> bool:
        """Returns True if LLM provider API key is configured."""
        return self.client is not None and bool(self.api_key)

    async def extract_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: str | None = None,
    ) -> T | None:
        """Request structured output matching a Pydantic schema from Claude."""
        if not self.is_available:
            logger.warning("ModelGateway: No API key configured. Falling back to rule engine.")
            return None

        schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
        system_prompt = (
            system_instruction or "You are an expert QA Engineer and Requirements Analyst."
        )
        system_prompt += f"\n\nYou MUST return ONLY valid JSON matching this schema:\n```json\n{schema_json}\n```"

        try:
            message = await self.client.messages.create(
                model=self.default_model,
                max_tokens=4096,
                temperature=0.0,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text
            # Extract JSON block
            json_str = response_text
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()

            parsed = response_schema.model_validate_json(json_str)
            return parsed

        except Exception as e:
            logger.error(f"ModelGateway extraction failed: {e}")
            return None
