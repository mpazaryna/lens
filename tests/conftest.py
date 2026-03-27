"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_opml(fixtures_dir: Path) -> Path:
    """Path to sample OPML file."""
    return fixtures_dir / "sample.opml"


@pytest.fixture
def sample_html(fixtures_dir: Path) -> str:
    """Sample HTML content for testing extraction."""
    return (fixtures_dir / "sample_article.html").read_text()


@pytest.fixture
def sample_extracted_text() -> str:
    """Sample extracted article text."""
    return (
        "AI models are becoming increasingly capable at complex reasoning tasks. "
        "Recent benchmarks show significant improvements in coding, mathematics, "
        "and multi-step problem solving. These advances raise important questions "
        "about safety, alignment, and responsible deployment."
    )


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Temporary data directory mimicking production layout."""
    for subdir in ["opml", "feeds", "fetched", "extracted", "processed", "ranked"]:
        (tmp_path / subdir).mkdir()
    return tmp_path
