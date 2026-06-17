# /sdd-bugfix — detailed behaviour

This is the playbook the `sdd-bugfix` skill follows. The skill is the single interface for the whole bug
lifecycle; it detects the current step from the bug file's `status:` field and does only that step.

---

## Create mode (no bug file yet)

The user invoked `/sdd-bugfix "<description>"`. Allocate the next id (`BUG-001`, `BUG-002`, … from
`ls bugs/`). Determine the **type**, then interrogate — ask only what the description doesn't already
answer, one question at a time, no forced count.

### Type-specific interrogation
- **unit** — Which test fails, and on which assertion? Paste the failure/stack trace. Is the *test* wrong
  or the *code* wrong? Smallest input that reproduces it?
- **functional** — Exact repro steps. Expected behaviour vs actual. Which input/record triggers it? Is it
  deterministic or intermittent (ordering, timing, partition)?
- **nfr** — Which metric (latency / throughput / memory / lag)? Measured value vs threshold/SLO? How was
  it measured, under what load? Is it a regression (when did it last meet the bar) or a never-met target?

### Analysis + doc-gap check (the load-bearing diagnostic)
1. Get to the **root cause** of the defect — the code-level reason. Write it into `## Analysis`.
2. **Doc-gap check** — ask: *does the expected behaviour already appear in `docs/design.md` or
   `requirements.md`?*
   - **YES** → the design was right and the implementation diverged. No doc change. Note where it's
     specified in `## Doc-gap check`.
   - **NO** → the design/requirements had a gap. Update the relevant section *now* (before the fix), and
     record what was added. A topology/state/serde gap means editing `docs/design.md`; a missing behaviour
     contract means editing `requirements.md` acceptance criteria.

Write the file from `templates/bug.template.md`, set `status: analysed`, fill `feature:` (originating
feature id or `cross-cutting`), `component:`, `severity:`.

---

## Fix-proposal + fix (status: analysed → fix-proposed → implementing → fixed)

1. Write a concrete `## Fix approach` (what changes, which files, why it resolves the root cause, and any
   regression risk). Set `status: fix-proposed`.
2. **Ask the human to confirm the approach in chat. This confirmation is the gate** — there is no
   `/sdd-approve` for a bug. Do not edit `src/` before it.
3. On confirmation, hand to **`/sdd-dev` (fix mode)**: it edits code per `AGENTS.md`, writes/updates the
   test that now fails-then-passes, and runs `./gradlew build` green. Set `status: implementing` while it
   works, `status: fixed` when the build is green.

---

## Inline review (status: fixed)

Run the independent review — reuse the existing reviewer, but keep it inline (no separate artifact):

- Dispatch the **code-reviewer subagent** (general-purpose Task, separate context) with
  `claude/skills/sdd-code-review/code-reviewer-prompt.md` as its prompt, passing: the changed files, the
  bug file `bugs/<id>.md`, `knowledge/AGENTS.md`, and (if relevant) `requirements.md` / `docs/design.md`.
- **Override the output instruction:** the subagent writes its findings into the `## Review` section of
  `bugs/<id>.md` (verdict line + findings table), **not** a `specs/<feature>/code-review.md`. It still
  stamps `AGENTS.md v<version>` in that section.
- If changes-requested, loop back to `/sdd-dev` (fix mode); re-review. The review clears when there is no
  open Blocker and every Major is fixed or human-signed-off (Minor/Nit may defer).

---

## Verify (status: fixed → verified)

The human re-invokes `/sdd-bugfix` on the file. Ask one question: **has the failing test / scenario /
metric been confirmed to pass in the real environment?** On yes, set `status: verified` and write the
confirmation into `## Verification`. (A code-green build is necessary but not sufficient — verification is
the human's environmental confirmation, especially for functional/nfr bugs.)

---

## Post-mortem (mandatory, status: verified → closed)

Every verified bug gets a post-mortem before close — this is the feedback loop, not optional.

1. Answer in `## Post-mortem`: **why did this defect leak through every gate** (requirements → design →
   architecture review → implementation → self-review → code review)? Identify the *single gate that
   should have caught it* and why it didn't.
2. Classify the systemic root cause into one of:
   - **missing/weak rule** → a standard (`AGENTS.md`, `design-standard.md`, `kafka-topology-rules.md`)
     had no rule that would have flagged it.
   - **reviewer blind spot** → a rule existed but the reviewer/dev checklist didn't look for it
     (`code-reviewer-prompt.md`, `architecture-reviewer-prompt.md`, `sdd-dev` self-review).
   - **process gap** → a gate itself was missing (`process-constitution.md`). *Recommend only.*
   - **not preventable** → external/environment-specific; note it and close (no feedback entry needed).
3. For the first three, **append a timestamped finding to `knowledge/feedback-log.md`** (status: open)
   and add its id to the frontmatter `open:` list. Do **not** edit any standard or prompt here — recording
   is recommend-only; `/sdd-standards-update` (a canonical-repo maintainer tool) actions it later under
   human interview.
4. Set `status: closed`. Append a one-line round to the bug file. Done.

### feedback-log entry format
```
## <timestamp> — <BUG-id>-pm  (status: open)
**Bug:** <one line>.
**Why it leaked:** <which gate, why it missed it>.
**Category:** missing-rule | reviewer-blind-spot | process-gap.
**Proposed systemic fix:** <which doc/prompt, what rule/check to add>.
```
And add the id to frontmatter `open: [...]`.
