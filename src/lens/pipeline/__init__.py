"""Pipeline orchestration: coordinates feed processing phases."""

from lens.pipeline.orchestrator import (
    PipelineResult,
    filter_new_urls,
    load_seen,
    mark_seen,
    run_pipeline,
    save_seen,
)

__all__ = [
    "run_pipeline",
    "PipelineResult",
    "load_seen",
    "save_seen",
    "filter_new_urls",
    "mark_seen",
]
