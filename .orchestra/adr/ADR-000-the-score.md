# ADR-000: The Score — Roadmaps as PRDs

**Date:** 2026-03-27
**Status:** Active
**Decision:** The product roadmap is a PRD. Milestones are PRDs. The hierarchy is PRDs all the way down.

## Context

The `.orchestra/` folder is named for a reason — agents are the orchestra, the founder is the conductor, and the work needs a score to play from. Without a score, ticket creation is reactive and milestone planning lives in the founder's head.

The PRD format already contains the shape of a milestone: an objective (what "done" looks like), success criteria (checkboxes), a materials table (the nodes/deliverables), and references to content files in the repo. A roadmap is just the top-level PRD whose materials table lists milestones instead of deliverables.

## Decision

### The hierarchy

```
Roadmap PRD (the score)
└── Milestone PRD (a movement)
    └── Deliverables (the notes)
        └── Content files in the repo
```

1. **The roadmap** is `.orchestra/roadmap.md` — the score. It is not a work item; it is the thing that generates work items. Its objective is the product vision. Its materials table lists milestones with status. One roadmap per project.

2. **Each milestone** is a PRD in `.orchestra/work/{name}/prd.md`. Its objective defines what "done" looks like for that milestone. Its materials table lists the deliverables/tickets needed to reach it.

3. **Deliverables** are the content files that already live in the repo. They are referenced by path in the milestone PRD's materials table.

4. **Tickets** are generated from the gap between a milestone's materials table and current state — rows marked "Not Started" or "Needs Refresh" become tasks.

### The materials table

The key structure at every level:

```markdown
| Material | Location | Status |
|----------|----------|--------|
| {deliverable or milestone name} | {path or link} | Done / In Progress / Not Started / Needs Refresh |
```

For the roadmap-level PRD, each row is a milestone. For a milestone-level PRD, each row is a deliverable.

### Roles

**The Composer** (human) writes the score — defines the roadmap, sets the milestones, decides what "done" looks like. Strategic. Evaluates all inputs before they enter the system. Always human.

**The Conductor** interprets the score — reads the active milestone, identifies what's not done, keeps tempo, and directs the orchestra (agents). Starts human, shifts agentic over time as structure improves.

**The Orchestra** (agents) performs the music — reads the score for context, picks up tickets as contracts, executes the work, and updates the score as part of closing the contract. An agent that completes work but doesn't update the PRD hasn't finished the job.

### The workflow

1. **Compose:** Define a milestone as a PRD — objective, done-conditions, materials table
2. **Conduct:** Read the milestone PRD, identify what's not done, propose or generate tickets
3. **Perform:** Each ticket becomes an agentic session. The agent reads the milestone PRD for context, executes the work, and the deliverable is created or updated in the repo
4. **Progress:** Status rolls up through the materials tables — deliverable status updates in the milestone PRD, milestone status updates in the roadmap PRD

## Rationale

- **No new artifact types.** The PRD format already works. Reusing it at every level keeps the system simple and learnable for agents.
- **The topology is the reference chain.** Roadmap PRD links to milestone PRDs, milestone PRDs link to content files. The graph is implicit in the links.
- **Machine-readable by convention.** Materials tables are structured enough for agents to parse and generate tickets from.
- **Matches the orchestra metaphor.** The roadmap is the score. Milestones are movements. Deliverables are the notes.

## Consequences

- `.orchestra/roadmap.md` must exist as the top-level score — one per project, not inside `work/`
- Every milestone must have a PRD in `.orchestra/work/{name}/prd.md`
- Agents proposing work should trace it back to a milestone, and milestones should trace back to the roadmap
- The agent session loop is: read the score -> perform -> update the score
