"""Collection pipeline: feed discovery, HTML retrieval, content extraction. No LLM."""

from lens.collect.opml import parse_opml, OpmlFeed
from lens.collect.rss import fetch_feed, fetch_feeds, FeedItem, Feed
from lens.collect.fetcher import fetch_articles, FetchResult
from lens.collect.extractor import extract_article, extract_articles, ExtractionResult

__all__ = [
    "parse_opml",
    "OpmlFeed",
    "fetch_feed",
    "fetch_feeds",
    "FeedItem",
    "Feed",
    "fetch_articles",
    "FetchResult",
    "extract_article",
    "extract_articles",
    "ExtractionResult",
]
