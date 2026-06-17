# /sdd-standards-update — detailed behaviour

The playbook for turning post-mortem findings into durable standard/prompt changes. Maintainer tool, run
in the canonical `sdd-kstream` repo only (see SKILL.md for why).

---

## 1. Read the queue
Open `knowledge/feedback-log.md`. The frontmatter `open: [...]` is the work queue; each id has a
timestamped `## ...` body entry with **Why it leaked**, **Category**, and **Proposed systemic fix**.
If `open:` is empty, say so and stop.

## 2. Per finding — interview before editing
Take findings one at a time. The proposed fix in the log is a *starting point*, not a spec. Confirm with
the human:
- **Is the root cause real and general?** A rule added for one bug applies to every future build — make
  sure it's worth that weight, not an over-fit to one incident.
- **Which document?** Map the category to the target:
  - `missing-rule` (code) → `knowledge/AGENTS.md`
  - `missing-rule` (design/architecture) → `knowledge/design-standard.md`
  - `missing-rule` (Kafka safety/topology) → `knowledge/kafka-topology-rules.md`
  - `reviewer-blind-spot` (code) → `claude/skills/sdd-code-review/code-reviewer-prompt.md` and/or the
    `sdd-dev` Level-1 self-review checklist
  - `reviewer-blind-spot` (architecture) → `claude/skills/sdd-architecture-review/architecture-reviewer-prompt.md`
  - `process-gap` → **recommend only**; describe the gate change for `process-constitution.md` and leave
    it for a deliberate human edit. Do not edit the process file.
- **Exact wording + enforcement tag.** For a standard rule, agree the sentence and tag it:
  `[HOOK]` (a script can detect it — and you must say which script needs updating), `[REVIEW]` (the
  reviewer checks it), `[HOOK][REVIEW]` (safety, both), or `[GUIDANCE]` (non-binding, never gates).
  Safety-relevant additions go to `kafka-topology-rules.md` and are append-stricter-only.

## 3. Apply the edit (additive only)
- **Standard:** append the new rule to the correct `[ORG]` subsection (or a `[PROJECT]` block only if the
  human says it's team-local). **Never modify or delete existing text.** Then bump that document's
  `version:` by one minor (`1.0 → 1.1`). Name unchanged.
- **Reviewer/dev prompt:** append a concrete check line so the reviewer/dev will look for it next time.
  Prompts are not versioned — record the edit in the feedback-log entry instead.
- If the rule is tagged `[HOOK]`, note that `scripts/check-topology.sh` (or the relevant hook) must be
  extended to detect it; flag that as a follow-up if you can't make the script change cleanly here.

## 4. Close the loop in feedback-log.md
For each actioned finding:
- Move its id from frontmatter `open:` to `actioned:` with a `resolved:` date and a `changed:` list, e.g.
  `changed: [kafka-topology-rules.md v1.0→1.1, code-reviewer-prompt.md]`.
- Append a line to its body entry: `**→ Actioned <date>:** <what was added, where>.` and flip the entry
  header to `(status: actioned)`.
- Update `last_actioned:` in the frontmatter to now.

## 5. Record it
Add a dated entry to the framework `audit_log.md` summarising which standards/prompts changed and why
(the bug that drove it). That keeps the standard's evolution auditable beyond the feedback log.

---

### feedback-log.md shape (read + write this)
```markdown
---
last_actioned: <timestamp or null>
actioned:
  - id: <BUG-id>-pm
    resolved: <date>
    changed: [<doc> v<a>→<b>, <prompt>]
open: [<BUG-id>-pm, ...]
---

## <timestamp> — <BUG-id>-pm  (status: open | actioned)
**Bug:** ...
**Why it leaked:** ...
**Category:** missing-rule | reviewer-blind-spot | process-gap
**Proposed systemic fix:** ...
**→ Actioned <date>:** ...        # added when actioned
```
