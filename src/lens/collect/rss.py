"""RSS/Atom feed fetcher and parser using feedparser."""

from __future__ import annotations

import asyncio
import logging
import ssl
from dataclasses import dataclass, field

import aiohttp
import certifi
import feedparser

from lens.errors import FeedFetchError, FeedParseError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FeedItem:
    """A single item from an RSS/Atom feed."""

    title: str
    link: str
    description: str
    pub_date: str
    guid: str


@dataclass(frozen=True)
class Feed:
    """A parsed RSS/Atom feed."""

    title: str
    link: str
    description: str
    items: list[FeedItem] = field(default_factory=list)


async def fetch_feed(
    url: str,
    timeout: float = 10.0,
    session: aiohttp.ClientSession | None = None,
) -> Feed:
    """Fetch and parse an RSS/Atom feed.

    Args:
        url: Feed URL to fetch.
        timeout: Request timeout in seconds.
        session: Optional aiohttp session to reuse.

    Returns:
        Parsed Feed object.

    Raises:
        FeedFetchError: On network errors.
        FeedParseError: On parse errors.
    """
    own_session = session is None
    if own_session:
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_ctx))

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
            resp.raise_for_status()
            xml_content = await resp.text()
    except aiohttp.ClientError as e:
        raise FeedFetchError(f"Failed to fetch feed {url}: {e}") from e
    finally:
        if own_session:
            await session.close()

    return parse_feed(xml_content)


def parse_feed(xml_content: str) -> Feed:
    """Parse RSS/Atom XML content into a Feed object."""
    parsed = feedparser.parse(xml_content)

    if parsed.bozo and not parsed.entries:
        raise FeedParseError(f"Failed to parse feed: {parsed.bozo_exception}")

    feed_info = parsed.feed
    items = [
        FeedItem(
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            description=entry.get("summary", entry.get("description", "")),
            pub_date=entry.get("published", entry.get("updated", "")),
            guid=entry.get("id", entry.get("link", "")),
        )
        for entry in parsed.entries
    ]

    return Feed(
        title=feed_info.get("title", ""),
        link=feed_info.get("link", ""),
        description=feed_info.get("subtitle", feed_info.get("description", "")),
        items=items,
    )


async def fetch_feeds(
    urls: list[str],
    concurrency: int = 5,
    timeout: float = 10.0,
) -> list[tuple[str, Feed | Exception]]:
    """Fetch multiple feeds concurrently.

    Args:
        urls: List of feed URLs.
        concurrency: Max concurrent requests.
        timeout: Per-request timeout in seconds.

    Returns:
        List of (url, Feed | Exception) tuples.
    """
    semaphore = asyncio.Semaphore(concurrency)
    results: list[tuple[str, Feed | Exception]] = []

    async def _fetch_one(url: str, session: aiohttp.ClientSession) -> None:
        async with semaphore:
            try:
                feed = await fetch_feed(url, timeout=timeout, session=session)
                results.append((url, feed))
            except (FeedFetchError, FeedParseError) as e:
                logger.warning("Feed failed: %s: %s", url, e)
                results.append((url, e))

    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_ctx)
    async with aiohttp.ClientSession(connector=connector) as session, asyncio.TaskGroup() as tg:
        for url in urls:
            tg.create_task(_fetch_one(url, session))

    return results
