"""Tests for pipeline agent."""

import json
from pathlib import Path

import pytest

from lens_py.agents.pipeline import SeenLedger


class TestSeenLedger:
    """Tests for the seen articles ledger."""

    def test_empty_ledger(self) -> None:
        ledger = SeenLedger()
        assert not ledger.is_seen("https://example.com/article")

    def test_mark_and_check_seen(self) -> None:
        ledger = SeenLedger()
        ledger.mark_seen("https://example.com/article", "Test Article")
        assert ledger.is_seen("https://example.com/article")

    def test_filter_new_urls(self) -> None:
        ledger = SeenLedger()
        ledger.mark_seen("https://example.com/old")

        urls = [
            "https://example.com/old",
            "https://example.com/new-1",
            "https://example.com/new-2",
        ]
        new = ledger.filter_new(urls)
        assert len(new) == 2
        assert "https://example.com/old" not in new

    def test_save_and_load(self, tmp_path: Path) -> None:
        path = tmp_path / "seen.json"

        # Save
        ledger = SeenLedger()
        ledger.mark_seen("https://example.com/article", "Test")
        ledger.save(path)

        # Load
        loaded = SeenLedger.load(path)
        assert loaded.is_seen("https://example.com/article")

    def test_load_nonexistent_returns_empty(self, tmp_path: Path) -> None:
        ledger = SeenLedger.load(tmp_path / "nonexistent.json")
        assert not ledger.is_seen("https://example.com/anything")

    def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        path = tmp_path / "deep" / "nested" / "seen.json"
        ledger = SeenLedger()
        ledger.mark_seen("https://example.com/article")
        ledger.save(path)
        assert path.exists()

    def test_mark_seen_records_timestamp(self) -> None:
        ledger = SeenLedger()
        ledger.mark_seen("https://example.com/article", "Test")
        entry = ledger.entries["https://example.com/article"]
        assert "processedAt" in entry
        assert "T" in entry["processedAt"]  # ISO format

    def test_mark_seen_records_title(self) -> None:
        ledger = SeenLedger()
        ledger.mark_seen("https://example.com/article", "My Title")
        entry = ledger.entries["https://example.com/article"]
        assert entry["title"] == "My Title"
