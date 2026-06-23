#!/usr/bin/env bash
# Handoff eval — prove /sdd-plan produces a complete, traceable plan from the ARTIFACTS ALONE, in a
# fresh headless session (no conversation history). This is the executable form of the framework's core
# invariant: "artifacts are the source of truth; the conversation is disposable."
#
# It stages a throwaway project (fixture + the sdd-plan skill + templates), runs the skill cold via
# `claude -p`, and checks the output deterministically. Requires the Claude CLI; skips cleanly without it.
#
# Two cases:
#   POSITIVE — design gate ticked  -> plan/tasks/traceability are produced and every requirement is traced.
#   NEGATIVE — design gate unticked -> /sdd-plan REFUSES (no tasks.md), proving the gate guard reads files,
#              not the chat.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
# Neutral skill invocation — NOT an imperative to produce files, so the skill's own gate guard can refuse.
PROMPT='Run the planning step (/sdd-plan) for the active feature in specs/.'

if ! command -v claude >/dev/null 2>&1; then
  echo "  SKIP: 'claude' CLI not found (headless handoff eval needs 'claude -p')."
  exit 0
fi

POS="$(mktemp -d)"; NEG="$(mktemp -d)"; trap 'rm -rf "$POS" "$NEG"' EXIT
fail=0

stage () {  # $1 = dest project dir — fixture + only what /sdd-plan needs to run
  cp -r "$HERE/fixture/." "$1/"
  mkdir -p "$1/.claude/skills"
  cp -r "$REPO/claude/skills/sdd-plan" "$1/.claude/skills/"
  cp -r "$REPO/templates" "$1/templates"
}
run_plan () {  # $1 = project dir — run the skill cold (fresh session, files only)
  ( cd "$1" && claude -p "$PROMPT" --permission-mode acceptEdits >/dev/null 2>&1 ) || true
}

# ---- POSITIVE: design approved -> a traceable plan must appear ----
stage "$POS"; run_plan "$POS"
SPEC="$POS/specs/001-handoff"
for f in plan.md tasks.md traceability.md; do
  [ -s "$SPEC/$f" ] || { echo "  FAIL: $f not produced from artifacts alone"; fail=1; }
done
if [ -s "$SPEC/traceability.md" ] && [ -s "$SPEC/tasks.md" ]; then
  for rid in $(grep -oE '\bR-[0-9]+\b' "$SPEC/requirements.md" | sort -u); do
    grep -q "$rid" "$SPEC/traceability.md" || { echo "  FAIL: $rid missing from traceability.md"; fail=1; }
    grep -q "$rid" "$SPEC/tasks.md"         || { echo "  FAIL: $rid not covered by any task"; fail=1; }
  done
  grep -qiE 'design|topology|runtime|§|S[0-9]' "$SPEC/tasks.md" \
    || { echo "  FAIL: tasks.md cites no design ref (tasks must trace to the design)"; fail=1; }
fi

# ---- NEGATIVE: design gate unticked -> /sdd-plan must refuse ----
# Use a clean, unambiguous unapproved STATE (every "approved" signal off) so a produced plan can only
# mean the gate guard ignored STATE.md.
stage "$NEG"
cp "$HERE/state-design-unapproved.md" "$NEG/specs/001-handoff/STATE.md"
run_plan "$NEG"
[ -s "$NEG/specs/001-handoff/tasks.md" ] && {
  echo "  FAIL: /sdd-plan produced tasks with the design gate unticked (gate guard isn't reading STATE.md)"; fail=1; }

[ $fail -eq 0 ] && echo "  ok (plan produced + fully traceable from files; refused when the gate was unticked)"
exit $fail
