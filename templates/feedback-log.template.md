---
last_actioned: null
actioned: []
open: []
---
# Feedback Log

The standards feedback loop. Bug post-mortems (`/sdd-bugfix`) **append** a timestamped finding here when a
defect leaked through a gate that should have caught it. Findings travel **upstream to the canonical
framework repo**, where a maintainer runs `/sdd-standards-update` to turn each into a new standard rule or
reviewer check, then flips the entry to `actioned`.

- **Frontmatter is the queue.** `open:` = findings recorded but not yet turned into a rule.
  `actioned:` = closed findings with the change they produced (`changed: [doc v1.0→1.1, ...]`).
- **Body is the narrative**, newest on top (matches `audit_log.md`). Recording is recommend-only —
  `/sdd-bugfix` never edits a standard.

See the finding format in `claude/skills/sdd-standards-update/standards-update-prompt.md`.

---

<!-- findings appended below, newest first -->
