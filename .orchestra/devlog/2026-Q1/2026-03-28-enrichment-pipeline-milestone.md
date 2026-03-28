# 2026-03-28: Enrichment Pipeline Milestone Complete

## What Happened

Completed the Enrichment Pipeline milestone in a single session, immediately following the Core Pipeline milestone earlier today. Executed 7 spec steps with strict TDD, all running against local Ollama with llama3.2.

### Prerequisite: Feed-Organized Output (Step 0)

Refactored fetcher and extractor to write output into feed-named subdirectories. Articles from "BBC Top Stories" now land in `fetched/bbc-top-stories/` and `extracted/bbc-top-stories/`. Backward compat preserved for flat files from prior runs. Added `sanitize_feed_name()` utility for filesystem-safe directory names.

### Per-Stage Provider Config (Step 1, ADR-004)

Each LLM stage can now use a different provider/model via `LENS_SUMMARIZE_PROVIDER`, `LENS_SUMMARIZE_MODEL`, `LENS_SUMMARIZE_API_KEY`. Falls back to default `LENS_PROVIDER` when not set. Enables running Ollama locally for summarization and a frontier model for ranking without config gymnastics.

### `lens enrich` CLI (Step 2)

New CLI command runs enrichment only against previously collected content. Requires API key for cloud providers, not for Ollama -- this asymmetry is documented in the help text. Supports `--retry-failed`.

### Enrichment Orchestrator (Step 3)

Created `src/lens/pipeline/enrichment.py` with `run_enrichment()` -- separate module from orchestrator.py per spec review feedback. Processes items at `extracted` status through summarization with per-item state tracking. Failed items isolated, idempotent second runs verified.

### Structured JSON Output + Observability (Steps 4-5)

Summary output is structured JSON with full schema: title, source_url, feed_name, summary_text, word_count, provider, model, timestamp, processing_time_ms, input_tokens, output_tokens. Run log integrated into enrichment -- log file written to `logs/` after each run.

### E2E Integration Test (Step 6)

Full enrichment pipeline test against local Ollama with llama3.2. Pre-populates extracted content, runs enrichment, verifies JSON summaries, state tracker status, and run log output. Second run verified as no-op. All passing in ~6 seconds.

## Implementation Stats

| Step | Ticket | Time | Tests |
|------|--------|------|-------|
| 0 - Feed folders | 86e0m72qm | ~4m | 9 |
| 1 - Per-stage provider | 86e0m75gr | ~1.5m | 6 |
| 2 - `lens enrich` CLI | 86e0m77j4 | ~2m | 5 |
| 3 - Enrichment orchestrator | 86e0m791f | ~1.5m | 6 |
| 4 - Structured JSON output | 86e0m7b95 | ~2m | 1 |
| 5 - Enrichment logging | 86e0m7b98 | (w/4) | 1 |
| 6 - E2E integration test | 86e0m7b9a | ~1m | 3 |

Total: ~12 minutes, 31 new tests, 164 total across the project.

## Key Decisions

- **Enrichment in its own module.** `enrichment.py` keeps orchestrator.py focused on collection and top-level `run_pipeline`. This was a spec review catch -- the reviewer flagged orchestrator.py would get heavy.
- **Ollama-first development.** All enrichment dev and E2E tests use local Ollama with llama3.2. No cloud API calls, no API keys, no cost during development.
- **Feed name as provenance.** JSON output carries `feed_name` so downstream consumers know where content came from. This was a spec review catch -- the original schema was missing it.
- **Token counts in output.** Added `usage` field to `SummaryResult` to capture input/output tokens from the LLM response, threaded into JSON output for cost tracking.
- **Steps 4-5 combined.** The structured JSON output and run log integration were small enough to implement together without losing test clarity.

## Bugs Found

- SSL cert verification (fixed in Core Pipeline step 7) also affected enrichment -- the fix in `rss.py` and `fetcher.py` with certifi carries through.

## Workflow Observations

- The PRD -> spec -> Gherkin -> ticket -> TDD workflow is now battle-tested across two full milestones.
- ClickUp REST API is more reliable than the MCP proxy. Switched permanently.
- Time tracking per ticket gives real data on implementation speed. Average ~2 minutes per step with TDD.

## What's Next

- Scaling Spike milestone (validates transport abstraction for horizontal scaling)
- Source Adapters milestone (RSS + Zotero, proving source-agnostic architecture)
- Ranking milestone (consumer-specific scoring, depends on enrichment)
- Organize extracted content by feed is done; consider same for processed/ output
