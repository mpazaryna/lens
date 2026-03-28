"""Enrichment pipeline orchestration.

Processes items at 'extracted' status through LLM-powered stages
(summarization, ranking, etc.) with per-item state tracking.
"""

from __future__ import annotations

import json
import logging
import time
from typing import TYPE_CHECKING

from lens.enrich.summarizer import summarize_article
from lens.pipeline.orchestrator import PipelineResult
from lens.pipeline.state import (
    items_at_status,
    load_state,
    save_state,
    transition_item,
)

if TYPE_CHECKING:
    from lens.config import Config
    from lens.providers import LLMProvider

logger = logging.getLogger(__name__)


def _find_extracted_text(config: Config, url: str, feed: str) -> str | None:
    """Find the extracted markdown file for a given item.

    Searches both feed subdirectories and flat extracted/ directory.
    """
    # Try feed subdirectory first
    if feed:
        feed_dir = config.extracted_dir / feed
        if feed_dir.exists():
            for md_file in feed_dir.glob("*.md"):
                return md_file.read_text(encoding="utf-8")

    # Fall back to flat directory
    for md_file in config.extracted_dir.glob("*.md"):
        return md_file.read_text(encoding="utf-8")

    return None


async def run_enrichment(
    config: Config,
    provider: LLMProvider,
    concurrency: int = 5,
    retry_failed: bool = False,
) -> PipelineResult:
    """Execute the enrichment pipeline against previously collected content.

    Processes items at 'extracted' status through summarization.
    Updates state tracker to 'summarized' on success or 'failed' on error.

    Args:
        config: Application configuration.
        provider: LLM provider for enrichment stages.
        concurrency: Max concurrent LLM calls.
        retry_failed: Reset failed enrichment items and reprocess.

    Returns:
        PipelineResult with enrichment counts and timing.
    """
    start = time.monotonic()
    result = PipelineResult()
    state = load_state(config.state_path)

    if retry_failed:
        failed = items_at_status(state, "failed")
        for item_id, item in failed.items():
            state[item_id] = {**item, "status": "extracted", "error": None}
        if failed:
            logger.info("Reset %d failed enrichment items for retry", len(failed))

    extracted = items_at_status(state, "extracted")
    if not extracted:
        logger.info("No items at 'extracted' status to enrich.")
        result.elapsed_seconds = time.monotonic() - start
        return result

    logger.info("Enriching %d articles...", len(extracted))
    config.processed_dir.mkdir(parents=True, exist_ok=True)

    for item_id, item in extracted.items():
        text = _find_extracted_text(config, item["url"], item.get("feed", ""))
        if not text:
            logger.warning("No extracted text found for %s", item["url"])
            state[item_id] = transition_item(item, "failed", error="No extracted text found")
            result.errors.append(f"No text: {item['url']}")
            continue

        stage_start = time.monotonic()
        summary_result = await summarize_article(text, item["url"], provider)
        stage_time = time.monotonic() - stage_start

        if summary_result.success and summary_result.summary:
            state[item_id] = transition_item(item, "summarized", stage_time=stage_time)
            result.articles_summarized += 1

            # Write structured JSON output
            out_path = config.processed_dir / f"{item_id}.json"
            output = {
                "title": item.get("title", ""),
                "source_url": item["url"],
                "feed_name": item.get("feed", ""),
                "summary_text": summary_result.summary,
                "word_count": len(summary_result.summary.split()),
                "provider": summary_result.model or "",
                "model": summary_result.model or "",
                "timestamp": state[item_id]["updated_at"],
                "processing_time_ms": summary_result.processing_time_ms or 0,
            }
            out_path.write_text(json.dumps(output, indent=2))
        else:
            state[item_id] = transition_item(
                item, "failed", error=summary_result.error or "Unknown error"
            )
            result.errors.append(f"Summary failed: {item['url']}: {summary_result.error}")

    save_state(config.state_path, state)
    result.elapsed_seconds = time.monotonic() - start
    return result
