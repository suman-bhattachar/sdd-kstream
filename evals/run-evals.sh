#!/usr/bin/env bash
# Deterministic framework checks (no model needed). Behavioral evals run via `claude -p`.
set -uo pipefail; cd "$(dirname "$0")/.."; fail=0
echo "1. skill descriptions are trigger-only (no numbered process steps in 'description:')..."
for f in claude/skills/sdd*/SKILL.md; do
  desc=$(awk '/^description:/{p=1} p&&/^---/{p=0} p' "$f")
  echo "$desc" | grep -qE '^\s*[0-9]+\.' && { echo "  FAIL $f: process steps in description"; fail=1; }
done; [ $fail -eq 0 ] && echo "  ok"
echo "2. approval hook blocks src edits with no .approved marker..."
printf '{"tool_input":{"file_path":"src/main/java/Foo.java"}}' | bash scripts/check-approval.sh 2>/dev/null \
  && { echo "  FAIL: edit allowed without approval"; fail=1; } || echo "  ok (blocked)"
echo "3. topology smell check flags blocking I/O in a processor..."
tmp=$(mktemp --suffix=.java); printf 'class P implements Processor { JdbcTemplate t; void f(){ t.query(); } }' > "$tmp"
printf '{"tool_input":{"file_path":"%s"}}' "$tmp" | bash scripts/check-topology.sh 2>/dev/null \
  && { echo "  FAIL: smell not flagged"; fail=1; } || echo "  ok (flagged)"; rm -f "$tmp"
echo; [ $fail -eq 0 ] && echo "PASS" || echo "FAILURES ABOVE"; exit $fail
