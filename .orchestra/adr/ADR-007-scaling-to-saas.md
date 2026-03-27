# ADR-007: Scaling to SaaS-Level Capacity

**Date:** 2026-03-27
**Status:** Proposed
**Decision:** The pipeline architecture must support a clear migration path from small-scale multi-tenant to SaaS-level capacity without rewriting stage logic.

## Context

Lens currently uses filesystem handoffs (ADR-002) and a JSON state tracker (ADR-006). These decisions are correct for the current scale but have a known ceiling at ~100 concurrent users. If Lens becomes a SaaS product serving many tenants, the infrastructure layer must change while the pipeline logic stays the same.

This ADR defines the scaling strategy and the architectural constraints that make it achievable.

## Decision

### Design principle

**Stage logic is transport-agnostic.** Stages process content. How content arrives and where output goes is an infrastructure concern, not a stage concern. The stage interface must be clean enough that swapping filesystem for a queue or database is a plumbing change, not a rewrite.

### Scaling tiers

| Tier | Users | Transport | State | Storage | When |
|------|-------|-----------|-------|---------|------|
| 1: Small-scale | 1-10 | Filesystem dirs | JSON file | Local disk | Now |
| 2: Mid-scale | 10-100 | Filesystem dirs | SQLite | Local/network disk | When contention appears |
| 3: SaaS | 100+ | Message queue (Redis Streams, SQS) | Postgres | Object storage (S3, GCS) | When multi-region or high-concurrency is required |

### Multi-tenancy model

- **Tier 1-2:** Tenant isolation via separate data directories (`~/.lens/tenants/{tenant_id}/`). Simple, no shared state between tenants.
- **Tier 3:** Tenant isolation via database-level partitioning. Shared infrastructure, logical separation. Each tenant's items are tagged with a tenant ID in the state database.

### What must NOT change across tiers

1. Stage function signatures and logic
2. Provider configuration model (ADR-004)
3. Observability contract -- log format and metadata (ADR-005)
4. Feed state lifecycle (new -> fetched -> extracted -> summarized -> failed) (ADR-006)

### What changes across tiers

1. Transport layer (how stages receive input and emit output)
2. State storage backend (JSON -> SQLite -> Postgres)
3. Data storage backend (local dirs -> object storage)
4. Concurrency model (async semaphore -> distributed workers)
5. Tenant isolation mechanism (directories -> database partitioning)

### Validation

The Scaling Spike milestone validates that the stage interface supports this migration path before significant code is built on top of the current transport layer.

## Rationale

- **Build for today, design for tomorrow.** Filesystem handoffs are the right choice now. But making that choice without an exit plan creates technical debt that compounds with every new stage and feature.
- **The stage interface is the invariant.** Everything else -- transport, storage, state backend -- is a pluggable implementation detail. Protecting this boundary is the single most important architectural decision for long-term scalability.
- **Incremental migration.** Tiers are not big-bang rewrites. Moving from Tier 1 to Tier 2 means swapping `state.json` for SQLite. Moving from Tier 2 to Tier 3 means adding a queue and Postgres. Each step is bounded.

## Consequences

- Stage functions must not import or depend on filesystem-specific code directly. I/O happens at the edges through an abstraction that can be swapped.
- The Scaling Spike milestone is the first validation checkpoint.
- ADR-002, ADR-003, and ADR-006 are all scoped to Tier 1. They remain active but are understood to be tier-specific implementations of the interfaces defined here.
- Future ADRs for Tier 2 and Tier 3 migrations will reference this ADR as the guiding strategy.
