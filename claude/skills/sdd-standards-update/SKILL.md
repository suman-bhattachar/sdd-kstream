---
name: sdd-standards-update
description: >-
  Use in the canonical framework repo to action accumulated post-mortem feedback — turn open findings in
  knowledge/feedback-log.md into new standard rules or reviewer checks. Trigger on /sdd-standards-update
  or when the user wants to process the feedback log / evolve the standards.
---

# /sdd-standards-update — Action the feedback loop (maintainer tool)

**This is a canonical-repo maintainer tool, not a per-project workflow skill.** It edits the `[ORG]`
sections of the standards — which is only legitimate in the canonical `sdd-kstream` source, where `[ORG]`
is owned. Running it on a consuming team's checkout would edit content that an upgrade later overwrites.
If you are on a team project, your only local standards edits are `[PROJECT]` (stricter additions);
findings travel upstream to the canonical repo, where this skill consumes them.

Reads open findings from `knowledge/feedback-log.md`, interviews the human, and **appends** rules /
checks to close each leak. The full behaviour is in **`standards-update-prompt.md`** — read and follow it.

## Core rules (do not deviate)
- **Additive only.** Append new `[HOOK]` / `[REVIEW]` / `[GUIDANCE]` rules to a standard, or a new check
  line to a reviewer/dev prompt. **Never modify or remove** an existing rule — that's what keeps every
  change backward-compatible.
- **Version bump on every standard append.** Each edited standard's `version:` ticks up one **minor**
  (`1.0 → 1.1`). There is no major bump — additive-only changes are always backward-compatible. The
  document **name never changes**.
- **Scope:** standards (`AGENTS.md`, `design-standard.md`, `kafka-topology-rules.md`) and review/dev
  prompts (`code-reviewer-prompt.md`, `architecture-reviewer-prompt.md`, `sdd-dev` self-review). Findings
  categorised `process-gap` are **recommended only** — surface them; don't edit `process-constitution.md`.

## Steps
1. List open findings (frontmatter `open:` + their body entries).
2. Per finding: interview the human to confirm the exact rule wording, the right document, and the
   enforcement tag. Don't blindly transcribe the proposed fix.
3. Apply the edit (append rule + minor version bump on standards; append check line on prompts).
4. Flip the feedback-log entry `open → actioned`: move its id from frontmatter `open:` to `actioned:`
   (with `resolved:` date and a `changed:` list), append a `→ Actioned` line to its body entry, and set
   `last_actioned:`.
