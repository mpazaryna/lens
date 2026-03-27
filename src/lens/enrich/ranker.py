"""Article ranking using any LLM provider with structured tool use."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field

from lens.providers.base import LLMProvider


@dataclass(frozen=True)
class RankingResult:
    """Result of ranking a single article."""

    success: bool
    source: str
    title: str
    score: float = 0.0
    confidence: float = 0.0
    reasoning: str = ""
    categories: list[str] = field(default_factory=list)
    estimated_read_time: int = 0
    error: str | None = None


# Tool definition for structured scoring output (Anthropic format, converted per-provider)
SCORE_TOOL = {
    "name": "score_article",
    "description": "Score an article's relevance and quality on a 0-10 scale.",
    "input_schema": {
        "type": "object",
        "properties": {
            "score": {
                "type": "number",
                "description": "Relevance score from 0 (irrelevant) to 10 (must-read)",
            },
            "confidence": {
                "type": "number",
                "description": "Confidence in the score from 0.0 to 1.0",
            },
            "reasoning": {
                "type": "string",
                "description": "Brief explanation of the score",
            },
            "categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Content categories (e.g., 'ai', 'security', 'policy')",
            },
            "estimated_read_time": {
                "type": "integer",
                "description": "Estimated reading time in minutes",
            },
        },
        "required": ["score", "confidence", "reasoning", "categories", "estimated_read_time"],
    },
}

RANKING_PROMPT = """Score this article for relevance and quality.
Consider: technical depth, timeliness, actionability, and clarity.

Title: {title}
Summary: {summary}

Use the score_article tool to provide your structured assessment."""


async def rank_article(
    title: str,
    summary: str,
    source: str,
    provider: LLMProvider,
) -> RankingResult:
    """Rank a single article using structured tool use.

    Args:
        title: Article title.
        summary: Article summary text.
        source: Source identifier.
        provider: LLM provider to use.

    Returns:
        RankingResult with structured score.
    """
    start = time.monotonic()
    try:
        response = await provider.complete_with_tools(
            prompt=RANKING_PROMPT.format(title=title, summary=summary),
            tools=[SCORE_TOOL],
            tool_choice={"type": "tool", "name": "score_article"},
            max_tokens=512,
        )

        # Look for the tool call in the response
        for tc in response.tool_calls:
            if tc.name == "score_article":
                data = tc.arguments
                return RankingResult(
                    success=True,
                    source=source,
                    title=title,
                    score=float(data["score"]),
                    confidence=float(data["confidence"]),
                    reasoning=str(data["reasoning"]),
                    categories=list(data.get("categories", [])),
                    estimated_read_time=int(data.get("estimated_read_time", 0)),
                )

        return RankingResult(
            success=False,
            source=source,
            title=title,
            error="No tool use response from model",
        )
    except Exception as e:
        return RankingResult(
            success=False,
            source=source,
            title=title,
            error=str(e),
        )


async def rank_batch(
    articles: list[dict],
    provider: LLMProvider,
    concurrency: int = 5,
) -> list[RankingResult]:
    """Rank multiple articles concurrently.

    Args:
        articles: List of dicts with 'title', 'summary', 'source' keys.
        provider: LLM provider to use.
        concurrency: Max concurrent calls.

    Returns:
        List of RankingResult sorted by score descending.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def _rank_one(article: dict) -> RankingResult:
        async with semaphore:
            return await rank_article(
                title=article["title"],
                summary=article["summary"],
                source=article["source"],
                provider=provider,
            )

    tasks = [_rank_one(a) for a in articles]
    results = list(await asyncio.gather(*tasks))

    return sorted(results, key=lambda r: r.score, reverse=True)
