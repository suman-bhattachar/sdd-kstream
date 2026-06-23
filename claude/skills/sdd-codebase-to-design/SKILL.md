---
name: sdd-codebase-to-design
description: >-
  Use to generate the as-is system **design baseline** (docs/design.md) for an EXISTING brownfield
  Java / Spring Boot / Kafka Streams codebase — arc42 structure + a complete Kafka Topology Inventory +
  C4 diagrams. Trigger when documenting, reverse-engineering, or extracting the architecture of an
  existing repo as the SDD design baseline, even if "arc42"/"C4" are never said. Generates the design
  only — not AGENTS.md (use sdd-codebase-to-coding-standard for that).
---

# Codebase → Design baseline (Java / Spring Boot / Kafka Streams)

Produces one artifact: `docs/design.md` — the complete, as-is architectural baseline that every future
enhancement is designed against. Works on large repos by extracting a compact evidence pack first.

## Non-negotiable principles
1. **Extract, then synthesize.** Never read the whole repo. Reason over the evidence pack; open only the
   files it points to.
2. **Ground every claim** in evidence (file path, count, config key). Not in the evidence → don't assert it.
3. **Never invent business intent.** Code shows *how*, not *why*. Leave `> ⚠️ HUMAN:` stubs for goals,
   quality scenarios, business constraints.
4. **Complete, not sampled.** This is the one output that must be complete — every module, topology, topic,
   state store, integration must appear (Coverage Checklist).
5. **Mandatory human verification.** A reverse-engineered baseline is derived; an engineer who knows the
   system must verify it (especially topology flows) before it is used as the SDD base.

## Workflow
1. **Evidence pack (shared).** If `evidence-pack.md` is absent or stale, run
   `python scripts/extract_evidence.py <repo-root>` (pure Python stdlib; works on Windows/macOS/Linux/WSL).
   Otherwise reuse it. Read `evidence-pack.md`.
2. **Read the architecturally-significant source — all of it** (the pack lists every topology/config/
   integration file). On a large repo, batch by module/topology and delegate each batch to a subagent with
   a clean context that returns only that slice's findings.
3. **Generate `docs/design.md`** from the shared **`templates/design.template.md`** — the one canonical
   structure every design skill uses (arc42 + orientation/binding layers + `[CONTRACT]`/`[INVARIANT]`/
   `[ADR]`/`[TEST]` markers). Apply it in **as-is baseline** mode (you document an existing system, you don't
   author a new one):
   - Fill each section from the evidence pack; **ground every claim** (`file:line` / counts). Per principle 3,
     leave a `> ⚠️ HUMAN:` stub wherever business intent (goals, quality scenarios, constraints) can't be inferred.
   - Mark the **[INVARIANT]/[CONTRACT]**s the code *already* enforces; point `[TEST]` at the existing test
     suite; `[ADR]`s capture decisions visible in the code (flag inferred rationale as such).
   - Produce at minimum: Executive Summary, the complete **Topology Inventory** (every topology) + a data-flow
     diagram each, and the arc42 sections. C4 Mermaid (`C4Context`/`C4Container`) is fine for §3/§5. Toolchain →
     a pointer to AGENTS.md; don't restate versions.
4. **Coverage gate (do not skip).** Cross-check against the evidence pack's complete inventory; the baseline
   isn't done until coverage is 100%. Confirm every architecturally-significant element is represented:
   - [ ] every **module** in the build (Building Block View);
   - [ ] every **topology / processor** has an inventory row **and** a data-flow diagram;
   - [ ] every **input/output topic** appears in a topology row; every **state store** is listed with owner + type;
   - [ ] every **external integration** (DB / REST / other clusters) appears in Context & Scope;
   - [ ] detected **anti-patterns** are recorded in Risks & Open Items;
   - [ ] an engineer who knows the system has reviewed and corrected the above.
5. **Hand off for verification.** State plainly the baseline is a draft until an engineer who knows the
   system reviews it.

## Output
- `docs/design.md` — the canonical design baseline (override path on request).
- `evidence-pack.md` — kept as the audit trail of what was detected (shared with the coding-standard skill).

## Refresh
Re-run on major re-architecture. For routine work, individual features edit `docs/design.md` directly on
their branch (the diff is the review unit); this skill is for the initial baseline / big resets.

## Scope (first iteration)
Heuristic extraction (regex) — expect some false positives; verify before asserting. Java / Spring Boot /
Kafka Streams only.
