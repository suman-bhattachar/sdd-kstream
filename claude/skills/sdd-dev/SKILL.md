---
name: sdd-dev
description: >-
  Use to implement approved tasks for a Kafka Streams / Spring Boot feature, or to fix code from review
  comments. Trigger after /sdd-approve, after a code review, on /sdd-dev, or when the user wants to work
  on the code.
---

# /sdd-dev — Implementation (implement or fix)

Edits code following `AGENTS.md`. **Only proceed if `IMPLEMENTATION APPROVED` is ticked** (a hook also
blocks `src/` edits otherwise). **Code review is a separate command** (`/sdd-code-review`); this skill
does not review independently — it does the developer self-review (Level 1) and the fixes.

## Start
**Ask the user one thing:** *implement from `tasks.md`, or fix from the review comments in
`code-review.md`?* (If only one applies, say what you're doing and proceed.)

## Orient first (both modes) — keep the window lean
Read `docs/design.md` for the affected area (the architecture map) and the `tasks.md` design refs before
touching code. Before modifying an existing file, read **that file and its test**. When you need code
context below design granularity (callers, existing serdes/wiring, related infra) — especially on a large
or brownfield codebase — **dispatch the researcher subagent** (read-only, separate context; prompt:
`sdd-architect/researcher-prompt.md`) with a focused question and work from its one-page digest. Do **not**
read large swaths of the codebase into this session; that bloat is what degrades implementation quality.

## Implement mode (per task)
1. Write the test first (unit + `TopologyTestDriver` as applicable), then the code per AGENTS.md
   (constructor injection, explicit serdes, no blocking I/O in the topology).
2. Run `./gradlew build` until **green** (compile + unit + topology tests).
3. **Level-1 self-review (mechanical checklist, no artifact):** confirm the AGENTS.md MUSTs are met, the
   task's acceptance criteria in `requirements.md` are satisfied, and tests exist. The green build is the
   hard backstop.
4. Mark the task `review` in `STATE.md`; tell the user to run `/sdd-code-review`.

## Fix mode
- Read `specs/<feature>/code-review.md`. Resolve open findings; re-run `./gradlew build` green.
- For each: mark `resolved`, or `deferred` (Minor/Nit only), or — for a Major accepted as risk — add a
  human **sign-off note in `code-review.md`** (not an ADR). A **Blocker** must be resolved.
- Mark the round resolved; update `STATE.md`.

## Gate
Code-review gate ticks only when: no open Blocker **and** every Major is fixed or signed-off (Minor/Nit
may be deferred). When all tasks are `done` and the gate is green, `next: human merge approval`.
