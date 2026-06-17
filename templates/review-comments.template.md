---
artifact: review
review_type: code         # code | architecture
status: changes-requested # changes-requested -> approved
round: 1
reviewed: {{branch diff / artifact under review}}
---
# Review — {{reviewed}} (round {{round}})

**Verdict:** {{changes-requested | approved}}   ·   Blocker {{n}} · Major {{n}} · Minor {{n}} · Nit {{n}}

> Calibration: only Blocker/Major affect approval. Don't invent findings — zero findings -> approved is valid.

| ID | Severity | Location | Finding | Recommendation | Status |
|---|---|---|---|---|---|
| R{{round}}-01 | Blocker | {{file:line / §}} | {{what's wrong}} | {{fix}} | open |
| R{{round}}-02 | Major | {{...}} | {{...}} | {{...}} | open |

**Severity:** Blocker (correctness / §7 safety / spec mismatch) · Major (significant quality/design/test
gap) · Minor (improve) · Nit (style).

**Status values & deferral rules:**
- `open` — not yet addressed.
- `resolved` — fixed in the artifact/code.
- `deferred` — **Minor/Nit only**, with a one-line reason. (Recorded here only — not in STATE.md.)
- `accepted-risk` — **Major only.** Architecture review: record an **ADR** and reference it here. Code
  review: add a **human sign-off note** here (who + why). Never for a Blocker.

**Gate ticks when:** no open Blocker **and** every Major is resolved or accepted-risk. Minor/Nit may
remain deferred.
