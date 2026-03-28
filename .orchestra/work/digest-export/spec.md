# Digest and Export -- Execution Spec

**PRD:** [Digest and Export](prd.md)
**Status:** Complete

## Approach

Implement in 4 steps. The digest generator and export formatter are pure functions in a new `src/lens/output/` package -- no classes, just functions that read processed JSON and produce formatted output. CLI commands are thin wrappers.

Steps are ordered by dependency. All work follows strict TDD with pytest. For each step: write failing tests first, then implement until tests pass. Tests must cover happy path, edge cases, and error conditions. No step is complete until `uv run pytest` passes and coverage for touched modules stays above 80%.

## Steps

### Step 1: Digest generator — ticket: 86e0m8jx8

Read processed JSON from `{data_dir}/processed/{feed}/` and generate a per-feed markdown briefing. Articles sorted by word count descending (longer = more substantial). Only includes items at `summarized` status. Overwrites previous digest on each run.

- Create `src/lens/output/__init__.py` and `src/lens/output/digest.py`
- `generate_digest(feed_name, articles) -> str` renders markdown from a list of summary dicts
- `generate_all_digests(config) -> list[Path]` reads processed JSON per feed, generates digest, writes to `{data_dir}/digest/{feed}.md`
- Header includes feed name, article count, generation timestamp
- Articles sorted by word_count descending

#### Tests

Derive from [gherkin.md](gherkin.md) -- Step 1 scenarios. Write first in `tests/output/test_digest.py`:

- Digest contains feed name header and article count
- Articles are sorted by word count descending
- Each article section includes title, source URL, summary text, and metadata
- Empty feed produces a digest with zero article count
- Only summarized items are included (failed items excluded)
- Digest file overwrites previous version
- Digest directory is created if it doesn't exist
- Multiple feeds produce separate digest files

Acceptance: all tests pass; `uv run pytest tests/output/test_digest.py` green

### Step 2: `lens digest` CLI command — ticket: 86e0m8kac

Add a `lens digest` command that generates digests from existing processed data. No LLM, no network -- reads JSON, writes markdown.

- Add `digest` command to `src/lens/cli.py`
- Accepts `--data-dir` and `--verbose` flags
- Output: list of generated digest files and article counts per feed
- No API key required

#### Tests

Write first in `tests/test_cli.py`:

- `lens digest` invokes digest generation
- `--data-dir` flag is passed through
- No API key required
- Output lists generated digest files

Acceptance: all tests pass; `uv run pytest tests/test_cli.py` green

### Step 3: Export formatter — ticket: 86e0m8kpk

Export all summaries as structured output. Default format is JSON (one file per feed with article array). Obsidian format writes individual markdown notes with YAML frontmatter.

- Create `src/lens/output/export.py`
- `export_feed_json(feed_name, articles) -> str` renders JSON array
- `export_feed_obsidian(feed_name, articles, output_dir) -> list[Path]` writes individual notes
- `export_all(config, format) -> list[Path]` reads processed JSON, exports per feed
- JSON written to `{data_dir}/export/{feed}.json`
- Obsidian notes written to `{data_dir}/export/obsidian/{feed}/`

#### Tests

Derive from [gherkin.md](gherkin.md) -- Step 3 scenarios. Write first in `tests/output/test_export.py`:

- JSON export contains all articles for a feed as an array
- JSON includes feed name and generation timestamp
- Obsidian export produces individual markdown files with YAML frontmatter
- Obsidian frontmatter includes title, source, feed, date, word_count, tags
- Empty feed produces valid empty JSON array
- Export directory is created if it doesn't exist

Acceptance: all tests pass; `uv run pytest tests/output/test_export.py` green

### Step 4: `lens export` CLI command — ticket: 86e0m8m0n

Add a `lens export` command with `--format` flag supporting `json` (default) and `obsidian`.

- Add `export` command to `src/lens/cli.py`
- Accepts `--data-dir`, `--format`, and `--verbose` flags
- `--format json` (default) writes per-feed JSON files
- `--format obsidian` writes individual markdown notes with frontmatter
- No API key required

#### Tests

Write first in `tests/test_cli.py`:

- `lens export` invokes JSON export by default
- `lens export --format obsidian` invokes Obsidian export
- `--data-dir` flag is passed through
- No API key required

Acceptance: all tests pass; `uv run pytest tests/test_cli.py` green

## Deliverables

| Step | Deliverable | Tests | Acceptance Criteria |
|------|-------------|-------|---------------------|
| 1 | src/lens/output/digest.py | tests/output/test_digest.py | Per-feed markdown digest generation |
| 2 | src/lens/cli.py (digest cmd) | tests/test_cli.py | `lens digest` produces markdown files |
| 3 | src/lens/output/export.py | tests/output/test_export.py | JSON and Obsidian export formats |
| 4 | src/lens/cli.py (export cmd) | tests/test_cli.py | `lens export --format json\|obsidian` |

## Risks

| Risk | Mitigation |
|------|------------|
| Word count sorting is a weak proxy for relevance | Placeholder until Ranking milestone; digest format supports swapping sort key |
| Obsidian vault structure varies by user | Use flat notes with tags; user can reorganize in Obsidian |
| Large feeds produce very long digest files | Consider a `--limit` flag in a future iteration |

## Notes

- Steps 1 and 3 have no dependency on each other and can be parallelized.
- Step 2 depends on step 1.
- Step 4 depends on step 3.
- All steps are read-only consumers of existing processed data -- no collection or enrichment dependency at runtime.
- Once Ranking milestone ships, `generate_digest` should accept a sort key parameter to sort by score instead of word count.
