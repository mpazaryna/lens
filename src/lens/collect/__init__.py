"""Collection pipeline: feed discovery, HTML retrieval, content extraction. No LLM."""

from lens.collect.extractor import (
    ExtractionResult,
    ExtractionResultItem,
    extract_article,
    extract_articles,
)
from lens.collect.fetcher import FetchResult, fetch_articles
from lens.collect.opml import OpmlFeed, parse_opml
from lens.collect.rss import Feed, FeedItem, fetch_feed, fetch_feeds

__all__ = [
    "ExtractionResult",
    "ExtractionResultItem",
    "Feed",
    "FeedItem",
    "FetchResult",
    "OpmlFeed",
    "extract_article",
    "extract_articles",
    "fetch_articles",
    "fetch_feed",
    "fetch_feeds",
    "parse_opml",
]
