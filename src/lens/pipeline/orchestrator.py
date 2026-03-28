"""Pipeline orchestration functions.

Coordinates the full feed processing pipeline:
Collection: feeds -> fetch -> extract
Enrichment: summarize -> rank

Each phase is a pure function with explicit inputs and outputs.
Uses the ADR-006 state tracker for per-item status tracking.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from lens.collect.extractor import ExtractionResultItem, extract_articles
from lens.collect.fetcher import FetchResult, fetch_articles
from lens.collect.opml import parse_opml
from lens.collect.rss import Feed, FeedItem, fetch_feeds
from lens.enrich.ranker import rank_batch
from lens.enrich.summarizer import SummaryResult, summarize_batch
from lens.pipeline.state import (
    discover_items,
    items_at_status,
    load_state,
    save_state,
    transition_item,
)

if TYPE_CHECKING:
    from lens.config import Config
    from lens.providers import LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Result of a full pipeline run."""

    feeds_found: int = 0
    articles_fetched: int = 0
    articles_extracted: int = 0
    articles_summarized: int = 0
    articles_ranked: int = 0
    errors: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0


# --- Pipeline phases ---


async def fetch_feed_items(
    config: Config,
    category_filter: str | None,
    result: PipelineResult,
) -> list[FeedItem]:
    """Phase 1: Parse OPML files and fetch all feed items."""
    opml_files = sorted(config.opml_dir.glob("*.opml"))
    if not opml_files:
        result.errors.append(f"No OPML files found in {config.opml_dir}")
        return []

    all_feed_sources = []
    for opml_path in opml_files:
        sources = parse_opml(opml_path, category_filter)
        all_feed_sources.extend(sources)

    if not all_feed_sources:
        result.errors.append("No feeds found in OPML files")
        return []

    result.feeds_found = len(all_feed_sources)
    logger.info("Found %d feeds in %d OPML file(s)", len(all_feed_sources), len(opml_files))

    urls = [s.xml_url for s in all_feed_sources]
    feed_results = await fetch_feeds(urls, concurrency=5)

    all_items: list[FeedItem] = []
    for url, feed_or_error in feed_results:
        if isinstance(feed_or_error, Exception):
            result.errors.append(f"Feed fetch failed: {url}: {feed_or_error}")
        else:
            all_items.extend(feed_or_error.items)

    # Save feed JSON
    config.feeds_dir.mkdir(parents=True, exist_ok=True)
    for _url, feed_or_error in feed_results:
        if isinstance(feed_or_error, Feed):
            feed = feed_or_error
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in feed.title)
            feed_path = config.feeds_dir / f"{safe_name.lower()}.json"
            feed_data = {
                "title": feed.title,
                "link": feed.link,
                "description": feed.description,
                "items": [
                    {
                        "title": i.title,
                        "link": i.link,
                        "description": i.description,
                        "pubDate": i.pub_date,
                        "guid": i.guid,
                    }
                    for i in feed.items
                ],
            }
            feed_path.write_text(json.dumps(feed_data, indent=2))

    logger.info("%d total items across all feeds", len(all_items))
    return all_items


async def fetch_html(
    urls: list[str],
    config: Config,
    result: PipelineResult,
    concurrency: int = 5,
    overwrite: bool = False,
) -> list[FetchResult]:
    """Phase 2: Fetch HTML content for article URLs."""
    fetch_results = await fetch_articles(
        urls,
        config.fetched_dir,
        concurrency=concurrency,
        overwrite=overwrite,
    )
    result.articles_fetched = sum(1 for r in fetch_results if r.success)
    for r in fetch_results:
        if not r.success:
            result.errors.append(f"Fetch failed: {r.url}: {r.error}")
    return fetch_results


def extract_content(
    config: Config,
    result: PipelineResult,
    overwrite: bool = False,
) -> list[ExtractionResultItem]:
    """Phase 3: Extract HTML to clean text (no LLM)."""
    extract_results = extract_articles(
        config.fetched_dir,
        config.extracted_dir,
        overwrite=overwrite,
    )
    result.articles_extracted = sum(1 for _, r in extract_results if not isinstance(r, Exception))
    for path, r in extract_results:
        if isinstance(r, Exception):
            result.errors.append(f"Extract failed: {path}: {r}")
    return extract_results


async def summarize_content(
    extract_results: list[ExtractionResultItem],
    config: Config,
    provider: LLMProvider,
    result: PipelineResult,
    concurrency: int = 5,
) -> list[SummaryResult]:
    """Phase 4: Summarize extracted articles via LLM."""
    articles_to_summarize = []
    for path, r in extract_results:
        if not isinstance(r, Exception):
            text = path.read_text(encoding="utf-8")
            articles_to_summarize.append((text, str(path)))

    if not articles_to_summarize:
        return []

    summaries = await summarize_batch(
        articles_to_summarize,
        provider=provider,
        concurrency=concurrency,
    )

    config.processed_dir.mkdir(parents=True, exist_ok=True)
    for s in summaries:
        if s.success and s.summary:
            result.articles_summarized += 1
            out_path = config.processed_dir / f"{Path(s.source).stem}-summary.md"
            out_path.write_text(
                f"# {Path(s.source).stem}\n\n{s.summary}\n\n"
                f"---\n*Model: {s.model} | {s.processing_time_ms:.0f}ms*\n",
                encoding="utf-8",
            )
        else:
            result.errors.append(f"Summary failed: {s.source}: {s.error}")

    return summaries


async def rank_content(
    summaries: list[SummaryResult],
    config: Config,
    provider: LLMProvider,
    result: PipelineResult,
    concurrency: int = 5,
) -> None:
    """Phase 5: Rank summarized articles via LLM tool use."""
    articles_to_rank = [
        {
            "title": Path(s.source).stem,
            "summary": s.summary,
            "source": s.source,
        }
        for s in summaries
        if s.success and s.summary
    ]

    if not articles_to_rank:
        return

    rankings = await rank_batch(
        articles_to_rank,
        provider=provider,
        concurrency=concurrency,
    )

    result.articles_ranked = sum(1 for r in rankings if r.success)

    config.ranked_dir.mkdir(parents=True, exist_ok=True)
    rankings_data = {
        "results": [
            {
                "title": r.title,
                "score": r.score,
                "confidence": r.confidence,
                "reasoning": r.reasoning,
                "categories": r.categories,
                "read_time": r.estimated_read_time,
            }
            for r in rankings
            if r.success
        ],
    }
    (config.ranked_dir / "rankings.json").write_text(json.dumps(rankings_data, indent=2))


# --- Collection orchestrator (state-tracker aware) ---


async def run_collection(
    config: Config,
    concurrency: int = 5,
    overwrite: bool = False,
    category_filter: str | None = None,
    retry_failed: bool = False,
) -> PipelineResult:
    """Execute the collection pipeline (feeds -> fetch -> extract).

    Uses the ADR-006 state tracker for per-item status tracking.
    Items already at 'fetched' skip to extraction. Items at 'extracted'
    or beyond are skipped entirely.

    Args:
        config: Application configuration.
        concurrency: Max concurrent operations per phase.
        overwrite: Whether to overwrite existing files.
        category_filter: Optional OPML category filter.
        retry_failed: Reset failed items and reprocess them.

    Returns:
        PipelineResult with counts and timing.
    """
    start = time.monotonic()
    result = PipelineResult()
    state = load_state(config.state_path)

    # Reset failed items if requested
    if retry_failed:
        failed = items_at_status(state, "failed")
        for item_id, item in failed.items():
            state[item_id] = {**item, "status": "new", "error": None}
        if failed:
            logger.info("Reset %d failed items for retry", len(failed))

    # Phase 1: Parse OPML and fetch feeds
    logger.info("Phase 1: Fetching feeds...")
    feed_items = await fetch_feed_items(config, category_filter, result)

    if not feed_items:
        result.elapsed_seconds = time.monotonic() - start
        return result

    # Discover new items in state tracker
    discovery_items = [
        {"url": item.link, "title": item.title, "feed": ""} for item in feed_items if item.link
    ]
    state = discover_items(state, discovery_items)

    # Phase 2: Fetch HTML for items at 'new' status
    new_items = items_at_status(state, "new")
    new_urls = [item["url"] for item in new_items.values()]

    logger.info(
        "%d new, %d already processed",
        len(new_urls),
        len(discovery_items) - len(new_urls),
    )

    if new_urls:
        logger.info("Phase 2: Fetching %d articles...", len(new_urls))
        fetch_results = await fetch_html(new_urls, config, result, concurrency, overwrite)

        # Update state per-item based on fetch results
        url_to_fetch = {r.url: r for r in fetch_results}
        for item_id, item in new_items.items():
            fetch_result = url_to_fetch.get(item["url"])
            if fetch_result and fetch_result.success:
                state[item_id] = transition_item(item, "fetched", stage_time=0.0)
            elif fetch_result and not fetch_result.success:
                state[item_id] = transition_item(
                    item, "failed", error=fetch_result.error or "Unknown fetch error"
                )

    # Phase 3: Extract HTML for items at 'fetched' status
    fetched_items = items_at_status(state, "fetched")
    if fetched_items:
        logger.info("Phase 3: Extracting content...")
        extract_content(config, result, overwrite)

        # Mark fetched items as extracted
        for item_id, item in fetched_items.items():
            state[item_id] = transition_item(item, "extracted", stage_time=0.0)

    # Save state
    save_state(config.state_path, state)

    result.elapsed_seconds = time.monotonic() - start
    return result


# --- Full pipeline orchestrator ---


async def run_pipeline(
    config: Config,
    provider: LLMProvider,
    concurrency: int = 5,
    overwrite: bool = False,
    category_filter: str | None = None,
) -> PipelineResult:
    """Execute the full pipeline (collection + enrichment).

    Args:
        config: Application configuration.
        provider: LLM provider for summarization and ranking.
        concurrency: Max concurrent operations per phase.
        overwrite: Whether to overwrite existing files.
        category_filter: Optional OPML category filter.

    Returns:
        PipelineResult with counts and timing.
    """
    start = time.monotonic()

    # Run collection
    result = await run_collection(config, concurrency, overwrite, category_filter)

    # Phase 4: Summarize
    logger.info("Phase 4: Summarizing %d articles...", result.articles_extracted)
    extract_results = extract_content(config, result, overwrite=False)
    summaries = await summarize_content(extract_results, config, provider, result, concurrency)

    # Phase 5: Rank
    logger.info("Phase 5: Ranking %d articles...", result.articles_summarized)
    await rank_content(summaries, config, provider, result, concurrency)

    result.elapsed_seconds = time.monotonic() - start
    return result
