# Scaling Spike

**Objective:** Validate that the pipeline's stage interface can be swapped from filesystem handoffs to queue-backed transport without rewriting stage code. De-risk the path from small-scale to SaaS.

## Success Criteria

- [ ] Implement a thin abstraction layer (e.g., StageInput/StageOutput protocol) over the current filesystem reads/writes
- [ ] Prove that at least one stage (e.g., extraction) runs identically against filesystem and an in-memory or queue-backed transport
- [ ] Measure overhead: abstraction layer adds <5% latency vs. direct filesystem calls
- [ ] Document findings in an ADR update to ADR-002 with a concrete migration checklist
- [ ] Spike is timeboxed -- no more than 2-3 days of effort

## Context

ADR-002 formalizes filesystem handoffs between pipeline stages. This works for small-scale multi-tenant use but has a known ceiling at ~100 concurrent users (file locking contention, no queryability, network filesystem fragility). Rather than discover this limit mid-build, this spike validates the escape hatch early.

The question is not "should we migrate now?" -- the answer is no. The question is: "can we migrate later without a rewrite?" If the stage interface is clean enough, the answer is yes and the team can build with confidence. If not, the interface needs adjustment before more stages are built on top of it.

Part of the [Lens Roadmap](../../roadmap.md).

## Materials

| Material | Location | Status |
|----------|----------|--------|
| Stage I/O abstraction prototype | src/lens/pipeline/ | Not Started |
| Alternative transport proof-of-concept | src/lens/pipeline/ | Not Started |
| ADR-002 update with findings | .orchestra/adr/ADR-002-inter-stage-contract.md | Not Started |

## References

- ADR-002: [Inter-Stage Contract](../../adr/ADR-002-inter-stage-contract.md)
- ADR-001: [Prefer Functions Over Classes](../../adr/ADR-001-prefer-functions-over-classes.md)

## Constraints

- Timeboxed: 2-3 days maximum. This is a spike, not a migration.
- No production code should depend on the alternative transport. The spike produces findings, not features.
- If the abstraction works cleanly, merge the abstraction layer only (not the alternative transport).
