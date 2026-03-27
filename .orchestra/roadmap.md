# Lens Roadmap

**Objective:** Lens is an AI-powered content intelligence pipeline -- the "lens" through which raw data is deeply summarized, categorized, and ranked by a model before it reaches the consumer. Starting with RSS feeds, Lens uses both frontier and local LLM providers to intelligently filter and recommend content based on user interests, distinguishing between content types (video, articles, papers) with specialized processing paths and learning user preferences over time. The architecture is source-agnostic: any document feed (arXiv, news, medical claims) can flow through the same pipeline.

## Success Criteria

- [ ] End-to-end pipeline processes RSS feeds through fetch, extract, summarize, and rank stages using local AI models
- [ ] Video and article content are detected and routed through specialized processing paths
- [ ] User preferences are learned and applied to improve content recommendations over time
- [ ] Every milestone ships production-grade: tested, logged, recoverable, documented

## Context

The current codebase has a working pipeline with multi-provider support (Anthropic, OpenAI, Ollama), staged filesystem handoffs, and async concurrency. The roadmap builds on this foundation toward full content intelligence.

## Milestones

| Material | Location | Dependency | Status |
|----------|----------|------------|--------|
| Core Pipeline | .orchestra/work/core-pipeline/prd.md | -- | In Progress |
| Ranking | .orchestra/work/ranking/prd.md | Core Pipeline | Not Started |
| Content Type Routing | .orchestra/work/content-type-routing/prd.md | Core Pipeline | Not Started |
| Preference Learning | .orchestra/work/preference-learning/prd.md | Ranking | Not Started |

## References

- ADR-000: [The Score](.orchestra/adr/ADR-000-the-score.md)
