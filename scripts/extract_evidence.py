#!/usr/bin/env python3
"""
extract_evidence.py — build a compact "evidence pack" from a Java / Spring Boot / Kafka Streams repo.

Usage:
    python extract_evidence.py [repo-root] [output-file]
    Defaults: repo-root=".", output-file="evidence-pack.md"
    On Windows: use `python` (or `py`); the command is identical in PowerShell, CMD, Git Bash, or WSL.

Cross-platform: pure Python standard library. No bash, ripgrep, or Unix tools required. Writes UTF-8
directly (so it does not depend on shell redirection, which on PowerShell can emit UTF-16).

First-iteration heuristics: regex over source text. Expect some false positives — verify before
asserting anything in a generated document.
"""
import os
import re
import sys
from datetime import datetime, timezone

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = sys.argv[2] if len(sys.argv) > 2 else "evidence-pack.md"
EXCLUDE_DIRS = {"target", "build", ".git", ".idea", "node_modules", "out", "bin", ".gradle"}


def norm(path):
    return path.replace("\\", "/")


def iter_files(exts):
    exts = tuple(exts)
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn.endswith(exts):
                yield os.path.join(dirpath, fn)


def read_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    except OSError:
        return []


def rel(path):
    try:
        return norm(os.path.relpath(path, ROOT))
    except ValueError:
        return norm(path)


# Cache Java sources once (most patterns search them).
JAVA_FILES = list(iter_files((".java",)))
JAVA_CACHE = {p: read_lines(p) for p in JAVA_FILES}


def search(pattern, cache=None, files=None):
    rx = re.compile(pattern)
    items = cache.items() if cache is not None else ((p, read_lines(p)) for p in files)
    hits = []
    for path, lines in items:
        for i, line in enumerate(lines, 1):
            if rx.search(line):
                hits.append((rel(path), i, line.strip()))
    return hits


def count(pattern):
    return len(search(pattern, cache=JAVA_CACHE))


def sample(pattern, n=6):
    return search(pattern, cache=JAVA_CACHE)[:n]


def files_matching(pattern):
    """Complete, deduplicated list of Java files containing the pattern (the worklist)."""
    rx = re.compile(pattern)
    return sorted({rel(p) for p, lines in JAVA_CACHE.items() if any(rx.search(l) for l in lines)})


out = []
def w(s=""):
    out.append(s)
def h(title):
    w("\n## " + title)
def kv(k, v):
    w("- **{}:** {}".format(k, v))
def block(hits, indent="  "):
    for path, ln, text in hits:
        w("{}{}:{}: {}".format(indent, path, ln, text))


w("# Evidence Pack")
w("_Heuristic output from extract_evidence.py — verify before asserting. Generated: {}_".format(
    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")))
kv("Repo root", os.path.abspath(ROOT))

# ---- Build tool, modules, toolchain ----
h("Build tool & modules")
maven = list(iter_files(("pom.xml",)))
gradle = list(iter_files(("build.gradle", "build.gradle.kts")))
if maven:
    kv("Maven (pom.xml count)", len(maven))
if gradle:
    kv("Gradle (build.gradle count)", len(gradle))
w("Build files:")
for p in maven + gradle:
    w("  - " + rel(p))

for p in iter_files(("gradle-wrapper.properties",)):
    for line in read_lines(p):
        m = re.search(r"gradle-([0-9.]+)", line)
        if m:
            kv("Gradle wrapper version", "{} ({})".format(m.group(1), rel(p)))
            break
    break

for p in iter_files(("settings.gradle", "settings.gradle.kts")):
    inc = [l.strip() for l in read_lines(p) if "include" in l]
    if inc:
        w("settings.gradle includes ({}):".format(rel(p)))
        for l in inc[:30]:
            w("  " + l)
    break

h("Java / language version (best-effort)")
build_meta = list(iter_files((".gradle", ".kts", ".xml", ".toml", ".properties")))
block(search(
    r"sourceCompatibility|targetCompatibility|languageVersion|JavaLanguageVersion\.of|"
    r"<java\.version>|<maven\.compiler\.(source|target)>",
    files=build_meta)[:12])

h("Key dependencies & plugin versions (from build files)")
block(search(
    r"kafka-streams|kafka-clients|spring-boot|spring-kafka|org\.apache\.kafka|io\.confluent|avro",
    files=build_meta)[:30])
for p in iter_files(("libs.versions.toml",)):
    w("Gradle version catalog ({}):".format(rel(p)))
    for l in read_lines(p)[:60]:
        w("  " + l)
    break

# ---- Package layout ----
h("Package layout (main source dirs)")
pkg_dirs = sorted({rel(os.path.dirname(p)) for p in JAVA_FILES if "/src/main/java/" in norm(p)})
for d in pkg_dirs[:40]:
    w("  " + d)

# ---- Architecturally-significant files: COMPLETE worklist for the design doc ----
h("Architecturally-significant files — COMPLETE worklist (read ALL of these for the design doc)")
topo = files_matching(r"StreamsBuilder|Topology|KStream<|KTable<|GlobalKTable<|\.process\(|ProcessorSupplier")
w("Topology / processor classes ({}):".format(len(topo)))
for f in topo:
    w("  - " + f)
cfgs = files_matching(r"@Configuration|StreamsConfig|@EnableKafkaStreams|KafkaStreamsConfiguration|StreamsBuilderFactoryBean")
w("Streams / Spring configuration classes ({}):".format(len(cfgs)))
for f in cfgs:
    w("  - " + f)
integ = files_matching(r"JdbcTemplate|MongoTemplate|RestTemplate|WebClient|FeignClient|@FeignClient|DataSource|Repository<")
w("External integration points ({}):".format(len(integ)))
for f in integ:
    w("  - " + f)

# ---- Kafka Streams ----
h("Kafka Streams constructs")
kv("StreamsBuilder", count(r"StreamsBuilder"))
kv("KStream<>", count(r"KStream<"))
kv("KTable<>", count(r"KTable<"))
kv("GlobalKTable<>", count(r"GlobalKTable<"))
kv("Processor/transform usages",
   count(r"\.process\(|\.transform\(|ProcessorSupplier|implements Processor|ContextualProcessor"))
w("Topology samples:")
block(sample(r"StreamsBuilder|KStream<|KTable<", 10))

h("Topics (stream/to/through/repartition)")
block(sample(r"\.stream\(|\.to\(|\.through\(|\.repartition\(", 15))

h("State stores")
kv("Stores./StoreBuilder/addStateStore/Materialized",
   count(r"Stores\.|StoreBuilder|addStateStore|Materialized"))
block(sample(r"Stores\.|StoreBuilder|addStateStore|Materialized\.as", 8))

h("Serdes / serialization")
kv("Serde/Serdes usages", count(r"Serde<|Serdes\.|JsonSerde|SpecificAvroSerde|GenericAvroSerde"))
block(sample(r"Serde<|Serdes\.|JsonSerde|AvroSerde", 8))

h("Processing guarantee & Streams config")
cfg_files = list(iter_files((".java", ".yml", ".yaml", ".properties")))
block(search(
    r"processing\.guarantee|exactly_once|EXACTLY_ONCE|StreamsConfig|application\.id|num\.stream\.threads",
    files=cfg_files)[:15])

# ---- Spring ----
h("Spring stereotypes")
kv("@RestController", count(r"@RestController"))
kv("@Service", count(r"@Service"))
kv("@Component", count(r"@Component"))
kv("@Repository", count(r"@Repository"))
kv("@Configuration", count(r"@Configuration"))

h("Dependency injection style (prevalence signal)")
kv("@Autowired (field/setter)", count(r"@Autowired"))
kv("Stereotype classes (approx beans)",
   count(r"@Service|@Component|@Repository|@RestController|@Configuration"))
w("  Note: constructor injection is inferred where beans exist WITHOUT @Autowired. Verify a few.")
block(sample(r"@Autowired", 6))

# ---- Error handling ----
h("Error handling")
kv("try/catch blocks", count(r"catch\s*\("))
kv("Dead-letter / DLQ references", count(r"dead.?letter|DLQ|DLT"))
kv("Streams exception handlers",
   count(r"DeserializationExceptionHandler|ProductionExceptionHandler|"
         r"StreamsUncaughtExceptionHandler|setUncaughtExceptionHandler"))

# ---- Testing ----
h("Testing")
kv("TopologyTestDriver", count(r"TopologyTestDriver"))
kv("@SpringBootTest", count(r"@SpringBootTest"))
kv("@EmbeddedKafka", count(r"@EmbeddedKafka"))
kv("Test files", len([p for p in JAVA_FILES if "/src/test/" in norm(p)]))

# ---- Anti-pattern smells (heuristic) ----
h("Potential anti-patterns (heuristic — verify)")
kv("Blocking/external clients (JdbcTemplate/MongoTemplate/RestTemplate/WebClient/FeignClient/.block()/"
   "Thread.sleep/HttpURLConnection/OkHttp/DriverManager/CountDownLatch/CompletableFuture)",
   count(r"JdbcTemplate|MongoTemplate|RestTemplate|WebClient|FeignClient|\.block\(\)|Thread\.sleep|"
         r"HttpURLConnection|OkHttp|DriverManager|CountDownLatch|CompletableFuture"))
w("  If any appear INSIDE topology/processor classes, that is a forbidden blocking-I/O-in-stream smell. Locations:")
block(sample(r"JdbcTemplate|MongoTemplate|RestTemplate|WebClient|FeignClient|\.block\(\)|Thread\.sleep|"
             r"HttpURLConnection|OkHttp|DriverManager|CountDownLatch|CompletableFuture", 10))

w("")
w("_End of evidence pack._")

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
print("Wrote evidence pack to {} ({} Java files scanned).".format(OUT, len(JAVA_FILES)))
