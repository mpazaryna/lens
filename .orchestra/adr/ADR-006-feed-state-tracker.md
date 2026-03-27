# ADR-006: Feed State Tracker and Recovery Model

**Date:** 2026-03-27
**Status:** Active
**Decision:** A JSON-based state tracker replaces the binary seen ledger, tracking per-item processing status across pipeline stages with support for resumption and retry.

## Context

The current seen ledger (`seen.json`) is binary: an item has either been seen or not. This is insufficient for a production pipeline that needs to:

- Know which stage each item has reached
- Resume from mid-run failures without reprocessing successful items
- Retry failed items without rerunning the entire pipeline
- Report on pipeline health (how many items stuck in what state?)

This component carries significant complexity -- five states, cross-run persistence, retry semantics, and per-item timing -- which is why it gets its own ADR.

## Decision

### State model

Each feed item is tracked with the following status:

| Status | Meaning |
|--------|---------|
| `new` | Discovered in feed, not yet processed |
| `fetched` | HTML retrieved successfully |
| `extracted` | Clean text extracted from HTML |
| `summarized` | LLM summary generated |
| `failed` | Processing failed at some stage |

Status reflects the last successfully completed stage, not the current stage. A `fetched` item has been fetched and is ready for extraction.

### Data model

```json
{
  "items": {
    "{item_id}": {
      "url": "https://...",
      "title": "...",
      "feed": "feed-name",
      "status": "summarized",
      "discovered_at": "2026-03-27T10:00:00Z",
      "updated_at": "2026-03-27T10:05:00Z",
      "stage_times": {
        "fetched": 1.2,
        "extracted": 0.3,
        "summarized": 4.8
      },
      "error": null,
      "retry_count": 0
    }
  },
  "last_run": "2026-03-27T10:05:00Z"
}
```

### Item ID

The item ID is derived from the feed item's URL (URL-safe hash). This ensures deduplication across runs regardless of feed ordering.

### Storage

- **Location:** `{data_dir}/state.json` (per ADR-003).
- **Format:** JSON. Human-readable, debuggable, no database dependency.
- **Writes:** Atomic write via temp file + rename to prevent corruption on crash.
- **Locking:** File-level advisory lock for concurrent access (horizontal scaling).

### Pipeline behavior

1. **Discovery:** When feeds are parsed, new items get status `new`. Known items are skipped unless their status is `failed` and retry is requested.
2. **Stage progression:** After each stage completes for an item, the state tracker updates that item's status and records timing.
3. **Failure:** If a stage fails for an item, status becomes `failed`, the error is recorded, and `retry_count` is incremented. Other items continue processing.
4. **Resumption:** On the next run, the orchestrator reads the state tracker and only processes items that haven't reached the final stage. A `fetched` item skips directly to extraction.
5. **Retry:** `lens run --retry-failed` resets `failed` items to their last successful status and reprocesses them.

### Concurrency

- The state tracker is updated after each item completes a stage, not in batch.
- For horizontal scaling, file locking prevents concurrent writes from corrupting state.
- Future: if JSON + file locking becomes a bottleneck, migrate to SQLite. But JSON is sufficient for the expected scale (hundreds to low thousands of items).

## Rationale

- **Replaces the seen ledger.** The binary seen/not-seen model can't support recovery, retry, or stage-aware resumption.
- **JSON over SQLite.** Debuggable (`cat state.json`), no binary format, no migration tooling. Upgrade path to SQLite exists if needed.
- **Atomic writes.** Temp file + rename is the standard POSIX pattern for crash-safe file updates.
- **Per-item granularity.** If 49 of 50 items succeed, only the 1 failed item needs attention.

## Consequences

- The seen ledger (`seen.json`) is replaced by `state.json`. Migration: treat all items in the old ledger as `summarized` (they completed the full pipeline).
- The orchestrator must query the state tracker before each stage to filter items.
- The CLI gains a `--retry-failed` flag.
- State tracker functions are pure functions operating on the state dict (per ADR-001), with I/O at the edges.
