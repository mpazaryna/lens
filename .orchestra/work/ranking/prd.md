# Ranking

**Objective:** Consumer-specific content ranking system that scores and prioritizes summarized content based on configurable user interest profiles, using LLM tool use for structured scoring.

## Success Criteria

- [ ] To be defined

## Context

Ranking is inherently consumer-specific -- an AI developer cares about Anthropic releases, not IoT articles. This milestone separates ranking from the core pipeline (which ends at summarization) so that scoring logic can evolve independently around user interests.

The existing ranking implementation (src/lens/ranking/ranker.py) uses Anthropic tool use for structured output (score, confidence, reasoning, categories, read_time). This is a solid foundation but currently applies a generic scoring rubric with no awareness of who the consumer is or what they care about.

Part of the [Lens Roadmap](../../roadmap.md).

## Materials

| Material | Location | Status |
|----------|----------|--------|
| Tool-use ranking (existing) | src/lens/ranking/ranker.py | Done |
| Ranking tests (existing) | tests/ranking/ | Done |
| User interest profiles | | Not Started |
| Profile-aware scoring prompts | | Not Started |
| Ranked output (rankings.json) | | Not Started |

## References

- ADR-000: [The Score](../../adr/ADR-000-the-score.md)
- ADR-001: [Prefer Functions Over Classes](../../adr/ADR-001-prefer-functions-over-classes.md)

## Notes

This milestone PRD needs to be fleshed out. Run `/orchestra:prd` to expand it when ready.

Key questions to resolve:
- How are user interest profiles defined and stored? (YAML/JSON config, or learned over time?)
- Does ranking happen as a pipeline stage or as a separate post-processing step?
- How does this relate to the Preference Learning milestone (which covers learning over time)?
