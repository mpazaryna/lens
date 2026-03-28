"""Tests for pipeline run log output.

Derived from spec Step 6:
- JSON log per run with per-item timing
- Log file written to {data_dir}/logs/
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from lens.pipeline.runlog import (
    create_run_log,
    finalize_run_log,
    record_error,
    record_item,
    write_run_log,
)

if TYPE_CHECKING:
    from pathlib import Path


class TestRunLog:
    """Tests for run log functions."""

    def test_create_run_log_has_start_time(self) -> None:
        log = create_run_log()
        assert "start" in log
        assert log["items"] == []
        assert log["errors"] == []

    def test_record_item_adds_entry(self) -> None:
        log = create_run_log()
        updated = record_item(log, url="https://example.com/a", status="fetched", stage_time=1.2)
        assert len(updated["items"]) == 1
        assert updated["items"][0]["url"] == "https://example.com/a"
        assert updated["items"][0]["status"] == "fetched"
        assert updated["items"][0]["stage_time"] == 1.2

    def test_record_error_adds_entry(self) -> None:
        log = create_run_log()
        updated = record_error(log, url="https://example.com/a", error="Connection refused")
        assert len(updated["errors"]) == 1
        assert updated["errors"][0]["url"] == "https://example.com/a"
        assert updated["errors"][0]["error"] == "Connection refused"

    def test_finalize_adds_end_and_elapsed(self) -> None:
        log = create_run_log()
        finalized = finalize_run_log(log)
        assert "end" in finalized
        assert "elapsed_seconds" in finalized
        assert finalized["elapsed_seconds"] >= 0

    def test_finalize_includes_item_count(self) -> None:
        log = create_run_log()
        log = record_item(log, url="https://example.com/a", status="fetched", stage_time=1.0)
        log = record_item(log, url="https://example.com/b", status="extracted", stage_time=0.5)
        finalized = finalize_run_log(log)
        assert finalized["item_count"] == 2

    def test_write_creates_logs_directory(self, tmp_path: Path) -> None:
        logs_dir = tmp_path / "logs"
        log = finalize_run_log(create_run_log())
        path = write_run_log(logs_dir, log)
        assert logs_dir.exists()
        assert path.exists()

    def test_write_produces_valid_json(self, tmp_path: Path) -> None:
        logs_dir = tmp_path / "logs"
        log = finalize_run_log(create_run_log())
        path = write_run_log(logs_dir, log)
        data = json.loads(path.read_text())
        assert "start" in data
        assert "end" in data

    def test_log_filename_contains_timestamp(self, tmp_path: Path) -> None:
        logs_dir = tmp_path / "logs"
        log = finalize_run_log(create_run_log())
        path = write_run_log(logs_dir, log)
        assert "-run.json" in path.name
        # Filename should start with date-like pattern
        assert path.name[:4].isdigit()

    def test_roundtrip_preserves_all_fields(self, tmp_path: Path) -> None:
        logs_dir = tmp_path / "logs"
        log = create_run_log()
        log = record_item(log, url="https://example.com/a", status="fetched", stage_time=1.5)
        log = record_error(log, url="https://example.com/b", error="Timeout")
        log = finalize_run_log(log)
        path = write_run_log(logs_dir, log)
        loaded = json.loads(path.read_text())
        assert loaded["items"][0]["url"] == "https://example.com/a"
        assert loaded["errors"][0]["error"] == "Timeout"
        assert loaded["item_count"] == 1

    def test_empty_run_writes_valid_log(self, tmp_path: Path) -> None:
        logs_dir = tmp_path / "logs"
        log = finalize_run_log(create_run_log())
        path = write_run_log(logs_dir, log)
        data = json.loads(path.read_text())
        assert data["item_count"] == 0
        assert data["items"] == []
        assert data["errors"] == []
