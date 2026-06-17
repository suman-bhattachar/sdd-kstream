# Independent Framework Review — 2026-06-18

> Brutally-honest, file-verified review of the `sdd-kstream` framework. Every claim below was checked
> against the actual files (paths cited). Nothing was fixed — this is assessment only.

## Verdict
The *design thinking* is genuinely strong — better than almost any AI-coding scaffold. But the framework
has **never been run**, several "non-negotiable" gates **don't actually hold**, and a large fraction of
its claimed rigor is **prose instruction with no mechanism behind it**. It's an excellent specification
of a system, presented as a working one.

## What's genuinely strong
- **Mechanism-per-responsibility is the right spine** (`guides/WORKFLOW-AND-ARTIFACTS.md:53-63`): skills
  for judgment, subagents for isolation, hooks for determinism, rules for policy.
- **Review isolation is sound** — reviewer runs as a separate-context, read-only subagent
  (`claude/skills/sdd-code-review/code-reviewer-prompt.md`), so it can't inherit the implementer's reasoning.
- **Domain specificity is real** — §7 topology safety, blue-green evolution as a whole-topology property,
  `TopologyTestDriver` before Spring tests, one canonical `docs/design.md` because the topology is a single graph.
- **Version-stamped standards** into review artifacts + gate ledger is a real audit property most frameworks lack.

## Central finding: it has never been executed end-to-end
The "worked example" (`specs/001-example-feature/`) is hand-authored fiction:
- **No build exists** — no `build.gradle`/`gradlew`/`pom.xml` anywhere, yet `STATE.md:26` asserts
  `tests passing — ./gradlew build green`.
- **No code exists** — the only `.java` file in the repo is `evals/planted-violation/BadProcessor.java`.
  `tasks.md` claims `domain/Payment.java`, `topology/TotalsTopology.java`, `config/StreamsConfig.java` are
  "done"; none exist.
- **Artifacts disagree** — `tasks.md` frontmatter `status: accepted` vs `STATE.md` `tasks.md | done`;
  review-round numbering uses two unreconciled schemes (`audit-log.md` rounds 1-4 global, `code-review.md`
  `round: 2`, `STATE.md` "code review round 4").

## The gates don't actually hold
First principle is "gates are non-negotiable" (`process-constitution.md:8`). Enforcement doesn't deliver:
1. **Approval is repo-wide, not per-feature** — `scripts/check-approval.sh:8` gates on `ls specs/*/.approved`;
   approving any feature unlocks `src/` for every feature.
2. **The §7 safety check only warns** — `scripts/check-topology.sh:10` exits `1` (non-blocking) on the most
   safety-critical automated check. Doc even says "Change to exit 2 to hard-block."
3. **The §7 pattern list is trivially incomplete** — `check-topology.sh:8` matches only a handful of class
   names; misses `Thread.sleep`, `CompletableFuture.get`, `HttpURLConnection`, `OkHttp`, `Future.get`,
   `CountDownLatch.await`, etc.
4. **Approval gate is bypassable by the agent** — `sdd-approve.md` correctly sets `disable-model-invocation:
   true`, but `scripts/approve.sh` is just `touch .approved`; the agent can run it (or `touch`) via Bash, and
   `check-approval.sh` only tests file existence.

Pattern: the deterministic layer that's supposed to be trustworthy is the weakest part.

## Governance is convention, not control
- **Org/project boundary unenforced** — `/sdd-standards-update` is "maintainer-only by convention"
  (prose only; no `disable-model-invocation`); can rewrite `[ORG]` on a team checkout.
- **No upgrade mechanism** — `upgrade.sh` deferred (`WORKFLOW-AND-ARTIFACTS.md:273-275`); "replaced on
  upgrade" is aspirational.
- **Known-broken brownfield skill ships anyway** — guide admits `sdd-codebase-to-coding-standard` still
  overwrites the `[ORG]` core (`WORKFLOW-AND-ARTIFACTS.md:278-280`).

## Other substantive issues
- **Load-bearing eval isn't automated** — the planted-violation reviewer test needs `claude -p` and isn't
  wired to CI; `run-evals.sh` only does 3 structural checks.
- **AGENTS.md ships with unfilled placeholders** — `knowledge/AGENTS.md:77-78` still has `Java {{N}}` /
  `Kafka Streams {{x.y}}`; copied verbatim on install.
- **Path drift** — canonical repo has `knowledge/AGENTS.md`; `code-reviewer-prompt.md:9` references bare
  `AGENTS.md` (post-install root) while `bugfix-prompt.md:55` references `knowledge/AGENTS.md`. One is wrong
  in each layout.
- **Concurrency unaddressed** — single `docs/design.md` + branch-per-feature ⇒ topology-touching features
  collide on merge, and the gate validated each *branch diff*, not the *merged* topology (where blue-green
  safety actually breaks). Biggest conceptual gap; not listed as a limitation.
- **Orchestrator runs on the weakest model** — `claude/skills/sdd/SKILL.md:7-8` pins `model: haiku, effort:
  low` on the component whose job is gate-guarding.
- **Ceremony with no escape hatch** — a 3-task feature still needs 7 gates, two manual review commands
  re-run per round, ~10 artifacts; no guidance on when the framework is too heavy.

## Meta-risk
Strip away what's actually mechanized (two shell hooks — one repo-wide, one warn-only, both pattern-limited —
plus a file-existence marker) and the rigor lives in prose the model is asked to follow ("interrogate before
designing," "grill don't blindly apply," "additive only," "maintainer-only by convention"). That's the same
"please remember" the framework warns against. The architecture *names* the right mechanisms; the
implementation mostly hasn't built them yet.

## Prioritized fixes
1. **Run the example for real** — minimal Gradle project, actual code, real `./gradlew build`, a genuine
   review round. The only honest proof it works; will surface integration bugs reading can't.
2. **Make `check-approval.sh` per-feature**, and **flip `check-topology.sh` to exit 2** with a much larger
   pattern set.
3. **Wire the planted-violation eval into CI** (headless `claude -p`) — the only guard on the reviewer.
4. **Resolve/strip AGENTS.md placeholders on install**; fix the `AGENTS.md` vs `knowledge/AGENTS.md` path drift.
5. **Decide and document the concurrency story** (even if it's "one feature at a time, for now").
6. **Enforce `/sdd-standards-update`'s maintainer-only rule** (repo-identity check, not prose) **or build
   `upgrade.sh`** — the `[ORG]` model isn't real without one of them.

---

# Next Session Prompt — sdd-restapi design

## What this repo is

`sdd-kstream` is a **Spec-Driven Development framework** (not an application) for Kafka Streams +
Spring Boot teams using Claude Code. Teams install it by cloning and copying. It enforces a fixed
lifecycle: requirements → design → plan → tasks → HUMAN APPROVAL → implement → self-review →
independent review → merge. Every phase writes a file; `STATE.md` is the heartbeat; sessions are
resumable from artifacts alone.

Read `guides/USER-GUIDE.md` and `guides/WORKFLOW-AND-ARTIFACTS.md` for the full picture before
proceeding.

---

## What was done in the previous session

The previous session introduced the **org-canonical standards model** — three documents
(`AGENTS.md`, `knowledge/design-standard.md`, `knowledge/kafka-topology-rules.md`) were
restructured with:
- `version:` frontmatter
- `[ORG]` section (canonical, replaced on upgrade) / `[PROJECT]` section (team-owned, stricter only)
- Per-rule enforcement tags: `[HOOK]` / `[REVIEW]` / `[HOOK][REVIEW]`
- Version stamping wired into review artifacts and the `STATE.md` gate ledger

Everything was committed to branch `feature/spec-architect-upgrade` and pushed to origin.
The four deferred items are logged in `audit_log.md`.

---

## The next task: design and brainstorm `sdd-restapi`

### Goal
Design a new, **separate repo** called `sdd-restapi` — a variant of this framework for
**Spring Boot + Spring MVC + JPA** REST API teams. It should follow the same org-canonical model,
lifecycle, and install pattern as `sdd-kstream`. The next session is **design and brainstorm only**
— no implementation.

### Decisions already made

| Decision | Answer |
|---|---|
| Repository strategy | New separate repo (`sdd-restapi`), not a branch of `sdd-kstream` |
| Session scope | Design + brainstorm only |
| Target stack | Spring Boot + Spring MVC + JPA (concrete reference stack; [PROJECT] handles WebFlux etc.) |
| Safety MUSTs | To be determined in this session (see below) |

### What the session should produce

A clear design for the `sdd-restapi` repo covering:

1. **What stays identical** from `sdd-kstream` (process layer, lifecycle, templates, orchestrator,
   approval hook, STATE.md, brownfield skills, etc.)

2. **What gets swapped** — the domain-specific files:
   - `AGENTS.md [ORG]` — replace §7 Kafka safety MUSTs with REST API safety MUSTs
   - `knowledge/kafka-topology-rules.md` → `knowledge/api-design-rules.md` (HTTP semantics,
     error contracts, pagination, versioning, idempotency, security, transaction boundaries)
   - `knowledge/design-standard.md` — adapt Kafka-specific sections to REST API concerns
     (API surface, sequence diagrams, error response shape, auth model)
   - `/sdd-architect` SKILL.md — replace Kafka failure-mode interrogation with REST API
     pre-design interrogation (auth model, error handling strategy, versioning, idempotency,
     pagination, transaction scope)
   - `/sdd-architecture-review` prompt — reference `api-design-rules.md` instead of
     `kafka-topology-rules.md`
   - `evals/run-evals.sh` — replace topology-smell check with a REST-specific smell

3. **The REST API safety MUSTs** (equivalent of `AGENTS.md §7`) — these are the zero-tolerance
   rules tagged `[HOOK][REVIEW]`. Candidates to interrogate and decide:
   - No business logic in controllers (validate + delegate only)
   - Transaction boundaries explicit (`@Transactional` propagation + rollback documented)
   - No sensitive data in logs or responses (PII, tokens, stack traces)
   - Idempotency documented per endpoint (POST/PUT/DELETE)
   - All external input validated at the boundary before reaching the service layer

4. **`api-design-rules.md` structure** — the REST equivalent of `kafka-topology-rules.md`:
   what sections, what rules, what enforcement tags

5. **Pre-design interrogation for `/sdd-architect`** — what questions the architect must resolve
   before writing the design (auth model, versioning strategy, error response contract, pagination
   approach, idempotency guarantees)

6. **What `sdd-restapi` does NOT need** — brownfield topology inventory, state-store rules,
   repartition rules, blue-green topology evolution. What replaces these concerns for REST?

---

## How to run this session

**Interrogate before designing.** Do not start writing files or making decisions. Instead, walk
the decision tree above with the human one question at a time, providing your recommended answer
for each. Resolve all dependencies before producing the design output.

Use the same structured interrogation pattern used to design the org-canonical model in the
previous session:
- One question at a time
- State your recommended answer
- Do not move to the next branch until the current one is resolved

A reference implementation of this interrogation pattern (the "grill-me" skill) is at:
https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md

The output of the session should be a written design document (not implementation) that the
following session can use to build the actual repo.

---

## Key files to read in this repo before starting

- `AGENTS.md` — see the [ORG]/[PROJECT] structure and enforcement tags
- `knowledge/kafka-topology-rules.md` — this is the template for `api-design-rules.md`
- `knowledge/design-standard.md` — this is the template for the adapted design rubric
- `claude/skills/sdd-architect/SKILL.md` — see the interrogation step to understand what to replace
- `audit_log.md` — full rationale for every decision made in the previous session
