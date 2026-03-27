# .orchestra — Agent Knowledge Base

This folder exists for the **process**, not the product. It contains every artifact an AI agent needs to understand, continue, or reconstruct the project context.

The dot-prefix follows the same convention as `.github/`, `.vscode/`, and `.claude/` — infrastructure that supports the work but isn't part of the deliverables themselves.

## Who reads this

**AI agents.** The primary consumers are Claude Code agents working in this repo. They read `.orchestra/` to orient themselves before executing work.

**Humans** may read these files for context, but they are not the target audience.

## Structure

```
.orchestra/
├── README.md          <- This file
├── roadmap.md         <- The score — top-level PRD
├── adr/               <- Decision Records (long-lived constraints)
├── work/              <- Per-ticket work items (PRDs + specs)
│   └── TEMPLATES/     <- PRD and spec templates
└── devlog/            <- Chronological journal by quarter
```

### `roadmap.md` — The Score

The top-level PRD. Its materials table lists milestones. Milestones are PRDs whose materials tables list deliverables. PRDs all the way down.

### `adr/` — Decision Records

Standing decisions that constrain how the project evolves. Long-lived — they outlast any individual task.

- **Format:** `ADR-{NNN}-{name}.md`
- **When to create:** When making a decision future agents must follow
- **When to read:** Before any work — CLAUDE.md points to relevant ADRs by topic

### `work/` — Per-Ticket Work Items

Each ticket gets a folder containing its PRD and/or spec.

- **Folder naming:** `{id}-{short-name}/`
- **PRD** (`prd.md`): What's the goal? What does success look like?
- **Spec** (`spec.md`): What steps? How to execute?

### `devlog/` — Journal

Chronological entries capturing what happened, what was learned, what changed. Organized by quarter.

- **Format:** `{YYYY-MM-DD}-{slug}.md`
- Not a changelog — captures decisions, outcomes, and context

## Why this folder exists

If the project context were reconstructed from scratch, an agent could read `.orchestra/` and understand:

- **What decisions were made and why** -> `adr/`
- **What the plan is** -> `roadmap.md`
- **What was executed for each task** -> `work/`
- **What happened along the way** -> `devlog/`
