---
artifact: requirements
status: draft        # draft → in-review → approved
feature: {{NNN-name}}
---
# Requirements — {{feature}}

## Requirements
- **R-1** {{requirement}}
- **R-2** {{requirement}}

## Acceptance Criteria  (the testable contract; reviews check code against this)
- **R-1** — given {{input}}, when {{event}}, then {{observable outcome}}.
- Correctness guarantees (e.g. exactly-once, ordering, idempotency): {{...}}
- Edge cases: {{...}}

## Topic / State mapping
| Input topic(s) | Output topic(s) | Key | State touched |
|---|---|---|---|
| {{in}} | {{out}} | {{key}} | {{store}} |

## Clarifications
- Q/A recorded here. Leave `⚠️ HUMAN:` where intent is unknown — do not guess.
