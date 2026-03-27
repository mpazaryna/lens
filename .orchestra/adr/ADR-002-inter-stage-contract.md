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
- **Vertical scaling.** Multiple async workers on a single machine process different items concurrently. In-memory passing locks you to a single orchestrator thread.
- **Composability.** Stages can be run independently via the CLI (`lens extract` already works this way). Adding a new stage doesn't require touching the orchestrator's data flow.
- **Simplicity.** The filesystem is the message queue. No need for Redis, Celery, or in-process pub/sub.

## Trade-offs

- **I/O overhead.** Writing and reading files is slower than passing Python objects. For the expected volume (hundreds of feed items, not millions), this is negligible compared to network and LLM latency.
- **Serialization cost.** Data must be serializable to JSON. This is already true of the frozen dataclasses used throughout.
- **Disk usage.** Intermediate files accumulate. Mitigated by the state tracker marking items as done and a future cleanup policy.

## Scaling: Vertical vs. Horizontal

### Vertical scaling (single machine, multiple workers)

Filesystem handoffs work well here. A single machine runs multiple async workers via the orchestrator's semaphore-based concurrency. All workers share a local filesystem with reliable POSIX file locking. `state.json` with advisory locks is sufficient because there's no network in the path.

This is the current model and it handles small-scale multi-tenant use (up to ~10 concurrent users) without issues.

### Horizontal scaling (multiple instances)

Filesystem handoffs break down as soon as you run multiple instances, even in the 1-10 user range. The problems:

1. **Work claiming.** Two instances poll the same feed queue and both try to summarize the same article. Without a coordination mechanism, work is duplicated or corrupted.
2. **Shared state.** `state.json` with advisory file locks does not work reliably across machines. NFS advisory locks are notoriously inconsistent across implementations and can silently fail.
3. **Output conflicts.** Two instances writing to the same directory on a network filesystem is a race condition, even with append-only semantics.

**Horizontal scaling requires upgrading the state tracker** to a shared backend with atomic work claiming, even at small user counts:

| Instances | State backend | Work coordination |
|-----------|--------------|-------------------|
| 1 | `state.json` (local) | Not needed |
| 2-5 | SQLite on shared disk, or Redis | Atomic status transitions (claim-before-process) |
| 5+ | Postgres or Redis | Distributed locks or queue-based work distribution |

Stage output can remain on a shared filesystem (each instance writes uniquely-named files), but the state tracker is the coordination point and must support atomic claims: "set this item to `processing` only if it's currently `new`."

### Migration path

1. **State tracker:** `state.json` -> SQLite/Redis (horizontal) -> Postgres (SaaS). The state lifecycle (ADR-006) stays the same; only the storage backend changes.
2. **Inter-stage transport:** filesystem directories -> message queue (Redis Streams, SQS) at SaaS scale. Stage contract (input -> process -> output) stays the same.
3. **Data storage:** local filesystem -> object storage (S3, GCS) at SaaS scale.

The key insight: the stage interface is stable. Stages consume input and produce output. Only the transport, coordination, and storage layers change. Design stages to accept an input source and output sink, not hardcoded paths, and the migration is mechanical.

**Revisit this ADR when:** a second instance is deployed, or file lock contention appears in run logs.

## Consequences

- All stage functions accept directory paths as arguments, not data objects.
- The orchestrator's job is sequencing and error handling, not data transformation.
- New stages must follow the same contract: read from input dir, write to output dir.
- The data directory layout (ADR-003) is load-bearing -- directory names and file formats are part of the stage contract.
