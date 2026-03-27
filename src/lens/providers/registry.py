"""Provider registry: create the right provider from configuration."""

from __future__ import annotations

from lens.providers.base import LLMProvider


def create_provider(
    provider: str,
    model: str,
    api_key: str = "",
    base_url: str | None = None,
) -> LLMProvider:
    """Create an LLM provider instance.

    Args:
        provider: Provider name ('anthropic', 'openai', 'ollama').
        model: Model identifier.
        api_key: API key (not needed for Ollama).
        base_url: Optional custom API endpoint.

    Returns:
        An LLMProvider instance.

    Raises:
        ValueError: If the provider name is not recognized.
    """
    match provider.lower():
        case "anthropic":
            from lens.providers.anthropic import AnthropicProvider

            return AnthropicProvider(api_key=api_key, model=model)

        case "openai":
            from lens.providers.openai import OpenAIProvider

            return OpenAIProvider(api_key=api_key, model=model, base_url=base_url)

        case "ollama":
            from lens.providers.ollama import OllamaProvider

            return OllamaProvider(
                model=model,
                base_url=base_url or "http://localhost:11434",
            )

        case _:
            raise ValueError(
                f"Unknown provider: '{provider}'. "
                f"Supported: anthropic, openai, ollama"
            )
