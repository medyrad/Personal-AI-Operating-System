"""AI Gateway.

The one place in the codebase that knows how to construct a model client. Every agent
asks this module for a model instead of importing `anthropic` or reading environment
variables directly — so swapping providers, adding retries, or adding cost tracking later
touches one file, not every agent.
"""

import os
from typing import Literal, cast

from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel

ProviderName = Literal["auto", "anthropic", "openai"]

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
DEFAULT_OPENAI_MODEL = "gpt-4.1"
PROVIDER_ENV = "AI_PROVIDER"


class GatewayNotConfigured(RuntimeError):
    """Raised when an agent tries to run but no API key is configured."""


def _provider_from_env() -> ProviderName:
    provider = os.environ.get(PROVIDER_ENV, "auto").lower()
    if provider in {"auto", "anthropic", "openai"}:
        return cast(ProviderName, provider)
    raise GatewayNotConfigured(
        "AI_PROVIDER must be one of: auto, anthropic, openai. See apps/backend/.env.example."
    )


def _anthropic_model(model_name: str | None = None) -> AnthropicModel:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise GatewayNotConfigured(
            "ANTHROPIC_API_KEY is not set. Add it to .env to enable AI agents; "
            "see apps/backend/.env.example."
        )
    return AnthropicModel(model_name or os.environ.get("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL))


def _openai_model(model_name: str | None = None) -> OpenAIChatModel:
    if not os.environ.get("OPENAI_API_KEY"):
        raise GatewayNotConfigured(
            "OPENAI_API_KEY is not set. Add it to .env to enable OpenAI-backed agents; "
            "see apps/backend/.env.example."
        )
    configured = model_name or os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    return OpenAIChatModel(configured)


def get_model(model_name: str | None = None) -> Model:
    provider = _provider_from_env()
    if provider == "anthropic":
        return _anthropic_model(model_name)
    if provider == "openai":
        return _openai_model(model_name)

    if os.environ.get("ANTHROPIC_API_KEY"):
        return _anthropic_model(model_name)
    if os.environ.get("OPENAI_API_KEY"):
        return _openai_model(model_name)

    raise GatewayNotConfigured(
        "No AI provider is configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env; "
        "optionally set AI_PROVIDER=anthropic or AI_PROVIDER=openai."
    )
