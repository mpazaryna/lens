"""Tests for provider registry."""

import pytest

from lens.errors import ConfigError
from lens.providers.anthropic import AnthropicProvider
from lens.providers.ollama import OllamaProvider
from lens.providers.openai import OpenAIProvider
from lens.providers.registry import create_provider


class TestCreateProvider:
    """Tests for create_provider factory."""

    def test_creates_anthropic_provider(self) -> None:
        provider = create_provider(
            "anthropic", model="claude-sonnet-4-20250514", api_key="test-key"
        )
        assert isinstance(provider, AnthropicProvider)
        assert provider.model_name == "claude-sonnet-4-20250514"

    def test_creates_openai_provider(self) -> None:
        provider = create_provider("openai", model="gpt-4o", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)
        assert provider.model_name == "gpt-4o"

    def test_creates_openai_with_custom_base_url(self) -> None:
        provider = create_provider(
            "openai", model="gpt-4o", api_key="key", base_url="https://custom.api.com"
        )
        assert isinstance(provider, OpenAIProvider)
        assert provider.base_url == "https://custom.api.com"

    def test_creates_ollama_provider(self) -> None:
        provider = create_provider("ollama", model="llama3.1")
        assert isinstance(provider, OllamaProvider)
        assert provider.model_name == "llama3.1"

    def test_ollama_default_base_url(self) -> None:
        provider = create_provider("ollama", model="llama3.1")
        assert isinstance(provider, OllamaProvider)
        assert provider.base_url == "http://localhost:11434"

    def test_ollama_custom_base_url(self) -> None:
        provider = create_provider("ollama", model="llama3.1", base_url="http://remote:11434")
        assert isinstance(provider, OllamaProvider)
        assert provider.base_url == "http://remote:11434"

    def test_case_insensitive(self) -> None:
        provider = create_provider("Anthropic", model="claude-sonnet-4-20250514", api_key="key")
        assert isinstance(provider, AnthropicProvider)

    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ConfigError, match="Unknown provider"):
            create_provider("unknown", model="model")

    def test_unknown_provider_lists_supported(self) -> None:
        with pytest.raises(ConfigError, match="anthropic, openai, ollama"):
            create_provider("gemini", model="model")
