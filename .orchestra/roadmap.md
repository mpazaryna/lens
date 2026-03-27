# Lens Roadmap

**Objective:** Lens is a next-generation feed aggregator that uses local AI models to intelligently filter, rank, and recommend content from RSS feeds based on user interests. The system distinguishes between different content types (particularly video vs. article content) and uses specialized processing paths for each, learning user preferences for topics and content formats over time.

## Success Criteria

- [ ] End-to-end pipeline processes RSS feeds through fetch, extract, summarize, and rank stages using local AI models
- [ ] Video and article content are detected and routed through specialized processing paths
- [ ] User preferences are learned and applied to improve content recommendations over time
- [ ] System is production-ready with reliable CLI, documentation, and deployment story

## Context

Lens serves any process requiring comprehensive summarization and categorization. The current codebase has a working pipeline with multi-provider support (Anthropic, OpenAI, Ollama), staged filesystem handoffs, and async concurrency. The roadmap builds on this foundation toward full local-AI-powered content intelligence.

## Milestones

| Material | Location | Status |
|----------|----------|--------|
| Core Pipeline | .orchestra/work/core-pipeline/prd.md | Not Started |
| Content Type Routing | .orchestra/work/content-type-routing/prd.md | Not Started |
| Preference Learning | .orchestra/work/preference-learning/prd.md | Not Started |
| Production Ready | .orchestra/work/production-ready/prd.md | Not Started |

## References

- ADR-000: [The Score](.orchestra/adr/ADR-000-the-score.md)
