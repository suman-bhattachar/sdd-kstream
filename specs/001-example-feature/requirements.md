---
artifact: requirements
status: approved
feature: 001-example-feature
---
# Requirements — example-feature (illustrative)

## Requirements
- **R-1** Aggregate per-customer payment totals from the payments stream.
- **R-2** Emit a running total to an output topic on each payment.

## Acceptance Criteria
- **R-1** — given payments keyed by customerId, when a payment arrives, then the stored total for that
  customer increases by the payment amount.
- **R-2** — every input payment produces exactly one output record with the updated total (idempotent
  on replay).
- Correctness: exactly-once (`exactly_once_v2`).

## Topic / State mapping
| Input topic(s) | Output topic(s) | Key | State touched |
|---|---|---|---|
| payments | customer-totals | customerId | totals-store (keyed) |

## Clarifications
- ⚠️ HUMAN: retention/window for totals-store? (assumed unbounded keyed store pending confirmation)
