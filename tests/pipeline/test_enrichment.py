"""Tests for enrichment pipeline orchestrator.

Derived from gherkin.md Step 3 scenarios:
- State-aware enrichment processing
- Failure isolation
- Idempotency
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest

from lens.config import Config
from lens.pipeline.enrichment import run_enrichment
from lens.pipeline.state import item_id_from_url, load_state, save_state
from lens.providers.base import LLMResponse

if TYPE_CHECKING:
    from pathlib import Path


def _make_config(tmp_data_dir: Path) -> Config:
    return Config(
        data_dir=tmp_data_dir,
        provider="ollama",
        api_key="",
        model="llama3.2",
        base_url="http://localhost:11434",
        log_level="info",
        opml_path=tmp_data_dir / "feeds.opml",
    )


def _make_state_item(url: str, status: str, **kwargs) -> dict:
    return {
        "url": url,
        "title": url.split("/")[-1],
        "feed": "test",
        "status": status,
        "discovered_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "stage_times": {},
        "error": None,
        "retry_count": 0,
        **kwargs,
    }


def _make_mock_provider(text: str = "This is a summary.") -> AsyncMock:
    provider = AsyncMock()
    provider.model_name = "test-model"
    provider.complete = AsyncMock(return_value=LLMResponse(text=text, model="test-model"))
    return provider


@pytest.mark.asyncio
class TestRunEnrichment:
    """Tests for the enrichment orchestrator."""

    async def test_processes_extracted_items(self, tmp_data_dir: Path) -> None:
        """Items at extracted status are summarized."""
        config = _make_config(tmp_data_dir)

        # Create extracted markdown files
        extracted_dir = tmp_data_dir / "extracted" / "test"
        extracted_dir.mkdir(parents=True)
        (extracted_dir / "a.md").write_text("# Article A\n\nSome content about AI.")

        # State with extracted item
        item_id = item_id_from_url("https://example.com/a")
        save_state(
            config.state_path,
            {
                item_id: _make_state_item("https://example.com/a", "extracted"),
            },
        )

        provider = _make_mock_provider()
        result = await run_enrichment(config, provider, concurrency=5)

        state = load_state(config.state_path)
        assert state[item_id]["status"] == "summarized"
        assert "summarized" in state[item_id]["stage_times"]
        assert result.articles_summarized == 1

    async def test_skips_non_extracted_items(self, tmp_data_dir: Path) -> None:
        """Items not at extracted status are skipped."""
        config = _make_config(tmp_data_dir)

        save_state(
            config.state_path,
            {
                item_id_from_url("https://example.com/a"): _make_state_item(
                    "https://example.com/a", "new"
                ),
                item_id_from_url("https://example.com/b"): _make_state_item(
                    "https://example.com/b", "fetched"
                ),
                item_id_from_url("https://example.com/c"): _make_state_item(
                    "https://example.com/c", "summarized"
                ),
            },
        )

        provider = _make_mock_provider()
        result = await run_enrichment(config, provider, concurrency=5)

        assert result.articles_summarized == 0
        provider.complete.assert_not_awaited()

    async def test_failed_summarization_isolates_error(self, tmp_data_dir: Path) -> None:
        """Failed summarization marks item as failed, others continue."""
        config = _make_config(tmp_data_dir)

        extracted_dir = tmp_data_dir / "extracted" / "test"
        extracted_dir.mkdir(parents=True)
        (extracted_dir / "a.md").write_text("# A\n\nContent A")
        (extracted_dir / "b.md").write_text("# B\n\nContent B")

        id_a = item_id_from_url("https://example.com/a")
        id_b = item_id_from_url("https://example.com/b")
        save_state(
            config.state_path,
            {
                id_a: _make_state_item("https://example.com/a", "extracted"),
                id_b: _make_state_item("https://example.com/b", "extracted"),
            },
        )

        # Provider succeeds first call, fails second
        call_count = 0

        async def _mock_complete(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("Rate limited")
            return LLMResponse(text="Summary text", model="test-model")

        provider = AsyncMock()
        provider.model_name = "test-model"
        provider.complete = _mock_complete

        result = await run_enrichment(config, provider, concurrency=1)

        state = load_state(config.state_path)
        statuses = {state[id_a]["status"], state[id_b]["status"]}
        assert "summarized" in statuses
        assert "failed" in statuses
        assert result.articles_summarized == 1

    async def test_second_run_is_noop(self, tmp_data_dir: Path) -> None:
        """Items already summarized are not reprocessed."""
        config = _make_config(tmp_data_dir)

        save_state(
            config.state_path,
            {
                item_id_from_url("https://example.com/a"): _make_state_item(
                    "https://example.com/a", "summarized"
                ),
            },
        )

        provider = _make_mock_provider()
        result = await run_enrichment(config, provider, concurrency=5)

        assert result.articles_summarized == 0
        provider.complete.assert_not_awaited()

    async def test_retry_failed_resets_to_extracted(self, tmp_data_dir: Path) -> None:
        """--retry-failed resets failed items to extracted for reprocessing."""
        config = _make_config(tmp_data_dir)

        extracted_dir = tmp_data_dir / "extracted" / "test"
        extracted_dir.mkdir(parents=True)
        (extracted_dir / "a.md").write_text("# A\n\nContent")

        item_id = item_id_from_url("https://example.com/a")
        save_state(
            config.state_path,
            {
                item_id: _make_state_item(
                    "https://example.com/a",
                    "failed",
                    error="Rate limited",
                    retry_count=1,
                ),
            },
        )

        provider = _make_mock_provider()
        result = await run_enrichment(config, provider, concurrency=5, retry_failed=True)

        state = load_state(config.state_path)
        assert state[item_id]["status"] == "summarized"
        assert result.articles_summarized == 1

    async def test_summary_json_written_to_processed(self, tmp_data_dir: Path) -> None:
        """Summary output is written as JSON to processed/."""
        config = _make_config(tmp_data_dir)

        extracted_dir = tmp_data_dir / "extracted" / "test"
        extracted_dir.mkdir(parents=True)
        (extracted_dir / "a.md").write_text("# Article A\n\nContent about AI.")

        item_id = item_id_from_url("https://example.com/a")
        save_state(
            config.state_path,
            {
                item_id: _make_state_item("https://example.com/a", "extracted"),
            },
        )

        provider = _make_mock_provider("This is the summary.")
        await run_enrichment(config, provider, concurrency=5)

        json_files = list((tmp_data_dir / "processed").glob("*.json"))
        assert len(json_files) >= 1

        data = json.loads(json_files[0].read_text())
        assert "summary_text" in data
        assert data["summary_text"] == "This is the summary."

    async def test_summary_json_has_full_schema(self, tmp_data_dir: Path) -> None:
        """JSON output contains all required fields from spec."""
        config = _make_config(tmp_data_dir)

        extracted_dir = tmp_data_dir / "extracted" / "test-feed"
        extracted_dir.mkdir(parents=True)
        (extracted_dir / "a.md").write_text("# Test\n\nContent.")

        item_id = item_id_from_url("https://example.com/a")
        save_state(
            config.state_path,
            {
                item_id: _make_state_item("https://example.com/a", "extracted", feed="test-feed"),
            },
        )

        provider = AsyncMock()
        provider.model_name = "llama3.2"
        provider.complete = AsyncMock(
            return_value=LLMResponse(
                text="A summary.",
                model="llama3.2",
                usage={"input_tokens": 150, "output_tokens": 30},
            )
        )

        await run_enrichment(config, provider, concurrency=5)

        json_files = list((tmp_data_dir / "processed").glob("*.json"))
        data = json.loads(json_files[0].read_text())

        required_fields = [
            "title",
            "source_url",
            "feed_name",
            "summary_text",
            "word_count",
            "provider",
            "model",
            "timestamp",
            "processing_time_ms",
            "input_tokens",
            "output_tokens",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        assert data["feed_name"] == "test-feed"
        assert data["model"] == "llama3.2"
        assert data["input_tokens"] == 150
        assert data["output_tokens"] == 30

    async def test_run_log_written_after_enrichment(self, tmp_data_dir: Path) -> None:
        """Enrichment run produces a log file in logs/."""
        config = _make_config(tmp_data_dir)

        extracted_dir = tmp_data_dir / "extracted" / "test"
        extracted_dir.mkdir(parents=True)
        (extracted_dir / "a.md").write_text("# Test\n\nContent.")

        item_id = item_id_from_url("https://example.com/a")
        save_state(
            config.state_path,
            {
                item_id: _make_state_item("https://example.com/a", "extracted"),
            },
        )

        provider = _make_mock_provider()
        await run_enrichment(config, provider, concurrency=5)

        log_files = list((tmp_data_dir / "logs").glob("*-run.json"))
        assert len(log_files) >= 1

        log_data = json.loads(log_files[0].read_text())
        assert log_data["item_count"] >= 1
        assert "elapsed_seconds" in log_data
