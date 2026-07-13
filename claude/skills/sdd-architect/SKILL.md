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

## Design document format
`docs/design.md` follows `templates/design.template.md` (arc42, ASCII-only). It has two layers:
**orientation** (context/goals — non-normative) and **binding** (the spec). Every normative statement
**MUST** carry a marker — `[CONTRACT]` (fixed interface/schema — implement exactly), `[INVARIANT]` (a
property that must always hold), `[ADR]` (a deliberate decision), `[TEST]` (an executable oracle). Unmarked
prose and pseudocode are illustrative. When creating `docs/design.md` for the first time, seed it from the
template.

## Start
1. Read `docs/design.md` if it exists (background context — always, greenfield or brownfield).
2. **Ask the user one thing:** *create/update the design from `requirements.md`, or fix it from the
   review comments in `design-review.md`?* (If only one applies — e.g. no open `design-review.md` — say
   what you're doing and proceed.)

## Create / update mode
- **Interrogate before designing.** Before editing `docs/design.md`, walk the failure modes in
  `knowledge/kafka-topology-rules.md` and ask the human only the ones `requirements.md` doesn't already
  settle: state-store corruption/retention, re-keying & undocumented repartitions, serde compatibility
  across releases, processing guarantee + idempotency, and blue-green coexistence with the running
  topology. Resolve each before writing the design; where the human defers, leave a `⚠️ HUMAN:` stub.
  Don't pad with questions the spec already answers (no forced count).
- Confirm `requirements.md` is `approved`. Edit `docs/design.md` to add/modify only the sections this
  change touches: topology, state stores, serdes, repartitions, processing guarantee, and the cross-release
  / blue-green plan. Obey AGENTS.md §Kafka and `knowledge/kafka-topology-rules.md`. Keep the **Topology
  Inventory** current (a row + a data-flow diagram per topology).
- **Make it binding, not prose.** Tag every normative statement with a marker (above); record significant
  choices as **[ADR]**s (table row + full record, mirrored to `docs/adr/`); and pin each **[INVARIANT]**/
  **[CONTRACT]** with a **[TEST]** oracle in §10 (this is what makes the design plannable and reviewable —
  the reviewer and `/sdd-plan` work from the marked elements). Keep orientation sections non-normative.
- **Investigate when needed (mainly brownfield).** If `docs/design.md`'s summary lacks the detail to
  safely modify the area this change touches, dispatch a **researcher subagent** (read-only, separate
  context; prompt: `researcher-prompt.md`) with a focused question — it returns a digest of the specific
  existing code (serdes, state-store config, processor chain) so the heavy reading stays out of your
  context. Use it only when the summary isn't enough, not on every feature.
- Set the design change `in-review`; tell the user to run `/sdd-architecture-review`.

## Feed design (when the feature's spec is `specs/<feature>/mapping.md`)
- **The Schema settings block is yours** (engineering-owned; the analyst never fills it —
  `knowledge/mapping-rules.md`): confirm/complete record name, namespace, record description,
  timestamp precision, and compatibility mode in the workbook, then re-run `convert_mapping.py`.
- Generate the target contract: `python scripts/generate_avro_schema.py specs/<feature>/mapping.md`.
  It applies `knowledge/mapping-rules.md` deterministically; any deviation needs an **[ADR]**.
- **Feed revision:** verify the new schema against the previously registered version under the
  feed's declared compatibility mode **before** the design gate — this is the serde/blue-green rule
  applied to feeds.

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
