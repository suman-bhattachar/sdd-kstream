---
name: sdd-analyst
description: >-
  Use to capture or refine requirements for a Kafka Streams / Spring Boot feature — including
  acceptance criteria and the topic/state mapping — before any design. Trigger when starting a
  feature's requirements, on /sdd-analyst, or when the user wants to write/clarify requirements.
---

# /sdd-analyst — Requirements

Produce `specs/<feature>/requirements.md` from `templates/requirements.template.md`.

## Steps
1. Read the feature's `STATE.md`. Greenfield: gather intent from the user. Brownfield: read
   `docs/design.md` for system context (it replaces a from-scratch mapping).
2. Fill `requirements.md`:
   - numbered requirements with stable IDs (R-1, R-2 …),
   - an **Acceptance Criteria** section (testable, per requirement) — this is the contract reviews check against,
   - the topic/state **mapping** (input/output topics, keys, state touched).
3. **Clarify, don't assume.** Ask focused questions; record answers in a Clarifications section. Leave
   `⚠️ HUMAN:` where intent is genuinely unknown.
4. Set status `in-review`; ask the user to approve. On approval set `approved`, tick the gate in
   `STATE.md`, set `next: design (/sdd-architect)`.
