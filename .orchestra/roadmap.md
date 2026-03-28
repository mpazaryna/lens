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

### Core Pipeline (Collection)

Builds a reliable content ingestion system that discovers, fetches, and extracts clean text from RSS feeds with full state tracking and recovery. This foundation ensures no data is lost and produces extracted text ready for downstream LLM processing.

- PRD: [.orchestra/work/core-pipeline/prd.md](.orchestra/work/core-pipeline/prd.md)
- Dependency: --
- Status: In Progress

### Enrichment Pipeline

Adds LLM-powered summarization, classification, and enrichment as a separate layer with its own scheduling, scaling, and cost controls. Reads extracted text from collection and produces enriched output (summaries, scores) on a best-effort basis.

- PRD: [.orchestra/work/enrichment-pipeline/prd.md](.orchestra/work/enrichment-pipeline/prd.md)
- Dependency: Core Pipeline
- Status: Not Started

### Scaling Spike

A time-boxed proof-of-concept validating that pipeline stage interfaces can swap from filesystem handoffs to queue-backed transport without rewriting stage code. De-risks the architectural path from small-scale to SaaS before more stages are built.

- PRD: [.orchestra/work/scaling-spike/prd.md](.orchestra/work/scaling-spike/prd.md)
- Dependency: Core Pipeline
- Status: Not Started

### Source Adapters

Extracts RSS-specific collection logic into a generic source adapter interface and proves it with a second adapter (Zotero). Both adapters produce the same extracted output format, ensuring enrichment works identically regardless of source.

- PRD: [.orchestra/work/source-adapters/prd.md](.orchestra/work/source-adapters/prd.md)
- Dependency: Core Pipeline
- Status: Not Started

### Ranking

Implements consumer-specific content ranking that scores and prioritizes summarized content based on user interest profiles. Leverages existing LLM tool-use infrastructure to produce structured scores tailored to individual users.

- PRD: [.orchestra/work/ranking/prd.md](.orchestra/work/ranking/prd.md)
- Dependency: Enrichment Pipeline
- Status: Not Started

### Content Type Routing

Detects whether content is a video or article and routes each type through specialized processing paths. Enables format-aware enrichment so videos get transcript-based summarization while articles get text-based analysis.

- PRD: [.orchestra/work/content-type-routing/prd.md](.orchestra/work/content-type-routing/prd.md)
- Dependency: Enrichment Pipeline
- Status: Not Started

### Preference Learning

Learns and adapts to user interests and content format preferences over time through implicit and explicit feedback signals. Closes the loop between ranking output and user behavior to continuously improve recommendations.

- PRD: [.orchestra/work/preference-learning/prd.md](.orchestra/work/preference-learning/prd.md)
- Dependency: Ranking
- Status: Not Started

## References

- ADR-000: [The Score](.orchestra/adr/ADR-000-the-score.md)
- ADR-008: [Collection vs. Enrichment Pipeline Separation](.orchestra/adr/ADR-008-collection-vs-enrichment.md)
- ADR-007: [Scaling to SaaS-Level Capacity](.orchestra/adr/ADR-007-scaling-to-saas.md)
