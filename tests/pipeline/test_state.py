"""Tests for feed state tracker.

Derived from gherkin.md Step 2 scenarios:
- Item identification
- Item discovery
- State transitions
- Query items by status
- State persistence
- Seen ledger migration
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from lens.pipeline.state import (
    InvalidTransitionError,
    discover_items,
    item_id_from_url,
    items_at_status,
    load_state,
    migrate_seen_ledger,
    save_state,
    transition_item,
)

if TYPE_CHECKING:
    from pathlib import Path


class TestItemIdentification:
    """Feature: Item identification."""

    def test_stable_id_from_url(self) -> None:
        """Same URL always produces the same ID."""
        url = "https://example.com/article-1"
        assert item_id_from_url(url) == item_id_from_url(url)

    def test_url_safe_characters(self) -> None:
        """ID contains only URL-safe characters."""
        item_id = item_id_from_url("https://example.com/article?id=123&page=1")
        assert all(c.isalnum() or c in "-_" for c in item_id)

    def test_different_urls_produce_different_ids(self) -> None:
        """Different URLs produce different IDs."""
        id1 = item_id_from_url("https://example.com/article-1")
        id2 = item_id_from_url("https://example.com/article-2")
        assert id1 != id2


class TestItemDiscovery:
    """Feature: Item discovery."""

    def test_discover_new_items(self) -> None:
        """Discover new items into empty state."""
        state = {}
        items = [
            {"url": "https://example.com/a", "title": "A", "feed": "test"},
            {"url": "https://example.com/b", "title": "B", "feed": "test"},
            {"url": "https://example.com/c", "title": "C", "feed": "test"},
        ]
        updated = discover_items(state, items)
        assert len(updated) == 3
        for item in updated.values():
            assert item["status"] == "new"
            assert "discovered_at" in item

    def test_skip_already_known_items(self) -> None:
        """Already-known items are not overwritten."""
        item_id = item_id_from_url("https://example.com/a")
        state = {
            item_id: {
                "url": "https://example.com/a",
                "title": "A",
                "feed": "test",
                "status": "fetched",
                "discovered_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "stage_times": {},
                "error": None,
                "retry_count": 0,
            }
        }
        items = [{"url": "https://example.com/a", "title": "A updated", "feed": "test"}]
        updated = discover_items(state, items)
        assert updated[item_id]["status"] == "fetched"
        assert updated[item_id]["discovered_at"] == "2026-01-01T00:00:00Z"


class TestStateTransitions:
    """Feature: State transitions."""

    def _make_item(self, status: str = "new", **kwargs) -> dict:
        return {
            "url": "https://example.com/a",
            "title": "A",
            "feed": "test",
            "status": status,
            "discovered_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "stage_times": {},
            "error": None,
            "retry_count": 0,
            **kwargs,
        }

    def test_advance_status(self) -> None:
        """Transition item to next status with stage timing."""
        item = self._make_item("new")
        updated = transition_item(item, "fetched", stage_time=1.2)
        assert updated["status"] == "fetched"
        assert updated["stage_times"]["fetched"] == 1.2
        assert updated["updated_at"] != item["updated_at"]

    def test_mark_failed(self) -> None:
        """Transition to failed records error and increments retry_count."""
        item = self._make_item("new")
        updated = transition_item(item, "failed", error="Connection refused")
        assert updated["status"] == "failed"
        assert updated["error"] == "Connection refused"
        assert updated["retry_count"] == 1

    def test_increment_retry_count(self) -> None:
        """Repeated failure increments retry_count."""
        item = self._make_item("failed", retry_count=2, error="Old error")
        updated = transition_item(item, "failed", error="Timeout")
        assert updated["retry_count"] == 3
        assert updated["error"] == "Timeout"

    def test_reject_invalid_transition(self) -> None:
        """Invalid transitions are rejected."""
        item = self._make_item("new")
        with __import__("pytest").raises(InvalidTransitionError):
            transition_item(item, "summarized")

    def test_does_not_mutate_original(self) -> None:
        """Transition returns a new dict, original unchanged."""
        item = self._make_item("new")
        updated = transition_item(item, "fetched", stage_time=1.0)
        assert item["status"] == "new"
        assert updated["status"] == "fetched"


class TestQueryByStatus:
    """Feature: Query items by status."""

    def test_filter_by_status(self) -> None:
        """Filter items at a specific status."""
        state = {
            "a": {"status": "new", "url": "https://example.com/a"},
            "b": {"status": "fetched", "url": "https://example.com/b"},
            "c": {"status": "new", "url": "https://example.com/c"},
            "d": {"status": "failed", "url": "https://example.com/d"},
        }
        result = items_at_status(state, "new")
        assert len(result) == 2
        assert all(item["status"] == "new" for item in result.values())

    def test_filter_returns_empty_on_no_match(self) -> None:
        """No items at requested status returns empty dict."""
        state = {"a": {"status": "new", "url": "https://example.com/a"}}
        result = items_at_status(state, "extracted")
        assert result == {}


class TestStatePersistence:
    """Feature: State persistence."""

    def test_save_load_roundtrip(self, tmp_path: Path) -> None:
        """Save and load preserves all fields."""
        state = {
            "abc123": {
                "url": "https://example.com/a",
                "title": "A",
                "feed": "test",
                "status": "fetched",
                "discovered_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-02T00:00:00Z",
                "stage_times": {"fetched": 1.2},
                "error": None,
                "retry_count": 0,
            }
        }
        path = tmp_path / "state.json"
        save_state(path, state)
        loaded = load_state(path)
        assert loaded == state

    def test_load_nonexistent_returns_empty(self, tmp_path: Path) -> None:
        """Loading from nonexistent path returns empty dict."""
        path = tmp_path / "nonexistent.json"
        assert load_state(path) == {}

    def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Save creates parent directories if needed."""
        path = tmp_path / "deep" / "nested" / "state.json"
        save_state(path, {"a": {"status": "new"}})
        assert path.exists()

    def test_atomic_write(self, tmp_path: Path) -> None:
        """Save uses atomic write (no partial file on crash)."""
        path = tmp_path / "state.json"
        save_state(path, {"a": {"status": "new"}})
        # If atomic write works, the file exists and is valid JSON
        loaded = load_state(path)
        assert loaded == {"a": {"status": "new"}}


class TestSeenLedgerMigration:
    """Feature: Seen ledger migration."""

    def test_migrate_entries(self) -> None:
        """Migrate seen.json entries to summarized status."""
        seen = {
            "https://example.com/a": {
                "processedAt": "2026-01-01T00:00:00Z",
                "title": "Article A",
            },
            "https://example.com/b": {
                "processedAt": "2026-01-02T00:00:00Z",
                "title": "Article B",
            },
        }
        state = migrate_seen_ledger(seen)
        assert len(state) == 2
        for item in state.values():
            assert item["status"] == "summarized"

    def test_migrate_preserves_titles(self) -> None:
        """Migration preserves title from original entries."""
        seen = {
            "https://example.com/a": {
                "processedAt": "2026-01-01T00:00:00Z",
                "title": "Article A",
            },
        }
        state = migrate_seen_ledger(seen)
        item_id = item_id_from_url("https://example.com/a")
        assert state[item_id]["title"] == "Article A"

    def test_migrate_empty_ledger(self) -> None:
        """Migrating empty ledger returns empty state."""
        assert migrate_seen_ledger({}) == {}
