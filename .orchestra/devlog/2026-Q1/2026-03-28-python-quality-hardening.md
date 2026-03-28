# 2026-03-28: Python Quality Hardening

## What Happened

Portfolio-quality review of the entire Python codebase, followed by implementation of 10 improvements across source, tests, CI, and developer tooling.

### Custom Exception Hierarchy
- Created `src/lens/errors.py` with `LensError` base class and 6 domain-specific subclasses: `FeedParseError`, `FeedFetchError`, `ArticleFetchError`, `ExtractionError`, `LLMProviderError`, `ConfigError`.
- Replaced all `ValueError` and bare `Exception` raises with the appropriate custom type.
- Updated all test assertions to match (`FeedParseError`, `ConfigError`).

### Structured Logging
- Replaced every `print()` in the pipeline with `logging.getLogger(__name__)` per module.
- Orchestrator, fetcher, RSS, extractor, summarizer, and ranker all emit structured log messages now.
- CLI configures the root logger from `LENS_LOG_LEVEL` config (or `--verbose` flag for DEBUG).
- `click.echo` retained only for user-facing CLI output (banner, summary table).

### Narrowed Exception Catches
- `fetcher.py`: catches `aiohttp.ClientError` and `OSError` instead of `Exception`.
- `rss.py`: catches `FeedFetchError` and `FeedParseError` in batch fetch.
- `extractor.py`: catches `OSError` and `ExtractionError` in batch extraction.
- Summarizer and ranker still catch broad `Exception` at the boundary (LLM providers can throw anything), but log warnings with context.

### asyncio.TaskGroup (Python 3.12+)
- Replaced `asyncio.gather()` + mutable results list pattern in `fetcher.py` and `rss.py` with `async with asyncio.TaskGroup() as tg`.
- Fetcher collects results from task objects after the group completes. RSS appends to a shared list inside the task (fire-and-forget pattern with error collection).

### Type System Improvements
- Added `type ExtractionResultItem = tuple[Path, ExtractionResult | Exception]` using Python 3.12 `type` statement. Used in extractor, orchestrator, and `__init__.py`.
- Moved imports used only for annotations into `TYPE_CHECKING` blocks across 6 modules (fetcher, opml, ranker, summarizer, registry, orchestrator). Satisfies ruff's TCH rules.
- Added `src/lens/py.typed` marker for PEP 561 compliance.

### Named Constants
- `MAX_ARTICLE_CHARS = 15_000` in summarizer (was hardcoded `15000` in format string).
- `FETCH_TIMEOUT_SECONDS = 15.0` in fetcher (was hardcoded default).

### Test Coverage Expansion
- **Fetcher async tests** (8 new): fetch-and-save, 404 handling, connection errors, skip existing, overwrite, concurrent fetches, directory creation, frozen dataclass. All use `aioresponses` for HTTP mocking.
- **Orchestrator phase tests** (4 new): `extract_content` with real HTML files, empty directory handling, `fetch_feed_items` with no OPML, `fetch_feed_items` with mocked feeds.
- Test count: 65 -> 92 (42% increase).

### CI Pipeline
- Added `.github/workflows/lint.yml`: runs on push/PR to main.
- Steps: checkout, install uv, set up Python 3.12, `uv sync`, `ruff format --check`, `ruff check`.
- Lint only -- no test execution in CI (intentional, keeps it fast and free-tier friendly).

### Claude Code Pre-Commit Hook
- Added `.claude/settings.json` with a `PreToolUse` hook on `Bash` filtered to `git commit:*`.
- Runs `uv run ruff format --check src/ tests/ && uv run ruff check src/ tests/` before commits.
- Same checks as CI -- catches lint violations before they reach the remote.

## Key Decisions

- **Logging over print.** ADR-005 already specified stdlib logging. This session implemented it. `click.echo` is still used for CLI banners/summaries (user-facing output vs. operational logging).
- **Custom exceptions are domain boundaries.** `FeedParseError` vs. `FeedFetchError` matters because the orchestrator handles them differently (retry logic for network errors, skip for parse errors).
- **TaskGroup over gather.** Since we target Python 3.12+, TaskGroup is the idiomatic choice. It also handles cancellation properly if one task raises.
- **TYPE_CHECKING blocks.** Keeps runtime import graph lean. Important for a project that imports `aiohttp`, `anthropic`, `openai` -- lazy loading matters for CLI startup time.
- **CI is lint-only.** Tests require API keys and network access. Lint is deterministic and catches the most common issues. Test CI can come later with mocked integration tests.

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Source files | 18 | 19 (+errors.py) |
| Test files | 13 | 13 (expanded) |
| Test count | ~65 | 92 |
| `print()` calls | 12 | 0 |
| Custom exceptions | 0 | 7 |
| Broad `except Exception` | 6 | 2 (at LLM boundary only) |
| CI workflows | 0 | 1 |
| `py.typed` | No | Yes |

## What's Next

- Implement ADR-005 observability: add timing metrics to each pipeline phase, log elapsed per-article in batch operations.
- Add `lens collect` and `lens enrich` as separate CLI commands (from architecture session).
- Consider adding pytest to CI once we have a way to run without API keys (all unit tests already skip integration).
