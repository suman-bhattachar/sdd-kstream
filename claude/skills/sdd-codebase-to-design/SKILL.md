---
name: sdd-codebase-to-design
description: >-
  Use to generate the as-is system **design baseline** (docs/design.md) for an EXISTING brownfield
  Java / Spring Boot / Kafka Streams codebase — arc42 structure + a complete Kafka Topology Inventory +
  C4 diagrams. Trigger when documenting, reverse-engineering, or extracting the architecture of an
  existing repo as the SDD design baseline, even if "arc42"/"C4" are never said. Generates the design
  only — not AGENTS.md (use sdd-codebase-to-coding-standard for that). Builds, enriches, and validates a
  self-contained knowledge graph (stdlib Python — no plugin) to corroborate the building-block, runtime,
  and context views.
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
6. **The knowledge graph is secondary, not gospel.** Treat the graph as a *corroborating* evidence source —
   it is itself heuristic (regex skeleton + LLM enrichment) and is **not Kafka-topology-aware** at the
   semantic level. The evidence pack and the actual source remain primary; the **Topology Inventory (S5) is
   always derived from source**, never from the graph alone.

## Workflow
1. **Evidence pack (shared).** If `evidence-pack.md` is absent or stale, run
   `python scripts/extract_evidence.py <repo-root>` (pure Python stdlib; works on Windows/macOS/Linux/WSL).
   Otherwise reuse it. Read `evidence-pack.md`.
2. **Build, enrich, and validate the knowledge graph (standard — correctness over cost).** Three gated
   sub-steps so the graph is correct on the first pass:
   - **Build the skeleton.** Run `python scripts/build_knowledge_graph.py <repo-root>` (pure stdlib — no
     Node/plugin) → `.understand-anything/knowledge-graph.json`. Deterministic regex pass that captures what
     the flat evidence pack can't: the **dependency graph** (imports), **architectural layers**, and
     **complete topic→topology flow edges**. Gate it:
     `python scripts/validate_knowledge_graph.py <graph> --stage skeleton` (must print `VALID`).
   - **Enrich.** Dispatch a **general-purpose** subagent (built-in Task subagent — *not* a plugin agent type)
     using the vendored prompt `graph-enricher-prompt.md` (pass `GRAPH_PATH`, `REPO_ROOT`, `EVIDENCE_PACK`) to
     fill node summaries/tags, refine layer names, reconcile Kafka topics/stores the regex missed (config-driven
     names) against the evidence pack, validate/supplement edges, and build the tour.
   - **Validate (gate).** The enricher must run `validate_knowledge_graph.py <graph> --stage enriched` and loop
     until it prints `VALID`. Do not consume a graph that has not passed this gate.
   - Use the graph per *Graph → design section mapping* below. **It never replaces the evidence pack or source
     reading** (principle 6); the Topology Inventory stays source-derived.
3. **Read the architecturally-significant source — all of it** (the pack lists every topology/config/
   integration file). On a large repo, batch by module/topology and delegate each batch to a subagent with
   a clean context that returns only that slice's findings.
4. **Generate `docs/design.md`** from the shared **`templates/design.template.md`** — the one canonical
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
5. **Coverage gate (do not skip).** Cross-check against the evidence pack's complete inventory; the baseline
   isn't done until coverage is 100%. Also cross-check the graph's node set against the worklist — files in one
   but not the other are gaps to explain. Confirm every architecturally-significant element is represented:
   - [ ] every **module** in the build (Building Block View);
   - [ ] every **topology / processor** has an inventory row **and** a data-flow diagram;
   - [ ] every **input/output topic** appears in a topology row; every **state store** is listed with owner + type;
   - [ ] every **external integration** (DB / REST / other clusters) appears in Context & Scope;
   - [ ] detected **anti-patterns** are recorded in Risks & Open Items;
   - [ ] an engineer who knows the system has reviewed and corrected the above.
6. **Hand off for verification.** State plainly the baseline is a draft until an engineer who knows the
   system reviews it.

## Graph → design section mapping
Draw on the validated graph as follows (always corroborate against source; cite source, not the graph):

| Graph artifact | Feeds design section |
|---|---|
| `layers[]` (id/name/description/nodeIds) | S5 Building Block View (container grouping / Level-1 whitebox) |
| `edges[]` `imports`/`calls`/`depends_on` | S5 component relationships |
| `edges[]` `subscribes`/`publishes` + `concept:topic:` nodes | S3 Scope & Context (interface table) + S6 Runtime flow |
| `edges[]` `reads_from`/`writes_to` + `concept:store:` nodes | S6 Runtime View + S5 Topology Inventory state-store column (verify in source) |
| node `summary` + `tags`, and `tour[]` | S1.1 Requirements overview, S5 responsibilities, source reading order |
| `concept:` nodes (domain terms) | S12 Glossary |
| `config:` nodes | S7 Deployment View + S8.8 Configuration |
| orphan nodes / dependency cycles | S11 Risks & Open Items |
| graph node set vs. evidence-pack worklist | Coverage gate cross-check |

The graph is **not** topology-aware enough to author the Topology Inventory (S5) — that stays source-derived.
Check the graph's `project.gitCommitHash` against HEAD; rebuild if stale.

## Plugin independence (self-contained — survives plugin deletion)
This skill has **no runtime dependency on the Understand-Anything plugin.** The whole knowledge-graph path is
vendored: `scripts/build_knowledge_graph.py` + `scripts/validate_knowledge_graph.py` (stdlib Python) and
`graph-enricher-prompt.md` (run by the built-in general-purpose subagent) + `knowledge-graph.schema.md`.
"Understand-Anything-compatible" means only that the output JSON matches that plugin's schema, so it *can*
drive its dashboard *if* the plugin is ever installed — it is never required. Do **not** reintroduce any
reference to plugin paths, `CLAUDE_PLUGIN_ROOT`, plugin agent types (`understand-anything:*`), or `/understand`.

## Output
- `docs/design.md` — the canonical design baseline (override path on request).
- `evidence-pack.md` — kept as the audit trail of what was detected (shared with the coding-standard skill).
- `.understand-anything/knowledge-graph.json` — the validated, enriched graph (audit trail; drives the
  Understand-Anything dashboard if that plugin is later installed).

## Refresh
Re-run on major re-architecture. For routine work, individual features edit `docs/design.md` directly on
their branch (the diff is the review unit); this skill is for the initial baseline / big resets.

## Scope (first iteration)
Heuristic extraction (regex) — expect some false positives; verify before asserting. Java / Spring Boot /
Kafka Streams only.
