# Evals

Tests for the **framework's own behavior** — so contributors can change skills/reviewers without
silently breaking them. Approach borrowed from Superpowers (skill-triggering + planted-bug tests).

Full behavioral evals need headless Claude Code (`claude -p`). The fixtures and expected outcomes
ship regardless, so they're runnable/reviewable even without CI.

## What to check
1. **Skill triggering** — each persona fires from a naive prompt (no slash command). If a skill stops
   triggering, its `description` probably leaked process detail (Superpowers' "Description Trap") —
   keep descriptions trigger-only.
2. **Planted violation review** — `planted-violation/` puts a known §7 breach (blocking I/O in a
   processor) in front of the code reviewer; the reviewer MUST flag it at Blocker/Major and refuse to
   approve. This is the load-bearing test — keep it green when editing `code-reviewer-prompt.md`.
3. **Gate / state** — editing `src/main/*.java` before `/sdd-approve` is blocked (check-approval.sh
   exits 2); `STATE.md` advances correctly across phases.

Run `bash evals/run-evals.sh` for the deterministic checks (the script-level ones); run the behavioral
ones via `claude -p` against the fixtures.
