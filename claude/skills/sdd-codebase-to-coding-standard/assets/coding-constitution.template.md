<!--
  CODING CONSTITUTION TEMPLATE — produced as AGENTS.md (the open standard agents auto-load).
  Rules: every rule carries MUST or SHOULD + a one-line rationale + (prevalence: __%) from the evidence.
  Write directives an agent can follow, NOT values. Conflicting conventions go to the Divergences appendix,
  not into the rules. The Toolchain section is AUTO-DERIVED each run — do not hand-edit it.
  Delete these comments in the final file. Keep it lean — high signal only.
-->

# AGENTS.md — {{System Name}} Coding Constitution

Rules for AI agents writing or modifying code in this repository. Read this before generating code and follow every **MUST**. Rules are advisory to agents; the critical ones are also enforced in hooks/CI.

## Project context
<!-- Only what an agent CANNOT infer from the code. One short paragraph. -->
> ⚠️ HUMAN: one or two sentences on the domain and any non-obvious constraint (e.g., "financial ledger — exactly-once and auditability are non-negotiable").

## Toolchain & Dependencies
<!-- AUTO-DERIVED from build files on each skill run. Source of truth = the build configuration. Do NOT hand-edit; re-run the skill to refresh. -->
**Last updated:** {{DATE}} · **Derived from:** {{build files}}

| Concern | Value | Source |
|---|---|---|
| Build tool | {{Gradle/Maven}} {{version}} | {{wrapper / pom}} |
| Java | {{version}} | {{build file}} |
| Spring Boot | {{version}} | {{build file}} |
| Kafka Streams | {{version}} | {{build file}} |
| Kafka clients | {{version}} | {{build file}} |
| {{other key library}} | {{version}} | {{source}} |

### Pinned constraints for code generation
> Keep this list short — only versions/APIs that actually change what you may write.
- Target **Java {{N}}** — {{e.g., records & sealed types OK; no preview features}}.
- **Kafka Streams {{x.y}}** — {{e.g., use the Processor API `process()`, not the deprecated `transform()`}}.
- {{build/runtime constraint}}

The full dependency tree lives in the build files — do not restate it here.

## Architecture & layering
- **MUST** keep domain/business logic free of framework code. _Rationale: testable without Spring/Kafka._ (prevalence: {{__%}})
- **MUST** respect the layer boundaries {{application → domain → infrastructure}}. (prevalence: {{__%}})

## Java conventions
- **MUST** use constructor injection; never field/`@Autowired` injection. _Rationale: immutability + testability._ (prevalence: {{__%}})
- **SHOULD** prefer immutable types / records for value objects. (prevalence: {{__%}})
- **MUST** handle errors explicitly; no silent catch-and-ignore. (prevalence: {{__%}})
- Naming: {{observed convention}}. (prevalence: {{__%}})

## Spring conventions
- **MUST** keep controllers and `@Configuration` thin; no business logic. (prevalence: {{__%}})
- **MUST** isolate Spring wiring from domain types. (prevalence: {{__%}})

## Kafka Streams rules
- **MUST** declare and manage state stores explicitly; name them per {{convention}}. (prevalence: {{__%}})
- **MUST** define serdes explicitly at each boundary; no reliance on defaults where types matter. (prevalence: {{__%}})
- **MUST** make keying/partitioning intentional and document any repartition. (prevalence: {{__%}})
- **MUST** target processing guarantee **{{at_least_once / exactly_once_v2}}** and write idempotent logic where required. (prevalence: {{__%}})
- **MUST NOT** perform blocking I/O, direct DB access, or synchronous external calls inside a topology/processor. _Rationale: stalls the stream thread; risks data loss._ (prevalence of violations: {{__}})

## Testing
- **MUST** cover topology logic with `TopologyTestDriver` before writing Spring integration tests. _Rationale: fast, deterministic verification of stream behavior._ (prevalence: {{__%}})
- **MUST NOT** let `@SpringBootTest` replace topology-level tests. (prevalence: {{__%}})

## Build / run / validate
<!-- The commands an agent should run before considering work done. -->
```bash
{{e.g., ./gradlew build}}     # compile + unit + topology tests
{{e.g., ./gradlew test}}
{{e.g., ./gradlew spotlessCheck}}  # style/lint, if present
```

## PR & commit conventions
- {{observed format, e.g., Conventional Commits}}. (prevalence: {{__%}})

## What to avoid
- {{anti-pattern observed in the code that new code must not copy}}.

---

## Appendix — Divergences (awaiting team ratification)
<!-- Conflicting conventions found in the codebase. These are NOT rules until a human picks one. -->
| Concern | Convention A (share) | Convention B (share) | Proposed rule | Ratified? |
|---|---|---|---|---|
| {{e.g., injection style}} | {{constructor — 84%}} | {{field — 16%}} | {{constructor injection}} | ☐ |

---

## Maintaining this file
Team-owned, living document. **Volatile sections (Toolchain & Dependencies, prevalence figures) are re-derived by re-running the `codebase-to-specs` skill — that is the periodic update.** Suggested cadence: each sprint and on any major dependency bump. Hand-written rules persist across re-runs; the skill shows a diff and any new divergences to ratify. Because agents may ignore advisory rules, enforce the critical **MUST**s with hooks/CI.
