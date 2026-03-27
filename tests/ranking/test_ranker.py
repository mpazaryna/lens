"""Tests for article ranker."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lens_py.ranking.ranker import RankingResult, rank_article, rank_batch


def _make_tool_use_response(score: float, confidence: float) -> MagicMock:
    """Create a mock Anthropic response with tool use."""
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "score_article"
    tool_block.input = {
        "score": score,
        "confidence": confidence,
        "reasoning": "Test reasoning",
        "categories": ["tech", "ai"],
        "estimated_read_time": 5,
    }

    message = MagicMock()
    message.content = [tool_block]
    return message


@pytest.mark.asyncio
class TestRankArticle:
    """Tests for rank_article function."""

    async def test_returns_structured_score(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_tool_use_response(8.5, 0.9)
        )

        with patch("lens_py.ranking.ranker.anthropic.AsyncAnthropic", return_value=mock_client):
            result = await rank_article(
                title="Test Article",
                summary="A great article about AI",
                source="test.md",
                api_key="test-key",
            )

        assert result.success is True
        assert result.score == 8.5
        assert result.confidence == 0.9
        assert result.reasoning == "Test reasoning"
        assert result.categories == ["tech", "ai"]
        assert result.estimated_read_time == 5

    async def test_uses_tool_choice(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            return_value=_make_tool_use_response(7.0, 0.8)
        )

        with patch("lens_py.ranking.ranker.anthropic.AsyncAnthropic", return_value=mock_client):
            await rank_article(
                title="Test", summary="Test", source="test.md", api_key="test-key"
            )

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["tool_choice"] == {"type": "tool", "name": "score_article"}
        assert len(call_kwargs["tools"]) == 1

    async def test_handles_api_error(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=Exception("Rate limited"))

        with patch("lens_py.ranking.ranker.anthropic.AsyncAnthropic", return_value=mock_client):
            result = await rank_article(
                title="Test", summary="Test", source="test.md", api_key="test-key"
            )

        assert result.success is False
        assert "Rate limited" in result.error

    async def test_handles_no_tool_use_response(self) -> None:
        mock_message = MagicMock()
        text_block = MagicMock()
        text_block.type = "text"
        mock_message.content = [text_block]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch("lens_py.ranking.ranker.anthropic.AsyncAnthropic", return_value=mock_client):
            result = await rank_article(
                title="Test", summary="Test", source="test.md", api_key="test-key"
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
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            side_effect=[
                _make_tool_use_response(8.0, 0.9),
                _make_tool_use_response(6.0, 0.7),
                _make_tool_use_response(9.0, 0.95),
            ]
        )

        articles = [
            {"title": f"Article {i}", "summary": f"Summary {i}", "source": f"art{i}.md"}
            for i in range(3)
        ]

        with patch("lens_py.ranking.ranker.anthropic.AsyncAnthropic", return_value=mock_client):
            results = await rank_batch(articles, api_key="test-key")

        assert len(results) == 3

    async def test_returns_sorted_by_score_descending(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(
            side_effect=[
                _make_tool_use_response(3.0, 0.5),
                _make_tool_use_response(9.0, 0.9),
                _make_tool_use_response(6.0, 0.7),
            ]
        )

        articles = [
            {"title": f"Article {i}", "summary": f"Summary {i}", "source": f"art{i}.md"}
            for i in range(3)
        ]

        with patch("lens_py.ranking.ranker.anthropic.AsyncAnthropic", return_value=mock_client):
            results = await rank_batch(articles, api_key="test-key")

        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)
