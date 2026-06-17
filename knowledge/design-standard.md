---
version: 1.0
---
# Design Standard (architecture-review rubric)

What `/sdd-architecture-review` checks `docs/design.md` (the feature's branch diff) against. **Every item
below is a `[REVIEW]` check** — this whole document is the reviewer's checklist, so the tag is stated
once here rather than repeated per line; there are no hook- or guidance-only items. The **safety** rules
are not repeated here — they live in `kafka-topology-rules.md`; this standard points to them so §7 stays
in one place.

Only the **[ORG]** section is org-canonical (do not edit; replaced on upgrade). A team may add *stricter*
checks under **[PROJECT]**, never relax an [ORG] one.

<!-- ============================ [ORG] — canonical · do not edit ============================ -->
## [ORG] Rubric

### Completeness
- Every requirement (R-x) in `requirements.md` is covered by a design element.
- Every topology has an Inventory row **and** a data-flow diagram.
- Every state store is named with its type and key; every external integration appears.

### Safety
- No §7-forbidden construct is designed in; repartitions are documented; processing guarantee stated;
  idempotency where required. **See `kafka-topology-rules.md` for the specifics.**

### Blue-green evolution
- A stated plan to deploy the change with zero state corruption / duplicate processing across releases.
- Serde / key / store-name compatibility across releases is addressed.

### Partitioning & scale
- Keying is intentional; partition implications considered.

### Traceability & clarity
- The design traces back to requirements; significant choices are captured as ADRs.
- A new engineer can understand the change from the doc alone.

### Severity (how the reviewer rates findings)
- **Blocker** — correctness / §7 safety / state-corruption risk. Never deferrable; keeps the gate red.
- **Major** — significant design risk. Resolve, or accept via an ADR (accepted risk).
- **Minor / Nit** — improvement / polish. Deferrable (recorded in `design-review.md`).

<!-- ===================== [PROJECT] — team-owned · stricter additions only ===================== -->
## [PROJECT] Additional Checks

Team-owned, survives upgrades. Add *stricter* review criteria here; never relax an [ORG] check.
<!-- e.g. "Every topic has a registered schema in the schema registry before merge." -->
