# Setup — `/dev-guideline setup`

A single command that detects project state and does the right thing: initialize
`.agent/` from scratch, migrate from legacy `.ai/`, or repair an existing setup.

## Detection logic

Run from the project root. The script `scripts/setup.py` detects state:

| State on disk | Mode | Action |
|---|---|---|
| `.ai/TASKS/` exists, no `.agent/` | `migrate` | Move and convert to new schema |
| Neither `.ai/` nor `.agent/` | `bootstrap` | Scaffold `.agent/` and seed MEMORY/PROGRESS from project knowledge |
| `.agent/` exists | `repair` | Verify structure, lint, report drift |
| Both `.ai/` and `.agent/` exist | `migrate --merge` | Move any newer `.ai/` tasks into `.agent/`, prompt user before deleting `.ai/` |

## Invocation

```
python ~/.claude/skills/dev-guideline/scripts/setup.py            # auto-detect
python ~/.claude/skills/dev-guideline/scripts/setup.py --dry-run  # show plan, no changes
python ~/.claude/skills/dev-guideline/scripts/setup.py --migrate  # force migrate
python ~/.claude/skills/dev-guideline/scripts/setup.py --bootstrap
python ~/.claude/skills/dev-guideline/scripts/setup.py --repair
```

Always run with `--dry-run` first when the user is unsure. The script prints a
plan and asks for confirmation before any destructive move.

## Migration mapping (legacy `.ai/` → `.agent/`)

| Legacy | New |
|---|---|
| `.ai/TASKS/active/<slug>.md` | `.agent/TASKS/active/<slug>.md` (schema upgraded) |
| `.ai/TASKS/completed/<slug>.md` | `.agent/TASKS/completed/<slug>.md` |
| `.ai/memory.md` | `.agent/MEMORY.md` (header rewritten with `last_updated`, entry count) |
| `.ai/credentials.json` | `.agent/credentials.json` |
| `.ai/data/` | `.agent/data/` |
| `.ai/.tmp/` | `.agent/.tmp/` |
| (none) | `.agent/PROGRESS.md` — created by the agent from project knowledge |

The script handles file moves and frontmatter normalization. The AGENT does the
intelligent parts (PROGRESS seeding, MEMORY review for stale entries) because
they need judgment.

## Task schema upgrade

Legacy tasks may have ad-hoc frontmatter. The script normalizes to:

```yaml
---
title: <inferred from first H1 or filename>
slug: <filename without extension>
created: <file mtime as date>
updated: <today>
status: <inferred from folder: active/completed>
owner: <preserved if present, else 'unknown'>
---
```

If the legacy task has no `Resume` section, the script adds an empty template
and the agent fills it during the next interaction.

## Bootstrap algorithm (greenfield)

When neither `.ai/` nor `.agent/` exists:

1. Script creates the directory tree and templates
2. Agent reads project signals:
   - `CLAUDE.md` / `AGENTS.md` / `README.md` for stack and conventions
   - `package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml` / `composer.json` for project type
   - `git log --oneline -50` for recently shipped features (if a git repo)
   - `gh pr list --state=open --json title,headRefName` for in-flight work (if `gh` available)
   - Top-level dirs (`src/`, `app/`, `lib/`, `tests/`) for project shape
3. Agent drafts `.agent/PROGRESS.md`:
   - `## Shipped` — features inferred from git log (use commit subjects, group by feature)
   - `## In progress` — open PRs (title + branch) and any incomplete-looking work
   - `## Planned` — leave empty; user fills in
4. Agent drafts `.agent/MEMORY.md` with at most 5 entries: project type, stack,
   any explicit conventions found in CLAUDE.md/README. Skip entries that are
   trivially derivable.
5. Agent presents the drafts and asks the user to confirm or trim.

The agent must NEVER invent decisions. If unsure, leave the entry out.

## Repair algorithm

When `.agent/` already exists:

1. Verify required files exist (`MEMORY.md`, `PROGRESS.md`, `TASKS/active/`, `TASKS/completed/`)
2. Create any missing dirs/files (empty templates)
3. Lint every task file:
   - frontmatter has required keys (`title`, `slug`, `created`, `updated`, `status`, `owner`)
   - `Resume` block present
   - file length within limits
4. Check `MEMORY.md` against compaction thresholds; suggest compact if exceeded
5. Check `.gitignore` includes `.agent/.tmp/` and `.agent/credentials.json`; add if missing
6. Report a summary; do NOT silently fix lint errors that need judgment

## What setup writes vs what the agent writes

| File | Written by |
|---|---|
| Directory tree | script |
| Empty MEMORY.md template | script |
| Empty PROGRESS.md template | script |
| Task frontmatter normalization | script |
| `.gitignore` entries | script |
| MEMORY.md seed entries | agent |
| PROGRESS.md seed entries from git log | agent |
| Task `Resume` block content | agent (during work) |

Keep this split sharp: the script does mechanical work, the agent does
judgment work. Never put LLM-generated content inside the script.

## Confirmation prompts

The script asks for explicit confirmation before:
- Deleting `.ai/` after a successful merge migrate
- Overwriting any existing `.agent/` file during migrate
- Modifying `.gitignore`

`--yes` flag skips prompts; reserve for the agent's automated repair runs after
the user has approved the plan.

## After setup

The agent should:
1. Show the user what was created/changed (one-line summary per file)
2. If `bootstrap` ran, present the drafted MEMORY/PROGRESS for review
3. Offer to run `scripts/install-hook.sh` to enable the SessionStart hook
4. Offer to run `/dev-guideline preview` so the user can see the dashboard
