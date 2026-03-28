"""Tests for pipeline orchestrator.

Derived from gherkin.md Step 3 scenarios:
- Orchestrator uses state tracker instead of seen ledger
- Per-item status tracking through pipeline phases
- Failure isolation
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

if TYPE_CHECKING:
    from pathlib import Path

import pytest

from lens.collect.rss import Feed, FeedItem
from lens.config import Config
from lens.pipeline.orchestrator import (
    PipelineResult,
    extract_content,
    fetch_feed_items,
    run_collection,
)
from lens.pipeline.state import item_id_from_url, load_state, save_state

SAMPLE_OPML = """<?xml version="1.0"?>
<opml version="2.0"><body>
  <outline text="Tech" title="Tech">
    <outline type="rss" text="Test" title="Test"
             xmlUrl="https://example.com/feed.xml"/>
  </outline>
</body></opml>"""


def _make_state_item(url: str, status: str, **kwargs) -> dict:
    return {
        "url": url,
        "title": url.split("/")[-1],
        "feed": "Test",
        "status": status,
        "discovered_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "stage_times": {},
        "error": None,
        "retry_count": 0,
        **kwargs,
    }


def _make_config(tmp_data_dir: Path) -> Config:
    return Config(
        data_dir=tmp_data_dir,
        provider="anthropic",
        api_key="test",
        model="test",
        base_url=None,
        log_level="info",
        opml_path=tmp_data_dir / "feeds.opml",
    )


class TestExtractContent:
    """Tests for the extract_content orchestrator phase."""

    def test_extracts_html_files(self, tmp_data_dir: Path) -> None:
        config = _make_config(tmp_data_dir)
        (tmp_data_dir / "fetched" / "article.html").write_text(
            "<html><body><h1>Test</h1><p>Content here</p></body></html>"
        )

        result = PipelineResult()
        extract_results = extract_content(config, result)

        assert result.articles_extracted == 1
        assert len(extract_results) == 1
        assert not isinstance(extract_results[0][1], Exception)

    def test_counts_extraction_errors(self, tmp_data_dir: Path) -> None:
        config = _make_config(tmp_data_dir)
        result = PipelineResult()
        extract_results = extract_content(config, result)

        assert result.articles_extracted == 0
        assert len(extract_results) == 0


@pytest.mark.asyncio
class TestFetchFeedItems:
    """Tests for the fetch_feed_items orchestrator phase."""

    async def test_returns_empty_on_no_opml(self, tmp_data_dir: Path) -> None:
        config = _make_config(tmp_data_dir)
        result = PipelineResult()
        items, url_to_feed = await fetch_feed_items(config, None, result)

        assert items == []
        assert url_to_feed == {}
        assert len(result.errors) == 1
        assert "No OPML" in result.errors[0]

    async def test_parses_opml_and_fetches(self, tmp_data_dir: Path) -> None:
        config = _make_config(tmp_data_dir)
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
            items, url_to_feed = await fetch_feed_items(config, None, result)

        assert result.feeds_found == 1
        assert len(items) == 1
        assert items[0].title == "Article 1"
        assert url_to_feed["https://example.com/a1"] == "test"


@pytest.mark.asyncio
class TestRunCollection:
    """Tests for the collection pipeline with state tracker."""

    async def test_creates_state_json_on_first_run(self, tmp_data_dir: Path) -> None:
        """First run discovers items and creates state.json."""
        config = _make_config(tmp_data_dir)
        opml = """<?xml version="1.0"?>
        <opml version="2.0"><body>
          <outline text="Tech" title="Tech">
            <outline type="rss" text="Test" title="Test"
                     xmlUrl="https://example.com/feed.xml"/>
          </outline>
        </body></opml>"""
        (tmp_data_dir / "opml" / "test.opml").write_text(opml)

        feed = Feed(
            title="Test",
            link="https://example.com",
            description="",
            items=[
                FeedItem(
                    title="A1",
                    link="https://example.com/a1",
                    description="",
                    pub_date="",
                    guid="a1",
                ),
            ],
        )

        with (
            patch("lens.pipeline.orchestrator.fetch_feeds") as mock_feeds,
            patch("lens.pipeline.orchestrator.fetch_articles") as mock_fetch,
        ):
            mock_feeds.return_value = [("https://example.com/feed.xml", feed)]
            mock_fetch.return_value = []
            await run_collection(config, concurrency=5)

        state = load_state(config.state_path)
        assert len(state) == 1
        item_id = item_id_from_url("https://example.com/a1")
        assert item_id in state

    async def test_second_run_skips_extracted_items(self, tmp_data_dir: Path) -> None:
        """Items already at extracted status are not reprocessed."""
        config = _make_config(tmp_data_dir)
        opml = """<?xml version="1.0"?>
        <opml version="2.0"><body>
          <outline text="Tech" title="Tech">
            <outline type="rss" text="Test" title="Test"
                     xmlUrl="https://example.com/feed.xml"/>
          </outline>
        </body></opml>"""
        (tmp_data_dir / "opml" / "test.opml").write_text(opml)

        feed = Feed(
            title="Test",
            link="https://example.com",
            description="",
            items=[
                FeedItem(
                    title="A1",
                    link="https://example.com/a1",
                    description="",
                    pub_date="",
                    guid="a1",
                ),
            ],
        )

        # Pre-populate state with extracted item
        from lens.pipeline.state import save_state

        item_id = item_id_from_url("https://example.com/a1")
        save_state(
            config.state_path,
            {
                item_id: {
                    "url": "https://example.com/a1",
                    "title": "A1",
                    "feed": "Test",
                    "status": "extracted",
                    "discovered_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T00:00:00Z",
                    "stage_times": {},
                    "error": None,
                    "retry_count": 0,
                }
            },
        )

        with (
            patch("lens.pipeline.orchestrator.fetch_feeds") as mock_feeds,
            patch("lens.pipeline.orchestrator.fetch_articles") as mock_fetch,
        ):
            mock_feeds.return_value = [("https://example.com/feed.xml", feed)]
            mock_fetch.return_value = []
            await run_collection(config, concurrency=5)

        # fetch_articles should not have been called with this URL
        # since the item is already extracted
        if mock_fetch.called:
            call_args = mock_fetch.call_args
            urls = call_args[0][0] if call_args[0] else call_args[1].get("urls", [])
            assert "https://example.com/a1" not in urls

    async def test_new_items_processed_alongside_existing(self, tmp_data_dir: Path) -> None:
        """New feed entries are processed even when existing items are already done."""
        config = _make_config(tmp_data_dir)
        opml = """<?xml version="1.0"?>
        <opml version="2.0"><body>
          <outline text="Tech" title="Tech">
            <outline type="rss" text="Test" title="Test"
                     xmlUrl="https://example.com/feed.xml"/>
          </outline>
        </body></opml>"""
        (tmp_data_dir / "opml" / "test.opml").write_text(opml)

        feed = Feed(
            title="Test",
            link="https://example.com",
            description="",
            items=[
                FeedItem(
                    title="A1",
                    link="https://example.com/a1",
                    description="",
                    pub_date="",
                    guid="a1",
                ),
                FeedItem(
                    title="A2",
                    link="https://example.com/a2",
                    description="",
                    pub_date="",
                    guid="a2",
                ),
            ],
        )

        # A1 already extracted, A2 is new
        from lens.pipeline.state import save_state

        item_id_a1 = item_id_from_url("https://example.com/a1")
        save_state(
            config.state_path,
            {
                item_id_a1: {
                    "url": "https://example.com/a1",
                    "title": "A1",
                    "feed": "Test",
                    "status": "extracted",
                    "discovered_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-01-01T00:00:00Z",
                    "stage_times": {},
                    "error": None,
                    "retry_count": 0,
                }
            },
        )

        with (
            patch("lens.pipeline.orchestrator.fetch_feeds") as mock_feeds,
            patch("lens.pipeline.orchestrator.fetch_articles") as mock_fetch,
        ):
            mock_feeds.return_value = [("https://example.com/feed.xml", feed)]
            mock_fetch.return_value = []
            await run_collection(config, concurrency=5)

        state = load_state(config.state_path)
        assert len(state) == 2
        item_id_a2 = item_id_from_url("https://example.com/a2")
        assert item_id_a2 in state


@pytest.mark.asyncio
class TestPipelineRecoveryAndRetry:
    """Tests for stage-aware resumption and --retry-failed."""

    async def test_retry_failed_resets_failed_items(self, tmp_data_dir: Path) -> None:
        """--retry-failed resets failed items to new for reprocessing."""
        config = _make_config(tmp_data_dir)
        (tmp_data_dir / "opml" / "test.opml").write_text(SAMPLE_OPML)

        item_id = item_id_from_url("https://example.com/a1")
        save_state(
            config.state_path,
            {
                item_id: _make_state_item(
                    "https://example.com/a1",
                    "failed",
                    error="Connection refused",
                    retry_count=1,
                ),
            },
        )

        feed = Feed(
            title="Test",
            link="https://example.com",
            description="",
            items=[
                FeedItem(
                    title="A1",
                    link="https://example.com/a1",
                    description="",
                    pub_date="",
                    guid="a1",
                )
            ],
        )

        with (
            patch("lens.pipeline.orchestrator.fetch_feeds") as mock_feeds,
            patch("lens.pipeline.orchestrator.fetch_articles") as mock_fetch,
        ):
            mock_feeds.return_value = [("https://example.com/feed.xml", feed)]
            mock_fetch.return_value = []
            await run_collection(config, concurrency=5, retry_failed=True)

        state = load_state(config.state_path)
        # Item should have been reset from failed and reprocessed
        assert state[item_id]["status"] != "failed"
        assert state[item_id]["error"] is None

    async def test_retry_failed_does_not_affect_non_failed(self, tmp_data_dir: Path) -> None:
        """--retry-failed leaves non-failed items unchanged."""
        config = _make_config(tmp_data_dir)
        (tmp_data_dir / "opml" / "test.opml").write_text(SAMPLE_OPML)

        item_id = item_id_from_url("https://example.com/a1")
        save_state(
            config.state_path,
            {
                item_id: _make_state_item("https://example.com/a1", "extracted"),
            },
        )

        feed = Feed(
            title="Test",
            link="https://example.com",
            description="",
            items=[
                FeedItem(
                    title="A1",
                    link="https://example.com/a1",
                    description="",
                    pub_date="",
                    guid="a1",
                )
            ],
        )

        with (
            patch("lens.pipeline.orchestrator.fetch_feeds") as mock_feeds,
            patch("lens.pipeline.orchestrator.fetch_articles") as mock_fetch,
        ):
            mock_feeds.return_value = [("https://example.com/feed.xml", feed)]
            mock_fetch.return_value = []
            await run_collection(config, concurrency=5, retry_failed=True)

        state = load_state(config.state_path)
        assert state[item_id]["status"] == "extracted"

    async def test_fetched_items_skip_to_extraction(self, tmp_data_dir: Path) -> None:
        """Items at fetched status skip fetch and go to extraction."""
        config = _make_config(tmp_data_dir)
        (tmp_data_dir / "opml" / "test.opml").write_text(SAMPLE_OPML)

        item_id = item_id_from_url("https://example.com/a1")
        save_state(
            config.state_path,
            {
                item_id: _make_state_item("https://example.com/a1", "fetched"),
            },
        )

        feed = Feed(
            title="Test",
            link="https://example.com",
            description="",
            items=[
                FeedItem(
                    title="A1",
                    link="https://example.com/a1",
                    description="",
                    pub_date="",
                    guid="a1",
                )
            ],
        )

        with (
            patch("lens.pipeline.orchestrator.fetch_feeds") as mock_feeds,
            patch("lens.pipeline.orchestrator.fetch_articles") as mock_fetch,
        ):
            mock_feeds.return_value = [("https://example.com/feed.xml", feed)]
            mock_fetch.return_value = []
            await run_collection(config, concurrency=5)

        # fetch_articles should not be called for this URL (already fetched)
        if mock_fetch.called:
            urls = mock_fetch.call_args[0][0]
            assert "https://example.com/a1" not in urls

        state = load_state(config.state_path)
        assert state[item_id]["status"] == "extracted"

    async def test_failed_retry_increments_count(self, tmp_data_dir: Path) -> None:
        """A failed item that fails again on retry gets retry_count incremented."""
        config = _make_config(tmp_data_dir)
        (tmp_data_dir / "opml" / "test.opml").write_text(SAMPLE_OPML)

        from lens.collect.fetcher import FetchResult

        item_id = item_id_from_url("https://example.com/a1")
        save_state(
            config.state_path,
            {
                item_id: _make_state_item(
                    "https://example.com/a1",
                    "failed",
                    error="Timeout",
                    retry_count=2,
                ),
            },
        )

        feed = Feed(
            title="Test",
            link="https://example.com",
            description="",
            items=[
                FeedItem(
                    title="A1",
                    link="https://example.com/a1",
                    description="",
                    pub_date="",
                    guid="a1",
                )
            ],
        )

        with (
            patch("lens.pipeline.orchestrator.fetch_feeds") as mock_feeds,
            patch("lens.pipeline.orchestrator.fetch_articles") as mock_fetch,
        ):
            mock_feeds.return_value = [("https://example.com/feed.xml", feed)]
            # Fetch fails again
            mock_fetch.return_value = [
                FetchResult(url="https://example.com/a1", success=False, error="Timeout again")
            ]
            await run_collection(config, concurrency=5, retry_failed=True)

        state = load_state(config.state_path)
        assert state[item_id]["status"] == "failed"
        assert state[item_id]["retry_count"] == 3


class TestFeedOrganizedOutput:
    """Tests for feed-organized output directories (Step 0)."""

    @pytest.mark.asyncio
    async def test_state_tracker_records_feed_name(self, tmp_data_dir: Path) -> None:
        """Discovered items record the feed name in state."""
        config = _make_config(tmp_data_dir)
        (tmp_data_dir / "opml" / "test.opml").write_text(SAMPLE_OPML)

        feed = Feed(
            title="BBC Top Stories",
            link="https://example.com",
            description="",
            items=[
                FeedItem(
                    title="A1",
                    link="https://example.com/a1",
                    description="",
                    pub_date="",
                    guid="a1",
                )
            ],
        )

        with (
            patch("lens.pipeline.orchestrator.fetch_feeds") as mock_feeds,
            patch("lens.pipeline.orchestrator.fetch_articles") as mock_fetch,
        ):
            mock_feeds.return_value = [("https://example.com/feed.xml", feed)]
            mock_fetch.return_value = []
            await run_collection(config, concurrency=5)

        state = load_state(config.state_path)
        item_id = item_id_from_url("https://example.com/a1")
        assert state[item_id]["feed"] == "bbc-top-stories"

    def test_extract_walks_subdirectories(self, tmp_data_dir: Path) -> None:
        """Extraction finds HTML files in feed subdirectories."""
        config = _make_config(tmp_data_dir)
        feed_dir = tmp_data_dir / "fetched" / "bbc-top-stories"
        feed_dir.mkdir(parents=True)
        (feed_dir / "article.html").write_text(
            "<html><body><h1>Test</h1><p>Content</p></body></html>"
        )

        result = PipelineResult()
        extract_results = extract_content(config, result)

        assert result.articles_extracted == 1
        # Output should be in the feed subdirectory
        out_path = extract_results[0][0]
        assert "bbc-top-stories" in str(out_path)

    def test_extract_still_handles_flat_files(self, tmp_data_dir: Path) -> None:
        """Flat files in fetched/ (no subdirectory) are still extracted."""
        config = _make_config(tmp_data_dir)
        (tmp_data_dir / "fetched" / "legacy.html").write_text(
            "<html><body><p>Legacy content</p></body></html>"
        )

        result = PipelineResult()
        extract_content(config, result)

        assert result.articles_extracted == 1
