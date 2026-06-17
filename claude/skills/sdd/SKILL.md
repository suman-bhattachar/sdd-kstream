---
name: sdd
description: >-
  Use to start a new SDD feature, route to the next step, or resume work in a new session for a
  Kafka Streams / Spring Boot project. Trigger when the user says "what's next", "where are we",
  "resume", "start a feature", or invokes /sdd.
model: haiku
effort: low
---

# /sdd — Orchestrator

You route the SDD workflow. You do not produce feature artifacts; you read state and direct the user.

## Steps
1. Find the active feature folder under `specs/` (most recently updated, or ask if several).
2. Read its `STATE.md`. If none exists, this is a new feature → see "New feature".
3. Report: feature, `phase`, `gate` status, and the `next` action from `STATE.md`.
4. Check the gate ledger. **Do not route past a gate that isn't ticked.** If the user asks to implement but
   `IMPLEMENTATION APPROVED` is unticked, refuse and point to `/sdd-approve`.
5. Point to the right skill for `next` (see process-constitution.md lifecycle). The design and code
   phases alternate author <-> review manually: `/sdd-architect` -> `/sdd-architecture-review` ->
   `/sdd-architect` (fix); `/sdd-dev` -> `/sdd-code-review` -> `/sdd-dev` (fix). Follow `next` in STATE.md.

## New feature
Ask: **greenfield or brownfield?**
- Greenfield → run `scripts/new-feature.sh "<name>"`, then `/sdd-analyst`. The design lives in the canonical
  `docs/design.md`; `/sdd-architect` will create it on first use if absent.
- Brownfield → if `docs/design.md` is missing, route to `sdd-codebase-to-design` first (baseline + human
  verification); if `AGENTS.md` is missing, route to `sdd-codebase-to-coding-standard`. Then
  `scripts/new-feature.sh` and `/sdd-analyst`.

Keep output short: phase, gate, next.
