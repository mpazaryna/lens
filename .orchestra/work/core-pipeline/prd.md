# Core Pipeline

**Objective:** End-to-end RSS feed processing pipeline that fetches, extracts, and summarizes content using both frontier and local LLM providers (Ollama) for privacy, with all stages connected, tested, and runnable from the CLI.

## Success Criteria

- [ ] Full pipeline runs end-to-end via `lens run` with any configured provider
- [ ] Each stage (feeds, retrieval, extraction, summarization) has unit tests with >80% coverage
- [ ] E2E integration test exercises all stages (feeds through summarization) against real RSS feeds
- [ ] Retrieval stage has proper async fetch tests (currently only URL conversion is tested)
- [ ] Feed state tracker tracks per-item processing status (new, queued, processing, done, failed) across runs
- [ ] Pipeline resumes from where it left off -- only unprocessed items flow through LLM stages
- [ ] Configurable data directory (defaults to `~/.lens` in production, gitignored `data/` for development)
- [ ] OPML source path is configurable (defaults to `~/.lens/feeds.opml`)
- [ ] Structured logging across all pipeline stages with configurable verbosity (Python logging, not print statements)
- [ ] Each pipeline run produces a run log with per-item timing, stage transitions, errors, and LLM call metadata
- [ ] Pipeline recovers from mid-run failures -- failed items are marked in the state tracker and can be retried without reprocessing successful items
- [ ] Summarization output written as JSON to `{data_dir}/processed/` with schema: title, source_url, summary_text, word_count, provider, model, timestamp
- [ ] Full pipeline run completes 50 feed items within 10 minutes on a single machine with Ollama
- [ ] Async fetcher respects configurable concurrency limit (default 5 concurrent requests)

## Context

The core pipeline is the foundation of Lens -- everything downstream (ranking, preference learning, content routing) depends on reliable content ingestion and summarization. The pipeline must fetch RSS feeds, retrieve full article HTML, extract clean text, and produce LLM-generated summaries with full observability and recoverability. It needs to behave like a sophisticated RSS reader: tracking what has and hasn't been processed, resuming from failures, and running reliably on remote machines with configurable storage.

Part of the [Lens Roadmap](../../roadmap.md).

## Materials

| Material | Location | Status |
|----------|----------|--------|
| Feed parsing (OPML + RSS) | src/lens/feeds/ | Done |
| Async HTML retrieval | src/lens/retrieval/fetcher.py | Done |
| Content extraction | src/lens/extraction/extractor.py | Done |
| LLM summarization | src/lens/processing/summarizer.py | Done |
| Pipeline orchestrator | src/lens/pipeline/orchestrator.py | Done |
| Provider registry (Anthropic, OpenAI, Ollama) | src/lens/providers/ | Done |
| CLI entry points | src/lens/cli.py | Done |
| Configurable data directory (~/.lens) | src/lens/config.py | Not Started |
| Structured logging | src/lens/logging.py | Not Started |
| Feed state tracker | src/lens/pipeline/ | Not Started |
| Pipeline recovery (retry failed items) | src/lens/pipeline/ | Not Started |
| Retrieval fetch tests | tests/retrieval/ | Not Started |
| E2E integration test | tests/ | Not Started |

## References

- ADR-000: [The Score](../../adr/ADR-000-the-score.md)
- ADR-001: [Prefer Functions Over Classes](../../adr/ADR-001-prefer-functions-over-classes.md)

## ADRs Required

These ADRs are a prerequisite gate -- no Not Started items should be implemented until the foundational ADRs (002, 003) are decided, as they affect the shape of everything downstream.

**Write in this order:**

1. **ADR-002: Inter-stage contract** -- filesystem handoffs vs. in-memory. This is foundational: the orchestrator, state tracker, recovery model, and data directory layout all depend on this decision. Must be resolved first.
2. **ADR-003: Data directory layout** -- `~/.lens` structure, config resolution, OPML default path (`~/.lens/feeds.opml`). Depends on ADR-002 (if stages use filesystem, the directory layout is load-bearing).
3. **ADR-004: Observability stack** -- stdlib `logging`, JSON in production, human-readable in dev. What metadata per LLM call (tokens, latency, model, prompt hash)? Can proceed in parallel with ADR-005.
4. **ADR-005: Feed state tracker and recovery model** -- this component carries the most complexity (five states, cross-run persistence, retry semantics, per-item timing). Needs its own ADR to nail down the data model and failure semantics before implementation.
