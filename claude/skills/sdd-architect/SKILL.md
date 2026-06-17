---
name: sdd-architect
description: >-
  Use to create a Kafka Streams design from approved requirements, or to fix a design from review
  comments. Trigger after requirements are approved, after an architecture review, on /sdd-architect, or
  when the user wants to work on the design.
---

# /sdd-architect — Design (create or fix)

The design is canonical: `docs/design.md` (whole-system). You edit it on the feature branch — the diff
is the change, the merge is the fold-in. Decisions go in `docs/adr/`. **Review is a separate command**
(`/sdd-architecture-review`); this skill does not review.

## Start
1. Read `docs/design.md` if it exists (background context — always, greenfield or brownfield).
2. **Ask the user one thing:** *create/update the design from `requirements.md`, or fix it from the
   review comments in `design-review.md`?* (If only one applies — e.g. no open `design-review.md` — say
   what you're doing and proceed.)

## Create / update mode
- Confirm `requirements.md` is `approved`. Edit `docs/design.md` to add/modify only the sections this
  change touches: topology, state stores, serdes, repartitions, processing guarantee, and the blue-green
  evolution plan. Obey AGENTS.md §Kafka and `knowledge/kafka-topology-rules.md`. Record significant
  choices as ADRs. Keep the Topology Inventory current.
- **Investigate when needed (mainly brownfield).** If `docs/design.md`'s summary lacks the detail to
  safely modify the area this change touches, dispatch a **researcher subagent** (read-only, separate
  context; prompt: `researcher-prompt.md`) with a focused question — it returns a digest of the specific
  existing code (serdes, state-store config, processor chain) so the heavy reading stays out of your
  context. Use it only when the summary isn't enough, not on every feature.
- Set the design change `in-review`; tell the user to run `/sdd-architecture-review`.

## Fix mode
- Read `specs/<feature>/design-review.md`. Work through open findings **collaboratively with the user**
  — grill and discuss how to resolve each; do not blindly apply the reviewer's wording. Update
  `docs/design.md`.
- For each finding: mark it `resolved`, or `deferred` (Minor/Nit only, with a reason), or — for a Major
  accepted as risk — record an **ADR** and mark it accepted. A **Blocker** must be resolved.
- Mark the addressed `design-review.md` round resolved (a fresh `/sdd-architecture-review` opens the next
  round). Update `STATE.md`.

## Gate
Design gate ticks only when: no open Blocker **and** every Major has an accepted-risk ADR (Minor/Nit may
be deferred). Then `next: planning (/sdd-plan)`. Shard `docs/design.md` into `docs/design/` only if large.
