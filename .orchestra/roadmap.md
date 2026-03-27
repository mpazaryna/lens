# Lens Roadmap

**Objective:** Lens is an AI-powered content intelligence pipeline -- the "lens" through which raw data is deeply summarized, categorized, and ranked by a model before it reaches the consumer. Starting with RSS feeds, Lens uses both frontier and local LLM providers to intelligently filter and recommend content based on user interests, distinguishing between content types (video, articles, papers) with specialized processing paths and learning user preferences over time. The architecture is source-agnostic: any document feed (arXiv, news, medical claims) can flow through the same pipeline.

## Success Criteria

- [ ] Collection pipeline reliably ingests content from multiple source types (RSS, Zotero, and future adapters) through a source adapter abstraction
- [ ] Source adapter interface is proven with at least two adapters (RSS and Zotero)
- [ ] Enrichment pipeline summarizes, ranks, and classifies collected content using configurable LLM providers
- [ ] Video and article content are detected and routed through specialized processing paths
- [ ] User preferences are learned and applied to improve content recommendations over time
- [ ] Every milestone ships production-grade: tested, logged, recoverable, documented

## Context

Lens operates as two distinct pipelines (ADR-008):

- **Collection** -- reliable data ingestion through source adapters (RSS, Zotero, future: arXiv, news APIs, document stores). Fast, cheap, must never lose data. No LLM dependency. Each source type gets its own adapter; all converge at the same extraction boundary.
- **Enrichment** -- LLM-powered intelligence (summarize -> rank -> classify -> agentic analysis). Best-effort, cost-conscious, independently scalable. Source-agnostic -- enrichment doesn't know or care where the content came from.

Content extraction is the handoff boundary. Collection produces clean text; enrichment consumes it. The two pipelines can run independently, on different schedules, and scale differently.

The long-term vision is a generic AI-infused collection and ranking system for any enterprise that needs to review large volumes of data in any format -- research papers behind paywalls (Zotero), regulatory filings, medical claims, news feeds, internal knowledge bases.

The pipeline architecture uses filesystem handoffs between stages (ADR-002). This is correct for small-scale multi-tenant use but has a known scaling ceiling. Horizontal scaling requires upgrading the state tracker to a shared backend even at small user counts. A dev spike early in the roadmap validates the migration path (ADR-007).

## Milestones

| Material | Location | Dependency | Status |
|----------|----------|------------|--------|
| Core Pipeline (Collection) | .orchestra/work/core-pipeline/prd.md | -- | In Progress |
| Enrichment Pipeline | .orchestra/work/enrichment-pipeline/prd.md | Core Pipeline | Not Started |
| Scaling Spike | .orchestra/work/scaling-spike/prd.md | Core Pipeline | Not Started |
| Source Adapters | .orchestra/work/source-adapters/prd.md | Core Pipeline | Not Started |
| Ranking | .orchestra/work/ranking/prd.md | Enrichment Pipeline | Not Started |
| Content Type Routing | .orchestra/work/content-type-routing/prd.md | Enrichment Pipeline | Not Started |
| Preference Learning | .orchestra/work/preference-learning/prd.md | Ranking | Not Started |

## References

- ADR-000: [The Score](.orchestra/adr/ADR-000-the-score.md)
- ADR-008: [Collection vs. Enrichment Pipeline Separation](.orchestra/adr/ADR-008-collection-vs-enrichment.md)
- ADR-007: [Scaling to SaaS-Level Capacity](.orchestra/adr/ADR-007-scaling-to-saas.md)
