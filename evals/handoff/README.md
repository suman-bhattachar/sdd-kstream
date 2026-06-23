# Handoff eval — "documents are the source of truth", tested

The framework's core promise is that each phase writes its work to disk, so the conversation is
disposable: you can `/clear`, start fresh, and the next skill resumes from files alone. That property is
normally only *trusted*. This eval **tests** it for the highest-value handoff — design → plan.

## The idea (cold resume)
Freeze a feature at "design approved", then run `/sdd-plan` in a **fresh headless session with no chat
history** (`claude -p`). If the skill can only succeed using something that was in the conversation
rather than in the files, it fails here — surfacing an otherwise-invisible gap in the artifacts.

Analogy: hand your project to a colleague using only your written notes, and have them start *without
ever talking to you*. If they get stuck, the notes were incomplete.

## What it runs
`run-plan-handoff.sh` stages a throwaway project (`fixture/` + the `sdd-plan` skill + `templates/`), then:

- **POSITIVE** (design gate ticked): asserts `plan.md`, `tasks.md`, `traceability.md` are produced, and
  that **every requirement id (R-x) is traced** — present in `traceability.md` *and* covered by a task —
  and that tasks cite a design ref. This is the executable answer to "is the design enough for `/sdd-plan`?"
- **NEGATIVE** (design gate unticked): asserts `/sdd-plan` **refuses** (no `tasks.md`), proving the gate
  guard reads `STATE.md`, not the chat.

Assertions are deterministic (grep/file checks) — no LLM judge — so a pass/fail is unambiguous.

## Run
```bash
bash evals/handoff/run-plan-handoff.sh     # or via: bash evals/run-evals.sh
```
Requires the Claude CLI (`claude -p`). Without it the eval **skips** cleanly (exit 0). The run uses
`--permission-mode acceptEdits` so the skill may write files unattended; adjust the flag in the script if
your CLI version differs.

## Scope & limits
- Best for the **deterministic** transformer skills (`/sdd-plan` here; `/sdd` routing and gate-refusals
  are natural next cases). The **collaborative** skills (`/sdd-analyst`, `/sdd-architect`, `/sdd-bugfix`)
  are interactive by design and can't be fully exercised headless — for those, test only the
  non-interactive parts (input reading, gate refusal) or script the human answers.
- Tests **sufficiency of the handoff**, not the *correctness* of the plan's content.
- Behavioral (model-backed) → run on a cadence in CI, not every commit; keep assertions structural.
