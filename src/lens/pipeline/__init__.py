"""Pipeline orchestration: coordinates feed processing phases."""

from lens.pipeline.enrichment import run_enrichment
from lens.pipeline.orchestrator import (
    PipelineResult,
    run_collection,
    run_pipeline,
)

__all__ = [
    "PipelineResult",
    "run_collection",
    "run_enrichment",
    "run_pipeline",
]
