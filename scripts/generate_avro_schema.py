"""Generate the target topic's Avro value schema (.avsc) from specs/<feed>/mapping.md.

Design-phase tool, run by /sdd-architect AFTER the Schema settings block is confirmed
(record name, namespace, etc. — engineering-owned). Applies knowledge/mapping-rules.md
deterministically:
  - type table (business type -> Avro, incl. decimal/enum/logical date-time),
  - Required=N -> ["null", T] + default null,
  - arrays are never null: required, default [],
  - a non-array sub-record is nullable only when ALL its fields are optional,
  - enum name = PascalCase(leaf) + "Enum"; docs mandatory on every field.

Pure Python stdlib (reads the fenced JSON block emitted by convert_mapping.py).

Usage:  python scripts/generate_avro_schema.py <mapping.md> [output.avsc]
Exit codes: 0 = written, 1 = error (e.g. Schema settings incomplete — the design gate working).
"""

import json
import re
import sys
from pathlib import Path

AVRO_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def pascal(name):
    return "".join(w.capitalize() for w in name.split("_"))


def load_mapping(path):
    text = Path(path).read_text(encoding="utf-8")
    m = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
    if not m:
        raise SystemExit(f"ERROR: no fenced JSON block in {path} — regenerate it with convert_mapping.py")
    return json.loads(m.group(1))


def avro_type(row):
    t, target = row["target_type"], row["target"]
    simple = {"text": "string", "whole number": "int", "big whole number": "long",
              "yes/no": "boolean"}
    logical = {"date": ("int", "date"), "time": ("int", "time-millis"),
               "timestamp": ("long", "timestamp-millis")}
    if t in simple:
        return simple[t]
    if t in logical:
        base, lt = logical[t]
        return {"type": base, "logicalType": lt}
    if t == "decimal number":
        p, s = (int(x) for x in row["precision_scale"].split(","))
        return {"type": "bytes", "logicalType": "decimal", "precision": p, "scale": s}
    if t == "choice list":
        leaf = target.split(".")[-1].replace("[]", "")
        symbols = [s.strip() for s in row["allowed_values"].split(",") if s.strip()]
        return {"type": "enum", "name": pascal(leaf) + "Enum", "symbols": symbols}
    raise SystemExit(f"ERROR: {target}: unknown Target Type '{t}'")


def wrap_optional(field, t, required, doc):
    if required:
        return {"name": field, "type": t, "doc": doc}
    return {"name": field, "type": ["null", t], "default": None, "doc": doc}


def build_fields(rows, prefix):
    """Build the Avro fields for all rows under `prefix` (already stripped)."""
    fields, groups, order = [], {}, []
    for row in rows:
        rest = row["target"][len(prefix):]
        head = rest.split(".")[0]
        if head not in groups:
            order.append(head)
        groups.setdefault(head, []).append(row)

    for head in order:
        grp = groups[head]
        is_array = head.endswith("[]")
        leaf = head.replace("[]", "")
        children = [g for g in grp if g["target"][len(prefix):] != head]

        if not children:                       # a plain (or array-of-primitive) field
            row = grp[0]
            t = avro_type(row)
            if is_array:                       # arrays are never null (mapping-rules.md)
                fields.append({"name": leaf, "type": {"type": "array", "items": t},
                               "default": [], "doc": row["description"]})
            else:
                fields.append(wrap_optional(leaf, t, row["required"] == "Y",
                                            row["description"]))
        else:                                  # a nested block
            sub = {"type": "record", "name": pascal(leaf),
                   "fields": build_fields(children, prefix + head + ".")}
            doc = f"{leaf} block"
            if is_array:                       # arrays are never null
                fields.append({"name": leaf, "type": {"type": "array", "items": sub},
                               "default": [], "doc": doc})
            else:                              # nullable only if ALL children optional
                all_optional = all(c["required"] != "Y" for c in children)
                fields.append(wrap_optional(leaf, sub, not all_optional, doc))
    return fields


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    mapping_path = Path(argv[1])
    out = Path(argv[2]) if len(argv) > 2 else mapping_path.with_suffix(".avsc")

    data = load_mapping(mapping_path)
    settings = data.get("schema_settings", {})
    record_name = settings.get("SCHEMA — target record name", "")
    namespace = settings.get("SCHEMA — namespace", "")
    if not record_name or not namespace or not AVRO_NAME.match(record_name):
        print("ERROR: Schema settings incomplete (record name / namespace). This block is")
        print("engineering-owned — /sdd-architect confirms it at design time (mapping-rules.md).")
        return 1

    rows = data["fields"]
    missing_doc = [r["target"] for r in rows if not r.get("description")]
    if missing_doc:
        print(f"ERROR: fields without a description (docs are mandatory): {missing_doc}")
        return 1

    schema = {
        "type": "record",
        "name": record_name,
        "namespace": namespace,
        "doc": settings.get("SCHEMA — record description", "") or data["feed"].get("Feed name", ""),
        "fields": build_fields(rows, ""),
    }
    out.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"written: {out}")
    print("Reminder (feed revision): check compatibility against the previously registered")
    print(f"schema under the feed's declared mode ({settings.get('SCHEMA — compatibility mode', '?')}).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
