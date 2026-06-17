# Install

No installer, no package manager. Clone and copy.

## Requirements
- Claude Code.
- Bash (the scripts). For the brownfield extractor (`scripts/extract_evidence.py`): **Python 3** (standard library
  only — no `pip`). Confirm `python3` (or `py`) is available if you'll use brownfield.

## Steps
```bash
git clone <this-repo> sdd-kstream
cd <your-project>
cp -r ../sdd-kstream/claude/.      .claude/          # skills, agents prompts, commands, settings.json
cp ../sdd-kstream/AGENTS.md ../sdd-kstream/CLAUDE.md ../sdd-kstream/process-constitution.md  .
cp -r ../sdd-kstream/templates ../sdd-kstream/scripts ../sdd-kstream/knowledge  .
chmod +x scripts/*.sh                                 # exec bit isn't preserved through a zip
```
Start Claude Code in the project and run `/sdd`.

## Notes
- Greenfield: `scripts/new-feature.sh "<name>"` then `/sdd-analyst`.
- Brownfield: run `sdd-codebase-to-design` once (generates `docs/design.md`) and `sdd-codebase-to-coding-standard`
  (generates `AGENTS.md`); verify the baseline, then proceed per-feature. Both share `scripts/extract_evidence.py`.
- `settings.json` hooks: verify the hook syntax against current Claude Code docs before relying on it
  (the event catalog evolves). The approval hook is a coarse repo-wide guard — refine to per-feature if needed.
