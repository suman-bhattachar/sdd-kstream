---
artifact: plan
status: accepted
feature: 001-example-feature
---
# Plan — example-feature

## Sequence
1. Domain: `Payment`, `Total` value types (records) + the aggregation function (framework-free).
2. Topology: `groupByKey` → `aggregate` into `totals-store`; wire serdes.
3. Spring wiring: `StreamsBuilderFactoryBean` config; topic names from config.

## Risks
- Serde drift across releases → state corruption. Mitigation: pin Json serdes; covered by ADR-0001 + blue-green note.

## Test strategy
Ladder for this feature: unit (aggregation fn) → TopologyTestDriver (end-to-end topology). No external integration.
