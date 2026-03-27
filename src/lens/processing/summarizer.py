"""Article summarization using any LLM provider."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from lens.providers.base import LLMProvider


@dataclass(frozen=True)
class SummaryResult:
    """Result of summarizing an article."""

    success: bool
    source: str
    summary: str | None = None
    model: str | None = None
    processing_time_ms: float | None = None
    error: str | None = None


SUMMARIZE_PROMPT = """Summarize the following article in 2-3 concise paragraphs.
Focus on the key points, decisions, and implications.
Do not add opinions or information not in the source text.

Article:
{text}"""


async def summarize_article(
    text: str,
    source: str,
    provider: LLMProvider,
) -> SummaryResult:
    """Summarize a single article.

    Args:
        text: Clean article text to summarize.
        source: Source identifier (filename, URL, etc.).
        provider: LLM provider to use.

    Returns:
        SummaryResult with the summary or error.
    """
    start = time.monotonic()
    try:
        response = await provider.complete(
            prompt=SUMMARIZE_PROMPT.format(text=text[:15000]),
            max_tokens=1024,
        )

        elapsed = (time.monotonic() - start) * 1000

        return SummaryResult(
            success=True,
            source=source,
            summary=response.text,
            model=provider.model_name,
            processing_time_ms=elapsed,
        )
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        return SummaryResult(
            success=False,
            source=source,
            error=str(e),
            processing_time_ms=elapsed,
        )


async def summarize_batch(
    articles: list[tuple[str, str]],
    provider: LLMProvider,
    concurrency: int = 5,
) -> list[SummaryResult]:
    """Summarize multiple articles concurrently.

    Args:
        articles: List of (text, source) tuples.
        provider: LLM provider to use.
        concurrency: Max concurrent calls.

    Returns:
        List of SummaryResult for each article.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def _summarize_one(text: str, source: str) -> SummaryResult:
        async with semaphore:
            return await summarize_article(text, source, provider)

    tasks = [_summarize_one(text, source) for text, source in articles]
    return list(await asyncio.gather(*tasks))
