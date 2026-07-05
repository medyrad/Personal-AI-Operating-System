"""AI Gateway.

The one place in the codebase that knows how to construct a model client. Every agent
asks this module for a model instead of importing `anthropic` or reading environment
variables directly — so swapping providers, adding retries, or adding cost tracking later
touches one file, not every agent.
"""

import os

from pydantic_ai.models.anthropic import AnthropicModel

DEFAULT_MODEL_NAME = "claude-sonnet-4-6"


class GatewayNotConfigured(RuntimeError):
    """Raised when an agent tries to run but no API key is configured."""


def get_model(model_name: str = DEFAULT_MODEL_NAME) -> AnthropicModel:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise GatewayNotConfigured(
            "ANTHROPIC_API_KEY is not set. Add it to .env to enable AI agents; "
            "see apps/backend/.env.example."
        )
    return AnthropicModel(model_name)
