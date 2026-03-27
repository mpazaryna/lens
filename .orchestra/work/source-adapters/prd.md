# Source Adapters

**Objective:** Extract the RSS-specific collection logic into a source adapter interface and prove the abstraction with a second adapter (Zotero), validating that Lens can ingest content from any structured data source.

## Success Criteria

- [ ] Source adapter protocol defines a common interface: discover items, fetch content, produce extracted text + metadata
- [ ] RSS adapter wraps existing collect/ modules behind the protocol
- [ ] Zotero adapter reads from a local Zotero SQLite database and/or Zotero API
- [ ] Zotero adapter handles paywall content by extracting text from cached PDFs/snapshots
- [ ] Both adapters produce output in the same format to `{data_dir}/extracted/` -- enrichment pipeline works identically regardless of source
- [ ] State tracker handles items from multiple sources without collision
- [ ] CLI supports `lens collect --source rss` and `lens collect --source zotero`

## Context

Lens is designed to be source-agnostic (ADR-008), but the current collection pipeline is hardcoded to RSS. Proving the abstraction with a second, fundamentally different source (Zotero) validates the architecture. Zotero is a strong test case because it differs from RSS in every dimension: no feed protocol (SQLite + API), paywall content (cached PDFs), rich metadata (authors, tags, DOIs), and a large existing corpus (~1000 articles).

If the adapter interface works for both RSS and Zotero, it will work for arXiv, news APIs, document stores, medical claims databases, and any other enterprise data source.

Part of the [Lens Roadmap](../../roadmap.md).

## Materials

| Material | Location | Status |
|----------|----------|--------|
| Source adapter protocol | src/lens/collect/ | Not Started |
| RSS adapter (refactor existing) | src/lens/collect/ | Not Started |
| Zotero adapter | src/lens/collect/ | Not Started |
| PDF text extraction | src/lens/collect/ | Not Started |
| Adapter tests | tests/collect/ | Not Started |

## References

- ADR-001: [Prefer Functions Over Classes](../../adr/ADR-001-prefer-functions-over-classes.md)
- ADR-008: [Collection vs. Enrichment Pipeline Separation](../../adr/ADR-008-collection-vs-enrichment.md)

## Notes

- Zotero stores data in a SQLite database (typically `~/Zotero/zotero.sqlite`) with attachments in a storage directory.
- Zotero also has a web API for synced libraries.
- PDF text extraction will need a library (e.g., pymupdf, pdfplumber) -- this is a new dependency.
- The adapter protocol should be minimal: discover items, fetch/extract content, return a common result type. Keep it functional (ADR-001).
- This milestone can run in parallel with Enrichment Pipeline and Scaling Spike -- they're independent concerns.
