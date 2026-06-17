#!/usr/bin/env bash
# PreToolUse(Write|Edit): block edits to Java source until a feature is approved. Exit 2 = block.
# Coarse, repo-wide guard (no jq dependency). Refine to per-feature if you need finer scope.
input=$(cat)
fp=$(printf '%s' "$input" | grep -o '"file_path"[^,}]*' | sed 's/.*"file_path"[": ]*//; s/"//g')
case "$fp" in
  *src/main/*.java|*src/test/*.java)
    if ! ls specs/*/.approved >/dev/null 2>&1; then
      echo "Blocked: no approved feature. Run /sdd-approve before implementing." >&2
      exit 2
    fi ;;
esac
exit 0
