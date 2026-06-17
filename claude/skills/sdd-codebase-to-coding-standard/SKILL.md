---
name: sdd-codebase-to-coding-standard
description: >-
  Use to generate or refresh the team **coding standards** as AGENTS.md from an EXISTING Java / Spring
  Boot / Kafka Streams codebase — auto-derived toolchain/versions + prevalence-tagged MUST/SHOULD rules.
  Trigger when the user wants to create or refresh AGENTS.md, coding standards/guidelines, or a coding
  "constitution" from existing code. Generates AGENTS.md only — not the design baseline. Living document:
  re-run to refresh toolchain/version facts and prevalence stats.
---

# Codebase → Coding standards (AGENTS.md)

> **Optional.** `AGENTS.md` already ships prescriptive with the non-negotiable §7 MUSTs (enforced by hooks
> + review). Run this only to enrich it from the codebase — auto-fill the toolchain/version table, tag the
> repo's real conventions by prevalence, surface divergences, and keep it refreshed. Skip it for greenfield
> or a small service and just hand-fill the version placeholders.

Produces one artifact: `AGENTS.md` — the prescriptive ruleset AI agents follow when writing new code.
Standalone — runs on counts, prevalence, and light sampling; it does not need the design baseline.

## Non-negotiable principles
1. **Extract, then synthesize.** Reuse `evidence-pack.md` if present; else run
   `python scripts/extract_evidence.py <repo-root>`. Light sampling (~5–10 files) is enough — this runs on
   counts and prevalence, not full reads.
2. **Report conventions with prevalence; never silently pick.** State the dominant convention with its
   share ("constructor injection: ~84%") and route every genuine conflict to the **Divergences** appendix
   for a human to ratify. An unratified divergence is not a rule.
3. **Re-derive volatile facts; never hand-maintain them.** Toolchain, versions, and prevalence are
   regenerated each run, date-stamped, and pointed back to their source.
4. **§7 safety rules are non-negotiable** — prescriptive, NOT prevalence-derived. If the codebase violates
   a §7 MUST (e.g. blocking I/O in a processor), record it in Risks/Divergences as **tech debt to fix** —
   never demote the rule. Tag these as fixed MUSTs the derived conventions sit *around*.
5. **Minimal, high-signal.** Write directives an agent can follow ("Use constructor injection; never field
   injection"), not values. Don't restate the dependency tree — it lives in the build files.

## Workflow
1. Ensure the evidence pack (reuse or regenerate, as above).
2. Light-sample to confirm conventions and prevalence.
3. Generate **AGENTS.md** from `assets/coding-constitution.template.md`: auto-derived Toolchain table
   (date-stamped, sourced), prevalence-tagged MUST/SHOULD rules (Java/Spring/Kafka/testing — Gradle only,
   no Maven), Divergences appendix. Keep the §7 MUSTs fixed (principle 4).
4. **Refresh run** (files already exist): regenerate only volatile sections, **preserve hand-written rule
   sections verbatim**, show a proposed diff, ask before writing. Never clobber human edits.
5. Ensure a thin `CLAUDE.md` points to AGENTS.md (create if absent).

## Output
- `AGENTS.md` (+ thin `CLAUDE.md` pointer) at the repo root.
- `evidence-pack.md` — shared audit trail.

## Maintaining (living document)
Team-owned. Re-run each sprint and on any major dependency bump: volatile sections refresh, hand-written
rules persist, new divergences surface to ratify. Because AGENTS.md is advisory, enforce the critical
MUSTs with hooks/CI (the framework's `settings.json` + review do this).
