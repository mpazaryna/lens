# ADR-008: Collection vs. Enrichment Pipeline Separation

**Date:** 2026-03-27
**Status:** Active
**Decision:** Lens operates as two distinct pipelines -- a collection pipeline and an enrichment pipeline -- with content extraction as the handoff boundary.

## Context

Enterprise monitoring systems (telecom, availability services, financial systems) have long distinguished between data collection and data enrichment. Collection is about reliable ingestion: get the data in, clean it up, don't lose anything. Enrichment is about intelligence: analyze, correlate, summarize, classify. They have fundamentally different reliability requirements, failure modes, scaling characteristics, and cost profiles.

Lens was initially designed as a single linear pipeline (fetch -> extract -> summarize -> rank). But summarization and ranking are LLM-powered enrichment stages with different properties than the collection stages that precede them. Treating them as a single pipeline conflates two distinct operational concerns.

## Decision

### Two pipelines

**Collection Pipeline** -- reliable data ingestion, no LLM dependency.

```
OPML -> parse feeds -> fetch HTML -> extract clean text
```

- **Stages:** feed parsing, retrieval, extraction
- **SLA:** must not lose items. If a fetch fails, retry. If extraction fails, flag and move on. Every discovered feed item must be tracked.
- **Scaling:** I/O-bound. Scales by network throughput and concurrent HTTP connections.
- **Failure modes:** network errors, DNS failures, HTTP timeouts, malformed HTML. All recoverable with retries.
- **Cost:** near-zero marginal cost per item (no LLM calls).
- **Scheduling:** runs on a cadence (poll feeds every N minutes).

**Enrichment Pipeline** -- LLM-powered processing, operates on collected content.

```
extracted text -> summarize -> rank -> classify -> (future: agentic analysis)
```

- **Stages:** summarization, ranking, content type classification, preference-based filtering, and future agentic processes.
- **SLA:** best-effort. A failed summarization can be retried later. A missing ranking doesn't lose data -- the extracted text is still there.
- **Scaling:** LLM-bound. Scales by model capacity, API rate limits, and cost budget. Horizontal scaling means running multiple enrichment workers, potentially with different models.
- **Failure modes:** rate limits, model errors, context length exceeded, provider outages, cost overruns. Require backoff, fallback models, and budget controls.
- **Cost:** significant marginal cost per item (LLM API calls or local GPU time).
- **Scheduling:** event-driven (new items collected) or batched (enrich all pending items).

### The handoff boundary

**Content extraction is the boundary.** The collection pipeline produces clean, structured text files in `{data_dir}/extracted/`. The enrichment pipeline reads from that directory. The state tracker (ADR-006) tracks each item's progress through both pipelines but the pipelines operate independently.

```
Collection: new -> fetched -> extracted (HANDOFF)
Enrichment: extracted -> summarized -> ranked -> enriched
```

An item with status `extracted` is complete from collection's perspective and ready for enrichment. Enrichment can run immediately, on a delay, or in batch -- collection doesn't care.

### Operational independence

1. **Collection can run without enrichment.** Useful for building up a corpus before spending on LLM calls, or when the LLM provider is down.
2. **Enrichment can run without collection.** Re-enrich previously collected items with a new model, updated prompts, or new enrichment stages.
3. **Different schedules.** Collection might poll feeds every 15 minutes. Enrichment might run hourly in batch, or trigger on-demand.
4. **Different scaling.** Collection scales horizontally by adding fetch workers. Enrichment scales by adding LLM workers with potentially different providers/models per stage (ADR-004).
5. **Different budgets.** Collection has a fixed infrastructure cost. Enrichment has a variable cost tied to LLM usage. Budget controls belong on the enrichment pipeline.

### CLI implications

```
lens collect          # Run collection pipeline only (feeds -> extract)
lens enrich           # Run enrichment pipeline only (summarize -> rank)
lens run              # Run both in sequence (current behavior)
lens run --collect    # Alias for lens collect
lens run --enrich     # Alias for lens enrich
```

### Future: agentic enrichment

As Lens adds agentic capabilities (autonomous analysis, cross-article correlation, trend detection), these are enrichment stages. They read from extracted or summarized content and produce enriched output. The enrichment pipeline is designed to accommodate long-running, stateful agents alongside fast stateless stages like summarization.

Agentic enrichment scales horizontally by running multiple agent workers. Each agent claims work from the state tracker, processes it, and updates state -- the same pattern as any other enrichment stage, but potentially longer-running and more resource-intensive.

## Rationale

- **Operational clarity.** "Collection is down" and "enrichment is slow" are different problems with different fixes. Separating them makes incident response obvious.
- **Cost control.** Collection is cheap. Enrichment is expensive. Separating them lets you budget, throttle, and monitor LLM spend independently.
- **Reliability.** Collection must never lose data. Enrichment is best-effort. Different SLAs need different error handling.
- **Proven pattern.** This is how enterprise monitoring systems (AT&T, SunGard) have handled collection and enrichment for decades. The pattern works at scale.
- **Agentic readiness.** When autonomous agents join the pipeline, they slot into the enrichment side without touching collection.

## Consequences

- Core Pipeline milestone is scoped to collection only (feeds, retrieval, extraction, state tracking, recovery).
- Enrichment Pipeline becomes a separate milestone with its own PRD.
- The state tracker (ADR-006) must support both pipelines -- items progress through collection states then enrichment states.
- The CLI exposes `collect` and `enrich` as separate commands.
- Ranking, Content Type Routing, and Preference Learning are all enrichment concerns and depend on the Enrichment Pipeline milestone.
- Per-stage provider config (ADR-004) applies to enrichment stages only -- collection has no LLM calls.
