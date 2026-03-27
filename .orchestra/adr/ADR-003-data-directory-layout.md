# ADR-003: Data Directory Layout

**Date:** 2026-03-27
**Status:** Active
**Decision:** All pipeline data lives under a single configurable root directory. Defaults to `~/.lens` in production and a gitignored `data/` in development.

## Context

The pipeline uses filesystem handoffs between stages (ADR-002). Each stage reads from and writes to directories. The data directory layout defines where those directories live, how config resolves paths, and where the OPML feed source is located. This layout must support running on remote machines and scaling horizontally.

## Decision

### Directory structure

```
{data_dir}/
├── feeds.opml              <- Feed subscriptions (OPML source)
├── feeds/                  <- Parsed feed metadata (JSON)
├── fetched/                <- Raw HTML downloads
├── extracted/              <- Cleaned text (markdown)
├── processed/              <- LLM summaries (JSON)
├── ranked/                 <- Scored and ranked output (JSON)
├── state.json              <- Feed state tracker (per-item processing status)
└── logs/                   <- Pipeline run logs
```

### Path resolution

1. **`LENS_DATA_DIR` environment variable** takes precedence if set.
2. **`--data-dir` CLI flag** overrides the environment variable.
3. **Default:** `~/.lens` (expands to the user's home directory).
4. **Development override:** when a `data/` directory exists in the project root and no explicit config is set, use it. This keeps development data gitignored and local.

### OPML source

- Default location: `{data_dir}/feeds.opml`
- Override: `LENS_OPML_PATH` environment variable or `--opml` CLI flag.
- The OPML file lives inside the data directory so that a remote deployment is self-contained.

### Config hierarchy

```
CLI flag > environment variable > default
```

## Rationale

- **Self-contained deployments.** A single directory contains everything needed to run the pipeline. Copy `~/.lens` to another machine and it works.
- **Development/production parity.** Same layout, different root. No code paths that only run in one environment.
- **Horizontal scaling.** Multiple workers can share a data directory on a network filesystem. Each worker processes different items, writes to the same directories.
- **Transparency.** `ls ~/.lens/processed/` shows you exactly what the pipeline has produced. No hidden databases.

## Consequences

- `config.py` must implement the resolution chain (CLI > env > default).
- All stage functions receive the data directory root and derive their paths from it.
- The `data/` directory in the project root must be in `.gitignore`.
- Stage output directories are created on demand if they don't exist.
