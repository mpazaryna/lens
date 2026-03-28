"""Enrichment pipeline orchestration.

Processes items at 'extracted' status through LLM-powered stages
(summarization, ranking, etc.) with per-item state tracking.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from lens.pipeline.orchestrator import PipelineResult
from lens.pipeline.state import items_at_status, load_state, save_state

if TYPE_CHECKING:
    from lens.config import Config
    from lens.providers import LLMProvider

logger = logging.getLogger(__name__)


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

    # TODO: Step 3 will implement actual summarization here

    save_state(config.state_path, state)
    result.elapsed_seconds = time.monotonic() - start
    return result
