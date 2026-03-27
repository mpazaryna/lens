"""Tests for article summarizer."""

from unittest.mock import AsyncMock

import pytest

from lens.enrich.summarizer import SummaryResult, summarize_article
from lens.providers.base import LLMResponse


def _make_mock_provider(text: str = "This is a summary.") -> AsyncMock:
    """Create a mock LLM provider."""
    provider = AsyncMock()
    provider.model_name = "test-model"
    provider.complete = AsyncMock(return_value=LLMResponse(text=text, model="test-model"))
    return provider


@pytest.mark.asyncio
class TestSummarizeArticle:
    """Tests for summarize_article function."""

    async def test_returns_summary_on_success(self) -> None:
        provider = _make_mock_provider("This is a summary.")
        result = await summarize_article(
            text="Some article text",
            source="test.md",
            provider=provider,
        )

        assert result.success is True
        assert result.summary == "This is a summary."
        assert result.source == "test.md"
        assert result.model == "test-model"
        assert result.processing_time_ms is not None
        assert result.processing_time_ms >= 0

    async def test_returns_error_on_provider_failure(self) -> None:
        provider = AsyncMock()
        provider.model_name = "test-model"
        provider.complete = AsyncMock(side_effect=Exception("API error"))

        result = await summarize_article(
            text="Some text",
            source="test.md",
            provider=provider,
        )

        assert result.success is False
        assert "API error" in result.error
        assert result.summary is None

    async def test_truncates_long_text(self) -> None:
        provider = _make_mock_provider("Summary")
        long_text = "word " * 100000

        await summarize_article(
            text=long_text,
            source="test.md",
            provider=provider,
        )

        # Verify the text was truncated in the provider call
        call_args = provider.complete.call_args
        prompt = call_args.kwargs["prompt"]
        assert len(prompt) < len(long_text)

    async def test_result_is_frozen(self) -> None:
        result = SummaryResult(success=True, source="test.md", summary="test")
        with pytest.raises(AttributeError):
            result.summary = "modified"  # type: ignore[misc]

    async def test_calls_provider_complete(self) -> None:
        provider = _make_mock_provider()
        await summarize_article(text="text", source="src", provider=provider)
        provider.complete.assert_awaited_once()
