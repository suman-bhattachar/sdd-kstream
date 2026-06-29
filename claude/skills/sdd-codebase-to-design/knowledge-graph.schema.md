# Knowledge-graph schema (Understand-Anything-compatible)

The `.understand-anything/knowledge-graph.json` produced by `scripts/build_knowledge_graph.py`
and refined by the `graph-enricher` subagent follows the Understand-Anything v1.0.0 graph
schema. Keeping to this schema means the same file drives the Understand-Anything dashboard
unchanged **if** the plugin is ever installed — but nothing here requires it.

## Top-level shape
```json
{
  "version": "1.0.0",
  "project": { "name", "languages": [], "frameworks": [], "description", "analyzedAt", "gitCommitHash" },
  "nodes":  [ /* see Node types */ ],
  "edges":  [ /* see Edge types */ ],
  "layers": [ { "id", "name", "description", "nodeIds": [] } ],
  "tour":   [ { "order", "title", "description", "nodeIds": [] } ]
}
```

## Node types & ID conventions
Every node has: `id`, `type`, `name`, `summary`, `tags` (3–5), `complexity`
(`simple`|`moderate`|`complex`). File-level nodes also carry `filePath`.

| Type | ID format | Used here for |
|---|---|---|
| `file` | `file:<rel-path>` | every `.java` file |
| `class` | `class:<rel-path>:<Name>` | top-level class / interface / enum / record |
| `config` | `config:<rel-path>` | `application.yml`/`.properties`, `pom.xml`, build files |
| `concept` | `concept:topic:<name>` / `concept:store:<name>` | **Kafka topics & state stores** (the Kafka-aware extension) |
| `function`, `module`, `document`, `service`, `table`, `endpoint`, `pipeline`, `schema`, `resource` | per Understand-Anything | available if needed; not emitted by the skeleton pass |

> The skeleton uses `concept:` for Kafka topics and state stores so the graph stays within the
> standard schema (no invented node types) while still being Kafka-aware. They are distinguished
> by ID prefix (`concept:topic:`, `concept:store:`) and tags (`kafka-topic`, `state-store`).

**File-level types** (must each belong to exactly one layer): `file`, `config`, `document`,
`service`, `pipeline`, `table`, `schema`, `resource`. `class`, `function`, `concept`, `module`
are not required to be in a layer.

## Edge types
Every edge has: `source`, `target`, `type`, `direction` (`forward`), `weight`. Emitted by the
skeleton: `contains` (1.0), `imports` (0.7), `subscribes` (0.8), `publishes` (0.8),
`writes_to` (0.6). The enricher may add: `calls` (0.8), `reads_from` (0.6), `tested_by` (0.5).

Full valid set (do not use others): `imports`, `exports`, `contains`, `inherits`, `implements`,
`calls`, `subscribes`, `publishes`, `middleware`, `reads_from`, `writes_to`, `transforms`,
`validates`, `depends_on`, `tested_by`, `configures`, `related`, `similar_to`, `deploys`,
`serves`, `provisions`, `triggers`, `migrates`, `documents`, `routes`, `defines_schema`.

## Validity rules (enforce before use)
- No duplicate node IDs; no self-edges; no duplicate `(source, target, type)` edges.
- Every edge `source`/`target` references a node that exists (drop dangling).
- Every file-level node appears in exactly one `layers[*].nodeIds`.
- Every `layers[*].nodeIds` / `tour[*].nodeIds` entry references an existing node.
