---
artifact: traceability
status: complete
feature: 001-example-feature
---
# Traceability — example-feature

| Requirement | Design ref | Task(s) | Test(s) |
|---|---|---|---|
| R-1 aggregate totals | docs/design.md §Topology Inventory (customer-totals) | T-1, T-2 | TotalAggregatorTest (unit), TotalsTopologyTest (TopologyTestDriver) |
| R-2 emit running total | docs/design.md §Runtime view | T-2, T-3 | TotalsTopologyTest (TopologyTestDriver) |

Gate: every requirement has ≥1 task and ≥1 test; no orphan tasks. ✓
