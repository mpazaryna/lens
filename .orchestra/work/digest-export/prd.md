# Digest and Export

**Objective:** Transform enriched pipeline output into consumable formats. `lens digest` produces a per-feed markdown briefing with summaries ready for human review. `lens export` outputs structured data for downstream workflows. The consumer shows up to a fully processed list, not a raw feed to browse.

## Success Criteria

- [ ] `lens digest` generates one markdown file per feed in `{data_dir}/digest/`
- [ ] Each digest file contains articles sorted by relevance (word count as proxy until ranking milestone ships)
- [ ] Digest includes: article title, source URL, summary text, and metadata (word count, processing time)
- [ ] Digest has a header with feed name, article count, and generation timestamp
- [ ] Running `lens digest` multiple times overwrites previous digest (not append)
- [ ] `lens digest` only includes items at `summarized` status (not failed or in-progress)
- [ ] `lens export` outputs all summaries as a single JSON array per feed, suitable for programmatic consumption
- [ ] `lens export --format obsidian` writes individual markdown notes with YAML frontmatter for Obsidian import
- [ ] Both commands respect `--data-dir` flag
- [ ] Both commands work against existing processed data without re-running collection or enrichment
- [ ] Unit tests with >80% coverage for digest generation and export formatting

## Context

The pipeline currently collects, extracts, and enriches content but the output is raw JSON files scattered across `processed/{feed}/` directories. To be useful as a daily intelligence tool, the output needs to be rendered into something a human can scan in 5 minutes over coffee.

The digest is the primary output -- a clean markdown file per feed that answers "what happened today in this feed?" The export is the machine-readable counterpart for feeding into other tools (Obsidian for knowledge management, newsletters, other pipelines like openclaw).

This milestone is sequenced before Ranking because even without scores, a summary digest sorted by word count (longer = more substantial) is immediately useful. Once Ranking ships, the digest sorts by score instead.

Part of the [Lens Roadmap](../../roadmap.md).

## Materials

| Material | Location | Status |
|----------|----------|--------|
| Digest generator | src/lens/output/digest.py | Not Started |
| Export formatter | src/lens/output/export.py | Not Started |
| CLI commands (digest, export) | src/lens/cli.py | Not Started |
| Digest tests | tests/output/test_digest.py | Not Started |
| Export tests | tests/output/test_export.py | Not Started |

## Digest Format

```markdown
# BBC News Digest

*Generated: 2026-03-28T16:30:00Z | 15 articles*

---

## Trump announces new trade policy framework

*Source: https://www.bbc.com/news/articles/abc123*
*1,265 words | Summarized in 2.1s*

The article discusses the new trade policy framework announced by...
[2-3 paragraph summary]

---

## Scientists discover high-temperature superconductor

*Source: https://www.bbc.com/news/articles/def456*
*892 words | Summarized in 1.8s*

Researchers at MIT have announced a breakthrough in...
[2-3 paragraph summary]

---
```

## Export Formats

### JSON (default)

```json
{
  "feed": "bbc-news",
  "generated_at": "2026-03-28T16:30:00Z",
  "articles": [
    {
      "title": "...",
      "source_url": "...",
      "summary_text": "...",
      "word_count": 1265,
      "provider": "llama3.2",
      "model": "llama3.2",
      "processing_time_ms": 2100
    }
  ]
}
```

### Obsidian (`--format obsidian`)

Each article becomes an individual markdown note with YAML frontmatter:

```markdown
---
title: "Trump announces new trade policy framework"
source: "https://www.bbc.com/news/articles/abc123"
feed: "bbc-news"
date: "2026-03-28"
word_count: 1265
tags: [lens, bbc-news]
---

The article discusses the new trade policy framework announced by...
```

## References

- ADR-002: [Inter-Stage Contract](../../adr/ADR-002-inter-stage-contract.md)
- ADR-008: [Collection vs. Enrichment Pipeline Separation](../../adr/ADR-008-collection-vs-enrichment.md)
