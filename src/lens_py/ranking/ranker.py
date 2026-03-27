"""Article ranking using Anthropic API with structured tool use."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field

import anthropic


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


# Tool definition for structured scoring output
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
    api_key: str,
    model: str = "claude-sonnet-4-20250514",
) -> RankingResult:
    """Rank a single article using Anthropic API tool use.

    Args:
        title: Article title.
        summary: Article summary text.
        source: Source identifier.
        api_key: Anthropic API key.
        model: Model to use.

    Returns:
        RankingResult with structured score.
    """
    client = anthropic.AsyncAnthropic(api_key=api_key)

    start = time.monotonic()
    try:
        message = await client.messages.create(
            model=model,
            max_tokens=512,
            tools=[SCORE_TOOL],
            tool_choice={"type": "tool", "name": "score_article"},
            messages=[
                {
                    "role": "user",
                    "content": RANKING_PROMPT.format(title=title, summary=summary),
                }
            ],
        )

        # Extract tool use result
        for block in message.content:
            if block.type == "tool_use" and block.name == "score_article":
                data = block.input
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
    api_key: str,
    model: str = "claude-sonnet-4-20250514",
    concurrency: int = 5,
) -> list[RankingResult]:
    """Rank multiple articles concurrently.

    Args:
        articles: List of dicts with 'title', 'summary', 'source' keys.
        api_key: Anthropic API key.
        model: Model to use.
        concurrency: Max concurrent API calls.

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
                api_key=api_key,
                model=model,
            )

    tasks = [_rank_one(a) for a in articles]
    results = list(await asyncio.gather(*tasks))

    # Sort by score descending
    return sorted(results, key=lambda r: r.score, reverse=True)
