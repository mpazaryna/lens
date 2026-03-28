"""Per-feed markdown digest generator.

Reads processed JSON summaries and produces a single markdown briefing
per feed, sorted by word count descending. Pure functions, no classes.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


def generate_digest(feed_name: str, articles: list[dict]) -> str:
    """Generate a markdown digest for a single feed.

    Args:
        feed_name: Feed identifier used as the heading.
        articles: List of summary dicts from processed JSON.

    Returns:
        Markdown string with header and sorted article summaries.
    """
    now = datetime.now(UTC).isoformat()
    sorted_articles = sorted(articles, key=lambda a: a.get("word_count", 0), reverse=True)

    lines = [
        f"# {feed_name}",
        "",
        f"*Generated: {now} | {len(sorted_articles)} articles*",
        "",
    ]

    for article in sorted_articles:
        title = article.get("title", "Untitled")
        source_url = article.get("source_url", "")
        summary = article.get("summary_text", "")
        word_count = article.get("word_count", 0)
        processing_time = article.get("processing_time_ms", 0)

        lines.extend(
            [
                "---",
                "",
                f"## {title}",
                "",
                f"*Source: {source_url}*",
                f"*{word_count} words | Summarized in {processing_time / 1000:.1f}s*",
                "",
                summary,
                "",
            ]
        )

    return "\n".join(lines)


def generate_all_digests(
    processed_dir: Path,
    digest_dir: Path,
) -> list[Path]:
    """Generate digests for all feeds with processed data.

    Args:
        processed_dir: Directory containing per-feed processed JSON.
        digest_dir: Directory to write digest markdown files.

    Returns:
        List of paths to generated digest files.
    """
    if not processed_dir.exists():
        return []

    digest_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    for feed_dir in sorted(processed_dir.iterdir()):
        if not feed_dir.is_dir():
            continue

        articles = []
        for json_file in sorted(feed_dir.glob("*.json")):
            articles.append(json.loads(json_file.read_text()))

        md = generate_digest(feed_dir.name, articles)
        out_path = digest_dir / f"{feed_dir.name}.md"
        out_path.write_text(md)
        paths.append(out_path)

        logger.info("Digest: %s (%d articles)", feed_dir.name, len(articles))

    return paths
