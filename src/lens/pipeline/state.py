"""Feed state tracker (ADR-006).

Replaces the binary seen ledger with per-item status tracking across
pipeline stages. Pure functions operating on state dicts with I/O at
the edges. Atomic writes via temp file + os.replace().
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from lens.errors import LensError

if TYPE_CHECKING:
    from pathlib import Path

# Valid status values and allowed transitions
VALID_STATUSES = frozenset({"new", "fetched", "extracted", "summarized", "failed"})

# Each status can transition to the next stage or to failed
ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "new": frozenset({"fetched", "failed"}),
    "fetched": frozenset({"extracted", "failed"}),
    "extracted": frozenset({"summarized", "failed"}),
    "summarized": frozenset({"failed"}),
    "failed": frozenset({"new", "fetched", "extracted", "failed"}),
}


class InvalidTransitionError(LensError):
    """Raised when a state transition is not allowed."""


def item_id_from_url(url: str) -> str:
    """Generate a stable, URL-safe item ID from a URL.

    Uses SHA-256 truncated to 16 characters for compactness.
    """
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def discover_items(
    state: dict[str, dict],
    items: list[dict],
) -> dict[str, dict]:
    """Add new feed items to the state tracker. Skip already-known items.

    Args:
        state: Current state dict.
        items: List of dicts with 'url', 'title', 'feed' keys.

    Returns:
        New state dict with discovered items added.
    """
    now = datetime.now(UTC).isoformat()
    updated = {**state}

    for item in items:
        item_id = item_id_from_url(item["url"])
        if item_id in updated:
            continue
        updated[item_id] = {
            "url": item["url"],
            "title": item["title"],
            "feed": item["feed"],
            "status": "new",
            "discovered_at": now,
            "updated_at": now,
            "stage_times": {},
            "error": None,
            "retry_count": 0,
        }

    return updated


def transition_item(
    item: dict,
    new_status: str,
    stage_time: float | None = None,
    error: str | None = None,
) -> dict:
    """Transition an item to a new status. Returns a new dict.

    Args:
        item: Current item dict.
        new_status: Target status.
        stage_time: Time in seconds for the completed stage.
        error: Error message (required when transitioning to 'failed').

    Returns:
        New item dict with updated status.

    Raises:
        InvalidTransitionError: If the transition is not allowed.
    """
    current = item["status"]
    allowed = ALLOWED_TRANSITIONS.get(current, frozenset())

    if new_status not in allowed:
        raise InvalidTransitionError(f"Cannot transition from '{current}' to '{new_status}'")

    now = datetime.now(UTC).isoformat()
    updated = {**item, "status": new_status, "updated_at": now}

    if new_status == "failed":
        updated["error"] = error
        updated["retry_count"] = item.get("retry_count", 0) + 1
    else:
        updated["error"] = None
        if stage_time is not None:
            updated["stage_times"] = {**item.get("stage_times", {}), new_status: stage_time}

    return updated


def items_at_status(state: dict[str, dict], status: str) -> dict[str, dict]:
    """Return items at a specific status.

    Args:
        state: Full state dict.
        status: Status to filter by.

    Returns:
        Dict of item_id -> item for matching items.
    """
    return {k: v for k, v in state.items() if v.get("status") == status}


def load_state(path: Path) -> dict[str, dict]:
    """Load state from disk. Returns empty dict if file doesn't exist."""
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_state(path: Path, state: dict[str, dict]) -> None:
    """Save state to disk using atomic write (temp file + rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(state, indent=2)

    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        os.write(fd, data.encode())
        os.close(fd)
        os.replace(tmp_path, path)
    except BaseException:
        os.close(fd) if not os.get_inheritable(fd) else None
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def migrate_seen_ledger(seen: dict[str, dict]) -> dict[str, dict]:
    """Migrate old seen.json entries to state tracker format.

    All seen entries are treated as 'summarized' since they completed
    the full pipeline.

    Args:
        seen: Old seen ledger dict (url -> {processedAt, title}).

    Returns:
        New state dict with migrated entries.
    """
    state: dict[str, dict] = {}

    for url, entry in seen.items():
        item_id = item_id_from_url(url)
        processed_at = entry.get("processedAt", datetime.now(UTC).isoformat())
        state[item_id] = {
            "url": url,
            "title": entry.get("title", ""),
            "feed": "",
            "status": "summarized",
            "discovered_at": processed_at,
            "updated_at": processed_at,
            "stage_times": {},
            "error": None,
            "retry_count": 0,
        }

    return state
