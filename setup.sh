#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-}"

if [[ -z "$TARGET_DIR" ]]; then
  echo "Usage: $0 <target_directory>"
  exit 1
fi

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Target directory does not exist: $TARGET_DIR"
  exit 1
fi

echo "Installing StreamFoundry framework into: $TARGET_DIR"

mkdir -p "$TARGET_DIR/.claude"

# Using cp -rf for recursive and forced copying
cp -rf templates "$TARGET_DIR/"
cp -rf scripts "$TARGET_DIR/"
cp -rf knowledge "$TARGET_DIR/"
cp -rf claude/. "$TARGET_DIR/.claude/"
cp -rf AGENTS.md CLAUDE.md process-constitution.md "$TARGET_DIR/"

chmod +x "$TARGET_DIR"/scripts/*.sh

echo "✓ Installation complete"
