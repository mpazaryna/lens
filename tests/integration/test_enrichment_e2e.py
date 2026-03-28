"""E2E integration test for the enrichment pipeline.

Exercises enrichment against pre-collected content using local Ollama.
Marked @pytest.mark.integration -- excluded from normal test runs.
Run with: uv run pytest -m integration
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from lens.config import load_config
from lens.pipeline.enrichment import run_enrichment
from lens.pipeline.state import item_id_from_url, load_state, save_state
from lens.providers.ollama import OllamaProvider

if TYPE_CHECKING:
    from pathlib import Path

SAMPLE_ARTICLE = """# AI Models Show Improved Reasoning

Artificial intelligence models have demonstrated significant improvements
in complex reasoning tasks according to recent benchmarks. The latest
generation of language models can now solve multi-step mathematical
problems and write functional code with higher accuracy than previous
versions.

Researchers attribute these gains to advances in training methodology,
including reinforcement learning from human feedback and improved
data curation. The models show particular strength in tasks requiring
logical deduction and step-by-step problem solving.

These developments raise important questions about deployment safety
and the need for robust evaluation frameworks. Industry leaders have
called for standardized benchmarks that test not just capability but
also reliability and alignment with human values.
"""


@pytest.mark.integration
@pytest.mark.asyncio
class TestEnrichmentE2E:
    """Full enrichment pipeline against local Ollama."""

    async def test_enrich_pre_collected_articles(self, tmp_path: Path) -> None:
        """Enrichment produces JSON summaries for pre-collected articles."""
        for subdir in ["opml", "feeds", "fetched", "extracted", "processed", "ranked"]:
            (tmp_path / subdir).mkdir()

        # Pre-populate extracted content
        feed_dir = tmp_path / "extracted" / "test-feed"
        feed_dir.mkdir()
        (feed_dir / "article-1.md").write_text(SAMPLE_ARTICLE)

        # Set up state tracker with extracted item
        item_id = item_id_from_url("https://example.com/ai-reasoning")
        save_state(
            tmp_path / "state.json",
            {
                item_id: {
                    "url": "https://example.com/ai-reasoning",
                    "title": "AI Models Show Improved Reasoning",
                    "feed": "test-feed",
                    "status": "extracted",
                    "discovered_at": "2026-03-28T00:00:00Z",
                    "updated_at": "2026-03-28T00:00:00Z",
                    "stage_times": {},
                    "error": None,
                    "retry_count": 0,
                }
            },
        )

        config = load_config(data_dir_override=tmp_path)
        provider = OllamaProvider(model="llama3.2", base_url="http://localhost:11434")

        result = await run_enrichment(config, provider, concurrency=1)

        # Should have summarized the article
        assert result.articles_summarized == 1
        assert len(result.errors) == 0

        # State should show summarized
        state = load_state(config.state_path)
        assert state[item_id]["status"] == "summarized"
        assert "summarized" in state[item_id]["stage_times"]

        # JSON output should exist
        json_files = list((tmp_path / "processed").glob("*.json"))
        assert len(json_files) == 1

        data = json.loads(json_files[0].read_text())
        assert len(data["summary_text"]) > 20
        assert data["model"] == "llama3.2"
        assert data["feed_name"] == "test-feed"

    async def test_second_run_is_noop(self, tmp_path: Path) -> None:
        """Second enrichment run does not reprocess summarized items."""
        for subdir in ["opml", "feeds", "fetched", "extracted", "processed", "ranked"]:
            (tmp_path / subdir).mkdir()

        item_id = item_id_from_url("https://example.com/already-done")
        save_state(
            tmp_path / "state.json",
            {
                item_id: {
                    "url": "https://example.com/already-done",
                    "title": "Already Done",
                    "feed": "test",
                    "status": "summarized",
                    "discovered_at": "2026-03-28T00:00:00Z",
                    "updated_at": "2026-03-28T00:00:00Z",
                    "stage_times": {"summarized": 2.5},
                    "error": None,
                    "retry_count": 0,
                }
            },
        )

        config = load_config(data_dir_override=tmp_path)
        provider = OllamaProvider(model="llama3.2", base_url="http://localhost:11434")

        result = await run_enrichment(config, provider, concurrency=1)

        assert result.articles_summarized == 0

    async def test_run_log_produced(self, tmp_path: Path) -> None:
        """Enrichment run produces a log file."""
        for subdir in ["opml", "feeds", "fetched", "extracted", "processed", "ranked"]:
            (tmp_path / subdir).mkdir()

        feed_dir = tmp_path / "extracted" / "test-feed"
        feed_dir.mkdir()
        (feed_dir / "article.md").write_text(SAMPLE_ARTICLE)

        item_id = item_id_from_url("https://example.com/log-test")
        save_state(
            tmp_path / "state.json",
            {
                item_id: {
                    "url": "https://example.com/log-test",
                    "title": "Log Test",
                    "feed": "test-feed",
                    "status": "extracted",
                    "discovered_at": "2026-03-28T00:00:00Z",
                    "updated_at": "2026-03-28T00:00:00Z",
                    "stage_times": {},
                    "error": None,
                    "retry_count": 0,
                }
            },
        )

        config = load_config(data_dir_override=tmp_path)
        provider = OllamaProvider(model="llama3.2", base_url="http://localhost:11434")

        await run_enrichment(config, provider, concurrency=1)

        log_files = list((tmp_path / "logs").glob("*-run.json"))
        assert len(log_files) >= 1

        log_data = json.loads(log_files[0].read_text())
        assert log_data["item_count"] >= 1
