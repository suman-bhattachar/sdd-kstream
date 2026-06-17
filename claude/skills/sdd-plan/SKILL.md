---
name: sdd-plan
description: >-
  Use to turn an approved design change into an implementation plan, an ordered task list, and a
  traceability matrix for a Kafka Streams / Spring Boot feature. Trigger after design approval, on
  /sdd-plan, or when the user wants the plan/tasks.
---

# /sdd-plan — Plan, Tasks, Traceability

Produce `specs/<feature>/{plan.md, tasks.md, traceability.md}` (templates of the same names).

## Steps (in order)
1. Confirm the design change is `approved` in `STATE.md` (else stop). Read `docs/design.md` (the relevant
   sections / the branch diff for this feature).
2. `plan.md`: build sequence, milestones, risks, the test strategy. From the design change.
3. `tasks.md`: decompose into small, individually verifiable tasks. Each lists the files it touches, its
   acceptance, and the **requirement/design ID** it satisfies. Status `ready-for-dev`.
4. `traceability.md`: map requirement → design section → task (→ test column later). Every requirement has
   ≥1 task; no orphan tasks.
5. Set `plan.md` `accepted`, tick the gate, set `next: human approval (/sdd-approve)`.
