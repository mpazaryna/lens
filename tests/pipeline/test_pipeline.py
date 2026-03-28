"""Tests for pipeline functions."""

from pathlib import Path
from unittest.mock import patch

import pytest

from lens.collect.rss import Feed, FeedItem
from lens.config import Config
from lens.pipeline.orchestrator import (
    PipelineResult,
    extract_content,
    fetch_feed_items,
    filter_new_urls,
    load_seen,
    mark_seen,
    save_seen,
)


class TestSeenLedger:
    """Tests for seen ledger functions."""

    def test_load_nonexistent_returns_empty(self, tmp_path: Path) -> None:
        ledger = load_seen(tmp_path / "nonexistent.json")
        assert ledger == {}

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        path = tmp_path / "seen.json"
        ledger = {"https://example.com/a": {"processedAt": "2026-01-01", "title": "A"}}
        save_seen(path, ledger)

        loaded = load_seen(path)
        assert loaded == ledger

    def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        path = tmp_path / "deep" / "nested" / "seen.json"
        save_seen(path, {"https://example.com": {}})
        assert path.exists()

    def test_filter_new_urls_removes_seen(self) -> None:
        seen = {"https://example.com/old": {"processedAt": "2026-01-01"}}
        urls = [
            "https://example.com/old",
            "https://example.com/new-1",
            "https://example.com/new-2",
        ]
        new = filter_new_urls(urls, seen)
        assert len(new) == 2
        assert "https://example.com/old" not in new

    def test_filter_new_urls_empty_ledger(self) -> None:
        urls = ["https://example.com/a", "https://example.com/b"]
        new = filter_new_urls(urls, {})
        assert new == urls

    def test_mark_seen_adds_entries(self) -> None:
        ledger: dict[str, dict] = {}
        title_map = {"https://example.com/a": "Article A"}
        updated = mark_seen(ledger, ["https://example.com/a"], title_map)

        assert "https://example.com/a" in updated
        assert updated["https://example.com/a"]["title"] == "Article A"
        assert "processedAt" in updated["https://example.com/a"]

    def test_mark_seen_preserves_existing(self) -> None:
        ledger = {"https://example.com/old": {"processedAt": "2026-01-01", "title": "Old"}}
        updated = mark_seen(ledger, ["https://example.com/new"], {"https://example.com/new": "New"})

        assert "https://example.com/old" in updated
        assert "https://example.com/new" in updated

    def test_mark_seen_does_not_mutate_original(self) -> None:
        ledger: dict[str, dict] = {}
        mark_seen(ledger, ["https://example.com/a"], {})
        assert ledger == {}  # Original unchanged


class TestExtractContent:
    """Tests for the extract_content orchestrator phase."""

    def test_extracts_html_files(self, tmp_data_dir: Path) -> None:
        config = Config(
            data_dir=tmp_data_dir,
            provider="anthropic",
            api_key="test",
            model="test",
            base_url=None,
            log_level="info",
        )
        # Write HTML files
        (tmp_data_dir / "fetched" / "article.html").write_text(
            "<html><body><h1>Test</h1><p>Content here</p></body></html>"
        )

        result = PipelineResult()
        extract_results = extract_content(config, result)

        assert result.articles_extracted == 1
        assert len(extract_results) == 1
        assert not isinstance(extract_results[0][1], Exception)

    def test_counts_extraction_errors(self, tmp_data_dir: Path) -> None:
        config = Config(
            data_dir=tmp_data_dir,
            provider="anthropic",
            api_key="test",
            model="test",
            base_url=None,
            log_level="info",
        )
        # Empty dir = no files to extract
        result = PipelineResult()
        extract_results = extract_content(config, result)

        assert result.articles_extracted == 0
        assert len(extract_results) == 0


@pytest.mark.asyncio
class TestFetchFeedItems:
    """Tests for the fetch_feed_items orchestrator phase."""

    async def test_returns_empty_on_no_opml(self, tmp_data_dir: Path) -> None:
        config = Config(
            data_dir=tmp_data_dir,
            provider="anthropic",
            api_key="test",
            model="test",
            base_url=None,
            log_level="info",
        )
        result = PipelineResult()
        items = await fetch_feed_items(config, None, result)

        assert items == []
        assert len(result.errors) == 1
        assert "No OPML" in result.errors[0]

    async def test_parses_opml_and_fetches(self, tmp_data_dir: Path) -> None:
        config = Config(
            data_dir=tmp_data_dir,
            provider="anthropic",
            api_key="test",
            model="test",
            base_url=None,
            log_level="info",
        )
        # Write a minimal OPML
        opml = """<?xml version="1.0"?>
        <opml version="2.0">
          <body>
            <outline text="Tech" title="Tech">
              <outline type="rss" text="Test" title="Test"
                       xmlUrl="https://example.com/feed.xml"
                       htmlUrl="https://example.com"/>
            </outline>
          </body>
        </opml>"""
        (tmp_data_dir / "opml" / "test.opml").write_text(opml)

        feed = Feed(
            title="Test",
            link="https://example.com",
            description="",
            items=[
                FeedItem(
                    title="Article 1",
                    link="https://example.com/a1",
                    description="Desc",
                    pub_date="2026-03-27",
                    guid="a1",
                ),
            ],
        )

        with patch("lens.pipeline.orchestrator.fetch_feeds") as mock_fetch:
            mock_fetch.return_value = [("https://example.com/feed.xml", feed)]
            result = PipelineResult()
            items = await fetch_feed_items(config, None, result)

        assert result.feeds_found == 1
        assert len(items) == 1
        assert items[0].title == "Article 1"
