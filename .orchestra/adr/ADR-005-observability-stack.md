# ADR-005: Observability Stack

**Date:** 2026-03-27
**Status:** Active
**Decision:** Use Python's stdlib `logging` with structured output. JSON logs in production, human-readable in development. No external tracing dependencies.

## Context

The current codebase uses print statements for output. The pipeline needs proper observability: what happened, how long it took, what failed, and what the LLM did. Tools like LangSmith exist but require LangChain, which this project does not use and will not adopt.

## Decision

### Logging framework

Python's stdlib `logging` module with structured formatters. No third-party logging libraries.

### Output formats

- **Development:** human-readable, colorized console output. One line per event with timestamp, level, stage, and message.
- **Production:** JSON lines (one JSON object per log line). Machine-parseable, compatible with any log aggregator (CloudWatch, Datadog, ELK, etc.).
- **Selection:** `LENS_LOG_FORMAT=json|text` environment variable. Default: `text`.

### Log levels

| Level | Usage |
|-------|-------|
| DEBUG | Per-item stage transitions, file paths read/written |
| INFO | Stage start/complete, item counts, run summary |
| WARNING | Retryable errors, slow responses, skipped items |
| ERROR | Failed items, provider errors, unrecoverable stage failures |

### Verbosity

- Default: INFO
- `--verbose` CLI flag: DEBUG
- `LENS_LOG_LEVEL` environment variable for fine-grained control.

### LLM call metadata

Every LLM call logs the following at DEBUG level:

| Field | Description |
|-------|-------------|
| `stage` | Which pipeline stage (summarize, rank) |
| `provider` | Provider name (anthropic, openai, ollama) |
| `model` | Model identifier |
| `input_tokens` | Token count (if available from provider response) |
| `output_tokens` | Token count (if available from provider response) |
| `latency_ms` | Wall-clock time for the call |
| `item_id` | Which feed item this call was for |
| `success` | Boolean |
| `error` | Error message if failed |

### Run log

Each pipeline run writes a summary log to `{data_dir}/logs/{timestamp}-run.json` containing:

- Run start/end timestamps
- Total items per stage (attempted, succeeded, failed)
- Per-item timing breakdown
- Aggregate LLM usage (total tokens, total latency, cost estimate if available)
- Errors with tracebacks

## Rationale

- **No vendor lock-in.** stdlib logging works everywhere. JSON lines are the universal log format.
- **No new dependencies.** No structlog, loguru, or OpenTelemetry. The stdlib is sufficient for this scale.
- **Debuggability.** Combined with filesystem handoffs (ADR-002), you can correlate log entries with files on disk for any item.
- **Cost awareness.** Logging token counts and latency per LLM call makes cost visible without external tooling.

## Consequences

- All print statements must be replaced with logger calls.
- A logging module (`src/lens/logging.py`) configures formatters and handlers.
- The orchestrator passes a logger or uses module-level loggers following Python conventions.
- Run logs accumulate in `{data_dir}/logs/` and need periodic cleanup (out of scope for this ADR).
