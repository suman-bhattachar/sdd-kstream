#!/usr/bin/env python3
"""
validate_knowledge_graph.py — deterministic correctness gate for the knowledge graph.

Usage:
    python validate_knowledge_graph.py [graph-file] [--stage skeleton|enriched]
    Defaults: graph-file=".understand-anything/knowledge-graph.json", --stage enriched

Exit code 0 = valid; non-zero = issues found (printed). Run it:
  - after build_knowledge_graph.py with `--stage skeleton` (structure only), and
  - after the graph-enricher subagent with `--stage enriched` (also requires every node to
    carry a non-empty summary + tags, every layer a description, and a non-empty tour).

The enricher MUST run this and fix all issues before its output is accepted — that is how the
graph is correct on the first pass rather than discovered wrong while authoring the design doc.

Pure Python standard library. No dependencies.
"""
import json
import os
import sys

VALID_NODE_TYPES = {
    "file", "function", "class", "module", "concept", "config", "document",
    "service", "table", "endpoint", "pipeline", "schema", "resource",
}
FILE_LEVEL_TYPES = {
    "file", "config", "document", "service", "pipeline", "table", "schema", "resource",
}
VALID_EDGE_TYPES = {
    "imports", "exports", "contains", "inherits", "implements", "calls", "subscribes",
    "publishes", "middleware", "reads_from", "writes_to", "transforms", "validates",
    "depends_on", "tested_by", "configures", "related", "similar_to", "deploys", "serves",
    "provisions", "triggers", "migrates", "documents", "routes", "defines_schema",
}
VALID_COMPLEXITY = {"simple", "moderate", "complex"}

args = [a for a in sys.argv[1:] if not a.startswith("--")]
GRAPH = args[0] if args else os.path.join(".understand-anything", "knowledge-graph.json")
stage = "enriched"
if "--stage" in sys.argv:
    i = sys.argv.index("--stage")
    if i + 1 < len(sys.argv):
        stage = sys.argv[i + 1]
ENRICHED = stage == "enriched"

issues = []


def err(msg):
    issues.append(msg)


try:
    with open(GRAPH, "r", encoding="utf-8") as fh:
        g = json.load(fh)
except (OSError, ValueError) as e:
    print("FATAL: cannot read/parse {}: {}".format(GRAPH, e))
    sys.exit(2)

for key in ("version", "project", "nodes", "edges", "layers", "tour"):
    if key not in g:
        err("missing top-level key: {}".format(key))

proj = g.get("project", {})
for key in ("name", "languages", "frameworks", "description", "analyzedAt", "gitCommitHash"):
    if key not in proj:
        err("project missing key: {}".format(key))

nodes = g.get("nodes", [])
edges = g.get("edges", [])
layers = g.get("layers", [])
tour = g.get("tour", [])

ids = set()
file_level_ids = set()
for i, n in enumerate(nodes):
    nid = n.get("id")
    if not nid:
        err("node[{}] missing id".format(i)); continue
    if nid in ids:
        err("duplicate node id: {}".format(nid))
    ids.add(nid)
    if n.get("type") not in VALID_NODE_TYPES:
        err("node {} invalid type: {}".format(nid, n.get("type")))
    if not n.get("name"):
        err("node {} missing name".format(nid))
    if n.get("complexity") not in VALID_COMPLEXITY:
        err("node {} invalid complexity: {}".format(nid, n.get("complexity")))
    if n.get("type") in FILE_LEVEL_TYPES:
        file_level_ids.add(nid)
        if not n.get("filePath"):
            err("file-level node {} missing filePath".format(nid))
    if ENRICHED:
        if not n.get("summary"):
            err("node {} missing summary (enriched stage)".format(nid))
        tags = n.get("tags")
        if not isinstance(tags, list) or not tags:
            err("node {} missing tags (enriched stage)".format(nid))

edge_seen = set()
for i, e in enumerate(edges):
    s, t, ty = e.get("source"), e.get("target"), e.get("type")
    if s not in ids:
        err("edge[{}] source not a node: {}".format(i, s))
    if t not in ids:
        err("edge[{}] target not a node: {}".format(i, t))
    if s == t:
        err("edge[{}] self-edge on {}".format(i, s))
    if ty not in VALID_EDGE_TYPES:
        err("edge[{}] invalid type: {}".format(i, ty))
    key = (s, t, ty)
    if key in edge_seen:
        err("duplicate edge: {}".format(key))
    edge_seen.add(key)
    if not isinstance(e.get("weight"), (int, float)):
        err("edge[{}] non-numeric weight".format(i))

assigned = {}
for layer in layers:
    lid = layer.get("id")
    if not lid:
        err("layer missing id")
    if ENRICHED and not layer.get("description"):
        err("layer {} missing description (enriched stage)".format(lid))
    for nid in layer.get("nodeIds", []):
        if nid not in ids:
            err("layer {} references missing node: {}".format(lid, nid))
        if nid in assigned:
            err("node {} in multiple layers ({}, {})".format(nid, assigned[nid], lid))
        assigned[nid] = lid

for nid in file_level_ids:
    if nid not in assigned:
        err("file-level node not in any layer: {}".format(nid))

if ENRICHED and not tour:
    err("tour is empty (enriched stage requires a guided tour)")
for i, step in enumerate(tour):
    if "order" not in step:
        err("tour[{}] missing order".format(i))
    if ENRICHED and not step.get("description"):
        err("tour[{}] missing description".format(i))
    for nid in step.get("nodeIds", []):
        if nid not in ids:
            err("tour[{}] references missing node: {}".format(i, nid))

if issues:
    print("INVALID ({} issue(s)) — stage={}:".format(len(issues), stage))
    for m in issues:
        print("  - " + m)
    sys.exit(1)

print("VALID — stage={} | {} nodes, {} edges, {} layers, {} tour steps".format(
    stage, len(nodes), len(edges), len(layers), len(tour)))
sys.exit(0)
