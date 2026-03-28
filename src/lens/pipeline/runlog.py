"""Pipeline run log output.

Writes a structured JSON log per pipeline run with per-item timing,
stage transitions, and error details. All pure functions.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def create_run_log() -> dict:
    """Create a new run log with a start timestamp."""
    return {
        "start": datetime.now(UTC).isoformat(),
        "items": [],
        "errors": [],
        "_start_mono": time.monotonic(),
    }


def record_item(
    log: dict,
    url: str,
    status: str,
    stage_time: float,
) -> dict:
    """Record a processed item in the run log. Returns a new log dict."""
    return {
        **log,
        "items": [*log["items"], {"url": url, "status": status, "stage_time": stage_time}],
    }


def record_error(log: dict, url: str, error: str) -> dict:
    """Record an error in the run log. Returns a new log dict."""
    return {
        **log,
        "errors": [*log["errors"], {"url": url, "error": error}],
    }


def finalize_run_log(log: dict) -> dict:
    """Finalize a run log with end timestamp, elapsed time, and item count."""
    elapsed = time.monotonic() - log["_start_mono"]
    finalized = {
        "start": log["start"],
        "end": datetime.now(UTC).isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "item_count": len(log["items"]),
        "items": log["items"],
        "errors": log["errors"],
    }
    return finalized


def write_run_log(logs_dir: Path, log: dict) -> Path:
    """Write a finalized run log to disk as JSON.

    Filename includes ISO timestamp for chronological ordering.

    Args:
        logs_dir: Directory to write the log file.
        log: Finalized run log dict.

    Returns:
        Path to the written log file.
    """
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = log["start"].replace(":", "-").replace("+", "")
    path = logs_dir / f"{timestamp}-run.json"
    path.write_text(json.dumps(log, indent=2))
    return path
