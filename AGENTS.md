# AGENTS.md — SDD-KStream Coding Standards

Rules for any agent writing or modifying code in this repository. Read this before generating code
and follow every **MUST**. These rules are advisory to the model — the critical ones are enforced by
hooks and review (see `process-constitution.md`).

The §7 safety rules below are **non-negotiable**: they are prescriptive, not derived from how the
codebase happens to be written. On a brownfield repo, `sdd-codebase-to-coding-standard` may add project conventions
*around* them, but never demotes a MUST because the code violates it — that becomes tech debt.

## Spec compliance (the *what*)
- **MUST** satisfy every acceptance criterion in the feature's `requirements.md` and conform to
  `docs/design.md` (topology, state stores, repartitions). _This is the spec-compliance check; the rest
  of this file is the code-quality check. Both the developer's self-review and the independent reviewer
  use this one file as the checklist._

## Java
- **MUST** use constructor injection; never field/`@Autowired` injection. _Testable, immutable._
- **MUST** keep business logic free of framework types (no Spring/Kafka imports in domain). _Testable without a container._
- **MUST** handle errors explicitly; no silent catch-and-ignore.
- **SHOULD** prefer immutable types / records for value objects.
- **MUST** keep clear package boundaries: application → domain → infrastructure.

## Spring Boot
- **MUST** keep controllers and `@Configuration` thin — no business logic.
- **MUST** isolate Spring wiring from domain types.
- **MUST** keep domain logic runnable without a Spring context.

## Kafka Streams
- **MUST** declare and manage state stores explicitly; name them by convention.
- **MUST** define serdes explicitly at each boundary; no silent defaults where types matter.
- **MUST** make keying/partitioning intentional and **document every repartition**.
- **MUST** target the declared processing guarantee and write idempotent logic where required.
- **MUST** keep topology evolution blue-green safe — zero tolerance for state corruption or duplicate
  processing across releases.
- **MUST NOT** inside a topology/processor: blocking I/O · direct DB access (JdbcTemplate/MongoTemplate)
  · synchronous external calls (RestTemplate/WebClient/Feign/`.block()`) · hidden mutable shared state
  · undocumented repartitions. _These stall the stream thread and risk data loss._
  (Detail: `knowledge/kafka-topology-rules.md`.)

## Testing (ordered — enforce in this order)
1. Unit → 2. `TopologyTestDriver` → 3. Component → 4. Spring Boot integration → 5. E2E → 6. Regression
- **MUST** verify topology logic with `TopologyTestDriver` **before** any Spring integration test.
- **MUST NOT** let `@SpringBootTest` replace topology-level tests.

## Build / validate (Gradle only — no Maven)
```bash
./gradlew build          # compile + unit + topology tests; must be green before "done"
./gradlew spotlessApply  # if configured
```

## Pinned constraints
> Keep short — only versions/APIs that change what an agent may write.
- Target **Java {{N}}** — {{e.g. records & sealed types OK; no preview features}}.
- **Kafka Streams {{x.y}}** — {{e.g. Processor API `process()`, not deprecated `transform()`}}.

---
_Brownfield: this file is generated/refreshed by the `sdd-codebase-to-coding-standard` skill (toolchain +
prevalence auto-derived; divergences routed to its appendix; §7 MUSTs stay fixed). Greenfield: it ships
prescriptive as above._
