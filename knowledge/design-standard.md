# Design Standard (architecture-review rubric)

What `/sdd-architecture-review` checks `docs/design.md` (the feature's branch diff) against. The
**safety** rules are not repeated here — they live in `kafka-topology-rules.md`; this standard points to
them so §7 stays in one place.

## Completeness
- Every requirement (R-x) in `requirements.md` is covered by a design element.
- Every topology has an Inventory row **and** a data-flow diagram.
- Every state store is named with its type and key; every external integration appears.

## Safety
- No §7-forbidden construct is designed in; repartitions are documented; processing guarantee stated;
  idempotency where required. **See `kafka-topology-rules.md` for the specifics.**

## Blue-green evolution
- A stated plan to deploy the change with zero state corruption / duplicate processing across releases.
- Serde / key / store-name compatibility across releases is addressed.

## Partitioning & scale
- Keying is intentional; partition implications considered.

## Traceability & clarity
- The design traces back to requirements; significant choices are captured as ADRs.
- A new engineer can understand the change from the doc alone.

## Severity (how the reviewer rates findings)
- **Blocker** — correctness / §7 safety / state-corruption risk. Never deferrable; keeps the gate red.
- **Major** — significant design risk. Resolve, or accept via an ADR (accepted risk).
- **Minor / Nit** — improvement / polish. Deferrable (recorded in `design-review.md`).
