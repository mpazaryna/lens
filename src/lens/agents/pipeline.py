"""Pipeline orchestration agent.

Coordinates the full feed processing pipeline:
feeds -> fetch -> extract -> summarize -> rank

Each phase is an independent async step with clean handoffs via the filesystem.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from lens.config import Config
from lens.extraction import extract_articles
from lens.feeds.opml import parse_opml
from lens.feeds.rss import fetch_feeds, Feed
from lens.processing.summarizer import summarize_batch
from lens.providers import LLMProvider, create_provider
from lens.ranking.ranker import rank_batch
from lens.retrieval.fetcher import fetch_articles


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


@dataclass
class SeenLedger:
    """Tracks which articles have been processed."""

    entries: dict[str, dict] = field(default_factory=dict)

    def is_seen(self, url: str) -> bool:
        return url in self.entries

    def mark_seen(self, url: str, title: str = "") -> None:
        from datetime import datetime, timezone

        self.entries[url] = {
            "processedAt": datetime.now(timezone.utc).isoformat(),
            "title": title,
        }

    def filter_new(self, urls: list[str]) -> list[str]:
        return [u for u in urls if not self.is_seen(u)]

    @classmethod
    def load(cls, path: Path) -> SeenLedger:
        if path.exists():
            data = json.loads(path.read_text())
            return cls(entries=data)
        return cls()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.entries, indent=2))


class PipelineAgent:
    """Orchestrates the content processing pipeline.

    Usage:
        config = load_config()
        agent = PipelineAgent(config)
        result = await agent.run()
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.provider: LLMProvider = create_provider(
            provider=config.provider,
            model=config.model,
            api_key=config.api_key,
            base_url=config.base_url,
        )

    async def run(
        self,
        concurrency: int = 5,
        overwrite: bool = False,
        category_filter: str | None = None,
    ) -> PipelineResult:
        """Execute the full pipeline.

        Args:
            concurrency: Max concurrent operations per phase.
            overwrite: Whether to overwrite existing files.
            category_filter: Optional OPML category filter.

        Returns:
            PipelineResult with counts and timing.
        """
        start = time.monotonic()
        result = PipelineResult()
        seen = SeenLedger.load(self.config.seen_path)

        # Phase 1: Parse OPML and fetch feeds
        print("Phase 1: Fetching feeds...")
        feed_items = await self._fetch_feeds(category_filter, result)

        if not feed_items:
            result.elapsed_seconds = time.monotonic() - start
            return result

        # Phase 2: Filter new items and fetch HTML
        urls = [item.link for item in feed_items if item.link]
        new_urls = seen.filter_new(urls)
        print(f"   {len(new_urls)} new, {len(urls) - len(new_urls)} already processed")

        if not new_urls:
            print("No new articles to process.")
            result.elapsed_seconds = time.monotonic() - start
            return result

        print(f"\nPhase 2: Fetching {len(new_urls)} articles...")
        fetch_results = await fetch_articles(
            new_urls,
            self.config.fetched_dir,
            concurrency=concurrency,
            overwrite=overwrite,
        )
        result.articles_fetched = sum(1 for r in fetch_results if r.success)
        for r in fetch_results:
            if not r.success:
                result.errors.append(f"Fetch failed: {r.url}: {r.error}")

        # Phase 3: Extract HTML to clean text
        print(f"\nPhase 3: Extracting content...")
        extract_results = extract_articles(
            self.config.fetched_dir,
            self.config.extracted_dir,
            overwrite=overwrite,
        )
        result.articles_extracted = sum(
            1 for _, r in extract_results if not isinstance(r, Exception)
        )
        for path, r in extract_results:
            if isinstance(r, Exception):
                result.errors.append(f"Extract failed: {path}: {r}")

        # Phase 4: Summarize with Anthropic API
        print(f"\nPhase 4: Summarizing {result.articles_extracted} articles...")
        articles_to_summarize = []
        for path, r in extract_results:
            if not isinstance(r, Exception):
                text = path.read_text(encoding="utf-8")
                articles_to_summarize.append((text, str(path)))

        if articles_to_summarize:
            summaries = await summarize_batch(
                articles_to_summarize,
                provider=self.provider,
                concurrency=concurrency,
            )

            self.config.processed_dir.mkdir(parents=True, exist_ok=True)
            for s in summaries:
                if s.success and s.summary:
                    result.articles_summarized += 1
                    out_path = self.config.processed_dir / f"{Path(s.source).stem}-summary.md"
                    out_path.write_text(
                        f"# {Path(s.source).stem}\n\n{s.summary}\n\n"
                        f"---\n*Model: {s.model} | {s.processing_time_ms:.0f}ms*\n",
                        encoding="utf-8",
                    )
                else:
                    result.errors.append(f"Summary failed: {s.source}: {s.error}")

        # Phase 5: Rank articles
        print(f"\nPhase 5: Ranking {result.articles_summarized} articles...")
        articles_to_rank = []
        for s in summaries if articles_to_summarize else []:
            if s.success and s.summary:
                articles_to_rank.append({
                    "title": Path(s.source).stem,
                    "summary": s.summary,
                    "source": s.source,
                })

        if articles_to_rank:
            rankings = await rank_batch(
                articles_to_rank,
                provider=self.provider,
                concurrency=concurrency,
            )

            result.articles_ranked = sum(1 for r in rankings if r.success)

            # Save rankings
            self.config.ranked_dir.mkdir(parents=True, exist_ok=True)
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
            (self.config.ranked_dir / "rankings.json").write_text(
                json.dumps(rankings_data, indent=2)
            )

        # Mark all new URLs as seen
        url_title_map = {item.link: item.title for item in feed_items}
        for url in new_urls:
            seen.mark_seen(url, url_title_map.get(url, ""))
        seen.save(self.config.seen_path)

        result.elapsed_seconds = time.monotonic() - start
        return result

    async def _fetch_feeds(
        self,
        category_filter: str | None,
        result: PipelineResult,
    ) -> list:
        """Parse OPML files and fetch all feeds."""
        from lens.feeds.rss import FeedItem

        opml_files = sorted(self.config.opml_dir.glob("*.opml"))
        if not opml_files:
            result.errors.append(f"No OPML files found in {self.config.opml_dir}")
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

        all_items = []
        for url, feed_or_error in feed_results:
            if isinstance(feed_or_error, Exception):
                result.errors.append(f"Feed fetch failed: {url}: {feed_or_error}")
            else:
                all_items.extend(feed_or_error.items)

        # Save feed JSON
        self.config.feeds_dir.mkdir(parents=True, exist_ok=True)
        for url, feed_or_error in feed_results:
            if isinstance(feed_or_error, Feed):
                feed = feed_or_error
                safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in feed.title)
                feed_path = self.config.feeds_dir / f"{safe_name.lower()}.json"
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
