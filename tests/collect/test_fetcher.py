"""Tests for content fetcher."""

from pathlib import Path

import aiohttp
import pytest
from aioresponses import aioresponses

from lens.collect.fetcher import FetchResult, _url_to_filename, fetch_articles


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


@pytest.mark.asyncio
class TestFetchArticles:
    """Tests for async article fetching."""

    async def test_fetches_and_saves_html(self, tmp_path: Path) -> None:
        url = "https://example.com/article-1"
        html = "<html><body><p>Hello</p></body></html>"

        with aioresponses() as m:
            m.get(url, body=html)
            results = await fetch_articles([url], tmp_path)

        assert len(results) == 1
        assert results[0].success is True
        assert results[0].path is not None
        assert results[0].path.read_text() == html

    async def test_returns_error_on_404(self, tmp_path: Path) -> None:
        url = "https://example.com/not-found"

        with aioresponses() as m:
            m.get(url, status=404)
            results = await fetch_articles([url], tmp_path)

        assert len(results) == 1
        assert results[0].success is False
        assert results[0].error is not None

    async def test_returns_error_on_connection_failure(self, tmp_path: Path) -> None:
        url = "https://example.com/down"

        with aioresponses() as m:
            m.get(url, exception=aiohttp.ClientConnectionError("Connection refused"))
            results = await fetch_articles([url], tmp_path)

        assert len(results) == 1
        assert results[0].success is False
        assert "Connection refused" in results[0].error

    async def test_skips_existing_without_overwrite(self, tmp_path: Path) -> None:
        url = "https://example.com/article-1"
        dest = tmp_path / "article-1.html"
        dest.write_text("existing content")

        with aioresponses():
            # Should not be called
            results = await fetch_articles([url], tmp_path, overwrite=False)

        assert len(results) == 1
        assert results[0].success is True
        assert dest.read_text() == "existing content"

    async def test_overwrites_with_flag(self, tmp_path: Path) -> None:
        url = "https://example.com/article-1"
        dest = tmp_path / "article-1.html"
        dest.write_text("old content")
        new_html = "<html><body><p>Updated</p></body></html>"

        with aioresponses() as m:
            m.get(url, body=new_html)
            results = await fetch_articles([url], tmp_path, overwrite=True)

        assert results[0].success is True
        assert dest.read_text() == new_html

    async def test_concurrent_fetches(self, tmp_path: Path) -> None:
        urls = [f"https://example.com/article-{i}" for i in range(5)]

        with aioresponses() as m:
            for url in urls:
                m.get(url, body=f"<html>{url}</html>")
            results = await fetch_articles(urls, tmp_path, concurrency=3)

        assert len(results) == 5
        assert all(r.success for r in results)

    async def test_creates_output_directory(self, tmp_path: Path) -> None:
        url = "https://example.com/article-1"
        out_dir = tmp_path / "deep" / "nested"

        with aioresponses() as m:
            m.get(url, body="<html></html>")
            await fetch_articles([url], out_dir)

        assert out_dir.exists()

    async def test_result_is_frozen(self) -> None:
        result = FetchResult(url="https://example.com", success=True)
        with pytest.raises(AttributeError):
            result.url = "modified"  # type: ignore[misc]
