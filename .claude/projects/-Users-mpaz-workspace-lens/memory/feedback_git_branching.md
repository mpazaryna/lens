---
name: Git branching convention
description: User uses ticket/{id}-{name} branch naming and a standardized pre-commit hook to block main
type: feedback
---

Use ticket branch naming convention: `ticket/{id}-{name}`. Pre-commit hooks should match the pattern used in resin-platform with two-line error message pointing to the branch naming format.

**Why:** Consistent workflow across projects (resin-platform, lens).

**How to apply:** When creating git hooks or suggesting branch names, use the `ticket/{id}-{name}` format and the two-line error style.
