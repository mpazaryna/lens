"""Application configuration loaded from environment."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


class Config(BaseModel):
    """Immutable application configuration."""

    data_dir: Path
    anthropic_api_key: str
    model: str
    log_level: str

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


def load_config(env_path: Path | None = None) -> Config:
    """Load configuration from environment variables."""
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    return Config(
        data_dir=Path(os.getenv("LENS_DATA_DIR", "data")),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        model=os.getenv("LENS_MODEL", "claude-sonnet-4-20250514"),
        log_level=os.getenv("LENS_LOG_LEVEL", "info"),
    )
