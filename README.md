# SDD-KStream

A Spec-Driven Development framework for **Kafka Streams + Spring Boot** teams using **Claude Code**.
Opinionated for streaming: topology safety, explicit state-store management, safe repartitioning, and
blue-green topology evolution with zero tolerance for state corruption or duplicate processing.
Implementation never precedes an approved specification and architecture.

Installs by `git clone` + copy — no Node, no Python package manager, no installer.

## Start here
- **Using it** → `guides/USER-GUIDE.md` (full greenfield + brownfield worked examples)
- **Extending it** → `guides/WORKFLOW-AND-ARTIFACTS.md` (exhaustive internals + rationale)
- **The rules** → `AGENTS.md` (coding standards) · `process-constitution.md` (process governance)
- **Install** → `install/INSTALL.md`

## How it works (one minute)
Each phase is a persona (a skill) that reads the prior artifact from disk, writes the next, and updates
`STATE.md`. You approve each gate. The conversation is disposable; the per-feature folder in `specs/` is
the memory, so any session resumes from files. Greenfield starts at requirements; brownfield runs the
`sdd-codebase-to-design` baseline once, then each enhancement edits that canonical design.

```
requirements → design (/sdd-architect ↔ /sdd-architecture-review, manual) → plan → tasks
   → HUMAN APPROVAL → implement + self-review (/sdd-dev) → /sdd-code-review → merge approval → deploy
```

## Personas
`/sdd` (orchestrator) · `/sdd-analyst` · `/sdd-architect` · `/sdd-architecture-review` · `/sdd-plan` · `/sdd-dev` · `/sdd-code-review`.
Reviews are their own commands (single reviewer subagent, separate context). Brownfield setup: `sdd-codebase-to-design` (→ `docs/design.md`) and, optionally, `sdd-codebase-to-coding-standard` (→ `AGENTS.md`).
Independent review runs as a **subagent** in a separate context (comment-only). Deterministic gates are
**hooks + scripts**. Coding rules live in `AGENTS.md` (enforced by hooks + review, not text alone).

## Layout
```
AGENTS.md  CLAUDE.md  process-constitution.md       rules + governance (repo root)
docs/        user guide + contributor reference
templates/   blank artifact templates (with status frontmatter)
docs/        canonical, living docs/design.md (the one design) + docs/adr/
guides/      framework help docs (USER-GUIDE, WORKFLOW-AND-ARTIFACTS) — NOT copied into a service
specs/       per-feature artifacts at runtime (requirements, plan, tasks, reviews, STATE) + one example
knowledge/   streaming guardrail reference
scripts/     pure-bash: new-feature, approve, hook checks
evals/       framework self-tests (skill triggering, planted-violation review)
claude/      installable payload → copied into the project's .claude/
  skills/    personas + the two review commands (+ their reviewer prompts) + the two brownfield skills
  commands/  /sdd-approve (human-only)
  settings.json  permissions + hooks
```

## License
MIT (set the copyright holder in `LICENSE` before publishing).
