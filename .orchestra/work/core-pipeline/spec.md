# Core Pipeline (Collection) -- Execution Spec

**PRD:** [Core Pipeline](prd.md)
**Status:** Draft

## Approach

Implement the remaining Core Pipeline work in 7 steps, each independently shippable. The feed state tracker (ADR-006) is the central piece -- it replaces the binary seen ledger and enables resumption, retry, and per-item stage tracking. Config changes (ADR-003) come first because the state tracker and CLI commands depend on the resolved data directory. The E2E integration test comes last as validation.

Steps are ordered by dependency. Steps without dependencies between them can be parallelized.

All work follows strict TDD with pytest. For each step: write failing tests first, then implement until tests pass. Tests must cover happy path, edge cases, and error conditions. No step is complete until `uv run pytest` passes and coverage for touched modules stays above 80%.

## Steps

### Step 1: Configurable data directory and OPML path — ticket: 86e0m6pd3

Implement the ADR-003 path resolution chain: CLI flag > environment variable > default (`~/.lens`). Add development override (use `data/` if it exists in the project root and no explicit config is set). Make OPML source path configurable via `LENS_OPML_PATH` env var and `--opml` CLI flag, defaulting to `{data_dir}/feeds.opml`.

- Update `Config` model in `src/lens/config.py` with resolution logic
- Add `--data-dir` and `--opml` CLI flags to `src/lens/cli.py`

#### Tests

Derive from [gherkin.md](gherkin.md) -- Step 1 scenarios. Write first in `tests/test_config.py`.

Acceptance: all scenarios implemented as tests; `uv run pytest tests/ -k config` green

### Step 2: Feed state tracker — ticket: 86e0m6pd5

Replace the binary seen ledger (`seen.json`) with the state tracker defined in ADR-006. Implement as pure functions operating on a state dict with I/O at the edges. Item ID is a URL-safe hash of the item URL. Atomic writes via temp file + rename.

- Create `src/lens/pipeline/state.py` with state model and pure functions
- States: `new`, `fetched`, `extracted`, `summarized`, `failed`
- Per-item fields: url, title, feed, status, discovered_at, updated_at, stage_times, error, retry_count
- Migration function: convert old `seen.json` entries to `summarized` status
- Atomic write: temp file + `os.replace()`

#### Tests

Derive from [gherkin.md](gherkin.md) -- Step 2 scenarios. Write first in `tests/pipeline/test_state.py`.

Acceptance: all scenarios implemented as tests; `uv run pytest tests/pipeline/test_state.py` green

### Step 3: Wire state tracker into orchestrator — ticket: 86e0m6v79

Replace seen ledger usage in the orchestrator with the state tracker. Each stage queries the tracker for items at the right status, processes them, and updates status on completion or failure. Failed items are marked with error and retry_count.

- Update `src/lens/pipeline/orchestrator.py` to use state tracker instead of seen ledger
- Remove `load_seen`, `save_seen`, `filter_new_urls`, `mark_seen` functions
- After each stage, update item status (not batch -- per-item)
- Failed items get `failed` status with error message, other items continue

#### Tests

Write first in `tests/pipeline/test_pipeline.py`:

- Orchestrator creates `state.json` on first run with discovered items
- After fetch phase, successfully fetched items are at `fetched` status
- After extract phase, extracted items are at `extracted` status
- Failed fetch marks item as `failed` with error, other items continue
- Second run with same feeds skips already-extracted items
- Second run processes only `new` items from new feed entries
- Existing pipeline test assertions updated for new state model

Acceptance: all tests pass; `uv run pytest tests/pipeline/` green; old seen ledger tests removed or migrated

### Step 4: `lens collect` CLI command — ticket: 86e0m6uuj

Add a `lens collect` command that runs only the collection pipeline (feeds -> fetch -> extract) without any LLM enrichment. This is the primary entry point for collection, separate from `lens run` which does the full pipeline.

- Add `collect` command to `src/lens/cli.py`
- Accepts `--concurrency`, `--data-dir`, `--opml`, `--verbose`, `--retry-failed` flags
- `--retry-failed` resets `failed` items to their last successful status
- Output: summary of items discovered, fetched, extracted, failed

#### Tests

Write first in `tests/test_cli.py`:

- `lens collect` invokes collection pipeline without summarization or ranking
- `--data-dir` flag is passed through to config
- `--opml` flag overrides OPML source path
- `--retry-failed` flag triggers failed item reset
- Missing API key does not block `lens collect` (no LLM needed)
- Output includes counts for each stage

Acceptance: all tests pass; `uv run pytest tests/ -k cli` green

### Step 5: Pipeline recovery and retry — ticket: 86e0m6wpb

Implement stage-aware resumption and failed item retry. On a normal run, the orchestrator skips items that have already reached a given stage. With `--retry-failed`, failed items are reset and reprocessed.

- Add retry logic to orchestrator: reset failed items to last successful status
- Ensure `fetched` items skip directly to extraction on resume
- Add `--retry-failed` flag to both `lens collect` and `lens run`

#### Tests

Write first in `tests/pipeline/test_pipeline.py`:

- Items at `fetched` status skip fetch and go directly to extraction
- Items at `extracted` status are skipped entirely in collection
- `--retry-failed` resets `failed` items to their last successful status
- `--retry-failed` does not affect non-failed items
- A `failed` item with retry_count=2 gets retry_count=3 after next failure
- Simulated mid-pipeline failure: items before failure point are persisted at correct status
- Resume after failure only processes remaining items

Acceptance: all tests pass; `uv run pytest tests/pipeline/` green

### Step 6: Run log output — ticket: 86e0m6xeg

Each pipeline run writes a structured log file to `{data_dir}/logs/` with per-item timing, stage transitions, and error details. Filename includes ISO timestamp for chronological ordering.

- Create run log writer in `src/lens/pipeline/runlog.py`
- Log format: JSON with run metadata (start, end, elapsed, item_count) and per-item detail (url, stages completed, timing per stage, errors)
- Write to `{data_dir}/logs/{timestamp}-run.json`
- Integrate into orchestrator -- populate during run, write at end

#### Tests

Write first in `tests/pipeline/test_runlog.py`:

- `RunLog` captures start/end timestamps and elapsed time
- `record_item` adds per-item stage timing and status
- `record_error` adds error detail for a specific item
- `write_log` produces valid JSON with all recorded data
- `write_log` creates the `logs/` directory if it doesn't exist
- Log filename contains ISO timestamp
- Roundtrip: write then read back, verify all fields preserved
- Empty run (no items) still writes a valid log with zero counts

Acceptance: all tests pass; `uv run pytest tests/pipeline/test_runlog.py` green

### Step 7: E2E integration test

A single integration test that exercises the full collection pipeline against real RSS feeds. Marked with `@pytest.mark.integration` so it's excluded from normal test runs.

- Create `tests/integration/test_collection_e2e.py`
- Uses a known stable public RSS feed (e.g., Hacker News, BBC)
- Exercises: OPML parse -> feed fetch -> HTML fetch -> extraction

#### Tests

Write in `tests/integration/test_collection_e2e.py` (marked `@pytest.mark.integration`):

- Full collection pipeline produces `state.json` with items at `extracted` status
- Markdown files exist in `extracted/` directory with non-empty content
- At least N items successfully extracted (not exact count -- feeds change)
- State tracker `stage_times` are populated for each completed stage
- Second run is a no-op (all items already extracted)
- Run log file is written to `logs/` directory

Acceptance: `uv run pytest -m integration` passes with real network access

## Deliverables

| Step | Deliverable | Tests | Acceptance Criteria |
|------|-------------|-------|---------------------|
| 1 | src/lens/config.py | tests/test_config.py | All resolution chain tests pass |
| 2 | src/lens/pipeline/state.py | tests/pipeline/test_state.py | All state transition and I/O tests pass |
| 3 | src/lens/pipeline/orchestrator.py | tests/pipeline/test_pipeline.py | Orchestrator uses state tracker, old ledger removed |
| 4 | src/lens/cli.py | tests/test_cli.py | `lens collect` runs collection only |
| 5 | src/lens/pipeline/orchestrator.py | tests/pipeline/test_pipeline.py | Resume and retry tests pass |
| 6 | src/lens/pipeline/runlog.py | tests/pipeline/test_runlog.py | Run log written with per-item timing |
| 7 | tests/integration/test_collection_e2e.py | (is the test) | `pytest -m integration` passes |

## Risks

| Risk | Mitigation |
|------|------------|
| Atomic write doesn't prevent corruption on network filesystems | Documented as local-only for now; SQLite upgrade path exists (ADR-006) |
| State tracker JSON grows unbounded with thousands of items | Add optional pruning of old `summarized` items in a future milestone |
| Public RSS feeds in E2E test change or go offline | Use multiple feeds; test checks for "at least N items extracted" not exact counts |
| Removing seen ledger breaks existing data directories | Migration function converts old format; test covers migration path |

## Notes

- Steps 1 and 2 have no dependency on each other and can be worked in parallel.
- Step 3 depends on both 1 and 2.
- Steps 4 and 5 depend on step 3.
- Step 6 can be worked in parallel with steps 4-5 (only needs orchestrator access).
- Step 7 depends on all prior steps.
- The PRD materials table has stale paths (src/lens/feeds/, src/lens/retrieval/) -- these were reorganized to src/lens/collect/ and should be updated when this spec is finalized.
