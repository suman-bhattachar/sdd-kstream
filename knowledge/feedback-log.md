---
last_actioned: null
actioned: []
open: []
---
# Feedback Log

The standards feedback loop. Bug post-mortems (`/sdd-bugfix`) **append** a timestamped finding here when a
defect leaked through a gate that should have caught it. `/sdd-standards-update` (a canonical-repo
maintainer tool) **actions** open findings — turning each into a new standard rule or reviewer check —
then flips the entry to `actioned`.

- **Frontmatter is the queue.** `open:` = findings recorded but not yet turned into a rule.
  `actioned:` = closed findings with the change they produced (`changed: [doc v1.0→1.1, ...]`).
- **Body is the narrative**, newest on top (matches `audit_log.md`). Recording is recommend-only —
  `/sdd-bugfix` never edits a standard; only `/sdd-standards-update` does, under human interview.

See `claude/skills/sdd-standards-update/standards-update-prompt.md` for the entry format and the
additive-only / minor-version-bump rules.

---

<!-- findings appended below, newest first -->
