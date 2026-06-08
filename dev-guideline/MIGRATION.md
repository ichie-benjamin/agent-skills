# Migrating from dev-guideline v1 to v2

## What changed

| v1 | v2 |
|---|---|
| `.ai/TASKS/` | `.agent/TASKS/` |
| `.ai/memory.md` | `.agent/MEMORY.md` |
| `.ai/credentials.json` | `.agent/credentials.json` |
| `.ai/data/` | `.agent/data/` |
| `.ai/.tmp/` | `.agent/.tmp/` |
| — | `.agent/PROGRESS.md` (new) |
| Task body — ad-hoc | Strict schema with embedded `Resume` block |
| No subcommands | `setup`, `preview`, `compact`, `new-task` |
| Inline rules in SKILL.md | Progressive disclosure via `references/` |

## Why `.agent/`

`.ai/` has become an overloaded convention (Cursor, Continue, several other tools
squat the name). `.agent/` is tool-agnostic, aligns with the emerging
`AGENTS.md` spec, and avoids collisions.

## How to migrate an existing project

From the project root:

```bash
python3 ~/.claude/skills/dev-guideline/scripts/setup.py --dry-run
```

This previews every move and frontmatter rewrite. Then for real:

```bash
python3 ~/.claude/skills/dev-guideline/scripts/setup.py
```

The script:
1. Creates `.agent/` tree
2. Moves every `.ai/TASKS/active/*.md` and `.ai/TASKS/completed/*.md` to the new tree
3. Normalizes task frontmatter to the v2 schema (adds missing keys, infers from filename and mtime)
4. Adds a `Resume` block to any task missing one
5. Merges `.ai/memory.md` into `.agent/MEMORY.md` with the new header (`last_updated`, `entries`)
6. Adds `.agent/.tmp/`, `.agent/credentials.json`, `.agent/data/` to `.gitignore`
7. Deletes the now-empty `.ai/` directory (with confirmation)

What the script does NOT do (the agent does after, with judgment):
- Seeding `PROGRESS.md` from git log
- Reviewing migrated MEMORY entries for stale facts
- Filling in empty `Resume` blocks (those get filled on next session resume)

## Manual fix-ups after migration

1. Open `.agent/MEMORY.md` — prune entries now codified in CLAUDE.md or the code itself
2. Draft `.agent/PROGRESS.md` from recent commits and open work
3. Optionally install the SessionStart hook so the skill fires automatically every session:
   ```bash
   bash ~/.claude/skills/dev-guideline/scripts/install-hook.sh
   ```
4. Run `/dev-guideline preview` to verify everything renders correctly

## Rollback

The script does not back up `.ai/` before moving (it relies on git). Always
have a clean git working tree before running, or use `--dry-run` first.

If you need to revert: `git checkout .` will restore both `.ai/` and `.agent/`
to the last committed state — assuming you had `.ai/` committed.
