#!/usr/bin/env bash
# Scaffold a new feature folder under specs/ with a fresh STATE.md. Run from the project root.
set -euo pipefail
name="${1:?usage: new-feature.sh \"<feature name>\"}"
slug=$(printf '%s' "$name" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-')
n=$(printf '%03d' $(( $(ls -d specs/[0-9]* 2>/dev/null | wc -l) + 1 )))
dir="specs/${n}-${slug}"; mkdir -p "$dir/adr"
sed "s/{{NNN-name}}/${n}-${slug}/g; s/{{ISO-8601}}/$(date -u +%Y-%m-%dT%H:%MZ)/g" \
    templates/STATE.template.md > "$dir/STATE.md"
echo "Created $dir"
