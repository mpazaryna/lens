"""Integration tests for Ollama provider against a local instance.

Requires a running Ollama instance at localhost:11434 with qwen2.5-coder:7b.
"""

import pytest

from lens.providers.ollama import OllamaProvider

MODEL = "qwen2.5-coder:7b"


@pytest.fixture
def provider() -> OllamaProvider:
    return OllamaProvider(model=MODEL)


@pytest.mark.integration
@pytest.mark.asyncio
class TestOllamaComplete:
    """Test basic completion against local Ollama."""

    async def test_returns_text(self, provider: OllamaProvider) -> None:
        response = await provider.complete(
            prompt="What is 2 + 2? Answer with just the number.",
            max_tokens=32,
            temperature=0.0,
        )
        assert response.text is not None
        assert "4" in response.text

    async def test_model_name_matches(self, provider: OllamaProvider) -> None:
        assert provider.model_name == MODEL

    async def test_returns_usage_stats(self, provider: OllamaProvider) -> None:
        response = await provider.complete(
            prompt="Say hello.",
            max_tokens=16,
        )
        assert response.usage.get("input_tokens", 0) > 0
        assert response.usage.get("output_tokens", 0) > 0

    async def test_respects_max_tokens(self, provider: OllamaProvider) -> None:
        response = await provider.complete(
            prompt="Write a very long essay about the history of computing.",
            max_tokens=20,
            temperature=0.0,
        )
        # Should be relatively short due to token limit
        assert response.text is not None
        assert len(response.text.split()) < 100


@pytest.mark.integration
@pytest.mark.asyncio
class TestOllamaToolUse:
    """Test structured JSON output (simulated tool use) against local Ollama."""

    async def test_returns_tool_call_with_score(self, provider: OllamaProvider) -> None:
        tools = [
            {
                "name": "score_article",
                "description": "Score an article on a 0-10 scale.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "score": {
                            "type": "number",
                            "description": "Score from 0 to 10",
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Brief explanation",
                        },
                    },
                    "required": ["score", "reasoning"],
                },
            }
        ]

        response = await provider.complete_with_tools(
            prompt="Score this article: 'Python 3.12 adds major performance improvements'",
            tools=tools,
            tool_choice={"type": "tool", "name": "score_article"},
            max_tokens=256,
        )

        assert len(response.tool_calls) == 1
        tc = response.tool_calls[0]
        assert tc.name == "score_article"
        assert "score" in tc.arguments
        assert isinstance(tc.arguments["score"], (int, float))
        assert 0 <= tc.arguments["score"] <= 10
        assert "reasoning" in tc.arguments
