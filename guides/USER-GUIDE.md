# SDD-KStream — User Guide

For engineers **using** the framework to build Kafka Streams / Spring Boot services with Claude Code.
(If you want to *change the framework itself*, read `WORKFLOW-AND-ARTIFACTS.md` instead.)

This is help documentation — never loaded into the agent's context during a build. Read it once, keep
it for reference.

---

## 1. What you're working with

You build each feature by moving it through a fixed lifecycle. At every phase you invoke a **persona**
(a Claude Code skill) that reads the previous artifact from disk, writes the next, and updates one
progress file, `STATE.md`. You approve each gate. Nothing is implemented until requirements and design
are approved.

```
requirements -> design -> plan -> tasks -> HUMAN APPROVAL -> implement -> code review -> test -> deploy
```

Two ideas make it work:
- **Artifacts are the source of truth, not the chat.** The per-feature folder under `specs/` (plus the
  one canonical `docs/design.md`) holds all state, so any session resumes from files.
- **The design is one canonical document.** `docs/design.md` is the whole-system design. A feature
  edits it on its branch; the diff is the change. There is no per-feature design file.

---

## 2. Install (once per project)

No installer, no package manager. From your Gradle project root:

```bash
git clone <this-repo> sdd-kstream
cd sdd-kstream && ./setup.sh <your-project-path>
chmod +x <your-project-path>/scripts/*.sh            # exec bit isn't preserved through a zip
```
Or manually — see `install/INSTALL.md` for the equivalent copy-by-hand steps.

Do **not** copy `guides/` — those are framework help docs, not part of your service. `docs/design.md`
is created in *your* project at design time (greenfield) or by the baseline skill (brownfield).

Open Claude Code in the project, run `/sdd`, confirm it responds. Check `/skills`, `/hooks`, `/memory`
registered. Fill the two placeholders (Java version, Kafka Streams version) in the **`[PROJECT]`** section
of `AGENTS.md` — never edit the `[ORG]` section (see §8).

Windows: run from a **Git Bash** or **WSL** terminal so the scripts and hooks find `bash`.

---

## 3. The commands

| Command | When | Produces |
|---|---|---|
| `/sdd` | start / resume / "what's next" | routing (reads `STATE.md`) |
| `/sdd-analyst` | capture requirements | `specs/<f>/requirements.md` |
| `/sdd-architect` | create or fix the design | edits `docs/design.md` + `docs/adr/` |
| `/sdd-architecture-review` | independent design review | `design-review.md` |
| `/sdd-plan` | plan the work | `plan.md`, `tasks.md`, `traceability.md` |
| `/sdd-approve` | **human** gate | unlocks implementation |
| `/sdd-dev` | implement (+ self-review) or fix | code, `test-report.md` |
| `/sdd-code-review` | independent code review | `code-review.md` |
| `sdd-codebase-to-design` | brownfield baseline | `docs/design.md` |
| `sdd-codebase-to-coding-standard` | brownfield, **optional** | `AGENTS.md` |
| `/sdd-bugfix` | a defect found after implementation | `bugs/<id>.md` |
| `/sdd-standards-update` | **maintainer**, canonical repo only | edits to standards / reviewer prompts |

`/sdd` is the one to remember — it tells you which of the others to run next.

---

## 4. Greenfield — a full worked example

Building "per-customer payment totals." This walks the real artifacts in `specs/001-example-feature/`
and `docs/design.md` that ship with the framework.

### 4.1 Start
```bash
git checkout -b feat/001-payment-aggregator
scripts/new-feature.sh "payment aggregator"     # creates specs/001-payment-aggregator/ + STATE.md
/sdd                                            # confirms greenfield, points you to /sdd-analyst
```

### 4.2 Requirements — /sdd-analyst
Writes `requirements.md`, runs a clarify loop, you approve. The load-bearing section is the
**acceptance criteria** — the contract the reviewer later checks code against:
```
## Requirements
- R-1 Aggregate per-customer payment totals from the payments stream.
- R-2 Emit a running total to an output topic on each payment.

## Acceptance Criteria
- R-1 — given payments keyed by customerId, when a payment arrives, the stored total increases by the amount.
- R-2 — every input payment produces exactly one output record (idempotent on replay).
- Correctness: exactly-once (exactly_once_v2).
```
Mark it `approved` -> the requirements gate ticks in `STATE.md`.

### 4.3 Design — /sdd-architect, then /sdd-architecture-review (manual)
Run **`/sdd-architect`**; it asks *create from requirements* or *fix from review* — you pick create. It
edits `docs/design.md` (adds the topology + a data-flow diagram) and records
`docs/adr/0001-state-store-choice.md`. `docs/design.md` follows `templates/design.template.md`: **arc42**
with an *orientation* layer (non-normative) and a *binding* layer where every normative statement carries a
marker — `[CONTRACT]` / `[INVARIANT]` / `[ADR]` / `[TEST]`. Tagging each invariant with a `[TEST]` oracle is
what later lets `/sdd-plan` and the reviewer work from the marked elements.

Then run **`/sdd-architecture-review`** — a single reviewer subagent reviews the *branch diff* in a
separate context against `knowledge/design-standard.md` and writes `design-review.md`. Round 1 flags a
**Blocker** (serde compatibility across releases — a state-corruption risk). Run **`/sdd-architect`
again**; it sees the open review, switches to *fix mode*, and works through the finding **with you**.
You re-run `/sdd-architecture-review` when ready; round 2 is clean. Tick the design gate (it only ticks
with no open Blocker and every Major carrying an ADR). The rounds are in `audit-log.md`.

### 4.4 Plan & tasks — /sdd-plan
Writes `plan.md` (build sequence, the serde-drift risk, the test strategy), then `tasks.md` (T-1 domain
+ aggregator, T-2 topology + serdes, T-3 Spring config — each tagged with the requirement it satisfies),
then `traceability.md` (R-1/R-2 -> tasks -> tests). Accept the plan.

### 4.5 Approval — /sdd-approve
Review `plan.md`/`tasks.md` in **plan mode**, then run `/sdd-approve`. It writes the approval marker; a
`PreToolUse` hook had been blocking edits to `src/main/*.java` until now. Implementation is unlocked.

### 4.6 Implement, then review — /sdd-dev, then /sdd-code-review (three levels)
**`/sdd-dev`** (implement mode): per task, write the test first (unit + `TopologyTestDriver`), then the
code per `AGENTS.md`, run `./gradlew build` until green. It then does **Level-1 self-review** — a
mechanical checklist against `AGENTS.md` (the single coding checklist) — and marks the task ready.

**`/sdd-code-review`** (Level 2, independent): a reviewer subagent runs two passes — spec-compliance
(vs `requirements.md` + `docs/design.md`) then code-quality (vs `AGENTS.md`) — and writes
`code-review.md`. Round 1 catches a **Major** (field injection). Run **`/sdd-dev` again** → it switches
to *fix mode*, you resolve it, rebuild; re-run `/sdd-code-review`, round 2 approves.

**Level 3:** you tick "code review approved" — the merge approval. The gate ticks only with no open
Blocker and every Major fixed or signed off.

### 4.7 Done
`STATE.md` shows every gate ticked and `next: merge the feature branch`. Merging folds the
`docs/design.md` change into `main` — it becomes the new as-is for the next feature. See
`specs/001-example-feature/STATE.md` for the finished ledger and `audit-log.md` for the full review
history (2 design rounds, 2 code rounds).

---

## 5. Brownfield — walkthrough

For an existing repo you don't author the design — you reverse-engineer the baseline first, then
enhance against it.

### 5.1 Baseline (once)
```
"Generate the design baseline for this repo"     # sdd-codebase-to-design -> docs/design.md
```
Runs `python scripts/extract_evidence.py` (Python 3, no pip) to build `evidence-pack.md`, reads the
architecturally-significant files, and writes `docs/design.md` — the complete as-is: Topology
Inventory, C4 diagrams, arc42 sections, with `HUMAN` stubs where business intent can't be inferred.

It also builds a **knowledge graph** of the repo: `python scripts/build_knowledge_graph.py` writes
`.understand-anything/knowledge-graph.json` (dependency edges, architectural layers, and every
topic→topology flow), a general-purpose subagent enriches it (summaries, layers, a guided tour) while
reconciling topics/stores against the evidence pack, and `scripts/validate_knowledge_graph.py` gates it
to `VALID` before use. The graph corroborates the building-block/runtime/context sections — but the
Topology Inventory stays source-derived. All stdlib Python + a built-in subagent: **no Node, no plugin.**
(The JSON is also Understand-Anything-dashboard-compatible if you ever install that plugin — never required.)

**You must verify it** — a reverse-engineered baseline is derived; an engineer who knows the system
checks the topology flows before it's used. This is a gate.

Optionally, `"Generate AGENTS.md for this repo"` (`sdd-codebase-to-coding-standard`) auto-fills the
toolchain table and tags the repo's real conventions by prevalence. Skip it and hand-fill the version
placeholders if you prefer — `AGENTS.md` already ships with the §7 safety rules.

### 5.2 Enhance (per feature)
```bash
git checkout -b feat/add-fraud-filter
scripts/new-feature.sh "add fraud filter"
/sdd-analyst        # enhancement requirements (lighter — the baseline supplies system context)
/sdd-architect      # edit docs/design.md on the branch; the reviewer checks the diff against the baseline
/sdd-plan ; /sdd-approve ; /sdd-dev
```
Everything from §4.3 on is identical to greenfield. Two brownfield specifics: the design already
exists (so `/sdd-architect` updates it rather than creating it), and when the baseline summary isn't
enough to safely modify an area, `/sdd-architect` dispatches a **researcher subagent** — a read-only
subagent that reads the specific existing classes and returns a one-page digest (serdes, state-store
config, processor chain), keeping that heavy reading out of the design context. **`/sdd-dev` dispatches the
same researcher** during implementation when it needs code context below design granularity — so on a large
codebase the digest lands in the main window, not the raw code. Your change is then reviewed against the
existing topology, which is what keeps a topology change blue-green safe.

---

## 6. Resuming in a new session

```
/sdd
```
Reads `STATE.md`, reports feature / phase / gate / next, loads only the current artifacts, continues.
`/clear` mid-feature is safe — the feature folder is the memory. This is why long features don't
degrade: the window only ever holds the current step.

**`/clear` at each gate, not just on resume.** `/sdd` phrases the next action as `/clear, then /<skill>`
at every phase boundary, so each phase runs in a fresh, lean window. On a **large codebase** this is the
difference between a workable session and a context blow-up: don't run the whole feature in one chat — clear
at the gate and let the next skill reload from disk. (Heavy code reading is offloaded to the researcher
subagent, §5, so it never accumulates in your window either.)

---

## 7. Common issues

- **A `src/` edit is blocked.** Expected before approval — run `/sdd-approve`. (The approval hook is a
  coarse repo-wide guard.)
- **Hooks don't fire (Windows).** Start Claude Code from Git Bash / WSL so `bash` is on PATH; verify
  with `/hooks`. If they register but don't run, it's a shell/quoting issue, not the script.
- **A skill doesn't trigger.** Check it's at `.claude/skills/<name>/SKILL.md`. Skills also trigger from
  plain requests ("review the design"), not only the slash form.
- **The design doc is getting big.** Shard `docs/design.md` into `docs/design/` (a Topology Inventory
  index + per-topology files) and edit the relevant shard. On demand, not up front.

---

## 8. Coding & design standards (what you may edit)

Three documents define the rules the AI follows: `AGENTS.md` (coding), `knowledge/design-standard.md`
(the architecture-review rubric), and `knowledge/kafka-topology-rules.md` (the Kafka safety rules). They
are **org-canonical** — shared across teams so AI output stays consistent. Each has two parts:

- **`[ORG]`** — owned centrally; **don't edit it.** An upgrade replaces this section wholesale, so local
  edits would be lost (and would defeat the point of a shared standard).
- **`[PROJECT]`** — yours, and it survives upgrades. Put your toolchain (the Java / Kafka Streams version
  placeholders live here) and local conventions here. You may only make a rule **stricter, never looser** —
  e.g. *"MUST use Avro serdes"* is fine; relaxing a safety MUST is not. Safety rules accept stricter
  additions only, never exceptions.

Each standard carries a `version:`. When a review runs, it records which version it checked against — in
the review artifact (`standards:`) and on the `STATE.md` gate line — so you can always tell which rules
gated a given design or code change. If you adopt a newer standard from the org repo, re-run the relevant
review so the gate reflects the new version.

---

## 9. Bugs & the standards feedback loop

A bug found after implementation (failing unit test, functional defect, or a non-functional miss like
latency) runs through its own lightweight workflow — **`/sdd-bugfix`** — not the full feature lifecycle.

### Fixing a bug
```
/sdd-bugfix "duplicate payments double-count the running total"
```
The skill interrogates you (the questions depend on the bug `type:` — unit / functional / nfr), writes a
standalone `bugs/<id>.md`, and finds the root cause. It checks whether `docs/design.md` / `requirements.md`
already specified the correct behaviour — if not, that's a design gap and it updates the doc before
fixing. It proposes a **fix approach**; you confirm in chat (there's no `/sdd-approve` gate for a bug).
Then it hands to `/sdd-dev` (fix mode) to implement, runs an independent review inline (written into the
bug file, no separate artifact), and asks you to **verify** the fix in your environment.

Bugs are standalone — the originating feature's `STATE.md` is never reopened; the `feature:` field keeps
the link. `ls bugs/` shows every bug; `grep "feature: 001" bugs/*.md` finds all bugs tied to a feature.

### The feedback loop — why this matters
Before a bug closes, `/sdd-bugfix` runs a **mandatory post-mortem**: *why did this defect leak through
every gate?* If a gate should have caught it, the finding is appended to **`knowledge/feedback-log.md`**
(it does not change any standard — recording only).

Later, in the **canonical framework repo**, a maintainer runs **`/sdd-standards-update`**. It reads the
open findings, interviews them, and turns each into a durable fix: a new rule appended to a standard
(bumping its `version:` a minor notch) or a new check added to a reviewer/dev prompt. Changes are
**additive only** — rules are never modified or removed, so every change is backward-compatible. This is
how a single escaped defect ratchets the whole org's standards tighter so the same class of bug can't
recur. (`/sdd-standards-update` is installed everywhere but is a **maintainer tool** — run it only in the
canonical repo; its `[ORG]` edits belong upstream, and a local run would be lost on the next upgrade.
Carry findings upstream rather than editing standards on your own checkout.)
