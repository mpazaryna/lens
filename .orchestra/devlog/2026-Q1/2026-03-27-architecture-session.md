# 2026-03-27: Architecture Session

## What Happened

Major architecture session that shaped the project foundation. Started with scaffolding .orchestra/ and ended with a fully restructured codebase and 8 ADRs.

### PRDs and Milestones
- Fleshed out Core Pipeline PRD with 14 success criteria and prerequisite ADR gate
- Extracted Ranking from Core Pipeline into its own milestone (consumer-specific, not generic)
- Removed Production Ready milestone -- production quality is a bar, not a phase
- Created Enrichment Pipeline milestone (LLM-powered, separate from collection)
- Created Scaling Spike milestone (validate transport abstraction for horizontal scaling)
- Created Source Adapters milestone (RSS + Zotero, proving source-agnostic architecture)
- Added dependency column to roadmap for parallel agent work

### ADRs Written
- ADR-001: Prefer functions over classes
- ADR-002: Inter-stage contract (filesystem handoffs, vertical vs. horizontal scaling analysis)
- ADR-003: Data directory layout (~/.lens, config resolution chain)
- ADR-004: Per-stage provider configuration (different model per LLM stage)
- ADR-005: Observability stack (stdlib logging, no LangSmith/LangChain)
- ADR-006: Feed state tracker and recovery model (replaces binary seen ledger)
- ADR-007: Scaling to SaaS-level capacity (three-tier migration path)
- ADR-008: Collection vs. enrichment pipeline separation

### Code Changes
- Reorganized src/ into collect/ (feeds, fetcher, extractor) and enrich/ (summarizer, ranker)
- Mirrored test directory structure
- Updated all imports across orchestrator, CLI, and 85 tests -- all passing

## Key Decisions

- **Collection vs. enrichment is the foundational split.** Collection is reliable, cheap, no LLM. Enrichment is best-effort, costly, independently scalable. Extraction is the handoff boundary. Pattern comes from enterprise monitoring (AT&T, SunGard).
- **Ranking is consumer-specific.** Moved out of core pipeline because what's relevant depends on who's reading. An AI developer and a policy analyst score the same article differently.
- **Per-stage provider config.** Haiku for cheap summarization, Sonnet for nuanced ranking, Ollama for privacy. Default provider with per-stage overrides.
- **Horizontal scaling requires shared state.** Even at 1-10 users, multiple instances break file locking. State tracker must upgrade to SQLite/Redis before a second instance is deployed.
- **Source-agnostic architecture.** RSS is the first adapter. Zotero (~1000 articles, paywall content, local SQLite) is the second. If both work, any enterprise data source can.

## What's Next

- Write the 4 prerequisite ADRs (002-006 are written but need review/approval)
- Implement Core Pipeline collection-only: configurable data dir, structured logging, feed state tracker, pipeline recovery
- Enrichment Pipeline: split orchestrator into collection + enrichment entry points, add `lens collect` and `lens enrich` CLI commands
