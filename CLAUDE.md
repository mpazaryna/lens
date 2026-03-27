# CLAUDE.md

## Project Overview

Lens-py is a content-aware feed aggregator built with Python that uses the Anthropic API to intelligently extract, summarize, rank, and recommend content from RSS feeds. It serves as a reference architecture for AI-powered document processing pipelines.

## Development Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov --cov-report=term-missing

# Run only unit tests (skip integration)
uv run pytest -m "not integration"

# Run specific test module
uv run pytest tests/extraction/

# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Run the full pipeline
uv run lens run --verbose

# Run only extraction (no LLM)
uv run lens extract
```

## Architecture

### Pipeline Phases

```
feeds -> fetch (async) -> extract (no LLM) -> summarize (async, Anthropic API) -> rank (async, tool use)
```

1. **Feeds** (`feeds/`): Parse OPML, fetch RSS/Atom feeds
2. **Retrieval** (`retrieval/`): Concurrent HTML download via aiohttp
3. **Extraction** (`extraction/`): HTML to clean text via BeautifulSoup (no LLM)
4. **Processing** (`processing/`): Summarization via Anthropic API
5. **Ranking** (`ranking/`): Structured scoring via Anthropic tool use
6. **Agents** (`agents/`): Pipeline orchestration agent

### Key Patterns

- **Staged pipeline with filesystem handoffs** between phases
- **asyncio concurrency** with semaphore-based throttling
- **Frozen dataclasses** for immutable data structures
- **Anthropic tool use** for structured LLM outputs
- **Seen ledger** for incremental processing (skip already-processed articles)

## Testing Strategy

- **Unit tests**: Fast, isolated, all mocked. Run on every commit.
- **Integration tests**: Hit real APIs, marked with `@pytest.mark.integration`.
- **Fixtures**: Shared via `conftest.py`, sample data in `tests/fixtures/`.
- **Coverage**: 80% minimum enforced via pytest-cov.

## Configuration

Environment variables via `.env` file. See `.env.example` for required variables.

## Code Style Guidelines

**No Emojis**: Do not use emojis in code, console output, or documentation.

## Project Tracking

- **ClickUp**: https://app.clickup.com/9017822495/v/li/901712328513
