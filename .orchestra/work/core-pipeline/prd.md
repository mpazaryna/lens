# Core Pipeline (Collection)

**Objective:** Reliable content ingestion pipeline that discovers, fetches, and extracts clean text from RSS feeds with full observability, state tracking, and recoverability. No LLM dependency. This is the collection half of Lens -- it must never lose data.

## Success Criteria

- [ ] Full collection pipeline runs via `lens collect` (feeds -> retrieval -> extraction)
- [ ] Each stage (feeds, retrieval, extraction) has unit tests with >80% coverage
- [ ] E2E integration test exercises all collection stages against real RSS feeds
- [ ] Retrieval stage has proper async fetch tests (currently only URL conversion is tested)
- [ ] Feed state tracker tracks per-item collection status (new, fetched, extracted, failed) across runs
- [ ] Pipeline resumes from where it left off -- only unprocessed items flow through remaining stages
- [ ] Configurable data directory (defaults to `~/.lens` in production, gitignored `data/` for development)
- [ ] OPML source path is configurable (defaults to `~/.lens/feeds.opml`)
- [ ] Structured logging across all collection stages with configurable verbosity (Python logging, not print statements)
- [ ] Each pipeline run produces a run log with per-item timing, stage transitions, errors
- [ ] Pipeline recovers from mid-run failures -- failed items are marked in the state tracker and can be retried without reprocessing successful items
- [ ] Extraction output written as structured files to `{data_dir}/extracted/` ready for enrichment pipeline handoff
- [ ] Full collection run completes 50 feed items within 2 minutes on a single machine (no LLM bottleneck)
- [ ] Async fetcher respects configurable concurrency limit (default 5 concurrent requests)

## Context

The collection pipeline is the foundation of Lens -- everything downstream (enrichment, ranking, preference learning) depends on reliable content ingestion. Collection must fetch RSS feeds, retrieve full article HTML, and extract clean text with full observability and recoverability. It behaves like a sophisticated RSS reader: tracking what has and hasn't been processed, resuming from failures, and running reliably on remote machines with configurable storage.

Collection has no LLM dependency. It is fast, cheap, and must never lose data. The handoff to the enrichment pipeline happens at extraction -- items with status `extracted` are ready for LLM processing (ADR-008).

Part of the [Lens Roadmap](../../roadmap.md).

## Materials

| Material | Location | Status |
|----------|----------|--------|
| Feed parsing (OPML + RSS) | src/lens/feeds/ | Done |
| Async HTML retrieval | src/lens/retrieval/fetcher.py | Done |
| Content extraction | src/lens/extraction/extractor.py | Done |
| Pipeline orchestrator | src/lens/pipeline/orchestrator.py | Done |
| Provider registry (Anthropic, OpenAI, Ollama) | src/lens/providers/ | Done |
| CLI entry points | src/lens/cli.py | Done |
| Configurable data directory (~/.lens) | src/lens/config.py | Not Started |
| Structured logging | src/lens/logging.py | Not Started |
| Feed state tracker (collection states) | src/lens/pipeline/ | Not Started |
| Pipeline recovery (retry failed items) | src/lens/pipeline/ | Not Started |
| Retrieval fetch tests | tests/retrieval/ | Not Started |
| E2E integration test (collection only) | tests/ | Not Started |

## References

- ADR-000: [The Score](../../adr/ADR-000-the-score.md)
- ADR-001: [Prefer Functions Over Classes](../../adr/ADR-001-prefer-functions-over-classes.md)
- ADR-002: [Inter-Stage Contract](../../adr/ADR-002-inter-stage-contract.md)
- ADR-003: [Data Directory Layout](../../adr/ADR-003-data-directory-layout.md)
- ADR-005: [Observability Stack](../../adr/ADR-005-observability-stack.md)
- ADR-006: [Feed State Tracker and Recovery Model](../../adr/ADR-006-feed-state-tracker.md)
- ADR-008: [Collection vs. Enrichment Pipeline Separation](../../adr/ADR-008-collection-vs-enrichment.md)

## ADRs Required

These ADRs are a prerequisite gate -- no Not Started items should be implemented until the foundational ADRs (002, 003) are decided, as they affect the shape of everything downstream.

**Write in this order:**

1. **ADR-002: Inter-stage contract** -- filesystem handoffs vs. in-memory. This is foundational: the orchestrator, state tracker, recovery model, and data directory layout all depend on this decision. Must be resolved first.
2. **ADR-003: Data directory layout** -- `~/.lens` structure, config resolution, OPML default path (`~/.lens/feeds.opml`). Depends on ADR-002 (if stages use filesystem, the directory layout is load-bearing).
3. **ADR-005: Observability stack** -- stdlib `logging`, JSON in production, human-readable in dev. Can proceed in parallel with ADR-006.
4. **ADR-006: Feed state tracker and recovery model** -- must support both collection and enrichment states (ADR-008). Can proceed in parallel with ADR-005.
