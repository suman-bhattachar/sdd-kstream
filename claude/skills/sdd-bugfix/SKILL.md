---
name: sdd-bugfix
description: >-
  Use to triage and fix a defect found after implementation — a failing unit test, a functional bug, or
  a non-functional (performance/memory) issue. Trigger on /sdd-bugfix, when the user reports a bug, or to
  resume/verify/close an existing bug in bugs/.
---

# /sdd-bugfix — Bug lifecycle (analyse → fix → verify → post-mortem)

One skill drives a defect from report to close. It is **skill-first**: the user invokes
`/sdd-bugfix "<description>"`; this skill interrogates and writes the bug file. Bugs are **standalone** —
a top-level `bugs/<id>.md`; the originating feature's `STATE.md` is never touched (the `feature:` field
preserves traceability). The fix runs through the **lighter flow** — no `/sdd-approve` gate; the human
confirming the fix approach in chat *is* the gate.

The full per-step behaviour (type-specific interrogation, doc-gap diagnostic, mode detection, the inline
review dispatch, and the mandatory post-mortem) is in **`bugfix-prompt.md`** — read it and follow it.

## Start — detect mode from the bug file's `status:`
- **No file yet** (`/sdd-bugfix "..."`): create mode → interrogate, write `bugs/<id>.md` from
  `templates/bug.template.md`, set `status: analysed`.
- **`status: analysed | fix-proposed`**: resume → confirm fix approach, then hand to `/sdd-dev` (fix mode).
- **`status: fixed`**: verify → ask the human whether the failing test/scenario/metric now passes; on yes
  set `status: verified` and run the **post-mortem** before closing.
- **`status: verified`**: run the post-mortem if not done, then `status: closed`.

## The flow (see bugfix-prompt.md for detail)
1. **Interrogate** by `type` (unit / functional / nfr); run the **doc-gap check** — update
   `docs/design.md`/`requirements.md` *only* if the bug exposes a design/requirements gap.
2. **Propose** a `## Fix approach`; the human confirms in chat (the gate).
3. **Fix** via `/sdd-dev` (fix mode) — it edits code per `AGENTS.md` and rebuilds green.
4. **Review** inline: dispatch the code-reviewer subagent (`code-reviewer-prompt.md`) scoped to the
   changed files, writing its verdict into the bug file's `## Review` section — no separate artifact.
5. **Verify** (human confirms) → **post-mortem** (mandatory): append the systemic finding to
   `knowledge/feedback-log.md` → `status: closed`.

## Gate
A bug closes only when: review has no open Blocker and every Major is fixed/signed-off, the human has
verified the fix, **and** the post-mortem finding is recorded in `knowledge/feedback-log.md`.
