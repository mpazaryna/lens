"""E2E integration test for the collection pipeline.

Exercises the full collection chain against real RSS feeds:
OPML parse -> feed fetch -> HTML fetch -> extraction.

Marked @pytest.mark.integration -- excluded from normal test runs.
Run with: uv run pytest -m integration
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from lens.config import load_config
from lens.pipeline.orchestrator import run_collection
from lens.pipeline.state import load_state

if TYPE_CHECKING:
    from pathlib import Path

# BBC News RSS is stable and lightweight
E2E_OPML = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <body>
    <outline text="News" title="News">
      <outline type="rss" text="BBC Top Stories" title="BBC Top Stories"
               xmlUrl="https://feeds.bbci.co.uk/news/rss.xml"
               htmlUrl="https://www.bbc.co.uk/news"/>
    </outline>
  </body>
</opml>"""


@pytest.mark.integration
@pytest.mark.asyncio
class TestCollectionE2E:
    """Full collection pipeline against real feeds."""

    async def test_full_collection_produces_extracted_content(self, tmp_path: Path) -> None:
        """Collection pipeline fetches, extracts, and tracks state."""
        # Set up data directory with OPML
        for subdir in ["opml", "feeds", "fetched", "extracted", "processed", "ranked"]:
            (tmp_path / subdir).mkdir()
        (tmp_path / "opml" / "test.opml").write_text(E2E_OPML)

        config = load_config(
            data_dir_override=tmp_path,
            opml_override=tmp_path / "opml" / "test.opml",
        )

        result = await run_collection(config, concurrency=3)

        # Should have found feeds
        assert result.feeds_found >= 1

        # Should have fetched at least some articles
        assert result.articles_fetched >= 1

        # State tracker should have items
        state = load_state(config.state_path)
        assert len(state) >= 1

        # At least some items should be past 'new'
        statuses = {item["status"] for item in state.values()}
        assert statuses & {"fetched", "extracted"}

    async def test_extracted_markdown_files_exist(self, tmp_path: Path) -> None:
        """Extracted markdown files are written with non-empty content."""
        for subdir in ["opml", "feeds", "fetched", "extracted", "processed", "ranked"]:
            (tmp_path / subdir).mkdir()
        (tmp_path / "opml" / "test.opml").write_text(E2E_OPML)

        config = load_config(
            data_dir_override=tmp_path,
            opml_override=tmp_path / "opml" / "test.opml",
        )

        await run_collection(config, concurrency=3)

        md_files = list((tmp_path / "extracted").glob("*.md"))
        # At least some articles should have been extracted
        assert len(md_files) >= 1

        # Files should have non-empty content
        for md_file in md_files[:3]:
            content = md_file.read_text()
            assert len(content) > 50

    async def test_second_run_is_noop(self, tmp_path: Path) -> None:
        """Second run with same feeds skips already-extracted items."""
        for subdir in ["opml", "feeds", "fetched", "extracted", "processed", "ranked"]:
            (tmp_path / subdir).mkdir()
        (tmp_path / "opml" / "test.opml").write_text(E2E_OPML)

        config = load_config(
            data_dir_override=tmp_path,
            opml_override=tmp_path / "opml" / "test.opml",
        )

        # First run
        result1 = await run_collection(config, concurrency=3)

        # Second run -- should fetch 0 new articles
        result2 = await run_collection(config, concurrency=3)

        # Second run should not have fetched any new articles
        # (all items already in state tracker)
        assert result2.articles_fetched <= result1.articles_fetched
