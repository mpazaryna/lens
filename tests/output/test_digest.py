"""Tests for digest generator.

Derived from gherkin.md Step 1 scenarios:
- Per-feed markdown digest generation
- Sorting, filtering, formatting
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from lens.output.digest import generate_all_digests, generate_digest

if TYPE_CHECKING:
    from pathlib import Path


SAMPLE_ARTICLES = [
    {
        "title": "Short Article",
        "source_url": "https://example.com/short",
        "feed_name": "test-feed",
        "summary_text": "A brief summary.",
        "word_count": 500,
        "provider": "llama3.2",
        "model": "llama3.2",
        "timestamp": "2026-03-28T12:00:00Z",
        "processing_time_ms": 1500,
        "input_tokens": 100,
        "output_tokens": 30,
    },
    {
        "title": "Long Article",
        "source_url": "https://example.com/long",
        "feed_name": "test-feed",
        "summary_text": "A detailed and comprehensive summary of the topic.",
        "word_count": 1200,
        "provider": "llama3.2",
        "model": "llama3.2",
        "timestamp": "2026-03-28T12:01:00Z",
        "processing_time_ms": 2800,
        "input_tokens": 250,
        "output_tokens": 60,
    },
    {
        "title": "Medium Article",
        "source_url": "https://example.com/medium",
        "feed_name": "test-feed",
        "summary_text": "A medium-length summary covering key points.",
        "word_count": 800,
        "provider": "llama3.2",
        "model": "llama3.2",
        "timestamp": "2026-03-28T12:02:00Z",
        "processing_time_ms": 2100,
        "input_tokens": 180,
        "output_tokens": 45,
    },
]


class TestGenerateDigest:
    """Feature: Per-feed markdown digest."""

    def test_digest_contains_header(self) -> None:
        """Header includes feed name and article count."""
        md = generate_digest("test-feed", SAMPLE_ARTICLES)
        assert "test-feed" in md.lower() or "Test Feed" in md
        assert "3 articles" in md

    def test_articles_sorted_by_word_count_descending(self) -> None:
        """Longest article appears first."""
        md = generate_digest("test-feed", SAMPLE_ARTICLES)
        long_pos = md.index("Long Article")
        medium_pos = md.index("Medium Article")
        short_pos = md.index("Short Article")
        assert long_pos < medium_pos < short_pos

    def test_article_includes_title_url_summary_metadata(self) -> None:
        """Each article has title, source URL, summary, and metadata."""
        md = generate_digest("test-feed", SAMPLE_ARTICLES[:1])
        assert "Short Article" in md
        assert "https://example.com/short" in md
        assert "A brief summary." in md
        assert "500" in md

    def test_empty_feed(self) -> None:
        """Empty feed produces digest with zero count."""
        md = generate_digest("empty-feed", [])
        assert "0 articles" in md

    def test_digest_is_valid_markdown(self) -> None:
        """Digest starts with a level-1 heading."""
        md = generate_digest("test-feed", SAMPLE_ARTICLES)
        assert md.startswith("#")


class TestGenerateAllDigests:
    """Feature: Generate digests from processed data on disk."""

    def test_generates_digest_per_feed(self, tmp_path: Path) -> None:
        """Each feed directory gets its own digest file."""
        _write_processed(tmp_path, "bbc-news", SAMPLE_ARTICLES[:1])
        _write_processed(tmp_path, "lobsters", SAMPLE_ARTICLES[1:2])

        paths = generate_all_digests(
            processed_dir=tmp_path / "processed",
            digest_dir=tmp_path / "digest",
        )

        assert len(paths) == 2
        assert (tmp_path / "digest" / "bbc-news.md").exists()
        assert (tmp_path / "digest" / "lobsters.md").exists()

    def test_creates_digest_directory(self, tmp_path: Path) -> None:
        """Digest directory is created if it doesn't exist."""
        _write_processed(tmp_path, "test", SAMPLE_ARTICLES[:1])

        generate_all_digests(
            processed_dir=tmp_path / "processed",
            digest_dir=tmp_path / "digest",
        )

        assert (tmp_path / "digest").exists()

    def test_overwrites_previous_digest(self, tmp_path: Path) -> None:
        """Running twice overwrites the previous digest."""
        _write_processed(tmp_path, "test", SAMPLE_ARTICLES[:1])
        digest_dir = tmp_path / "digest"

        generate_all_digests(processed_dir=tmp_path / "processed", digest_dir=digest_dir)
        assert (digest_dir / "test.md").exists()

        # Add a second article and regenerate
        _write_processed(tmp_path, "test", SAMPLE_ARTICLES[:2])
        generate_all_digests(processed_dir=tmp_path / "processed", digest_dir=digest_dir)
        content = (digest_dir / "test.md").read_text()

        assert "2 articles" in content  # Overwritten with new data

    def test_no_processed_dir_returns_empty(self, tmp_path: Path) -> None:
        """Missing processed directory returns empty list."""
        paths = generate_all_digests(
            processed_dir=tmp_path / "nonexistent",
            digest_dir=tmp_path / "digest",
        )
        assert paths == []


def _write_processed(base: Path, feed: str, articles: list[dict]) -> None:
    """Helper to write processed JSON files for testing."""
    feed_dir = base / "processed" / feed
    feed_dir.mkdir(parents=True, exist_ok=True)
    for i, article in enumerate(articles):
        (feed_dir / f"item-{i}.json").write_text(json.dumps(article))
