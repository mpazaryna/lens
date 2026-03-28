"""Tests for export formatter.

Derived from gherkin.md Step 3 scenarios:
- JSON export per feed
- Obsidian markdown notes with YAML frontmatter
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from lens.output.export import export_all, export_feed_json, export_feed_obsidian

if TYPE_CHECKING:
    from pathlib import Path


SAMPLE_ARTICLES = [
    {
        "title": "AI Advances",
        "source_url": "https://example.com/ai",
        "feed_name": "lobsters",
        "summary_text": "A summary about AI advances.",
        "word_count": 800,
        "provider": "llama3.2",
        "model": "llama3.2",
        "timestamp": "2026-03-28T12:00:00Z",
        "processing_time_ms": 2100,
        "input_tokens": 200,
        "output_tokens": 50,
    },
    {
        "title": "What's New in Rust? (2026)",
        "source_url": "https://example.com/rust",
        "feed_name": "lobsters",
        "summary_text": "Rust language updates for 2026.",
        "word_count": 600,
        "provider": "llama3.2",
        "model": "llama3.2",
        "timestamp": "2026-03-28T12:01:00Z",
        "processing_time_ms": 1800,
        "input_tokens": 150,
        "output_tokens": 40,
    },
]


class TestExportFeedJson:
    """Feature: JSON export."""

    def test_json_contains_articles_array(self) -> None:
        result = json.loads(export_feed_json("lobsters", SAMPLE_ARTICLES))
        assert result["feed"] == "lobsters"
        assert len(result["articles"]) == 2

    def test_json_includes_generation_timestamp(self) -> None:
        result = json.loads(export_feed_json("lobsters", SAMPLE_ARTICLES))
        assert "generated_at" in result

    def test_empty_feed_produces_valid_json(self) -> None:
        result = json.loads(export_feed_json("empty", []))
        assert result["articles"] == []
        assert result["feed"] == "empty"


class TestExportFeedObsidian:
    """Feature: Obsidian export."""

    def test_produces_individual_markdown_files(self, tmp_path: Path) -> None:
        paths = export_feed_obsidian("lobsters", SAMPLE_ARTICLES, tmp_path)
        assert len(paths) == 2
        assert all(p.suffix == ".md" for p in paths)

    def test_obsidian_note_has_yaml_frontmatter(self, tmp_path: Path) -> None:
        paths = export_feed_obsidian("lobsters", SAMPLE_ARTICLES[:1], tmp_path)
        content = paths[0].read_text()
        assert content.startswith("---")
        assert "title:" in content
        assert "feed:" in content
        assert "tags:" in content
        assert "lobsters" in content

    def test_obsidian_note_body_has_summary(self, tmp_path: Path) -> None:
        paths = export_feed_obsidian("lobsters", SAMPLE_ARTICLES[:1], tmp_path)
        content = paths[0].read_text()
        assert "A summary about AI advances." in content

    def test_obsidian_filename_is_safe(self, tmp_path: Path) -> None:
        """Titles with special characters produce safe filenames."""
        paths = export_feed_obsidian("lobsters", SAMPLE_ARTICLES[1:2], tmp_path)
        filename = paths[0].name
        assert "?" not in filename
        assert "(" not in filename


class TestExportAll:
    """Feature: Export all feeds."""

    def test_json_export_writes_per_feed(self, tmp_path: Path) -> None:
        _write_processed(tmp_path, "lobsters", SAMPLE_ARTICLES)
        export_all(
            processed_dir=tmp_path / "processed",
            export_dir=tmp_path / "export",
            fmt="json",
        )
        assert (tmp_path / "export" / "lobsters.json").exists()

    def test_obsidian_export_writes_per_feed(self, tmp_path: Path) -> None:
        _write_processed(tmp_path, "lobsters", SAMPLE_ARTICLES)
        export_all(
            processed_dir=tmp_path / "processed",
            export_dir=tmp_path / "export",
            fmt="obsidian",
        )
        obsidian_dir = tmp_path / "export" / "obsidian" / "lobsters"
        assert obsidian_dir.exists()
        assert len(list(obsidian_dir.glob("*.md"))) == 2

    def test_creates_export_directory(self, tmp_path: Path) -> None:
        _write_processed(tmp_path, "test", SAMPLE_ARTICLES[:1])
        export_all(
            processed_dir=tmp_path / "processed",
            export_dir=tmp_path / "export",
            fmt="json",
        )
        assert (tmp_path / "export").exists()

    def test_missing_processed_returns_empty(self, tmp_path: Path) -> None:
        paths = export_all(
            processed_dir=tmp_path / "nonexistent",
            export_dir=tmp_path / "export",
            fmt="json",
        )
        assert paths == []


def _write_processed(base: Path, feed: str, articles: list[dict]) -> None:
    feed_dir = base / "processed" / feed
    feed_dir.mkdir(parents=True, exist_ok=True)
    for i, article in enumerate(articles):
        (feed_dir / f"item-{i}.json").write_text(json.dumps(article))
