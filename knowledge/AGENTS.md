---
version: 1.0
---
# AGENTS.md — SDD-KStream Coding Standards

Rules for any agent writing or modifying code in this repository. Read this before generating code
and follow every **MUST**.

Each binding rule is tagged by how it is enforced — advisory text alone is not enforcement:
- **[HOOK]** — a script detects it deterministically (blocks or warns regardless of model discretion).
- **[REVIEW]** — the independent reviewer checks it against the diff.
- A rule that can be enforced by both carries **[HOOK][REVIEW]** (defense-in-depth for safety).
- Rules that cannot be enforced live under **Guidance (non-binding)** and never affect a gate.

Only the **[ORG]** section is org-canonical — do not edit it locally; it is replaced on upgrade. The
**[PROJECT]** section is team-owned, survives upgrades, and may make a rule *stricter*, never looser.

<!-- ============================ [ORG] — canonical · do not edit ============================ -->
## [ORG] Coding Standards

The safety rules (§Kafka `MUST NOT`, blue-green evolution) are **non-negotiable**: prescriptive, not
derived from how the codebase happens to be written. On a brownfield repo,
`sdd-codebase-to-coding-standard` may add project conventions *around* them, but never demotes a MUST
because the code violates it — that becomes tech debt.

### Spec compliance (the *what*)
- **[REVIEW] MUST** satisfy every acceptance criterion in the feature's `requirements.md` and conform to
  `docs/design.md` (topology, state stores, repartitions). _This is the spec-compliance check; the rest
  of this section is the code-quality check. Both the developer's self-review and the independent
  reviewer use this one file as the checklist._

### Java
- **[REVIEW] MUST** use constructor injection; never field/`@Autowired` injection. _Testable, immutable._
- **[REVIEW] MUST** keep business logic free of framework types (no Spring/Kafka imports in domain). _Testable without a container._
- **[REVIEW] MUST** handle errors explicitly; no silent catch-and-ignore.
- **[REVIEW] MUST** keep clear package boundaries: application → domain → infrastructure.

### Spring Boot
- **[REVIEW] MUST** keep controllers and `@Configuration` thin — no business logic.
- **[REVIEW] MUST** isolate Spring wiring from domain types.
- **[REVIEW] MUST** keep domain logic runnable without a Spring context.

### Kafka Streams
- **[REVIEW] MUST** declare and manage state stores explicitly; name them by convention.
- **[REVIEW] MUST** define serdes explicitly at each boundary; no silent defaults where types matter.
- **[REVIEW] MUST** make keying/partitioning intentional and **document every repartition**.
- **[REVIEW] MUST** target the declared processing guarantee and write idempotent logic where required.
- **[REVIEW] MUST** keep topology evolution blue-green safe — zero tolerance for state corruption or
  duplicate processing across releases.
- **[HOOK][REVIEW] MUST NOT** inside a topology/processor: blocking I/O · direct DB access (JdbcTemplate/MongoTemplate)
  · synchronous external calls (RestTemplate/WebClient/Feign/`.block()`) · hidden mutable shared state
  · undocumented repartitions. _These stall the stream thread and risk data loss._
  (Detail: `knowledge/kafka-topology-rules.md`. `scripts/check-topology.sh` flags these; the reviewer also checks them.)

### Testing (ordered — enforce in this order)
1. Unit → 2. `TopologyTestDriver` → 3. Component → 4. Spring Boot integration → 5. E2E → 6. Regression
- **[REVIEW] MUST** verify topology logic with `TopologyTestDriver` **before** any Spring integration test.
- **[REVIEW] MUST NOT** let `@SpringBootTest` replace topology-level tests.

### Build / validate (Gradle only — no Maven)
```bash
./gradlew build          # compile + unit + topology tests; must be green before "done"
./gradlew spotlessApply  # if configured
```

### Guidance (non-binding)
_Advisory only — does not affect any gate._
- **SHOULD** prefer immutable types / records for value objects.

<!-- ===================== [PROJECT] — team-owned · survives upgrades ===================== -->
## [PROJECT] Conventions

Team-owned. Add local conventions and the toolchain here. May tighten an [ORG] rule, never relax it.

### Pinned constraints
> Keep short — only versions/APIs that change what an agent may write.
- Target **Java {{N}}** — {{e.g. records & sealed types OK; no preview features}}.
- **Kafka Streams {{x.y}}** — {{e.g. Processor API `process()`, not deprecated `transform()`}}.

<!-- Add team-specific conventions below (e.g. "MUST use Avro serdes", approved-library list). -->

---
_Brownfield: the [PROJECT] section is generated/refreshed by the `sdd-codebase-to-coding-standard` skill
(toolchain + prevalence auto-derived; divergences routed to its appendix). The [ORG] section ships
prescriptive and is org-canonical — §Kafka MUSTs stay fixed._
