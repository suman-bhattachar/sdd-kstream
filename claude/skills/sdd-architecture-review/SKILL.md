---
name: sdd-architecture-review
description: >-
  Use to independently review a Kafka Streams design change before planning. Trigger after
  /sdd-architect has created or updated docs/design.md, on /sdd-architecture-review, or when the user
  wants the design reviewed.
---

# /sdd-architecture-review — Independent design review

Dispatches a single reviewer subagent in a separate context to review the design change, then writes
the findings. Comment-only — it never edits `docs/design.md`; `/sdd-architect` (fix mode) does that.

## Steps
1. Confirm `docs/design.md` has an unreviewed change for this feature (the branch diff).
2. **Dispatch the architecture reviewer** as a general-purpose Task subagent (separate context), passing
   paths to: the `docs/design.md` branch diff, `requirements.md`, `knowledge/design-standard.md`, and the
   output path `specs/<feature>/design-review.md`. Prompt: `architecture-reviewer-prompt.md`.
3. The subagent writes `design-review.md` from `templates/review-comments.template.md` (severity per
   finding) and returns a one-line verdict. Append the round to `specs/<feature>/audit-log.md`.
4. Report the verdict. If changes-requested, the user runs `/sdd-architect` (fix mode) next. The design
   gate ticks only when: no open Blocker **and** every Major has an accepted-risk ADR (Minor/Nit may be
   deferred). This is manual — re-run this command after a fix when you want another pass.
