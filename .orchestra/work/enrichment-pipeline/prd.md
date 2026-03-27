# Enrichment Pipeline

**Objective:** LLM-powered content processing pipeline that summarizes, classifies, and enriches collected content. Operates on extracted text produced by the collection pipeline, with independent scaling, scheduling, and cost controls.

## Success Criteria

- [ ] Enrichment pipeline runs via `lens enrich` against previously collected content
- [ ] `lens run` executes both collection and enrichment in sequence (current behavior preserved)
- [ ] Each LLM stage (summarization, etc.) can be configured with a different provider/model (ADR-004)
- [ ] Summarization stage has unit tests with >80% coverage
- [ ] E2E integration test exercises enrichment against pre-collected extracted text
- [ ] State tracker extends collection states: items progress from `extracted` -> `summarized` (and future enrichment states)
- [ ] Enrichment respects configurable concurrency limits per stage
- [ ] Enrichment can run independently of collection -- re-enrich with a new model or updated prompts without re-collecting
- [ ] Structured logging captures per-LLM-call metadata: tokens, latency, model, provider, cost estimate
- [ ] Pipeline recovers from mid-run failures -- failed enrichment does not affect collection state
- [ ] Summarization output written as JSON to `{data_dir}/processed/` with schema: title, source_url, summary_text, word_count, provider, model, timestamp
- [ ] Full enrichment run completes 50 items within 10 minutes on a single machine with Ollama

## Context

The enrichment pipeline is the intelligence layer of Lens -- where raw collected content passes through the "lens" of AI models. It reads extracted text from the collection pipeline's output directory and produces enriched output (summaries, classifications, scores).

Enrichment is fundamentally different from collection (ADR-008):

- **Cost:** significant marginal cost per item (LLM API calls or local GPU time)
- **SLA:** best-effort. A failed summarization can be retried later. The extracted text is safe in the collection pipeline's output.
- **Scaling:** LLM-bound. Scales by model capacity, rate limits, and cost budget. Horizontal scaling means running multiple enrichment workers.
- **Failure modes:** rate limits, model errors, context length exceeded, provider outages, cost overruns

The handoff from collection is the `extracted` status in the state tracker. Items at this status are ready for enrichment.

Part of the [Lens Roadmap](../../roadmap.md).

## Materials

| Material | Location | Status |
|----------|----------|--------|
| LLM summarization (existing) | src/lens/processing/summarizer.py | Done |
| Summarizer tests (existing) | tests/processing/ | Done |
| Provider registry (existing) | src/lens/providers/ | Done |
| Per-stage provider config | src/lens/config.py | Not Started |
| Enrichment orchestrator | src/lens/pipeline/ | Not Started |
| Enrichment CLI commands | src/lens/cli.py | Not Started |
| Enrichment state transitions | src/lens/pipeline/ | Not Started |
| E2E enrichment test | tests/ | Not Started |

## References

- ADR-001: [Prefer Functions Over Classes](../../adr/ADR-001-prefer-functions-over-classes.md)
- ADR-004: [Per-Stage Provider Configuration](../../adr/ADR-004-per-stage-provider-config.md)
- ADR-005: [Observability Stack](../../adr/ADR-005-observability-stack.md)
- ADR-006: [Feed State Tracker and Recovery Model](../../adr/ADR-006-feed-state-tracker.md)
- ADR-008: [Collection vs. Enrichment Pipeline Separation](../../adr/ADR-008-collection-vs-enrichment.md)

## Future Enrichment Stages

The enrichment pipeline is designed to grow. Future stages slot in alongside summarization:

- **Ranking** (separate milestone) -- consumer-specific scoring
- **Content type classification** (separate milestone) -- video vs. article routing
- **Agentic analysis** -- autonomous cross-article correlation, trend detection, deep research
- **Preference-based filtering** (separate milestone) -- learning what the user cares about

Each stage reads from extracted or previously enriched content and writes enriched output. The state tracker extends with new statuses as stages are added.
