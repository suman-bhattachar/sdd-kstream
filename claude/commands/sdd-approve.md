---
description: Human-only gate — approve the plan and unlock implementation.
disable-model-invocation: true
---

# /sdd-approve

The implementation gate. A human runs this after reviewing `plan.md` and `tasks.md` (use plan mode).

Steps:
1. Confirm `plan.md` is `accepted` and `tasks.md` is generated.
2. Run `scripts/approve.sh <feature>` to write the approval marker (`specs/<feature>/.approved`) and
   tick `IMPLEMENTATION APPROVED` in `STATE.md`.
3. Tell the user implementation is unlocked: `/sdd-dev`.

Never invoke this on the model's behalf — it exists to require a human decision.
