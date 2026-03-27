"""Tests for pipeline functions."""

import json
from pathlib import Path

import pytest

from lens.pipeline.orchestrator import (
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
