# Lens

An AI-powered content intelligence pipeline. Lens is the model you look through -- it deeply summarizes, categorizes, and ranks raw content before it reaches you, surfacing what matters and filtering what doesn't.

Starting with RSS feeds, Lens uses both frontier and local LLM providers to fetch, extract, and summarize content from any document source. The architecture is source-agnostic: the same pipeline that processes your RSS subscriptions can handle arXiv papers, news articles, medical claims, or regulatory filings.

## Why "Lens"?

Every feed, every paper, every article is raw data. A model that summarizes, ranks, and filters that data becomes the lens through which you see it -- sharpening signal, discarding noise, and adapting to what you care about over time.

## Features

- **Multi-stage pipeline**: fetch, extract, summarize, and rank content end-to-end
- **Multi-provider**: Anthropic, OpenAI, and Ollama (local models for privacy)
- **Source-agnostic**: RSS today, any document feed tomorrow
- **Async and concurrent**: aiohttp with semaphore-based throttling
- **Incremental processing**: tracks what's been processed, resumes from where it left off

## Quick Start

```bash
# Install dependencies
uv sync

# Configure your provider and feeds
cp .env.example .env

# Run the full pipeline
uv run lens run --verbose

# Run extraction only (no LLM)
uv run lens extract
```

## Development

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov --cov-report=term-missing

# Lint and format
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```
