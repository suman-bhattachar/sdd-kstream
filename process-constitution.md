# Process Constitution

Governance for the SDD process. `AGENTS.md` governs *what code to write*; this file governs *how the
work runs*. Highest authority for process decisions.

## Principles
1. **Specification precedes implementation.** No code before requirements + design are approved.
2. **Gates are non-negotiable.** No phase advances automatically. Skipping a gate is prohibited; the
   Orchestrator stops and flags it.
3. **Artifacts are the source of truth, not the conversation.** Every phase writes a file with a
   `status:` field; personas read the prior artifact from disk. A fresh session resumes from files.
4. **Right mechanism per responsibility.** Personas = skills · independent review = subagents
   (separate context) · deterministic enforcement = hooks/scripts · pipeline gates = CI. Prefer the
   simplest mechanism that closes the failure mode.

## Lifecycle
```
[brownfield only] sdd-codebase-to-design → docs/design.md   ·   sdd-codebase-to-coding-standard → AGENTS.md
requirements → design: /sdd-architect (create) → /sdd-architecture-review → /sdd-architect (fix) [manual, repeat as needed] → plan → tasks → traceability
   → HUMAN APPROVAL → implement → code review → human merge approval → deploy
```

## Gates
| Gate | Passes when |
|---|---|
| requirements approved | acceptance criteria + mapping complete, human-approved |
| design approved | no open Blocker AND every Major has an accepted-risk ADR (Minor/Nit may be deferred) |
| plan accepted | plan + tasks + traceability complete |
| IMPLEMENTATION APPROVED | **human-only**, via `/sdd-approve` |
| code review approved | no open Blocker AND every Major fixed or human-signed-off in code-review.md (Minor/Nit may be deferred) |
| tests passing | `./gradlew build` green, ordered ladder satisfied |
| human merge approval | a human approves the merge after code review approved |

## Mechanism map
- **Personas** — skills: `/sdd`, `/sdd-analyst`, `/sdd-architect` (create/fix design), `/sdd-plan`, `/sdd-dev` (implement/fix + Level-1 self-review).
- **Reviews are separate commands** — `/sdd-architecture-review`, `/sdd-code-review` — each dispatches a single reviewer subagent (separate context, comment-only) into its own command. Council deferred.
- **Researcher subagent** — `/sdd-architect` **and `/sdd-dev`** dispatch a read-only subagent to investigate
  specific existing code and return a digest (brownfield or any large codebase), keeping volume out of the
  main context.
- **Self-review (Level 1)** is a mechanical checklist inside `/sdd-dev` (AGENTS.md MUSTs + acceptance criteria + green build); no artifact. Independent review (Level 2) writes the artifact; human approval (Level 3) ticks the gate.
- **Determinism** — `scripts/` + `claude/settings.json` hooks (approval gate, topology smell check).
- `AGENTS.md` states the rules; hooks + review enforce the critical ones. Advisory text alone is not enforcement.

## Review flow (architecture & code — same shape, manual)
1. The author skill self-reviews, then **stops** — review is a separate command the user runs.
2. The review command (`/sdd-architecture-review` or `/sdd-code-review`) dispatches a single reviewer
   subagent (separate context, comment-only) which writes findings to `templates/review-comments.template.md`
   with a severity per finding, and returns a verdict. The round is appended to `audit-log.md`.
3. The author skill in **fix mode** resolves findings **collaboratively with the human** (grilling, not
   blind application). Per finding: resolve, defer (Minor/Nit + reason), or accept a Major as risk
   (design → ADR; code → human sign-off in `code-review.md`). A Blocker must be resolved.
4. The user **manually** re-runs the review command for another pass when ready. No automatic loop.
   Calibrate: only Blocker/Major affect approval; never invent findings (zero findings -> approved).

## Severity & deferral governance
- **Blocker** — never deferrable; keeps the gate red until resolved.
- **Major** — resolve, or accept as risk: architecture → an **ADR**; code → a **human sign-off** in
  `code-review.md`. Not deferrable without that record.
- **Minor / Nit** — deferrable freely; recorded only in the review artifact, never in `STATE.md`.
- No framework debt register — "fix later" goes to the team's issue tracker.

## Post-implementation defects & the feedback loop
A defect found after implementation does **not** re-enter the feature lifecycle — it runs through
`/sdd-bugfix`, a standalone lifecycle (`bugs/<id>.md`, never reopens a feature's `STATE.md`):
- **Lighter gate.** No `/sdd-approve`; the human confirming the fix approach in chat is the gate. The fix
  is made via `/sdd-dev` (fix mode) and independently reviewed inline (no separate artifact).
- **Conditional doc update.** If the bug exposes a gap, `docs/design.md`/`requirements.md` is updated
  before the fix; an implementation-only bug touches no doc.
- **Mandatory post-mortem.** Before close, every bug answers *why it leaked through the gates* and records
  a finding in `knowledge/feedback-log.md` (recommend-only — it edits no standard).

The loop closes in the **canonical repo only**: a maintainer runs `/sdd-standards-update`, which (under
human interview) **appends** a new rule to a standard or a check to a reviewer/dev prompt — additive only,
minor `version:` bump, never modifying or removing an existing rule. `process-gap` findings are
**recommended only**; a change to this constitution is always a deliberate human edit, never auto-applied.
