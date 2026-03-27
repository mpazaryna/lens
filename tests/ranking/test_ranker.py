"""Tests for article ranker."""

from unittest.mock import AsyncMock

import pytest

from lens.providers.base import LLMResponse, ToolCall
from lens.ranking.ranker import RankingResult, rank_article, rank_batch


def _make_mock_provider(score: float = 8.5, confidence: float = 0.9) -> AsyncMock:
    """Create a mock LLM provider that returns a tool call."""
    provider = AsyncMock()
    provider.model_name = "test-model"
    provider.complete_with_tools = AsyncMock(
        return_value=LLMResponse(
            model="test-model",
            tool_calls=[
                ToolCall(
                    name="score_article",
                    arguments={
                        "score": score,
                        "confidence": confidence,
                        "reasoning": "Test reasoning",
                        "categories": ["tech", "ai"],
                        "estimated_read_time": 5,
                    },
                )
            ],
        )
    )
    return provider


@pytest.mark.asyncio
class TestRankArticle:
    """Tests for rank_article function."""

    async def test_returns_structured_score(self) -> None:
        provider = _make_mock_provider(8.5, 0.9)
        result = await rank_article(
            title="Test Article",
            summary="A great article about AI",
            source="test.md",
            provider=provider,
        )

        assert result.success is True
        assert result.score == 8.5
        assert result.confidence == 0.9
        assert result.reasoning == "Test reasoning"
        assert result.categories == ["tech", "ai"]
        assert result.estimated_read_time == 5

    async def test_passes_tool_definition(self) -> None:
        provider = _make_mock_provider()
        await rank_article(
            title="Test", summary="Test", source="test.md", provider=provider
        )

        call_kwargs = provider.complete_with_tools.call_args.kwargs
        assert call_kwargs["tool_choice"] == {"type": "tool", "name": "score_article"}
        assert len(call_kwargs["tools"]) == 1
        assert call_kwargs["tools"][0]["name"] == "score_article"

    async def test_handles_provider_error(self) -> None:
        provider = AsyncMock()
        provider.model_name = "test-model"
        provider.complete_with_tools = AsyncMock(side_effect=Exception("Rate limited"))

        result = await rank_article(
            title="Test", summary="Test", source="test.md", provider=provider
        )

        assert result.success is False
        assert "Rate limited" in result.error

    async def test_handles_no_tool_use_response(self) -> None:
        provider = AsyncMock()
        provider.model_name = "test-model"
        provider.complete_with_tools = AsyncMock(
            return_value=LLMResponse(text="Just text, no tool call", model="test-model")
        )

        result = await rank_article(
            title="Test", summary="Test", source="test.md", provider=provider
        )

        assert result.success is False
        assert "No tool use response" in result.error

    async def test_result_is_frozen(self) -> None:
        result = RankingResult(success=True, source="test.md", title="Test", score=8.0)
        with pytest.raises(AttributeError):
            result.score = 5.0  # type: ignore[misc]


@pytest.mark.asyncio
class TestRankBatch:
    """Tests for rank_batch function."""

    async def test_ranks_multiple_articles(self) -> None:
        call_count = 0

        async def _mock_complete_with_tools(**kwargs):
            nonlocal call_count
            call_count += 1
            return LLMResponse(
                model="test-model",
                tool_calls=[
                    ToolCall(
                        name="score_article",
                        arguments={
                            "score": 10.0 - call_count,
                            "confidence": 0.9,
                            "reasoning": "Good",
                            "categories": ["tech"],
                            "estimated_read_time": 3,
                        },
                    )
                ],
            )

        provider = AsyncMock()
        provider.model_name = "test-model"
        provider.complete_with_tools = _mock_complete_with_tools

        articles = [
            {"title": f"Article {i}", "summary": f"Summary {i}", "source": f"art{i}.md"}
            for i in range(3)
        ]

        results = await rank_batch(articles, provider=provider)
        assert len(results) == 3

    async def test_returns_sorted_by_score_descending(self) -> None:
        scores = [3.0, 9.0, 6.0]
        call_count = 0

        async def _mock_complete_with_tools(**kwargs):
            nonlocal call_count
            idx = call_count
            call_count += 1
            return LLMResponse(
                model="test-model",
                tool_calls=[
                    ToolCall(
                        name="score_article",
                        arguments={
                            "score": scores[idx],
                            "confidence": 0.8,
                            "reasoning": "OK",
                            "categories": [],
                            "estimated_read_time": 2,
                        },
                    )
                ],
            )

        provider = AsyncMock()
        provider.model_name = "test-model"
        provider.complete_with_tools = _mock_complete_with_tools

        articles = [
            {"title": f"Article {i}", "summary": f"Summary {i}", "source": f"art{i}.md"}
            for i in range(3)
        ]

        results = await rank_batch(articles, provider=provider)
        result_scores = [r.score for r in results]
        assert result_scores == sorted(result_scores, reverse=True)
