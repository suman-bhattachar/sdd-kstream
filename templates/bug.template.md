---
id: {{BUG-001}}
title: {{one-line summary}}
type: {{unit | functional | nfr}}
status: open      # open → analysed → fix-proposed → implementing → fixed → verified → post-mortem → closed
feature: {{originating feature id, or "cross-cutting"}}
component: {{affected area — topology / serde / config / ...}}
severity: {{blocker | major | minor}}
created: {{timestamp}}
updated: {{timestamp}}
---
# {{BUG-001}} — {{title}}

## Summary
{{What is wrong, in one or two sentences.}}

## Reproduction
{{type=unit}}     Failing test + assertion + stack trace.
{{type=functional}} Steps → expected behaviour vs actual behaviour.
{{type=nfr}}       Metric + threshold + how it was measured (e.g. p99 latency 800ms vs 200ms SLO).

## Impact
{{Who/what is affected, and how badly. Drives severity.}}

## Analysis
{{Root cause of the defect itself — the code-level reason. Filled in the analyse step.}}

## Doc-gap check
{{Does the expected behaviour already appear in docs/design.md or requirements.md?
  - YES → design was right, implementation wrong. No doc update. Note where it's specified.
  - NO  → design/requirements gap. Update the relevant section before the fix, and note what was added.}}

## Fix approach
{{Proposed fix, written by the skill, confirmed by the human in chat before implementation.
  This confirmation is the (lighter) gate — there is no /sdd-approve for a bug.}}

## Review
{{Inline verdict from the independent reviewer subagent, scoped to the changed files.
  Verdict · Blocker n · Major n · Minor n · Nit n, then the findings. No separate code-review.md.}}

## Verification
{{Human confirmation that the failing test / scenario / metric now passes. Sets status: verified.}}

## Post-mortem
{{Mandatory before close. WHY did this leak through requirements → design → review → self-review?
  Identify which gate should have caught it. The systemic finding is appended to
  knowledge/feedback-log.md (status: open) for /sdd-standards-update to action later.}}
