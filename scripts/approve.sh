#!/usr/bin/env bash
# Human approval marker (called by /sdd-approve). Unlocks implementation for one feature.
set -euo pipefail
feat="${1:?usage: approve.sh <NNN-feature>}"; dir="specs/${feat}"
[ -d "$dir" ] || { echo "no such feature: $dir" >&2; exit 1; }
touch "$dir/.approved"; echo "Approved: $dir (implementation unlocked)."
