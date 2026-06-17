# Audit Log — 001-example-feature

Append-only. One row per review round. Never edit prior rows.

| Round | Date | Artifact | Reviewer | Findings (B/M/m/n) | Verdict | Author action | Resulting status |
|---|---|---|---|---|---|---|---|
| 1 | 2026-06-16 | docs/design.md | architecture-reviewer | 1/0/1/0 | changes-requested | resolved R1-01 (serde compat), R1-02 (retention) | in-review |
| 2 | 2026-06-16 | docs/design.md | architecture-reviewer | 0/0/0/0 | approved | — | approved |
| 3 | 2026-06-16 | code (T-1..T-3) | code-reviewer | 0/1/0/1 | changes-requested | fixed Major (constructor injection) | in-review |
| 4 | 2026-06-16 | code (T-1..T-3) | code-reviewer | 0/0/0/1 | approved | Nit accepted | approved |
