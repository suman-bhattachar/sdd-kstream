---
version: 1.0
---
# Kafka Topology Rules (§7 safety — reference)

Detail behind the AGENTS.md §Kafka MUSTs. Linked from AGENTS.md; not loaded wholesale.

**Pure core — locked.** These are the non-negotiable safety invariants. A team may add a *stricter* rule
under [PROJECT] below, but **never** an exception or relaxation. Enforcement: the forbidden-construct
list is **[HOOK][REVIEW]** (`scripts/check-topology.sh` flags it and the reviewer checks it); the
design-level rules are **[REVIEW]** (architecture review).

<!-- ============================ [ORG] — canonical · do not edit ============================ -->
## [ORG]

### Forbidden inside a topology / processor — [HOOK][REVIEW]
Blocking I/O · direct DB access (`JdbcTemplate`, `MongoTemplate`) · synchronous external calls
(`RestTemplate`, `WebClient`, `FeignClient`, `.block()`) · hidden mutable shared state · undocumented
repartitions. Reason: these stall the single stream thread and risk data loss / duplicates. Move
external lookups to a `GlobalKTable`, a co-partitioned join, or an async pattern outside the topology.

### State stores — [REVIEW]
Declare and name explicitly; pick the store type deliberately (keyed, windowed, session). Document the
key and retention. State size is a design concern — note it in `design.md`.

### Repartitioning — [REVIEW]
Every repartition is documented in `design.md` (where and why). Implicit repartitions from re-keying
are a smell — make them intentional.

### Processing guarantee & idempotency — [REVIEW]
State the guarantee (`at_least_once` / `exactly_once_v2`). Where at-least-once can duplicate, make the
downstream logic idempotent.

### Blue-green topology evolution (zero state-corruption tolerance) — [REVIEW]
Changing keys, store names, partitions, or serdes can corrupt or strand state across a release. The
`design.md` blue-green section must state how the new topology coexists with / migrates from the
running one without duplicate processing or state loss. When unsure, leave `⚠️ HUMAN:` and ask.

<!-- ===================== [PROJECT] — team-owned · stricter additions only ===================== -->
## [PROJECT] Stricter additions only

Team-owned, survives upgrades. Add *stricter* safety rules here; **never** an exception or relaxation of
an [ORG] rule.
<!-- e.g. "Also forbid in-memory caches inside any processor." -->
