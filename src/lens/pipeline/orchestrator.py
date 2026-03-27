"""Pipeline orchestration functions.

Coordinates the full feed processing pipeline:
Collection: feeds -> fetch -> extract
Enrichment: summarize -> rank

Each phase is a pure function with explicit inputs and outputs.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from lens.config import Config
from lens.collect.extractor import extract_articles
from lens.collect.opml import parse_opml
from lens.collect.rss import fetch_feeds, Feed, FeedItem
from lens.collect.fetcher import fetch_articles
from lens.enrich.summarizer import summarize_batch
from lens.enrich.ranker import rank_batch
from lens.providers import LLMProvider


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


# --- Seen ledger (pure data + functions) ---


def load_seen(path: Path) -> dict[str, dict]:
    """Load the seen ledger from disk."""
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_seen(path: Path, ledger: dict[str, dict]) -> None:
    """Save the seen ledger to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2))


def filter_new_urls(urls: list[str], seen: dict[str, dict]) -> list[str]:
    """Return only URLs not already in the seen ledger."""
    return [u for u in urls if u not in seen]


def mark_seen(
    ledger: dict[str, dict],
    urls: list[str],
    title_map: dict[str, str],
) -> dict[str, dict]:
    """Return a new ledger with the given URLs marked as seen."""
    now = datetime.now(timezone.utc).isoformat()
    updated = {**ledger}
    for url in urls:
        updated[url] = {"processedAt": now, "title": title_map.get(url, "")}
    return updated


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
    print(f"   Found {len(all_feed_sources)} feeds in {len(opml_files)} OPML file(s)")

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

    print(f"   {len(all_items)} total items across all feeds")
    return all_items


async def fetch_html(
    urls: list[str],
    config: Config,
    result: PipelineResult,
    concurrency: int = 5,
    overwrite: bool = False,
) -> None:
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


def extract_content(
    config: Config,
    result: PipelineResult,
    overwrite: bool = False,
) -> list[tuple[Path, object]]:
    """Phase 3: Extract HTML to clean text (no LLM)."""
    extract_results = extract_articles(
        config.fetched_dir,
        config.extracted_dir,
        overwrite=overwrite,
    )
    result.articles_extracted = sum(
        1 for _, r in extract_results if not isinstance(r, Exception)
    )
    for path, r in extract_results:
        if isinstance(r, Exception):
            result.errors.append(f"Extract failed: {path}: {r}")
    return extract_results


async def summarize_content(
    extract_results: list[tuple[Path, object]],
    config: Config,
    provider: LLMProvider,
    result: PipelineResult,
    concurrency: int = 5,
) -> list:
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
    summaries: list,
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


# --- Top-level orchestrator ---


async def run_pipeline(
    config: Config,
    provider: LLMProvider,
    concurrency: int = 5,
    overwrite: bool = False,
    category_filter: str | None = None,
) -> PipelineResult:
    """Execute the full pipeline.

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
    result = PipelineResult()
    seen = load_seen(config.seen_path)

    # Phase 1: Parse OPML and fetch feeds
    print("Phase 1: Fetching feeds...")
    feed_items = await fetch_feed_items(config, category_filter, result)

    if not feed_items:
        result.elapsed_seconds = time.monotonic() - start
        return result

    # Phase 2: Filter new items and fetch HTML
    urls = [item.link for item in feed_items if item.link]
    new_urls = filter_new_urls(urls, seen)
    print(f"   {len(new_urls)} new, {len(urls) - len(new_urls)} already processed")

    if not new_urls:
        print("No new articles to process.")
        result.elapsed_seconds = time.monotonic() - start
        return result

    print(f"\nPhase 2: Fetching {len(new_urls)} articles...")
    await fetch_html(new_urls, config, result, concurrency, overwrite)

    # Phase 3: Extract HTML to clean text
    print("\nPhase 3: Extracting content...")
    extract_results = extract_content(config, result, overwrite)

    # Phase 4: Summarize
    print(f"\nPhase 4: Summarizing {result.articles_extracted} articles...")
    summaries = await summarize_content(extract_results, config, provider, result, concurrency)

    # Phase 5: Rank
    print(f"\nPhase 5: Ranking {result.articles_summarized} articles...")
    await rank_content(summaries, config, provider, result, concurrency)

    # Update seen ledger
    title_map = {item.link: item.title for item in feed_items}
    updated_seen = mark_seen(seen, new_urls, title_map)
    save_seen(config.seen_path, updated_seen)

    result.elapsed_seconds = time.monotonic() - start
    return result
