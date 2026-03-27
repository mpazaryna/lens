"""Concurrent HTML content fetcher."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path

import aiohttp


@dataclass(frozen=True)
class FetchResult:
    """Result of fetching a single URL."""

    url: str
    success: bool
    path: Path | None = None
    error: str | None = None


def _url_to_filename(url: str) -> str:
    """Convert a URL to a safe filename."""
    # Use last path segment, fall back to hostname
    from urllib.parse import urlparse

    parsed = urlparse(url)
    segment = parsed.path.rstrip("/").split("/")[-1] if parsed.path.strip("/") else parsed.hostname
    # Sanitize
    safe = re.sub(r"[^\w\-.]", "_", segment or "page")
    return f"{safe}.html"


async def fetch_articles(
    urls: list[str],
    output_dir: Path,
    concurrency: int = 5,
    timeout: float = 15.0,
    overwrite: bool = False,
) -> list[FetchResult]:
    """Fetch HTML content from multiple URLs concurrently.

    Args:
        urls: Article URLs to fetch.
        output_dir: Directory to save HTML files.
        concurrency: Max concurrent downloads.
        timeout: Per-request timeout in seconds.
        overwrite: Whether to overwrite existing files.

    Returns:
        List of FetchResult for each URL.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(concurrency)
    results: list[FetchResult] = []

    async def _fetch_one(url: str, session: aiohttp.ClientSession) -> FetchResult:
        filename = _url_to_filename(url)
        dest = output_dir / filename

        if dest.exists() and not overwrite:
            return FetchResult(url=url, success=True, path=dest)

        async with semaphore:
            try:
                headers = {"User-Agent": "lens-py/0.1 (content aggregator)"}
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    headers=headers,
                ) as resp:
                    resp.raise_for_status()
                    html = await resp.text()

                dest.write_text(html, encoding="utf-8")
                return FetchResult(url=url, success=True, path=dest)
            except Exception as e:
                return FetchResult(url=url, success=False, error=str(e))

    async with aiohttp.ClientSession() as session:
        tasks = [_fetch_one(url, session) for url in urls]
        results = await asyncio.gather(*tasks)

    return list(results)
