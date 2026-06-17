---
artifact: adr
status: accepted
id: 0001
---
# ADR-0001 — Keyed state store over external lookup

**Context** — totals must be read/updated per payment inside the topology.
**Options** — (A) keyed RocksDB state store; (B) external DB lookup per record.
**Decision** — (A) keyed state store.
**Consequences** — no blocking I/O in the topology (AGENTS.md §Kafka); state grows with customer count;
rebuildable from the changelog. (B) rejected: a synchronous DB call inside the topology is forbidden.
