# Enrichment Pipeline -- Execution Spec

**PRD:** [Enrichment Pipeline](prd.md)
**Status:** Draft

## Approach

Implement the enrichment pipeline in 7 steps, starting with a prerequisite refactor to organize content by feed. The enrichment pipeline reads extracted text from the collection pipeline and produces enriched output (summaries, structured JSON) via LLM. It operates independently of collection -- you can re-enrich with a new model without re-collecting.

Steps are ordered by dependency. All work follows strict TDD with pytest. For each step: write failing tests first, then implement until tests pass. Tests must cover happy path, edge cases, and error conditions. No step is complete until `uv run pytest` passes and coverage for touched modules stays above 80%.

## Steps

### Step 0: Organize fetched and extracted content by feed — ticket: 86e0m72qm

Refactor the fetcher and extractor to write output into feed-named subdirectories instead of a flat directory. The state tracker already records the feed name per item. This makes output browsable by source and sets up clean input boundaries for enrichment.

- Update `fetch_html` in orchestrator to pass feed name, create `fetched/{feed_name}/` subdirectories
- Update `extract_content` to mirror the feed structure in `extracted/{feed_name}/`
- Update state tracker item discovery to normalize feed names into safe directory names
- Preserve backward compat: if flat files exist, still process them

#### Tests

Derive from Gherkin (to be written). Write first in `tests/collect/test_fetcher.py` and `tests/pipeline/test_pipeline.py`:

- Fetched HTML is written to `fetched/{feed_name}/{filename}.html`
- Extracted markdown is written to `extracted/{feed_name}/{filename}.md`
- Feed name is sanitized for filesystem safety (no special chars)
- Multiple feeds produce separate subdirectories
- Flat files from prior runs are still found and processed

Acceptance: all tests pass; `uv run lens collect` produces feed-organized output

### Step 1: Per-stage provider configuration (ADR-004)

Implement the per-stage provider config resolution chain. Each LLM stage can use a different provider/model. Falls back to default when no stage-specific config is set.

- Add per-stage resolution to `src/lens/config.py`: `LENS_SUMMARIZE_PROVIDER`, `LENS_SUMMARIZE_MODEL`, `LENS_SUMMARIZE_API_KEY` with fallback to `LENS_PROVIDER`, `LENS_MODEL`, `LENS_API_KEY`
- Add `create_stage_provider` function that resolves config per stage
- Update `.env.example` with per-stage variables

#### Tests

Write first in `tests/test_config.py`:

- Default config returns same provider for all stages
- `LENS_SUMMARIZE_PROVIDER` overrides default provider for summarization
- `LENS_SUMMARIZE_MODEL` overrides default model for summarization
- `LENS_RANK_PROVIDER` overrides independently from summarize
- Partial override: set model but not provider, inherits default provider
- API key falls back: stage-specific > default > env

Acceptance: all tests pass; `uv run pytest tests/test_config.py` green

### Step 2: `lens enrich` CLI command

Add a `lens enrich` command that runs only the enrichment pipeline against previously collected content. Reads items at `extracted` status from the state tracker and processes them through summarization.

- Add `enrich` command to `src/lens/cli.py`
- Accepts `--concurrency`, `--data-dir`, `--verbose`, `--retry-failed` flags
- Requires API key (unlike `lens collect`)
- Output: summary of items enriched, errors, elapsed time

#### Tests

Write first in `tests/test_cli.py`:

- `lens enrich` invokes enrichment pipeline, not collection
- `lens enrich` requires API key (errors without one)
- `--retry-failed` resets failed enrichment items
- Output includes enrichment counts

Acceptance: all tests pass; `uv run pytest tests/test_cli.py` green

### Step 3: Enrichment orchestrator with state tracker

Create `run_enrichment()` function that processes items at `extracted` status through summarization, updating the state tracker to `summarized` on success or `failed` on error. Mirrors `run_collection()` pattern.

- Add `run_enrichment()` to `src/lens/pipeline/orchestrator.py`
- Query state tracker for items at `extracted` status
- Pass each item through summarization with per-stage provider
- Update state to `summarized` with stage timing on success
- Update state to `failed` with error on failure, other items continue
- Update `run_pipeline()` to call `run_enrichment()` after `run_collection()`
- Write summary output as JSON to `{data_dir}/processed/`

#### Tests

Write first in `tests/pipeline/test_pipeline.py`:

- `run_enrichment` processes items at `extracted` status
- Items transition to `summarized` on success with stage timing
- Failed summarization marks item as `failed`, other items continue
- Items not at `extracted` are skipped
- `--retry-failed` resets failed enrichment items to `extracted`
- Summary JSON written to `processed/` with expected schema

Acceptance: all tests pass; `uv run pytest tests/pipeline/` green

### Step 4: Structured summarization output

Update summarization output from markdown to structured JSON with schema: title, source_url, summary_text, word_count, provider, model, timestamp, processing_time_ms.

- Update `summarize_content()` to write JSON instead of markdown
- JSON schema matches PRD requirement
- Per-LLM-call metadata: tokens, latency, model, provider

#### Tests

Write first in `tests/enrich/test_summarizer.py`:

- Summary output is valid JSON with all required fields
- Token counts from provider response are captured
- Processing time is recorded
- Provider and model name are included

Acceptance: all tests pass; `uv run pytest tests/enrich/` green

### Step 5: Enrichment logging and observability

Add per-LLM-call metadata to structured logging: tokens in/out, latency, model, provider, cost estimate. Integrate run log output into enrichment runs.

- Add token/latency logging to summarizer calls
- Integrate `runlog` functions into `run_enrichment()`
- Log cost estimates based on provider pricing (configurable rates)

#### Tests

Write first in `tests/enrich/test_summarizer.py` and `tests/pipeline/test_pipeline.py`:

- Summarizer logs include token counts and latency
- Run log captures per-item enrichment timing
- Run log written after enrichment completes

Acceptance: all tests pass; enrichment run produces a log file in `logs/`

### Step 6: E2E enrichment integration test

Integration test that exercises enrichment against pre-collected extracted text. Uses a mock or local LLM provider (Ollama if available, mock otherwise).

- Create `tests/integration/test_enrichment_e2e.py`
- Pre-populate `extracted/` with known markdown files
- Run enrichment, verify `processed/` has JSON output and state tracker shows `summarized`
- Marked `@pytest.mark.integration`

#### Tests

Write in `tests/integration/test_enrichment_e2e.py`:

- Enrichment produces JSON summaries for pre-collected articles
- State tracker shows items at `summarized` status
- Second run is a no-op (items already summarized)
- Run log file written to `logs/`

Acceptance: `uv run pytest -m integration` passes

## Deliverables

| Step | Deliverable | Tests | Acceptance Criteria |
|------|-------------|-------|---------------------|
| 0 | Fetcher/extractor feed folders | tests/collect/, tests/pipeline/ | Feed-organized output directories |
| 1 | Per-stage provider config | tests/test_config.py | Stage-specific provider resolution |
| 2 | `lens enrich` CLI | tests/test_cli.py | Enrichment-only command |
| 3 | Enrichment orchestrator | tests/pipeline/test_pipeline.py | State-aware enrichment with failure isolation |
| 4 | Structured JSON output | tests/enrich/test_summarizer.py | JSON schema with metadata |
| 5 | Enrichment logging | tests/enrich/, tests/pipeline/ | Per-call metadata in logs |
| 6 | E2E integration test | tests/integration/ | Full enrichment against pre-collected content |

## Risks

| Risk | Mitigation |
|------|------------|
| LLM rate limits during batch enrichment | Semaphore-based concurrency already in place; add exponential backoff |
| Ollama not available for E2E test | Fall back to mock provider in integration test |
| Per-stage config complexity | Simple fallback chain; zero config needed for single-provider use |
| Feed folder refactor breaks existing data directories | Backward compat: flat files still processed |

## Notes

- Step 0 is a prerequisite refactor from the Core Pipeline -- it touches collection code but is needed before enrichment can organize output cleanly.
- Steps 0 and 1 have no dependency on each other and can be parallelized.
- Step 2 depends on step 1 (needs per-stage provider config for the CLI).
- Step 3 depends on steps 1 and 2.
- Steps 4 and 5 depend on step 3.
- Step 6 depends on all prior steps.
- The PRD materials table has stale paths (src/lens/processing/) -- these were reorganized to src/lens/enrich/.
