"""Application configuration loaded from environment.

Resolution chain (ADR-003): CLI flag > environment variable > default.
Default data directory is ~/.lens. Development fallback uses data/ if it
exists in the project root and no explicit config is set.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


class Config(BaseModel):
    """Immutable application configuration."""

    data_dir: Path
    provider: str
    api_key: str
    model: str
    base_url: str | None
    log_level: str
    opml_path: Path

    @property
    def opml_dir(self) -> Path:
        return self.data_dir / "opml"

    @property
    def feeds_dir(self) -> Path:
        return self.data_dir / "feeds"

    @property
    def fetched_dir(self) -> Path:
        return self.data_dir / "fetched"

    @property
    def extracted_dir(self) -> Path:
        return self.data_dir / "extracted"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def ranked_dir(self) -> Path:
        return self.data_dir / "ranked"

    @property
    def seen_path(self) -> Path:
        return self.data_dir / "seen.json"

    @property
    def state_path(self) -> Path:
        return self.data_dir / "state.json"

    @property
    def logs_dir(self) -> Path:
        return self.data_dir / "logs"


def _resolve_data_dir(
    data_dir_override: Path | None = None,
    project_root: Path | None = None,
) -> Path:
    """Resolve the data directory using the ADR-003 precedence chain.

    Order: CLI flag > LENS_DATA_DIR env var > dev data/ fallback > ~/.lens default.
    """
    # CLI flag takes precedence
    if data_dir_override is not None:
        return data_dir_override

    # Environment variable
    env_val = os.getenv("LENS_DATA_DIR")
    if env_val:
        return Path(env_val)

    # Development fallback: data/ in project root
    root = project_root or Path.cwd()
    dev_data = root / "data"
    if dev_data.is_dir():
        return dev_data

    # Default
    return Path.home() / ".lens"


def _resolve_opml_path(
    data_dir: Path,
    opml_override: Path | None = None,
) -> Path:
    """Resolve the OPML source path.

    Order: CLI flag > LENS_OPML_PATH env var > {data_dir}/feeds.opml default.
    """
    if opml_override is not None:
        return opml_override

    env_val = os.getenv("LENS_OPML_PATH")
    if env_val:
        return Path(env_val)

    return data_dir / "feeds.opml"


def load_config(
    env_path: Path | None = None,
    data_dir_override: Path | None = None,
    opml_override: Path | None = None,
    project_root: Path | None = None,
) -> Config:
    """Load configuration from environment variables with CLI overrides.

    Args:
        env_path: Path to .env file.
        data_dir_override: CLI --data-dir flag value.
        opml_override: CLI --opml flag value.
        project_root: Project root for dev data/ fallback detection.

    Returns:
        Resolved Config instance.
    """
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    data_dir = _resolve_data_dir(data_dir_override, project_root)
    opml_path = _resolve_opml_path(data_dir, opml_override)

    return Config(
        data_dir=data_dir,
        provider=os.getenv("LENS_PROVIDER", "anthropic"),
        api_key=os.getenv("LENS_API_KEY", os.getenv("ANTHROPIC_API_KEY", "")),
        model=os.getenv("LENS_MODEL", "claude-sonnet-4-20250514"),
        base_url=os.getenv("LENS_BASE_URL"),
        log_level=os.getenv("LENS_LOG_LEVEL", "info"),
        opml_path=opml_path,
    )
