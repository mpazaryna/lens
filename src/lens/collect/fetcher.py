"""Concurrent HTML content fetcher."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

import aiohttp

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

# Per-request timeout for downloading article HTML (seconds)
FETCH_TIMEOUT_SECONDS = 15.0


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
    timeout: float = FETCH_TIMEOUT_SECONDS,
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
                logger.debug("Fetched %s -> %s", url, dest.name)
                return FetchResult(url=url, success=True, path=dest)
            except aiohttp.ClientError as e:
                logger.warning("Fetch failed: %s: %s", url, e)
                return FetchResult(url=url, success=False, error=str(e))
            except OSError as e:
                logger.warning("Write failed: %s: %s", dest, e)
                return FetchResult(url=url, success=False, error=str(e))

    async with aiohttp.ClientSession() as session:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(_fetch_one(url, session)) for url in urls]
        results = [t.result() for t in tasks]

    return results
