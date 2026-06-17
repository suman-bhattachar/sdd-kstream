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
