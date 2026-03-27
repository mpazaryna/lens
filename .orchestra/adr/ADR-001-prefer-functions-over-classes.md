# ADR-001: Prefer Functions Over Classes

**Date:** 2026-03-27
**Status:** Active
**Decision:** Default to pure functions and modules. Only use classes when there is a clear, concrete reason.

## Context

The codebase recently underwent a refactor replacing `PipelineAgent` with pure functions (commit 72143a7). That change simplified testing, reduced coupling, and removed unnecessary state. This ADR codifies that direction as a standing constraint.

Classes introduce implicit state, inheritance hierarchies, and lifecycle concerns that make code harder to test in isolation and more brittle to refactor. Python's module system, closures, and first-class functions already provide the composition mechanisms most code needs.

## Decision

1. **Default to functions.** New code should be plain functions in modules unless a class is clearly warranted.
2. **Use frozen dataclasses for data.** When you need a structured data container, use `@dataclass(frozen=True)`. These are value types, not objects with behavior.
3. **Classes are justified when** there is genuine encapsulated mutable state that must be managed across a lifecycle (e.g., connection pools, async context managers, rate limiters). "I need to group related functions" is not sufficient — a module does that.
4. **No inheritance for code reuse.** If two things share behavior, extract a function. Inheritance is acceptable only for framework requirements (e.g., abstract base classes imposed by a library).

## Rationale

- **Testability.** Pure functions with explicit inputs and outputs are trivially testable — no setup, no mocking of `self`, no state leakage between tests.
- **Readability.** A function signature tells you everything it needs. A class requires understanding construction, mutation, and method call order.
- **Refactorability.** Functions compose freely. Classes couple callers to an interface and make extraction/reorganization harder.
- **Track record.** The `PipelineAgent` -> pure functions refactor proved this out in practice for this codebase.

## Consequences

- Code reviewers (human or agent) should push back on new classes that lack encapsulated mutable state.
- Existing classes that are just function bags should be refactored to modules when touched.
- Frozen dataclasses are encouraged and do not violate this ADR — they are data, not objects.
