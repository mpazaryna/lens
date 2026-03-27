"""Article summarization using the Anthropic API."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

import anthropic


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
    api_key: str,
    model: str = "claude-sonnet-4-20250514",
) -> SummaryResult:
    """Summarize a single article using the Anthropic API.

    Args:
        text: Clean article text to summarize.
        source: Source identifier (filename, URL, etc.).
        api_key: Anthropic API key.
        model: Model to use for summarization.

    Returns:
        SummaryResult with the summary or error.
    """
    client = anthropic.AsyncAnthropic(api_key=api_key)

    start = time.monotonic()
    try:
        message = await client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": SUMMARIZE_PROMPT.format(text=text[:15000]),
                }
            ],
        )

        elapsed = (time.monotonic() - start) * 1000

        summary = message.content[0].text if message.content else None

        return SummaryResult(
            success=True,
            source=source,
            summary=summary,
            model=model,
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
    api_key: str,
    model: str = "claude-sonnet-4-20250514",
    concurrency: int = 5,
) -> list[SummaryResult]:
    """Summarize multiple articles concurrently.

    Args:
        articles: List of (text, source) tuples.
        api_key: Anthropic API key.
        model: Model to use.
        concurrency: Max concurrent API calls.

    Returns:
        List of SummaryResult for each article.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def _summarize_one(text: str, source: str) -> SummaryResult:
        async with semaphore:
            return await summarize_article(text, source, api_key, model)

    tasks = [_summarize_one(text, source) for text, source in articles]
    return list(await asyncio.gather(*tasks))
