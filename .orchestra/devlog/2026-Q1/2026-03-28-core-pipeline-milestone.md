# 2026-03-28: Core Pipeline Milestone Complete

## What Happened

Completed the full Core Pipeline (Collection) milestone in a single session. Started with a portfolio quality review and Python hardening pass, then executed all 7 spec steps with strict TDD.

### Morning: Python Quality Hardening

Before starting the milestone, reviewed the codebase for portfolio readiness and implemented 10 improvements:

- Custom exception hierarchy (`LensError` base + 6 subclasses)
- Replaced all `print()` with structured `logging`
- Narrowed `except Exception` catches to specific types
- Upgraded to `asyncio.TaskGroup` (Python 3.12+)
- Type aliases, named constants, `TYPE_CHECKING` blocks
- `py.typed` PEP 561 marker
- GitHub Actions lint CI (ruff check + format)
- Claude Code pre-commit lint hook (skips non-Python commits)
- Shared git pre-commit hook in `.githooks/` blocking direct commits to main

### Afternoon: Core Pipeline Spec + Execution

Wrote the execution spec with 7 steps, created Gherkin behavior specifications as the source of truth for test cases, then implemented each step with TDD.

| Step | Ticket | Time | Tests |
|------|--------|------|-------|
| 1 - Config resolution (ADR-003) | 86e0m6pd3 | 3m | 8 |
| 2 - Feed state tracker (ADR-006) | 86e0m6pd5 | 1m | 19 |
| 3 - Wire state tracker into orchestrator | 86e0m6v79 | ~3m | 7 |
| 4 - `lens collect` CLI command | 86e0m6uuj | 1m | 5 |
| 5 - Pipeline recovery and retry | 86e0m6wpb | ~1.5m | 4 |
| 6 - Run log output | 86e0m6xeg | ~1m | 10 |
| 7 - E2E integration test | 86e0m6xna | ~2.5m | 3 |

Total: ~13 minutes implementation, 56 new tests (136 total across the project).

### Workflow Established

Defined the PRD -> spec -> Gherkin -> ClickUp ticket -> branch -> TDD workflow:

- **Gherkin** is the behavior contract (business-readable, test source of truth)
- **Spec** is the implementation plan (references Gherkin for test cases)
- **ClickUp tickets** are minimal contracts to the agent (1-2 sentence summary + spec link)
- **Ticket IDs** annotated in the spec with `— ticket: {id}` format
- **Branch naming** follows `ticket/{id}-{name}` convention
- **ClickUp timer** tracks time per ticket via REST API

### Bugs Found and Fixed

- SSL certificate verification failure on macOS: aiohttp wasn't using certifi's CA bundle. Fixed in `rss.py` and `fetcher.py` by creating `ssl.create_default_context(cafile=certifi.where())`. Surfaced by the E2E integration test -- exactly the kind of thing integration tests are for.
- Python architecture mismatch: system Python 3.12 was x86_64, needed uv-managed arm64 Python. Fixed with `uv python install 3.12`.

## Key Decisions

- **Seen ledger is gone.** Replaced entirely by the ADR-006 state tracker with per-item status (new/fetched/extracted/summarized/failed), stage timing, retry counting, and atomic writes.
- **`run_collection()` is the collection entry point.** Separate from `run_pipeline()` which does collection + enrichment. Maps to `lens collect` CLI.
- **Run log is pure functions, not a class.** `create_run_log()`, `record_item()`, `finalize_run_log()`, `write_run_log()` -- follows ADR-001 functional-first approach.
- **ClickUp REST API over MCP proxy.** The MCP proxy had intermittent 502s. Switched to direct API calls with the key from `.env`.
- **Extracted content organization by feed is deferred.** Currently flat in `data/extracted/`. Will address in the enrichment spec when the write step is designed.

## What's Next

- Enrichment Pipeline milestone (depends on Core Pipeline -- now unblocked)
- Organize extracted content by feed source (deferred to enrichment spec)
- Add `lens collect` and `lens enrich` as separate docs in README
