# ADR-004: Per-Stage Provider Configuration

**Date:** 2026-03-27
**Status:** Active
**Decision:** Each LLM stage can be independently configured with its own provider and model. A default provider/model applies when no stage-specific override is set.

## Context

Different pipeline stages have different requirements. Summarization processes high volume and benefits from a fast, cheap model. Ranking requires stronger reasoning and may justify a more capable (and expensive) model. A user might want Ollama locally for privacy on some stages but a frontier model for others.

The current implementation uses a single provider for the entire pipeline. This ADR introduces per-stage configuration.

## Decision

### Config structure

Each LLM stage has three config keys following the pattern:

```
LENS_{STAGE}_PROVIDER   (e.g., LENS_SUMMARIZE_PROVIDER)
LENS_{STAGE}_MODEL      (e.g., LENS_SUMMARIZE_MODEL)
LENS_{STAGE}_API_KEY    (e.g., LENS_SUMMARIZE_API_KEY)
```

### Resolution chain

Per-stage config falls back to the default:

```
LENS_SUMMARIZE_PROVIDER > LENS_PROVIDER > "anthropic"
LENS_SUMMARIZE_MODEL    > LENS_MODEL    > provider default
LENS_SUMMARIZE_API_KEY  > LENS_API_KEY  > env default
```

### Current LLM stages

| Stage | Env prefix | Typical use case |
|-------|-----------|-----------------|
| Summarization | `LENS_SUMMARIZE_` | High volume, fast model (e.g., Haiku, llama3.1) |
| Ranking | `LENS_RANK_` | Stronger reasoning (e.g., Sonnet, gpt-4o) |

### Implementation

- The provider registry (`create_provider`) remains unchanged -- it creates a provider from a provider name, model, and API key.
- The orchestrator creates one provider instance per LLM stage by reading stage-specific config, falling back to defaults.
- Config resolution happens in `config.py`, not in the orchestrator.

## Rationale

- **Cost optimization.** Summarizing 50 articles with Haiku is significantly cheaper than Sonnet. Ranking 50 pre-summarized items with Sonnet is affordable.
- **Speed.** Fast models for high-volume stages, capable models where quality matters.
- **Privacy flexibility.** Run summarization on local Ollama (data never leaves the machine) but use a frontier model for ranking where the input is already a summary, not raw content.
- **Simple default.** If you only set `LENS_PROVIDER` and `LENS_MODEL`, every stage uses the same provider. Zero additional config needed for the simple case.

## Consequences

- `config.py` grows a per-stage resolution function.
- The orchestrator instantiates multiple providers (one per LLM stage) instead of one.
- `.env.example` documents both default and per-stage variables.
- Future LLM stages (e.g., content classification) follow the same pattern: add a prefix, fall back to default.
