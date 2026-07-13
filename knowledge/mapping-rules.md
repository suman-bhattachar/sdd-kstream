---
version: 1.0
---
# Mapping Rules (feed mapping workbook → Avro contract)

How a feed mapping workbook (`templates/mapping.template.xlsx`) becomes the target topic's Avro
value schema. **Enforcement:** `scripts/convert_mapping.py` and `scripts/generate_avro_schema.py`
apply these rules deterministically (script); the architecture reviewer verifies the generated
`.avsc` against them (**[REVIEW]**). A generated schema that deviates from a rule needs an ADR.

Ownership boundary (do not blur): the **analyst** owns business truth — field meaning, rules,
worked examples, logical types, optionality, allowed values. The **architect** owns the physical
contract — everything in this document plus the Schema settings block and schema evolution.

Only the **[ORG]** section is org-canonical (do not edit; replaced on upgrade). A team may add
*stricter* rules under **[PROJECT]**, never relax an [ORG] one.

<!-- ============================ [ORG] — canonical · do not edit ============================ -->
## [ORG] Rules

### Type table (business type → Avro)
| Workbook `Target Type` | Avro type |
|---|---|
| text | `string` |
| whole number | `int` |
| big whole number | `long` |
| decimal number | `bytes` + `logicalType: decimal` (precision/scale from `Precision,Scale`) |
| yes/no | `boolean` |
| date | `int` + `logicalType: date` |
| time | `int` + `logicalType: time-millis` |
| timestamp | `long` + `logicalType: timestamp-millis` (org default precision) |
| choice list | `enum` (symbols from `Allowed Values`) |

### Conventions
- **Optionality.** `Required = N` → union `["null", <type>]` with `default: null`. `Required = Y`
  → the bare type, no union.
- **Arrays are never null.** A repeating block (`items[]`) is a **required** field of type `array`
  with `default: []` — "no entries" is an empty array. (Consumers must not need a null-check *and*
  an empty-check on lists.)
- **Sub-records.** A non-array block (`customer.city`) whose fields are ALL optional is nullable:
  `["null", <record>]`, `default: null`. If any child is required, the block is required.
- **Enum naming.** Enum type name = PascalCase of the field's leaf name + `Enum`
  (`risk_band` → `RiskBandEnum`). Symbols must each be valid Avro names.
- **Naming.** Every path segment of `Target Field (path)` must match `[A-Za-z_][A-Za-z0-9_]*`.
  Sub-record type name = PascalCase of the segment.
- **Docs are mandatory.** `Field Description` → the field's `doc`; the Feed sheet's record
  description → the record's `doc`. A field without a doc fails generation.
- **The two defaults.** `On-Error Default` is runtime behaviour (USE_DEFAULT) and never enters the
  schema. `Schema Default` (rarely used) becomes the Avro field default and must be type-valid.
- **Key.** The message key is a plain string: the declared key field(s) joined by the declared
  separator. No key schema is registered.
- **Schema settings are design-phase.** Record name, namespace, record description, timestamp
  precision, and compatibility mode are confirmed by `/sdd-architect` — never by the analyst, and
  intake (`convert_mapping.py`) does not validate them.
- **Evolution.** On a feed revision, the newly generated schema must satisfy the feed's declared
  compatibility mode against the previously registered version **before** the design gate ticks
  (this is the serde-compatibility / blue-green rule applied to feeds).

<!-- ===================== [PROJECT] — team-owned · stricter additions only ===================== -->
## [PROJECT] Stricter additions only

Team-owned, survives upgrades. Add *stricter* rules here (e.g. "namespace must start with
`com.yourorg.`", "FULL compatibility for all feeds"); never relax an [ORG] rule.
