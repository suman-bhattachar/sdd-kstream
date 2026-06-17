---
feature: {{NNN-name}}
track: {{greenfield | brownfield}}
branch: {{feature branch}}
phase: requirements      # requirements → design → planning → approval → implementation → review → deploy
gate: draft
updated: {{ISO-8601}}
updated_by: {{/sdd-*}}
next: "{{the next action}}"
---
## Artifacts
| Artifact | Status | Owner | Updated |
|---|---|---|---|
| requirements.md | — | /sdd-analyst | — |
| docs/design.md (this feature's change, on branch) | — | /sdd-architect | — |
| plan.md | — | /sdd-plan | — |
| tasks.md | — | /sdd-plan | — |

## Gate ledger
- [ ] requirements approved
- [ ] design approved        (architecture review of the branch diff)
- [ ] plan accepted
- [ ] IMPLEMENTATION APPROVED      ← human-only (/sdd-approve)
- [ ] code review approved
- [ ] tests passing

## Review loops
- (none yet)

## Task progress
- (populated at implementation; mirrors tasks.md)
