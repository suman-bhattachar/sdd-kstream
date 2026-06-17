# Framework Audit Log

Tracks changes to the **SDD-KStream framework itself** (skills, hooks, standards, templates, docs).
Distinct from the per-feature `specs/<feature>/audit-log.md`, which logs review rounds within a build.
Newest entries on top.

---

## 2026-06-18 — §7 topology hook widened + standards v1.1

Hardened the deterministic §7 detection ahead of a brownfield trial install, and folded the matching
clarification into the [ORG] standards.

### 1. Widened forbidden-construct detection
- **`scripts/check-topology.sh`:** extended the in-topology forbidden-construct regex beyond the original
  `JdbcTemplate|MongoTemplate|RestTemplate|WebClient|FeignClient|.block()` to also flag `Thread.sleep`,
  `HttpURLConnection`, `OkHttp`, `DriverManager`, `CountDownLatch`, and `CompletableFuture`.
- **Deliberately kept exit 1 (warn-only).** Not escalated to exit 2: a brownfield repo's existing
  processors will trip these, and a hard block would prevent editing legacy files. Plan: flip to exit 2
  once a file is known-clean / for all new topology code.
- **`scripts/extract_evidence.py`:** synced the anti-pattern grep (count + sample + label) to the same
  widened set, so the brownfield evidence pack's smell counts match what the hook enforces.

### 2. Standards alignment (additive, version bump)
- **`knowledge/kafka-topology-rules.md` and `knowledge/AGENTS.md`:** expanded the illustrative example
  lists in the §7 forbidden-construct rule to name the newly-detected constructs, and added an explicit
  "examples illustrative, not exhaustive — the rule is the category" note. **Both bumped `version:` 1.0 → 1.1.**
- The rule itself is unchanged — the prose categories ("blocking I/O", "synchronous external calls",
  "direct DB access") already covered these constructs; only the examples and the hook's coverage changed.

### Justification
The original list enumerated only ~6 class names while the §7 categories already forbid the added
constructs — the hook now detects more of what the standard already says. Widening is strictly safer
regardless of warn-vs-block. The standards edit is additive-only (no rule modified/removed), so it takes a
**minor** bump per the feedback-loop governance; historical v1.0 review stamps (e.g. the worked example)
remain truthful — they were reviewed against the narrower v1.0 surface. Found during the independent
framework review (recorded in `next-session-prompt.md`, 2026-06-18).

### Related / not yet done
- Optional: add a non-DB fixture (e.g. `Thread.sleep`) to `evals/run-evals.sh` to lock in the widened set
  (current fixture uses `JdbcTemplate`, which still matches).
- Pre-existing, unrelated bug noticed: `evals/planted-violation/README.md` points the reviewer at
  `claude/skills/sdd-dev/code-reviewer-prompt.md`; the prompt actually lives at
  `claude/skills/sdd-code-review/code-reviewer-prompt.md`.

---

## 2026-06-18 — Bug workflow + standards feedback loop

Added a defect lifecycle and the loop that turns escaped defects into durable standards changes.

### 1. `/sdd-bugfix` — bug lifecycle skill
- **New:** `claude/skills/sdd-bugfix/SKILL.md` (trigger + high-level flow) + `bugfix-prompt.md` (detailed
  playbook); `templates/bug.template.md`; top-level `bugs/` folder.
- **Behaviour:** skill-first (`/sdd-bugfix "..."` creates the file), `type:`-driven interrogation
  (unit/functional/nfr), conditional doc-gap update, lighter gate (human confirms fix approach in chat —
  no `/sdd-approve`), `/sdd-dev` fix mode for the edit, **inline** independent review (reuses
  `code-reviewer-prompt.md`, writes into the bug file's `## Review` — no separate artifact), human
  verification, then a **mandatory post-mortem**. Mode is detected from the file's `status:`
  (open → analysed → fix-proposed → implementing → fixed → verified → post-mortem → closed).
- **Standalone:** bugs never reopen a feature's `STATE.md`; the `feature:` field preserves traceability.

### 2. Standards feedback loop
- **New:** `knowledge/feedback-log.md` (frontmatter `open:`/`actioned:` queue + newest-on-top timestamped
  body) and `claude/skills/sdd-standards-update/SKILL.md` + `standards-update-prompt.md`.
- **Flow:** `/sdd-bugfix`'s post-mortem appends a finding (recommend-only — touches no standard).
  `/sdd-standards-update` (a **canonical-repo maintainer tool**) reads open findings, interviews, and
  **appends** a rule to a standard or a check to a reviewer/dev prompt, then flips the entry to actioned.
- **Rules:** additive only (never modify/remove an existing rule); each standard append bumps `version:`
  one **minor** (always backward-compatible, so no major bump); document names never change. Scope is
  standards + review/dev prompts; `process-gap` findings are recommended only, not auto-applied.
- **Justification:** closes the loop from "fix the symptom" to "fix the system that let it through." The
  `[ORG]` boundary is respected — standards evolve in one governed place (the canonical repo), not on
  consuming checkouts where an upgrade would clobber the edit. Keeping the version-bump-on-append (rather
  than freezing version) preserves the review version-stamp's meaning from the previous session.

### 3. Install/consistency wiring (same change set)
- `setup.sh` + `install/INSTALL.md`: seed an empty `knowledge/feedback-log.md` (from new
  `templates/feedback-log.template.md`) and a `bugs/` folder in the target. `sdd-standards-update` ships
  to every project (maintainer-only by convention — its in-skill guard is the protection, not exclusion).
- `README.md`: corrected the stale `AGENTS.md` location (now `knowledge/AGENTS.md`, a miss from the prior
  AGENTS.md move) and the layout/personas lists; added `/sdd-bugfix` + the feedback loop.
- `process-constitution.md`: documented the post-implementation defect path and the feedback loop.

### Deferred
- `[HOOK]`-tagged feedback additions still need the matching detector wired into `scripts/check-topology.sh`
  (or a new script) by hand — `/sdd-standards-update` flags this as a follow-up but does not auto-edit hooks.
- Whether `/sdd` should surface open bugs in its routing (currently bugs are invoked directly).

---

## Baseline — 2026-06-17 (commit `ede45e8`)

State of the framework before this session's changes:

- **Orchestrator (`/sdd`)** ran on the active session model with no per-skill model/effort scoping.
- **`/sdd-architect` create mode** edited `docs/design.md` directly from requirements; structured
  interrogation of Kafka failure modes happened only in *fix* mode (after a review found problems).
- **`install/INSTALL.md`** documented only the manual clone-and-copy steps; `setup.sh` existed but was
  undocumented.
- **Standards documents** (`AGENTS.md`, `knowledge/design-standard.md`, `knowledge/kafka-topology-rules.md`)
  were flat prescriptive files: no version identifier, no org-vs-team ownership boundary, and no per-rule
  declaration of how each rule is enforced.
- **Reviews** (`/sdd-code-review`, `/sdd-architecture-review`) did not record which version of a standard
  a given review was performed against — review artifacts and the `STATE.md` gate ledger carried no
  standard-version stamp.

---

## 2026-06-17T18:05Z — Efficiency, architect rigor, and the org-standard model

### 1. Orchestrator efficiency
- **Change:** added `model: haiku` + `effort: low` to `claude/skills/sdd/SKILL.md`.
- **Justification:** `/sdd` is pure routing (read `STATE.md`, report phase/gate/next) and the
  highest-frequency skill. Running it on the session's judgment-tier model was the dominant local-usage
  cost. The override reverts after the turn, so it cannot downgrade the judgment personas.
- **Open caveat:** confirm the VS Code extension honors per-skill `model`/`effort` (verified valid for the CLI).

### 2. Architect interrogates before designing
- **Change:** `claude/skills/sdd-architect/SKILL.md` create mode now interrogates the human about the
  failure modes in `knowledge/kafka-topology-rules.md` (state-store corruption, repartitions, serde drift,
  guarantee/idempotency, blue-green) *before* writing the design — calibrated, no forced question count.
- **Justification:** for a zero-data-loss context, catching a topology hazard during requirements
  interrogation is cheaper and safer than catching it in a later review round. Grounded in the existing
  rules file (single source of truth); only salvaged idea from an external upgrade proposal.

### 3. Install via `setup.sh`
- **Change:** `install/INSTALL.md` now leads with `setup.sh` (Quick install) and keeps the manual copy as
  an alternative.
- **Justification:** `setup.sh` performs the same copies deterministically. **Known risk recorded:**
  `setup.sh` uses `cp -rf`, which clobbers team-owned files (`AGENTS.md` `[PROJECT]` section,
  `settings.json` permissions) on a re-run — an upgrade-safe mode is deferred.

### 4. Org-canonical standards model
Reshaped the three standards documents (`AGENTS.md`, `knowledge/design-standard.md`,
`knowledge/kafka-topology-rules.md`) to a shared structure decided via a design interrogation:
- **`version:` frontmatter** on each — enables reproducibility/audit.
- **`[ORG]` / `[PROJECT]` boundary** — `[ORG]` is org-canonical (replaced on upgrade); `[PROJECT]` is
  team-owned and may make a rule *stricter, never looser*. Safety rules are pure-core, append-stricter-only.
- **Per-rule enforcement tags** — `[HOOK]` / `[REVIEW]` / `[GUIDANCE]`; `[GUIDANCE]` is barred from the
  binding core.
- **Justification:** the goal is *enforceable* standards across teams (advisory text alone is not
  enforcement). A canonical, versioned, enforcement-tagged standard is the prerequisite for consistent
  AI output org-wide without per-team drift.
- **Two refinements found while applying the model to real content:**
  1. Safety rules carry **`[HOOK][REVIEW]`** (both) — the topology hook only *warns*, and the reviewer
     must still catch §7 breaches (the `planted-violation` eval depends on it).
  2. **Tag granularity follows where enforcement varies** — per-rule when mixed (`AGENTS.md`), per-section
     when clustered (`kafka-topology-rules.md`), once-per-doc when uniform (`design-standard.md`).

### 5. Version stamping into review artifacts
- **Change:** `templates/review-comments.template.md` gained a `standards:` field; both reviewer prompts
  read the `version:` from the relevant standard doc and write it in; both review skills record it on the
  `STATE.md` gate-ledger line at tick; `STATE.template.md` shows the format; the worked-example artifacts
  were updated to demonstrate it.
- **Justification:** in a regulated context, "which rules was this code/design checked against?" must be
  answerable months later. Since teams pull standards deliberately, different teams sit on different
  versions — without a stamp, a gate tick is not reproducible.

### 6. Guides updated
- **Change:** documented the org-standard model in the guides — new `§10 The org-standard model` in
  `guides/WORKFLOW-AND-ARTIFACTS.md` (rationale, the three properties, the two calibration refinements,
  deferred items), updated `§4.1` and the `§6` review flow there, and added `§8 Coding & design standards
  (what you may edit)` + an install note to `guides/USER-GUIDE.md`.
- **Justification:** the framework's own invariant — detail/rationale belongs in the guides, not the lean
  runtime files. A future maintainer now has the narrative behind the `[ORG]`/`[HOOK][REVIEW]` markers.

### Deferred (recorded, not yet done)
- Upgrade/pull mechanism (manual for now); change governance (CODEOWNERS + classified changelog).
- `sdd-codebase-to-coding-standard` skill + `coding-constitution.template.md` still emit the pre-restructure
  AGENTS.md shape — reconcile to write the `[PROJECT]` section in the new shape.
- Optional: a line in `process-constitution.md` noting version stamping in the review flow.
- Optional eval: assert each standard doc carries `version:` + `[ORG]`/`[PROJECT]` markers.

### Verification
- `evals/run-evals.sh` green (skill descriptions trigger-only · approval hook blocks · topology smell fires).
- Code reviewer prompt confirmed to reference `AGENTS.md` generically — restructure is transparent to it.
