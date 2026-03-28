"""Export formatter for processed summaries.

JSON export: one file per feed with articles array.
Obsidian export: individual markdown notes with YAML frontmatter.
Pure functions, no classes.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


def export_feed_json(feed_name: str, articles: list[dict]) -> str:
    """Export a feed's summaries as a JSON string.

    Args:
        feed_name: Feed identifier.
        articles: List of summary dicts.

    Returns:
        JSON string with feed metadata and articles array.
    """
    return json.dumps(
        {
            "feed": feed_name,
            "generated_at": datetime.now(UTC).isoformat(),
            "articles": articles,
        },
        indent=2,
    )


def export_feed_obsidian(
    feed_name: str,
    articles: list[dict],
    output_dir: Path,
) -> list[Path]:
    """Export a feed's summaries as individual Obsidian markdown notes.

    Each note has YAML frontmatter with metadata and the summary as body.

    Args:
        feed_name: Feed identifier.
        articles: List of summary dicts.
        output_dir: Directory to write notes.

    Returns:
        List of paths to written note files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    for article in articles:
        title = article.get("title", "Untitled")
        source_url = article.get("source_url", "")
        summary = article.get("summary_text", "")
        word_count = article.get("word_count", 0)
        timestamp = article.get("timestamp", "")
        date = timestamp[:10] if timestamp else ""

        frontmatter = "\n".join(
            [
                "---",
                f'title: "{title}"',
                f'source: "{source_url}"',
                f'feed: "{feed_name}"',
                f'date: "{date}"',
                f"word_count: {word_count}",
                f"tags: [lens, {feed_name}]",
                "---",
            ]
        )

        content = f"{frontmatter}\n\n{summary}\n"

        safe_name = re.sub(r"[^\w\s-]", "", title).strip()
        safe_name = re.sub(r"\s+", "-", safe_name).lower()[:80]
        filename = f"{safe_name or 'untitled'}.md"

        path = output_dir / filename
        path.write_text(content)
        paths.append(path)

    return paths


def export_all(
    processed_dir: Path,
    export_dir: Path,
    fmt: str = "json",
) -> list[Path]:
    """Export all feeds from processed data.

    Args:
        processed_dir: Directory containing per-feed processed JSON.
        export_dir: Directory to write export output.
        fmt: Export format ('json' or 'obsidian').

    Returns:
        List of paths to written export files/directories.
    """
    if not processed_dir.exists():
        return []

    export_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    for feed_dir in sorted(processed_dir.iterdir()):
        if not feed_dir.is_dir():
            continue

        articles = []
        for json_file in sorted(feed_dir.glob("*.json")):
            articles.append(json.loads(json_file.read_text()))

        if fmt == "obsidian":
            obsidian_dir = export_dir / "obsidian" / feed_dir.name
            note_paths = export_feed_obsidian(feed_dir.name, articles, obsidian_dir)
            paths.extend(note_paths)
            logger.info("Obsidian export: %s (%d notes)", feed_dir.name, len(note_paths))
        else:
            json_str = export_feed_json(feed_dir.name, articles)
            out_path = export_dir / f"{feed_dir.name}.json"
            out_path.write_text(json_str)
            paths.append(out_path)
            logger.info("JSON export: %s (%d articles)", feed_dir.name, len(articles))

    return paths
