# Kafka Topology Rules (reference)

Detail behind the AGENTS.md §Kafka MUSTs. Linked from AGENTS.md; not loaded wholesale.

## Forbidden inside a topology / processor
Blocking I/O · direct DB access (`JdbcTemplate`, `MongoTemplate`) · synchronous external calls
(`RestTemplate`, `WebClient`, `FeignClient`, `.block()`) · hidden mutable shared state · undocumented
repartitions. Reason: these stall the single stream thread and risk data loss / duplicates. Move
external lookups to a `GlobalKTable`, a co-partitioned join, or an async pattern outside the topology.

## State stores
Declare and name explicitly; pick the store type deliberately (keyed, windowed, session). Document the
key and retention. State size is a design concern — note it in `design.md`.

## Repartitioning
Every repartition is documented in `design.md` (where and why). Implicit repartitions from re-keying
are a smell — make them intentional.

## Processing guarantee & idempotency
State the guarantee (`at_least_once` / `exactly_once_v2`). Where at-least-once can duplicate, make the
downstream logic idempotent.

## Blue-green topology evolution (zero state-corruption tolerance)
Changing keys, store names, partitions, or serdes can corrupt or strand state across a release. The
`design.md` blue-green section must state how the new topology coexists with / migrates from the
running one without duplicate processing or state loss. When unsure, leave `⚠️ HUMAN:` and ask.
