#!/usr/bin/env python3
"""
build_knowledge_graph.py — produce an Understand-Anything-compatible knowledge graph
from a Java / Spring Boot / Kafka Streams repo, with NO Node/pnpm/tree-sitter toolchain.

Usage:
    python build_knowledge_graph.py [repo-root] [output-file]
    Defaults: repo-root=".", output-file=".understand-anything/knowledge-graph.json"
    On Windows: use `python` (or `py`); identical in PowerShell, CMD, Git Bash, or WSL.

This is the "understand-lite" structural pass — the offline equivalent of the plugin's
tree-sitter core. It emits the deterministic skeleton (nodes + structural/Kafka edges +
package-derived layers). An LLM enricher (see assets/graph-enricher.agent.md) then fills
node summaries/tags, refines layer names, and adds the guided tour.

The output validates against the Understand-Anything schema (see
assets/knowledge-graph.schema.md), so if the plugin is ever installed, the same
.understand-anything/knowledge-graph.json drives its dashboard unchanged.

Cross-platform: pure Python standard library. Heuristic (regex over source) — expect
some false positives. Verify before asserting anything in a generated document.
"""
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(".understand-anything", "knowledge-graph.json")
EXCLUDE_DIRS = {"target", "build", ".git", ".idea", "node_modules", "out", "bin", ".gradle"}

CONFIG_EXTS = (".yml", ".yaml", ".properties", ".json", ".xml")


def norm(path):
    return path.replace("\\", "/")


def rel(path):
    try:
        return norm(os.path.relpath(path, ROOT))
    except ValueError:
        return norm(path)


def iter_files(exts):
    exts = tuple(exts)
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn.endswith(exts):
                yield os.path.join(dirpath, fn)


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------
JAVA_FILES = sorted(JAVA for JAVA in iter_files((".java",)))
JAVA_TEXT = {p: read_text(p) for p in JAVA_FILES}

PKG_RE = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.M)
TYPE_RE = re.compile(
    r"^\s*(?:public\s+|final\s+|abstract\s+|sealed\s+|non-sealed\s+)*"
    r"(?:class|interface|enum|record)\s+(\w+)", re.M)
IMPORT_RE = re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+)\s*;", re.M)

# Kafka Streams construct signals (file is a topology if any hit).
TOPOLOGY_RE = re.compile(
    r"StreamsBuilder|\bTopology\b|KStream<|KTable<|GlobalKTable<|\.process\(|ProcessorSupplier")

# Topic literals: source + sink operators with a string-literal arg.
TOPIC_SOURCE_RE = re.compile(r"\.(?:stream|table|globalTable)\s*\(\s*\"([^\"]+)\"")
TOPIC_SINK_RE = re.compile(r"\.(?:to|through|repartition)\s*\(\s*\"([^\"]+)\"")
# State store name literals.
STORE_RE = re.compile(r"(?:Materialized\.as|Stores\.\w+Store)\s*\(\s*\"([^\"]+)\"")

CFG_DIR_HINT = re.compile(r"/src/main/resources/|/src/test/resources/")

nodes = {}            # id -> node dict
edges = []            # list of edge dicts
edge_seen = set()     # (source, target, type)
fqn_to_file = {}      # fully-qualified type name -> file: node id
file_pkg = {}         # file: node id -> package
file_is_main = {}     # file: node id -> bool (src/main vs src/test)


def add_node(node):
    nodes[node["id"]] = node


def add_edge(source, target, etype, weight, direction="forward"):
    key = (source, target, etype)
    if source == target or key in edge_seen:
        return
    edge_seen.add(key)
    edges.append({"source": source, "target": target, "type": etype,
                  "direction": direction, "weight": weight})


# --- Pass 1: file + class + config nodes, build FQN map -------------------
for path, text in JAVA_TEXT.items():
    r = rel(path)
    fid = "file:" + r
    is_main = "/src/main/" in ("/" + r)
    is_test = "/src/test/" in ("/" + r) or r.endswith("Test.java") or "Test" in os.path.basename(r)
    pkg_m = PKG_RE.search(text)
    pkg = pkg_m.group(1) if pkg_m else ""
    file_pkg[fid] = pkg
    file_is_main[fid] = is_main and not is_test
    is_topology = bool(TOPOLOGY_RE.search(text))
    add_node({
        "id": fid,
        "type": "file",
        "name": os.path.basename(r),
        "filePath": r,
        "summary": "",          # enricher fills
        "tags": (["kafka-streams", "topology"] if is_topology else [])
                + (["test"] if is_test else []),
        "complexity": "simple",
        "_topology": is_topology,   # internal hint for enricher; harmless extra field
    })
    for tname in TYPE_RE.findall(text):
        cid = "class:{}:{}".format(r, tname)
        add_node({
            "id": cid, "type": "class", "name": tname, "filePath": r,
            "summary": "", "tags": [], "complexity": "simple",
        })
        add_edge(fid, cid, "contains", 1.0)
        if pkg:
            fqn_to_file[pkg + "." + tname] = fid

# config files (only those that look like app config, not every xml)
for path in iter_files(CONFIG_EXTS):
    r = rel(path)
    base = os.path.basename(r)
    in_resources = bool(CFG_DIR_HINT.search("/" + r))
    is_build = base in ("pom.xml", "build.gradle", "build.gradle.kts")
    if not (in_resources or is_build):
        continue
    cid = "config:" + r
    add_node({
        "id": cid, "type": "config", "name": base, "filePath": r,
        "summary": "", "tags": ["build-system"] if is_build else ["configuration"],
        "complexity": "simple",
    })

# --- Pass 2: imports (resolve to project files) --------------------------
for path, text in JAVA_TEXT.items():
    fid = "file:" + rel(path)
    for fqn in IMPORT_RE.findall(text):
        target = fqn_to_file.get(fqn)
        if target and target != fid:
            add_edge(fid, target, "imports", 0.7)

# --- Pass 3: Kafka topics & stores (concept nodes + flow edges) ----------
for path, text in JAVA_TEXT.items():
    fid = "file:" + rel(path)
    if not nodes[fid].get("_topology"):
        continue
    for topic in set(TOPIC_SOURCE_RE.findall(text)):
        tid = "concept:topic:" + topic
        add_node({"id": tid, "type": "concept", "name": topic,
                  "summary": "", "tags": ["kafka-topic", "input"], "complexity": "simple"})
        add_edge(fid, tid, "subscribes", 0.8)
    for topic in set(TOPIC_SINK_RE.findall(text)):
        tid = "concept:topic:" + topic
        if tid not in nodes:
            add_node({"id": tid, "type": "concept", "name": topic,
                      "summary": "", "tags": ["kafka-topic", "output"], "complexity": "simple"})
        add_edge(fid, tid, "publishes", 0.8)
    for store in set(STORE_RE.findall(text)):
        sid = "concept:store:" + store
        add_node({"id": sid, "type": "concept", "name": store,
                  "summary": "", "tags": ["state-store"], "complexity": "simple"})
        add_edge(fid, sid, "writes_to", 0.6)

# --- Layers: derive from package structure -------------------------------
# Common-prefix strip so layer names are the meaningful sub-package segment.
main_files = [fid for fid in nodes if fid.startswith("file:") and file_is_main.get(fid)]
pkgs = [file_pkg[f] for f in main_files if file_pkg.get(f)]


def common_prefix(parts_list):
    if not parts_list:
        return []
    out = []
    for tup in zip(*parts_list):
        if len(set(tup)) == 1:
            out.append(tup[0])
        else:
            break
    return out


base = common_prefix([p.split(".") for p in pkgs]) if pkgs else []
base_len = len(base)

layer_members = defaultdict(list)
for fid in nodes:
    node = nodes[fid]
    if node["type"] not in ("file", "config"):
        continue
    if node["type"] == "config":
        layer_members["Configuration"].append(fid)
        continue
    if not file_is_main.get(fid):
        layer_members["Tests & fixtures"].append(fid)
        continue
    pkg = file_pkg.get(fid, "")
    segs = pkg.split(".") if pkg else []
    tail = segs[base_len:] if len(segs) > base_len else []
    layer = tail[0].capitalize() if tail else "Core"
    layer_members[layer].append(fid)

layers = []
for name in sorted(layer_members):
    layers.append({
        "id": "layer:" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"),
        "name": name,
        "description": "",   # enricher fills
        "nodeIds": sorted(layer_members[name]),
    })

# --- Project metadata ----------------------------------------------------
artifact = os.path.basename(os.path.abspath(ROOT))
pom = read_text(os.path.join(ROOT, "pom.xml"))
m = re.search(r"<artifactId>([^<]+)</artifactId>", pom)
if m:
    artifact = m.group(1)
frameworks = []
all_build = pom + "".join(read_text(p) for p in iter_files(("build.gradle", "build.gradle.kts")))
if "kafka-streams" in all_build:
    frameworks.append("Kafka Streams")
if "spring-boot" in all_build or "spring-kafka" in all_build:
    frameworks.append("Spring Boot")

# Drop internal helper field before writing.
for n in nodes.values():
    n.pop("_topology", None)

graph = {
    "version": "1.0.0",
    "project": {
        "name": artifact,
        "languages": ["java"],
        "frameworks": frameworks,
        "description": "",   # enricher / human fills
        "analyzedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "gitCommitHash": "",
    },
    "nodes": list(nodes.values()),
    "edges": edges,
    "layers": layers,
    "tour": [],   # enricher fills
}

out_dir = os.path.dirname(OUT)
if out_dir and not os.path.isdir(out_dir):
    os.makedirs(out_dir, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(graph, fh, indent=2)
    fh.write("\n")

topics = sum(1 for n in nodes.values() if n["id"].startswith("concept:topic:"))
stores = sum(1 for n in nodes.values() if n["id"].startswith("concept:store:"))
print("Wrote knowledge graph to {}".format(OUT))
print("  {} Java files | {} nodes | {} edges | {} layers".format(
    len(JAVA_FILES), len(nodes), len(edges), len(layers)))
print("  Kafka: {} topic concepts, {} state-store concepts".format(topics, stores))
print("  Summaries/tags/tour are intentionally empty — run the graph-enricher subagent next.")
