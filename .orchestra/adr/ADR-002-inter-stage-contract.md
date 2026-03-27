# ADR-002: Inter-Stage Contract -- Filesystem Handoffs

**Date:** 2026-03-27
**Status:** Active
**Decision:** Pipeline stages communicate through filesystem handoffs. Each stage reads from and writes to a directory. No in-memory passing between stages.

## Context

The pipeline has five stages: feeds, retrieval, extraction, summarization, and ranking. Each stage produces output that the next stage consumes. The question is whether stages pass data in-memory (function return values piped through the orchestrator) or through the filesystem (each stage writes files, the next stage reads them).

The existing codebase already uses filesystem handoffs. This ADR formalizes that choice and explains why.

## Decision

1. **Each stage writes its output to a directory** inside the data directory (e.g., `fetched/`, `extracted/`, `processed/`). Output format is JSON or markdown depending on the stage.
2. **Each stage reads its input from the previous stage's output directory.** Stages are decoupled -- they don't import each other or share in-memory state.
3. **The orchestrator coordinates stage execution** but does not shuttle data between stages. It invokes stages in order and passes directory paths, not data.
4. **Stage output is append-only during a run.** Files written by a stage are not modified by subsequent stages. This makes debugging and recovery straightforward.

## Rationale

- **Debuggability.** When something goes wrong, every intermediate result is on disk. You can inspect fetched HTML, extracted text, and summaries independently without re-running the pipeline.
- **Recovery.** If the pipeline crashes mid-summarization, extraction output is still on disk. The state tracker can resume from the last completed stage per item without reprocessing.
- **Horizontal scaling.** Multiple machines can share a data directory (NFS, S3-backed FUSE, etc.) and process different items. In-memory passing locks you to a single process.
- **Composability.** Stages can be run independently via the CLI (`lens extract` already works this way). Adding a new stage doesn't require touching the orchestrator's data flow.
- **Simplicity.** The filesystem is the message queue. No need for Redis, Celery, or in-process pub/sub.

## Trade-offs

- **I/O overhead.** Writing and reading files is slower than passing Python objects. For the expected volume (hundreds of feed items, not millions), this is negligible compared to network and LLM latency.
- **Serialization cost.** Data must be serializable to JSON. This is already true of the frozen dataclasses used throughout.
- **Disk usage.** Intermediate files accumulate. Mitigated by the state tracker marking items as done and a future cleanup policy.

## Consequences

- All stage functions accept directory paths as arguments, not data objects.
- The orchestrator's job is sequencing and error handling, not data transformation.
- New stages must follow the same contract: read from input dir, write to output dir.
- The data directory layout (ADR-003) is load-bearing -- directory names and file formats are part of the stage contract.
