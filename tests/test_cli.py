"""Tests for CLI commands.

Derived from spec Step 4:
- lens collect runs collection only
- CLI flags pass through correctly
- No API key required for collection
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

from click.testing import CliRunner

from lens.cli import cli

if TYPE_CHECKING:
    from pathlib import Path


class TestCollectCommand:
    """Tests for the lens collect CLI command."""

    def test_collect_runs_collection_only(self, tmp_data_dir: Path) -> None:
        """lens collect invokes run_collection, not run_pipeline."""
        runner = CliRunner()
        with patch("lens.cli.run_collection", new_callable=AsyncMock) as mock_collect:
            mock_collect.return_value = _make_pipeline_result()
            result = runner.invoke(cli, ["collect", "--data-dir", str(tmp_data_dir)])

        assert result.exit_code == 0
        mock_collect.assert_awaited_once()

    def test_collect_does_not_require_api_key(self, tmp_data_dir: Path) -> None:
        """Missing API key does not block lens collect."""
        runner = CliRunner()
        with patch("lens.cli.run_collection", new_callable=AsyncMock) as mock_collect:
            mock_collect.return_value = _make_pipeline_result()
            result = runner.invoke(
                cli,
                ["collect", "--data-dir", str(tmp_data_dir)],
                env={"LENS_API_KEY": "", "ANTHROPIC_API_KEY": ""},
            )

        assert result.exit_code == 0

    def test_collect_passes_data_dir(self, tmp_data_dir: Path) -> None:
        """--data-dir flag is passed through to config."""
        runner = CliRunner()
        with patch("lens.cli.run_collection", new_callable=AsyncMock) as mock_collect:
            mock_collect.return_value = _make_pipeline_result()
            result = runner.invoke(cli, ["collect", "--data-dir", str(tmp_data_dir)])

        assert result.exit_code == 0
        call_kwargs = mock_collect.call_args
        config = call_kwargs[1]["config"] if "config" in call_kwargs[1] else call_kwargs[0][0]
        assert config.data_dir == tmp_data_dir

    def test_collect_output_includes_counts(self, tmp_data_dir: Path) -> None:
        """Output includes counts for each stage."""
        runner = CliRunner()
        with patch("lens.cli.run_collection", new_callable=AsyncMock) as mock_collect:
            mock_collect.return_value = _make_pipeline_result(
                feeds_found=3, articles_fetched=10, articles_extracted=8
            )
            result = runner.invoke(cli, ["collect", "--data-dir", str(tmp_data_dir)])

        assert result.exit_code == 0
        assert "3" in result.output
        assert "10" in result.output
        assert "8" in result.output

    def test_collect_retry_failed_flag(self, tmp_data_dir: Path) -> None:
        """--retry-failed flag is accepted and passed through."""
        runner = CliRunner()
        with patch("lens.cli.run_collection", new_callable=AsyncMock) as mock_collect:
            mock_collect.return_value = _make_pipeline_result()
            result = runner.invoke(
                cli, ["collect", "--data-dir", str(tmp_data_dir), "--retry-failed"]
            )

        assert result.exit_code == 0
        call_kwargs = mock_collect.call_args[1]
        assert call_kwargs.get("retry_failed") is True


def _make_pipeline_result(**kwargs):
    from lens.pipeline.orchestrator import PipelineResult

    return PipelineResult(**kwargs)
