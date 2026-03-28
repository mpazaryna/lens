"""Tests for application configuration.

Derived from gherkin.md Step 1 scenarios:
- Data directory resolution (CLI > env > default)
- OPML source path resolution
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from lens.config import load_config, resolve_stage_provider

if TYPE_CHECKING:
    import pytest


class TestDataDirectoryResolution:
    """Feature: Data directory resolution."""

    def test_default_data_directory(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Scenario: Default data directory.

        Given no LENS_DATA_DIR environment variable is set
        And no --data-dir CLI flag is provided
        Then the data directory resolves to ~/.lens
        """
        monkeypatch.delenv("LENS_DATA_DIR", raising=False)
        # Use a project_root with no data/ dir to avoid dev fallback
        config = load_config(project_root=tmp_path)
        assert config.data_dir == Path.home() / ".lens"

    def test_env_var_overrides_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scenario: Environment variable overrides default.

        Given LENS_DATA_DIR is set to /tmp/lens-data
        And no --data-dir CLI flag is provided
        Then the data directory resolves to /tmp/lens-data
        """
        monkeypatch.setenv("LENS_DATA_DIR", "/tmp/lens-data")
        config = load_config()
        assert config.data_dir == Path("/tmp/lens-data")

    def test_cli_flag_overrides_env_var(self) -> None:
        """Scenario: CLI flag overrides environment variable.

        Given LENS_DATA_DIR is set to /tmp/lens-data
        And the --data-dir CLI flag is set to /opt/lens
        Then the data directory resolves to /opt/lens
        """
        config = load_config(data_dir_override=Path("/opt/lens"))
        assert config.data_dir == Path("/opt/lens")

    def test_dev_fallback(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Scenario: Development fallback.

        Given no LENS_DATA_DIR environment variable is set
        And no --data-dir CLI flag is provided
        And a data/ directory exists in the project root
        Then the data directory resolves to data/
        """
        monkeypatch.delenv("LENS_DATA_DIR", raising=False)
        dev_data = tmp_path / "data"
        dev_data.mkdir()
        config = load_config(project_root=tmp_path)
        assert config.data_dir == dev_data

    def test_derived_paths_resolve_from_root(self) -> None:
        """Scenario: Derived paths resolve from configured root.

        Given the data directory resolves to /tmp/lens-data
        Then all subdirectory properties resolve from that root.
        """
        config = load_config(data_dir_override=Path("/tmp/lens-data"))
        assert config.feeds_dir == Path("/tmp/lens-data/feeds")
        assert config.fetched_dir == Path("/tmp/lens-data/fetched")
        assert config.extracted_dir == Path("/tmp/lens-data/extracted")
        assert config.processed_dir == Path("/tmp/lens-data/processed")
        assert config.ranked_dir == Path("/tmp/lens-data/ranked")


class TestOpmlPathResolution:
    """Feature: OPML source path resolution."""

    def test_default_opml_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Scenario: Default OPML path.

        Given the data directory resolves to ~/.lens
        And no LENS_OPML_PATH environment variable is set
        Then the OPML path resolves to ~/.lens/feeds.opml
        """
        monkeypatch.delenv("LENS_DATA_DIR", raising=False)
        monkeypatch.delenv("LENS_OPML_PATH", raising=False)
        config = load_config(project_root=tmp_path)
        assert config.opml_path == Path.home() / ".lens" / "feeds.opml"

    def test_env_var_overrides_default_opml(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scenario: Environment variable overrides default.

        Given LENS_OPML_PATH is set to /etc/lens/my-feeds.opml
        Then the OPML path resolves to /etc/lens/my-feeds.opml
        """
        monkeypatch.setenv("LENS_OPML_PATH", "/etc/lens/my-feeds.opml")
        config = load_config()
        assert config.opml_path == Path("/etc/lens/my-feeds.opml")

    def test_cli_flag_overrides_env_opml(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Scenario: CLI flag overrides environment variable.

        Given LENS_OPML_PATH is set to /etc/lens/my-feeds.opml
        And the --opml CLI flag is set to /tmp/test.opml
        Then the OPML path resolves to /tmp/test.opml
        """
        monkeypatch.setenv("LENS_OPML_PATH", "/etc/lens/my-feeds.opml")
        config = load_config(opml_override=Path("/tmp/test.opml"))
        assert config.opml_path == Path("/tmp/test.opml")


class TestPerStageProviderResolution:
    """Feature: Per-stage provider resolution (ADR-004)."""

    def test_default_provider_when_no_stage_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Default provider used when no stage-specific config is set."""
        monkeypatch.setenv("LENS_PROVIDER", "ollama")
        monkeypatch.setenv("LENS_MODEL", "llama3.2")
        monkeypatch.delenv("LENS_SUMMARIZE_PROVIDER", raising=False)
        monkeypatch.delenv("LENS_SUMMARIZE_MODEL", raising=False)

        result = resolve_stage_provider("summarize")
        assert result["provider"] == "ollama"
        assert result["model"] == "llama3.2"

    def test_stage_provider_overrides_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Stage-specific provider overrides default."""
        monkeypatch.setenv("LENS_PROVIDER", "ollama")
        monkeypatch.setenv("LENS_SUMMARIZE_PROVIDER", "anthropic")
        monkeypatch.setenv("LENS_SUMMARIZE_MODEL", "claude-haiku-4-5-20251001")

        result = resolve_stage_provider("summarize")
        assert result["provider"] == "anthropic"
        assert result["model"] == "claude-haiku-4-5-20251001"

    def test_partial_override_inherits_provider(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Partial override: set model but not provider, inherits default."""
        monkeypatch.setenv("LENS_PROVIDER", "ollama")
        monkeypatch.setenv("LENS_MODEL", "llama3.2")
        monkeypatch.setenv("LENS_SUMMARIZE_MODEL", "devstral:24b")
        monkeypatch.delenv("LENS_SUMMARIZE_PROVIDER", raising=False)

        result = resolve_stage_provider("summarize")
        assert result["provider"] == "ollama"
        assert result["model"] == "devstral:24b"

    def test_stage_api_key_overrides_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Stage-specific API key overrides default."""
        monkeypatch.setenv("LENS_API_KEY", "default-key")
        monkeypatch.setenv("LENS_SUMMARIZE_API_KEY", "summarize-key")

        result = resolve_stage_provider("summarize")
        assert result["api_key"] == "summarize-key"

    def test_independent_stage_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Summarize and rank resolve independently."""
        monkeypatch.setenv("LENS_PROVIDER", "ollama")
        monkeypatch.setenv("LENS_SUMMARIZE_PROVIDER", "ollama")
        monkeypatch.setenv("LENS_SUMMARIZE_MODEL", "llama3.2")
        monkeypatch.setenv("LENS_RANK_PROVIDER", "anthropic")
        monkeypatch.setenv("LENS_RANK_MODEL", "claude-sonnet-4-20250514")

        summarize = resolve_stage_provider("summarize")
        rank = resolve_stage_provider("rank")
        assert summarize["provider"] == "ollama"
        assert rank["provider"] == "anthropic"
        assert summarize["model"] != rank["model"]

    def test_default_api_key_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """API key falls back through chain: stage > LENS_API_KEY > ANTHROPIC_API_KEY."""
        monkeypatch.delenv("LENS_SUMMARIZE_API_KEY", raising=False)
        monkeypatch.delenv("LENS_API_KEY", raising=False)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-fallback")

        result = resolve_stage_provider("summarize")
        assert result["api_key"] == "anthropic-fallback"
