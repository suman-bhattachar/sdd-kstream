# SDD-KStream — Framework Internals & Enhancement Reference

For people **changing the framework itself**. It documents every component, how the pieces fit, and —
crucially — *why* each mechanism was chosen, so you can extend it without breaking the invariants. If
you only want to *use* the framework, read `USER-GUIDE.md`.

Help documentation; not loaded into the agent's context at runtime.

---

## 1. Design philosophy (the invariants — don't break these)

1. **Specification precedes implementation.** No code before requirements + design are approved.
2. **Gates are non-negotiable.** No phase advances automatically; the Orchestrator stops on a skip.
3. **Artifacts are the source of truth, not the conversation.** Every phase writes a file with a
   `status:` field; personas read prior artifacts from disk. This is what makes sessions resumable and
   keeps the context window lean — the single most important property.
4. **Right mechanism per responsibility.** See §3. The wrong mechanism is the most common way these
   systems rot (e.g. trying to enforce a deterministic rule with a "please remember" in a prompt).
5. **Lean runtime files.** Anything loaded into the agent's context (skills, `AGENTS.md`, `CLAUDE.md`,
   `process-constitution.md`, rules) is terse and high-signal. Verbosity there makes the next agent
   worse. (These two guides are the exception — humans read them, the agent never loads them.)
6. **§7 safety is absolute.** The Kafka topology rules (no blocking I/O / DB / sync calls in a
   processor, explicit state stores, documented repartitions, blue-green safety) are prescriptive and
   never relaxed by what a codebase happens to do.

---

## 2. The lifecycle and gates

```
[brownfield] sdd-codebase-to-design -> docs/design.md   (+ optional sdd-codebase-to-coding-standard -> AGENTS.md)
requirements -> design: /sdd-architect (create) <-> /sdd-architecture-review <-> /sdd-architect (fix) [manual]
   -> plan -> tasks -> HUMAN APPROVAL -> implement+self-review (/sdd-dev) -> /sdd-code-review -> merge approval -> deploy
```

| Gate | Passes when | Enforced by |
|---|---|---|
| requirements approved | acceptance criteria + mapping complete, human-approved | human + Orchestrator routing |
| design approved | no open Blocker AND every Major has an accepted-risk ADR (Minor/Nit may be deferred) | `/sdd-architecture-review` + human |
| plan accepted | plan + tasks + traceability complete | human |
| IMPLEMENTATION APPROVED | human runs `/sdd-approve` | `PreToolUse` hook + marker |
| code review approved | no open Blocker AND every Major fixed or human-signed-off in `code-review.md` (Minor/Nit may be deferred) | `/sdd-code-review` + human |
| tests passing | `./gradlew build` green, ordered ladder satisfied | `/sdd-dev` self-check (+ optional hook) |
| human merge approval | a human approves the merge after code review approved | human |

---

## 3. Mechanism selection — the decision framework (the "why")

Each failure mode in agentic coding has a mechanism that closes it. Pick by failure mode, not habit.

| Responsibility | Mechanism | Why this and not another |
|---|---|---|
| Persistent policy / coding rules | `AGENTS.md`, rules | Always-on, human+AI readable. Not a skill (no trigger) and not a hook (it's guidance, not a binary check). |
| A repeatable capability / persona | **skill** | Loads a role + checklist into the *main* context where shared, accumulating context is wanted (requirements, decisions). A subagent would isolate context you actually need shared. |
| Independent review | **subagent** (Task tool) | Runs in a *separate* context, so the reviewer doesn't inherit the implementer's reasoning — it reads only the diff. Read-only tools mean it can't "fix and move on." A skill can't provide either. |
| Deterministic, must-not-be-skipped check | **hook + script** | Fires automatically at a lifecycle event regardless of model discretion; `PreToolUse` exit code 2 blocks. A skill *decides* whether to run; a hook always runs. |
| Whole-repo extraction (brownfield) | **script** (`extract_evidence.py`) | Mechanical, cheap, runs outside the model's context so a large repo never floods the window. |
| Deep static/topology checks at release | CI / static-analysis MCP | Belongs in the pipeline, not the local agent loop. |

Rule of thumb (Superpowers): **automate mechanical constraints; reserve skills for judgment.** A
mechanism whose failure mode isn't present is unnecessary complexity — say so and remove it.

---

## 4. Component reference

### 4.1 Governance (repo root)
- **`AGENTS.md`** — coding standards, an **org-canonical** document (see §10): an `[ORG]` core (fixed,
  replaced on upgrade) plus a team-owned `[PROJECT]` section, every rule tagged `[HOOK]`/`[REVIEW]`/
  `[GUIDANCE]`, with a `version:` in frontmatter. The Kafka safety MUSTs are non-negotiable. Advisory to
  the model — enforced by hooks + the code reviewer.
- **`CLAUDE.md`** — thin pointer to `AGENTS.md` and `process-constitution.md`. Loaded every session;
  kept tiny on purpose.
- **`process-constitution.md`** — process governance (lifecycle, gates, mechanism map, review-loop
  rules). Separate from `AGENTS.md` because it's *workflow law*, not coding directives.
- **`knowledge/design-standard.md`** — the architecture-review rubric (what `/sdd-architecture-review`
  checks). Org-canonical, same `[ORG]`/`[PROJECT]` + `version:` shape (§10).
- **`knowledge/kafka-topology-rules.md`** — detail behind the Kafka safety MUSTs; **pure core / locked**
  (teams may append stricter rules only), `version:` stamped. Linked, not inlined, so it loads only when needed.
- **`knowledge/feedback-log.md`** — the standards feedback loop's queue (§11): bug post-mortems append
  findings; `/sdd-standards-update` actions them. Frontmatter `open:`/`actioned:` is the queue, body is the
  newest-on-top narrative.

### 4.2 Personas (`claude/skills/sdd*/SKILL.md`)
Each has a **trigger-only `description`** (says *when* to use it, never *how* — the "Description Trap":
if the description summarizes the process, the model follows the blurb and skips the body). The body is
the checklist: read input -> do work -> write artifact (`status:`) -> update `STATE.md`.

| Skill | Reads | Writes | Why a skill, not a subagent |
|---|---|---|---|
| `sdd` (Orchestrator) | `STATE.md` | routing, `STATE.md` | Pure routing in the main context; resume + gate guard |
| `sdd-analyst` | inputs / baseline | `requirements.md` | Collaborative clarify loop; wants shared context |
| `sdd-architect` | `requirements.md` / `design-review.md` | `docs/design.md`, `docs/adr/` | Create or fix design; collaborative, main context |
| `sdd-architecture-review` | `docs/design.md` diff, `design-standard.md` | `design-review.md` | Separate command; *dispatches* the reviewer subagent |
| `sdd-plan` | `docs/design.md` | `plan.md`, `tasks.md`, `traceability.md` | Decomposition needs the full design context |
| `sdd-dev` | `tasks.md` / `code-review.md` | code, `test-report.md` | Implement or fix; Level-1 self-review built in |
| `sdd-code-review` | code, `AGENTS.md`, `requirements.md`, `docs/design.md` | `code-review.md` | Separate command; *dispatches* the reviewer subagent (2 passes) |
| `sdd-bugfix` | bug report, code, `docs/design.md` | `bugs/<id>.md`, `feedback-log.md` | Full bug lifecycle in one skill; mode by `status:`; collaborative, main context (§11) |
| `sdd-standards-update` | `feedback-log.md`, standards, reviewer prompts | edits to standards / prompts | Maintainer tool; interviews the human, *appends* rules; canonical repo only (§11) |

### 4.3 Review commands (each dispatches one reviewer subagent)
Review is **its own command**, not a loop inside the author skill — `/sdd-architecture-review` and
`/sdd-code-review`. Each dispatches a **single** reviewer as a general-purpose Task (separate context,
comment-only); the prompt lives with the review command (single source of truth, no drift). Council of
reviewers is deferred. Reviewers never edit the artifact — the author skill's *fix mode* does.

- **`/sdd-architecture-review`** — reviews the `docs/design.md` branch diff against
  `knowledge/design-standard.md` (which points to `kafka-topology-rules.md` for §7). Writes `design-review.md`.
- **`/sdd-code-review`** — two ordered passes: spec-compliance (vs `requirements.md` acceptance criteria +
  `docs/design.md`) then code-quality (vs `AGENTS.md`, the single checklist). Writes `code-review.md`.
- **Three review levels (code):** L1 developer self-review (mechanical checklist in `/sdd-dev`, no
  artifact, backed by a green build) · L2 independent review (`/sdd-code-review`) · L3 human approval
  (ticks the gate = merge approval).

### 4.4 Researcher subagent (read-only investigation)
`/sdd-architect` dispatches a **researcher subagent** (prompt: `sdd-architect/researcher-prompt.md`)
when `docs/design.md`'s summary lacks the detail to safely modify an area — mainly on brownfield. Same
isolation pattern as the reviewers, but for *reading*: it reads the relevant existing classes in its own
context and returns a one-page digest (topics, keys, serdes, state stores, processor chain, refs),
keeping the volume out of the architect's window. Read-only; never edits.

### 4.4 Hooks + scripts
Hooks are registered in `claude/settings.json` (`hooks` -> event -> matcher -> command). Scripts are
pure bash (no package manager) except the Python extractor.

| File | Trigger | Does | Rationale / caveat |
|---|---|---|---|
| `check-approval.sh` | `PreToolUse` Write\|Edit | exit 2 (block) if editing `src/**/*.java` and no `.approved` marker | Makes "no code before approval" deterministic. Coarse (repo-wide); refine per-feature if needed. |
| `check-topology.sh` | `PostToolUse` Write\|Edit | warn (exit 1) on §7-forbidden constructs in processor code | Patterns reused from `extract_evidence.py`. Escalate to exit 2 to hard-block. |
| `new-feature.sh` | manual | scaffold `specs/<NNN-feature>/` + `STATE.md` | Deterministic numbering. |
| `approve.sh` | via `/sdd-approve` | write the approval marker | The human-only half of the approval gate. |
| `extract_evidence.py` | both brownfield skills | walk the repo -> `evidence-pack.md` | Pure Python stdlib; cross-platform; shared single source. |

### 4.5 Templates (`templates/`)
Blank forms with `status:` frontmatter and short inline guidance. Filled instances live in
`specs/<feature>/` — except `design.template.md`, which seeds the **canonical** `docs/design.md`.

### 4.6 Brownfield skills (`claude/skills/sdd-codebase-to-*`)
Split from one combined skill so they can run on **independent cadence** (the design baseline rarely
changes; coding standards refresh each sprint). Both call the shared `scripts/extract_evidence.py` and
reuse `evidence-pack.md` if present (run both back-to-back -> extract once).
- `sdd-codebase-to-design` -> `docs/design.md` (complete, coverage-gated, human-verified). Needed for
  brownfield.
- `sdd-codebase-to-coding-standard` -> `AGENTS.md` (prevalence-tagged, living refresh, §7 fixed).
  **Optional** — `AGENTS.md` already ships prescriptive.

### 4.7 Evals (`evals/`)
Framework self-tests so an enhancer can change skills/reviewers without silently breaking them
(Superpowers practice). `run-evals.sh` checks: skill descriptions stay trigger-only; the approval hook
blocks; the topology smell fires. `planted-violation/` is the load-bearing behavioral test — a known
§7 breach the code reviewer must flag at Blocker/Major. Run it after any reviewer-prompt change.

---

## 5. The state & handoff model

`STATE.md` (one per feature) is the heartbeat: `phase`, `gate`, per-artifact status, the gate ledger,
review-loop state, and `next`. **Handoff is file-based, not context-based**: each persona reads its
input artifact, checks the prior gate is ticked in `STATE.md` (refuses if not), does the work, writes
its output with a `status:`, updates `STATE.md`, and appends to `audit-log.md` on a review round. The
next persona needs nothing from the prior conversation. Subagent handoff: the dispatcher passes file
*paths* (the subagent starts fresh and reads them); the subagent returns a digest written to a file,
never raw output. Resume = `/sdd` reconstructs everything from `STATE.md` + files.

---

## 6. The review flow (manual, same shape for design and code)

1. The author skill self-reviews, then **stops** — review is a separate command.
2. `/sdd-architecture-review` or `/sdd-code-review` dispatches one reviewer (separate context,
   comment-only) which writes findings to `review-comments.template.md` with a severity each, returns a
   verdict, appends the round to `audit-log.md`. The reviewer also **stamps `standards:`** with the
   `version:` of the standard(s) it checked against; that version is recorded on the `STATE.md`
   gate-ledger line when the gate ticks, so every tick is reproducible against an exact standard (§10).
3. The author skill's **fix mode** resolves findings **collaboratively with the human** (grilling, not
   blind application).
4. The user **manually** re-runs the review command for another pass. No auto-loop. **Calibration:** only
   Blocker/Major affect approval; never force a minimum count (hallucinated findings — BMAD's lesson).

### Severity & deferral governance (both reviews)
- **Blocker** — never deferrable; gate stays red until resolved.
- **Major** — resolve, or accept as risk: design -> an **ADR**; code -> a **human sign-off** in
  `code-review.md`. (ADRs are architectural, so code uses a sign-off, not an ADR.)
- **Minor / Nit** — deferrable; recorded only in the review artifact, never in `STATE.md` (no point
  loading consciously-deferred items into context).
- No framework debt register; "fix later" -> the team's issue tracker. Gates tick when no open Blocker
  and every Major is resolved-or-accepted.

---

## 7. The canonical design model (why one `docs/design.md`)

Design is a single living document, not per-feature, because **in Kafka the topology is one
interconnected graph** — features share topics, state stores, and partitioning, and blue-green safety
is a whole-topology property. You can't safely design a topology change while looking at an isolated
per-feature doc. A feature edits `docs/design.md` on its branch: **the branch diff is the change, the
merge is the fold-in** — git provides the delta and the as-is/to-be boundary for free, with no separate
delta file and no manual fold-in step. Shard into `docs/design/` only when the file grows large
(BMAD's on-demand sharding) — don't pay the structure cost early. Trade-off accepted: this leans on
branch-per-feature; if you don't branch per feature, change the review unit from "the diff" to an
explicit section.

---

## 8. Extending the framework

- **Add a persona** -> new `claude/skills/sdd-<role>/SKILL.md`. Trigger-only description; body =
  read -> do -> write -> update-STATE. Add its artifact to the table in §4.2 and a gate row if it
  introduces one.
- **Add a gate** -> a row in `process-constitution.md` + a `STATE.md` ledger item. Deterministic ->
  hook/script; judgment -> checklist + review.
- **Change a reviewer** -> edit the prompt template, then run `evals/` — the planted-violation test
  must still flag the §7 breach at Blocker/Major.
- **Design stays canonical** — never add per-feature design files; a feature changes `docs/design.md`
  on its branch.
- **Keep runtime files lean** (invariant 5). Detail goes in these guides, not in skills/rules.
- **Verify Claude Code specifics** (hook/skill/subagent syntax) against the docs before relying on them
  — the catalog evolves: https://docs.anthropic.com/en/docs/claude-code/claude_code_docs_map.md

---

## 9. What we took from each framework (grounding)

- **BMAD** — traceability + validation loops; **document sharding** for context management; segregating
  ephemeral per-feature artifacts from long-term docs; the "don't force a minimum finding count" lesson.
- **Spec-Kit** — Constitution as living memory; numbered `specs/NNN/` per-feature folders; hierarchical
  detail (keep the main doc navigable, push detail to sub-files); specs as living, continuously refined.
- **Superpowers** — two-stage review (spec-compliance then code-quality) as **loops** capped at 3 with
  calibration; self-review before handoff; trigger-only skill descriptions (the Description Trap);
  dispatch a general-purpose Task with a prompt template (single source of truth); automate mechanical
  constraints, reserve skills for judgment; skill self-tests / planted-bug evals; file-size awareness.

---

## 10. The org-standard model (org-canonical standards)

The three standards — `AGENTS.md`, `knowledge/design-standard.md`, `knowledge/kafka-topology-rules.md` —
are designed to be **org-wide canonical artifacts**: shared across every team adopting the framework so
AI output stays consistent and bounded, rather than 12 teams drifting into 12 local dialects. They share
one structure.

### Why this exists
The goal is **enforceable**, org-consistent standards — *advisory text alone is not enforcement*. A
standard is only worth centralizing if something can actually check it; "deterministic across teams"
follows from everyone meeting the same enforceable floor, not from the document merely being shared.

### The three structural properties
- **`version:` frontmatter.** Each standard is versioned. Reviews stamp the version they checked against
  into the review artifact (`standards:`) and onto the `STATE.md` gate-ledger line — so every gate tick is
  reproducible against an exact standard version (an audit/compliance property). Teams pull standards
  deliberately, so different teams sit on different versions; the stamp makes *"which rules gated this?"*
  answerable months later.
- **`[ORG]` / `[PROJECT]` boundary.** `[ORG]` is org-canonical — owned centrally, replaced on upgrade,
  never edited locally. `[PROJECT]` is team-owned, survives upgrades, and may only **ratchet tighter**
  (add or strengthen a rule), never relax an `[ORG]` rule. The org sets the floor; teams may raise it.
  Safety rules (`kafka-topology-rules.md`) are **pure core, append-stricter-only** — a team may add a
  stricter rule, never an exception.
- **Per-rule enforcement tags.** Every binding rule declares how it's checked: `[HOOK]` (a script detects
  it deterministically), `[REVIEW]` (the reviewer verifies it against the diff), or `[HOOK][REVIEW]`
  (both). Rules that can't be enforced live under **Guidance (non-binding)** and never affect a gate. The
  tags double as the reviewer's worklist; an unenforceable rule cannot enter the binding core.

### Two calibration rules (learned applying the model to real content)
1. **Safety rules carry `[HOOK][REVIEW]`, not just `[HOOK]`.** The topology hook only *warns*, and the
   reviewer must still catch §7 breaches (the planted-violation eval depends on it). A pure `[HOOK]` tag
   would tell the reviewer to skip the most safety-critical rule.
2. **Tag granularity follows where enforcement varies** — per-rule when mixed (`AGENTS.md`), per-section
   when it clusters (`kafka-topology-rules.md`), once-per-doc when uniform (`design-standard.md`, which is
   entirely a `[REVIEW]` rubric).

### Deferred (not yet built)
- **Pull/upgrade mechanism** — manual today (re-run install). The intended safe path is an `upgrade.sh`
  that replaces only `[ORG]` content and never touches a team's `[PROJECT]` sections or runtime artifacts.
- **Change governance** — a `CODEOWNERS`-gated change on the canonical repo, with a mandatory `version:`
  bump and a changelog entry classified breaking-vs-additive (safety-rule changes: two approvers).
- **Brownfield reconciliation** — `sdd-codebase-to-coding-standard` still emits the pre-model `AGENTS.md`
  shape; it should be repurposed to write only the `[PROJECT]` section + a divergence report against the
  `[ORG]` floor, never the core.

---

## 11. The bug workflow and the standards feedback loop

A defect found *after* implementation (a failing unit test, a functional bug, or a non-functional miss)
doesn't re-enter the full feature lifecycle — it runs through **`/sdd-bugfix`**, and on close it feeds the
**standards feedback loop** so the same class of defect gets designed out org-wide.

### The bug lifecycle (`/sdd-bugfix`)
One skill drives the whole lifecycle; it detects the current step from the bug file's `status:` and does
only that step (same mode-detection pattern as `/sdd-architect` and `/sdd-dev`):

```
open → analysed → fix-proposed → implementing → fixed → verified → post-mortem → closed
```

Design choices and their rationale:
- **Skill-first, standalone file.** `/sdd-bugfix "..."` creates a top-level `bugs/<id>.md` (from
  `templates/bug.template.md`). Bugs live outside `specs/` because a defect can be cross-cutting and may
  not belong to one feature; the `feature:` field preserves traceability without reopening a feature's
  sealed `STATE.md`.
- **`type:`-driven interrogation** (unit / functional / nfr) — each surfaces different evidence (stack
  trace vs repro steps vs metric+threshold), so the questions differ.
- **Lighter gate.** No `/sdd-approve` and no hook change — the design is already approved and the fix is
  narrow. The human confirming the `## Fix approach` in chat *is* the gate; then `/sdd-dev` (fix mode)
  does the edit (which already unlocks `src/`).
- **Conditional doc update.** A doc-gap diagnostic asks whether `docs/design.md`/`requirements.md` already
  specified the correct behaviour. If yes → implementation bug, no doc change. If no → design gap, update
  the doc *before* the fix. Trivial fixes stay light; design-gap bugs don't get silently patched in code.
- **Inline review.** The independent reviewer (reusing `code-reviewer-prompt.md`) runs scoped to the
  changed files and writes its verdict into the bug file's `## Review` section — no separate artifact for a
  narrow fix; one file tells the whole story.
- **Mandatory post-mortem before close.** Every verified bug answers *why did this leak through every
  gate?* This is the feedback trigger, not optional.

### The feedback loop (`/sdd-bugfix` post-mortem → `/sdd-standards-update`)
The loop is deliberately **two-stage and human-gated**, to respect the `[ORG]` boundary (§10):

1. **Record (recommend-only).** The post-mortem classifies the systemic root cause — `missing-rule`,
   `reviewer-blind-spot`, or `process-gap` — and **appends** a timestamped finding to
   `knowledge/feedback-log.md` (status: open). `/sdd-bugfix` never edits a standard; recording is all it does.
2. **Action (maintainer, canonical repo only).** `/sdd-standards-update` reads open findings, **interviews
   the human** to confirm wording/target/tag, then **appends** a rule to a standard or a check to a
   reviewer/dev prompt, and flips the entry to `actioned`. The skill is installed on every project for
   convenience but is **maintainer-only by convention** — its in-skill guard warns that running it outside
   the canonical repo edits `[ORG]` content that the next upgrade overwrites. `setup.sh` seeds an empty
   local `knowledge/feedback-log.md` from `templates/feedback-log.template.md` so each team has its own queue.

Why this shape:
- **Two stages, not one.** A bug fix on a team checkout must not silently mutate an `[ORG]` standard — an
  upgrade would clobber it, and a standards change has org-wide blast radius. So the *consuming* side only
  records; the *governed* change happens upstream in the canonical repo where `[ORG]` is owned.
- **Additive only, minor bump.** New rules are appended, never modifying or removing existing ones, so
  every change is backward-compatible — hence always a **minor** `version:` bump (`1.0 → 1.1`), never major,
  and the document name never changes. This keeps the §10 version stamp truthful (a frozen version with a
  silently-growing ruleset would make the review stamp a lie) without the churn of major versioning.
- **Scope discipline.** The skill edits standards + review/dev prompts (the two highest-frequency leak
  causes: "no rule existed" and "a rule existed but the reviewer didn't check it"). `process-gap` findings
  are **recommended only** — process changes are structural and higher-risk, left for a deliberate human edit.

### Deferred
- A `[HOOK]`-tagged feedback addition still needs its detector wired into `scripts/check-topology.sh` (or a
  new script) by hand; `/sdd-standards-update` flags this as a follow-up rather than auto-editing hooks.
- Whether `/sdd` should surface open bugs in routing (today bugs are invoked directly, not via the
  Orchestrator).
