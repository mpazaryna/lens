"""Tests for article summarizer."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lens.processing.summarizer import SummaryResult, summarize_article


@pytest.mark.asyncio
class TestSummarizeArticle:
    """Tests for summarize_article function."""

    async def test_returns_summary_on_success(self) -> None:
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="This is a summary.")]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch("lens.processing.summarizer.anthropic.AsyncAnthropic", return_value=mock_client):
            result = await summarize_article(
                text="Some article text",
                source="test.md",
                api_key="test-key",
            )

        assert result.success is True
        assert result.summary == "This is a summary."
        assert result.source == "test.md"
        assert result.processing_time_ms is not None
        assert result.processing_time_ms >= 0

    async def test_returns_error_on_api_failure(self) -> None:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))

        with patch("lens.processing.summarizer.anthropic.AsyncAnthropic", return_value=mock_client):
            result = await summarize_article(
                text="Some text",
                source="test.md",
                api_key="test-key",
            )

        assert result.success is False
        assert "API error" in result.error
        assert result.summary is None

    async def test_truncates_long_text(self) -> None:
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Summary")]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        long_text = "word " * 100000  # Very long text

        with patch("lens.processing.summarizer.anthropic.AsyncAnthropic", return_value=mock_client):
            await summarize_article(
                text=long_text,
                source="test.md",
                api_key="test-key",
            )

        # Verify the text was truncated in the API call
        call_args = mock_client.messages.create.call_args
        content = call_args.kwargs["messages"][0]["content"]
        assert len(content) < len(long_text)

    async def test_result_is_frozen(self) -> None:
        result = SummaryResult(success=True, source="test.md", summary="test")
        with pytest.raises(AttributeError):
            result.summary = "modified"  # type: ignore[misc]
