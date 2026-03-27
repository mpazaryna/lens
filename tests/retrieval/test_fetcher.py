"""Tests for content fetcher."""

from pathlib import Path

import pytest

from lens_py.retrieval.fetcher import _url_to_filename


class TestUrlToFilename:
    """Tests for URL to filename conversion."""

    def test_uses_last_path_segment(self) -> None:
        assert _url_to_filename("https://example.com/news/my-article") == "my-article.html"

    def test_falls_back_to_hostname(self) -> None:
        assert _url_to_filename("https://example.com") == "example.com.html"

    def test_sanitizes_special_characters(self) -> None:
        result = _url_to_filename("https://example.com/article?id=123&page=1")
        assert "?" not in result
        assert "&" not in result

    def test_handles_trailing_slash(self) -> None:
        result = _url_to_filename("https://example.com/article/")
        assert result == "article.html"
