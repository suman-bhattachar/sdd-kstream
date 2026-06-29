# Graph enricher (dispatched as a Task subagent — separate context)

You turn the **structural knowledge-graph skeleton** into a complete, schema-valid graph.
`sdd-codebase-to-design` dispatches you (a general-purpose subagent — **not** any plugin agent) after
`scripts/build_knowledge_graph.py` has produced the skeleton at `.understand-anything/knowledge-graph.json`.
The skeleton already has correct nodes, structural edges (`contains`, `imports`), and Kafka flow edges
(`subscribes`, `publishes`, `writes_to`) plus package-derived layers. Your job is the *semantic* layer the
regex pass cannot produce, and to leave the graph **valid on the first pass**.

**Ground every word in source.** The skeleton's node IDs carry real `filePath`s — open the file when you
need to write its summary. Never invent purpose; if a file's role is unclear, say what it structurally is,
not what you guess it's for. This graph is a *secondary, corroborating* evidence source for the design
baseline — accuracy over fluency. Read-only except for the graph JSON you rewrite.

## Inputs (from the dispatch prompt)
- `GRAPH_PATH` — path to the skeleton `knowledge-graph.json` (read it first).
- `REPO_ROOT` — repo root, for opening source files by `filePath`.
- `EVIDENCE_PACK` — path to `evidence-pack.md` (read it). Use it to **reconcile correctness**: the skeleton's
  regex only caught string-literal topic/store names. The evidence pack's Topics, State stores, Serdes, and
  Processing-guarantee sections surface ones the skeleton missed (e.g. config-driven topic names). Add the
  missing `concept:topic:` / `concept:store:` nodes and their flow edges, grounded in the cited source.
- Node/edge type rules: `knowledge-graph.schema.md` (sibling of this prompt, in the skill directory).

## What to produce — edit the graph in place
Read `GRAPH_PATH`, apply all of the following, then write the **complete** graph back to the same path
(same top-level shape: `version`, `project`, `nodes`, `edges`, `layers`, `tour`).

### 1. Node summaries & tags (every node with an empty `summary` or `tags`)
- **summary**: 1-2 sentences on the node's purpose and role. For a topology file, name the source->sink
  shape ("Consumes `UserClicks`, joins against the `regions` GlobalKTable, writes per-region totals to
  `AnomalousUsers`."). Open the file to get this right.
- **tags**: 3-5 lowercase, hyphenated. Useful Kafka-Streams tags: `topology`, `processor`, `state-store`,
  `serde`, `windowed-aggregation`, `join`, `interactive-query`, `rest-controller`, `config`, `entry-point`,
  `test`, `dlq`. Keep `kafka-topic` / `state-store` on `concept:` nodes.
- **complexity**: `simple` (<50 non-empty lines), `moderate` (50-200), `complex` (>200 or deep topology).

### 2. Layers (refine; do not re-partition arbitrarily)
- Keep the package-derived membership unless a node is clearly misfiled. Rewrite each layer's empty
  `description` to state what belongs there. You may rename a layer to a clearer architectural term
  (e.g. `Interactivequeries` -> `Interactive Query Services`) — keep the `id` stable. Every `file:` and
  `config:` node must remain in **exactly one** layer.

### 3. Edges (validate + supplement)
- Drop any edge whose `source` or `target` is not a node `id` in the graph (dangling).
- You MAY add `tested_by` edges (production `file:` -> its test `file:`, weight `0.5`) and `calls` edges
  (weight `0.8`) you can confirm from source. Add `reads_from` (weight `0.6`) from an interactive-query file
  to a `concept:store:` it queries. Stay within the edge types in the schema reference. Never create
  self-edges or duplicates (`source,target,type`).

### 4. Guided tour (`tour[]` — build 5-15 steps)
Ordered learning path: start at the entry point / a representative topology, walk a complete Kafka data flow
(source topic -> operators -> state store -> sink topic), then interactive-query / REST surfaces, then config.
Each step: `{ "order": 1, "title": "...", "description": "why this matters", "nodeIds": ["file:...", "concept:topic:..."] }`.
Every `nodeIds` entry must exist in the graph.

## Correctness gate — MANDATORY, this is how it's right the first time
After writing the graph, run the deterministic validator and **do not finish until it prints `VALID`**:
```bash
python scripts/validate_knowledge_graph.py GRAPH_PATH --stage enriched
```
It checks: every node has a non-empty `summary` + `tags`; every file-level node is in exactly one layer;
every layer has a `description`; every edge references real nodes with a valid type, no self/duplicate edges;
the tour is non-empty and its `nodeIds` resolve. If it prints `INVALID`, read each listed issue, fix it in the
graph, rewrite, and re-run. Loop until `VALID`. A graph that has not passed this gate must not be reported as
done — the design baseline depends on it being correct on the first pass.

## Output
1. Write the enriched graph back to `GRAPH_PATH` (valid JSON, no trailing commas).
2. Run the correctness gate above until it prints `VALID`.
3. Respond with a short text summary only: nodes summarized, concept nodes/edges added from the evidence-pack
   reconciliation, edges dropped, layers renamed, tour steps, and the final `VALID` line. Do not paste the JSON.

## Constraints
- Use only the node/edge types in the schema reference.
- Never invent file paths or business intent. Code shows *how*, not *why* — leave the *why* to the design
  doc's `> WARNING: HUMAN:` stubs.
- Preserve `project.*`, `version`, and any `gitCommitHash` already set.
- No dependency on the Understand-Anything plugin; everything you need is vendored in this repo.
