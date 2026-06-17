---
name: sdd-code-review
description: >-
  Use to independently review implemented code before merge. Trigger after /sdd-dev reports a task built
  and self-reviewed, on /sdd-code-review, or when the user wants the code reviewed.
---

# /sdd-code-review — Independent code review (Level 2)

Dispatches a single reviewer subagent in a separate context that runs two ordered passes, then writes
the findings. Comment-only — it never edits code; `/sdd-dev` (fix mode) does that. This is the
independent review; the developer's own self-review (Level 1) already happened inside `/sdd-dev`, and
human merge approval (Level 3) follows.

## Steps
1. Confirm `./gradlew build` is green for the change under review (Level-1 precondition).
2. **Dispatch the code reviewer** as a general-purpose Task subagent (separate context), passing paths
   to: the changed files, `AGENTS.md` (the single checklist), `requirements.md`, `docs/design.md`, and
   the output path `specs/<feature>/code-review.md`. Prompt: `code-reviewer-prompt.md`. Two ordered
   passes: **spec-compliance** (vs the acceptance criteria in `requirements.md` + `docs/design.md`), then
   **code-quality** (vs `AGENTS.md`).
3. The subagent writes `code-review.md` from `templates/review-comments.template.md` (stamping
   `standards: AGENTS.md v<version>` from the doc's frontmatter) and returns a verdict. Append the round
   to `audit-log.md`. When the gate ticks, record that version on the `STATE.md` ledger line.
4. Report the verdict. If changes-requested, the user runs `/sdd-dev` (fix mode). The code-review gate
   ticks only when: no open Blocker **and** every Major is fixed or human-signed-off in `code-review.md`
   (Minor/Nit may be deferred). Manual — re-run after a fix for another pass.
