---
name: Functional programming default
description: Prefer functions over classes per ADR-001, only use OOP when it provides clear benefit
type: feedback
---

Default to functional programming. Only use classes when OOP provides a clear structural benefit (e.g., Protocol definitions, Pydantic models, frozen dataclasses for data).

**Why:** ADR-001 decision. Functions are easier to test, compose, and reason about. Classes add indirection without payoff for pipeline-style code.

**How to apply:** When writing new code, reach for plain functions first. Use classes only for data containers (frozen dataclasses), protocols, or Pydantic config models. Never wrap a set of related functions in a class just for organization -- use a module instead.
