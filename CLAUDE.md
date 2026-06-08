# Custom Skills — canonical home

This directory is the single source of truth for Benny's custom AI skills.
Every skill lives here once and is symlinked into each AI tool's skills
directory. **Never edit a skill from inside a tool directory** — edit it here.

## Layout

```
/Users/benny/Documents/agents/skills/
├── CLAUDE.md            ← this file
├── sync-skills.sh       ← idempotent symlink installer
├── dev-guideline/       ← source of truth
├── queek-cofounder/
└── queek-premium-video/
```

Each subdirectory with a `SKILL.md` is treated as a skill by `sync-skills.sh`.

## AI tool targets

| Tool        | Skills dir            |
|-------------|------------------------|
| Claude Code | `~/.claude/skills/`    |
| Codex       | `~/.codex/skills/`     |
| Cursor      | `~/.cursor/skills/`    |

Each skill is symlinked into all three. To add another tool, append its
skills directory to the `TARGETS` array in `sync-skills.sh`.

## Day-to-day rules

1. **Add a new skill** → create `<name>/` here with a `SKILL.md`, then run
   `./sync-skills.sh`. The script creates symlinks in every tool.
2. **Edit an existing skill** → edit it here. Tools see changes immediately
   (symlinks resolve live; no sync needed).
3. **Rename a skill** → rename the dir here, then run `./sync-skills.sh --prune`
   to remove the old dangling symlinks and create new ones.
4. **Delete a skill** → `rm -rf <name>/` here, then `./sync-skills.sh --prune`.
5. **Onboarding a new machine** → clone this folder, run `./sync-skills.sh`,
   done.
6. **Never** `rm -rf` inside `~/.claude/skills/<skill>/` etc. — that would
   delete the source through the symlink. Always operate from this folder.

## Co-existence with non-custom skills

Other directories in each tool's skills folder are either:
- Skills from other source trees (e.g. `~/.agents/skills/<name>` — Benny's
  HyperFrames-related skills live there and are symlinked separately)
- Skills installed by the tool itself or via plugins (do not touch)
- Real directories that pre-date this convention — sync-skills.sh refuses to
  overwrite a non-symlink and logs `SKIP …`; resolve those manually

The script never touches anything it didn't create. Only symlinks pointing
back into this canonical folder are managed.

## sync-skills.sh

```
./sync-skills.sh             # sync all skills to all targets
./sync-skills.sh --dry-run   # show what would change, no writes
./sync-skills.sh --prune     # also remove dangling/renamed symlinks
```

The script is idempotent — re-running fixes drift without duplicating links.
Run it after any add/rename/delete here, or on a new machine.

## Conventions for skill authoring

- Every skill directory must contain `SKILL.md` with YAML frontmatter
  (`name`, `description`). Anything without `SKILL.md` is ignored by the sync.
- `name` in frontmatter must match the directory name.
- Keep `SKILL.md` under ~500 lines; push detail into `references/` files using
  progressive disclosure.
- Use `assets/` for static files the skill ships (templates, vendored libs,
  HTML/CSS for browser previews).
- Use `scripts/` for executable helpers — `chmod +x` and prefer Python 3
  stdlib so they run anywhere.
- Treat the skills folder as a real codebase: small, focused commits;
  meaningful skill descriptions; no half-finished drafts in the canonical
  home (use a branch or `WIP/` subfolder during work).

## Backups

When a skill is replaced (e.g. dev-guideline v1 → v2 on 2026-05-23), the old
version is backed up to `/tmp/<name>-v<n>-backup-<unix-ts>` before being
overwritten. macOS preserves `/tmp` for ~3 days; copy elsewhere if you want
it longer.
