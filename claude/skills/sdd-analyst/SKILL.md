---
name: sdd-analyst
description: >-
  Use to capture or refine requirements for a Kafka Streams / Spring Boot feature — including
  acceptance criteria and the topic/state mapping — before any design. Trigger when starting a
  feature's requirements, on /sdd-analyst, when the user wants to write/clarify requirements, or
  when a feed mapping workbook (.xlsx) needs intake.
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

## Feed-mapping intake (when the input is a mapping workbook)
For a feed whose spec arrives as an analyst workbook (`templates/mapping.template.xlsx` format):
1. Run `python scripts/convert_mapping.py <workbook.xlsx> specs/<feature>/mapping.md`. It validates
   the **analyst-owned** content only (rule types, worked examples, allowed values / precision where
   the type demands, lookup definitions) and fails with row-level errors — resolve them **with the
   analyst** and re-run until `VALID`.
2. The workbook's **Schema settings block is not yours**: it is design-phase input owned by
   `/sdd-architect` (`knowledge/mapping-rules.md`). Pass it through unvalidated; never ask the
   analyst to fill it.
3. Acceptance criteria come from the mapping rows: one criterion per row using its worked example
   (sample source value → expected target value), plus feed-level criteria (key, filter, DLQ
   behaviour, processing guarantee).
4. `requirements.md` wraps the feed-level requirements and points to `mapping.md`. Analyst approval
   means the business signs off **what goes out** — never schema technicalities.
