---
name: dev-guideline
description: Project development workflow with session-resumable tasks, project memory, progress tracking, browser preview, and one-command setup/migration. Use whenever starting a coding session, resuming work, completing a task, recording a project decision ("remember this", "note this"), shipping a feature, running /dev-guideline setup or /dev-guideline preview, working with .agent/ or legacy .ai/ state, or doing any non-trivial development work that should not lose context across sessions. Also use when calling a backend API, handling dev tokens or credentials, or writing scratch/throwaway files.
license: proprietary
metadata:
  author: Ichie Benjamin
  version: "2.0.0"
---

# Dev Guideline

A project-development discipline skill. It keeps three small, agent-readable files alive in every project so any future agent (or you, after a lost session) can resume work without losing context:

- `.agent/TASKS/active/<slug>.md` — open work units with an embedded `Resume` block
- `.agent/MEMORY.md` — decisions and lessons that are NOT derivable from code
- `.agent/PROGRESS.md` — tiny project-wide feature checklist

The skill also provides `/dev-guideline setup` (init or migrate) and `/dev-guideline preview` (local browser dashboard).

## When to apply

- **Session start on any project** — run the session-start protocol (see below) BEFORE doing any other work
- **User invokes a subcommand** — `setup`, `preview`, `compact`, `new-task`
- **Starting, updating, or completing a development task**
- **User says "remember this", "note this", "update your memory"** — writes to project `.agent/MEMORY.md`, never to global user memory
- **Before context compaction** — refresh the active task's `Resume` block
- **Before committing code** — run the self-review gate
- **Shipping a new feature** — append to `.agent/PROGRESS.md`
- **Frontend code calls a backend API, or you need a dev token** — load `references/backend-api.md`
- **Any throwaway/probe/sample file** — write to `.agent/.tmp/`

## Subcommands

| Invocation | What it does |
|---|---|
| `/dev-guideline setup` | Detect state and init/migrate/repair. See `references/setup.md`. |
| `/dev-guideline preview` | Run `scripts/preview.py` and open the local dashboard. See `references/preview.md`. |
| `/dev-guideline compact` | Run `scripts/compact-memory.py` to compact `.agent/MEMORY.md`. |
| `/dev-guideline archive` | Run `scripts/archive.py` — interactively move completed tasks to `archived/`. Default: archive all; also offers "older than 30/7 days". |
| `/dev-guideline new-task <slug>` | Run `scripts/new-task.sh` to scaffold a task file. |

## Session-start protocol (MANDATORY)

Run this BEFORE accepting any new work, on every session, in every project:

```
1. Check for .agent/TASKS/active/ — list any task files there
2. If .agent/ is missing but .ai/TASKS/ exists →
     say: "Legacy .ai/TASKS/ detected. Run /dev-guideline setup to migrate.
           I won't start new work until this is resolved (or you say 'skip')."
3. If neither .agent/ nor .ai/ exists AND project looks active
   (has CLAUDE.md, AGENTS.md, src/, or package.json/pyproject.toml/go.mod) →
     suggest: "No agent state. Run /dev-guideline setup to initialize."
4. If active tasks exist → report each task's title + status + next_step (one line each)
   then ask: "Resume one of these, or start something new?"
5. NEVER silently start a new task while active tasks exist
6. Once user picks a path → capture a one-paragraph description of THIS session's
   intent BEFORE making any code changes, and write it to the chosen task's
   Resume block (or to a new task if starting fresh)
```

The user can override with "skip" once per session.

## Task lifecycle (one concept, no separate SESSIONS)

Each task is a single markdown file with strict frontmatter and a `Resume` block.
The Resume block IS the session snapshot — there is no separate `SESSIONS/` folder.

See `references/tasks.md` for the full schema, lifecycle states, and self-review gate.

```
.agent/TASKS/
  active/      <slug>.md   pending → in_progress → blocked → completed
  completed/   <slug>.md
  archived/    <slug>.md   auto-rotated after 90 days
```

## Memory discipline

`.agent/MEMORY.md` holds project decisions and lessons that a future agent could NOT
infer from reading the code or git log. Examples: "we chose Drizzle over Prisma because
edge bundle size", "all timestamps stored UTC, convert at the edge", "do NOT mock the
DB in integration tests — Q4 incident".

See `references/memory.md` for: the "worth saving" gate, append protocol with read-back,
compaction triggers (>150 lines or >40 entries).

## Progress tracking

`.agent/PROGRESS.md` is a single-page feature checklist. Three sections: `## Shipped`,
`## In progress`, `## Planned`. Every new feature must be added when introduced; every
completed task must update PROGRESS before being closed.

See `references/progress.md` for format and flooding limits.

## Backend API + credentials

Load `references/backend-api.md` when:
- frontend code needs to hit a backend API
- you need a dev token
- no credentials are configured

That reference covers: cached responses in `.agent/data/`, credentials in
`.agent/credentials.json`, dev tokens in `.agent/.tmp/` only, never committed.

## Scratch space — MANDATORY

Any file you create that is not production code and not a committed artifact
goes in `.agent/.tmp/`. This includes probe scripts, sample JSON, fake fixtures,
decoded tokens, benchmark output, diff dumps, "let me just check" scripts.

Rules:
1. `mkdir -p .agent/.tmp` (idempotent)
2. Use the repo's `.agent/.tmp/` — never `/tmp`, never repo root
3. Clean up on task completion unless the user asks you to keep something
4. `.agent/.tmp/` is git-ignored — do not add exceptions
5. If sharing scratch output with the user, print to chat instead of leaving the file

Why: keeps the working tree clean and prevents accidental commits of secrets,
sample data, or one-off scripts that later confuse readers.

## Self-review gate (before closing any task)

1. List the project rules that touched this task (max 5 bullets)
2. State PASS / FAIL with one-line evidence per rule
3. Fix every FAIL, then conclude with **GATE: PASS**
4. Update task checklist, move file to `.agent/TASKS/completed/`
5. Update `.agent/PROGRESS.md` (check the box, add ship date)

Do not close a task with FAILs outstanding. Do not close without updating PROGRESS.

## Quick reference

| Need | Go to |
|---|---|
| Setup or migrate a project | `references/setup.md` |
| Task file schema and lifecycle | `references/tasks.md` |
| MEMORY.md rules and compaction | `references/memory.md` |
| PROGRESS.md format | `references/progress.md` |
| Backend API / dev tokens | `references/backend-api.md` |
| Run the browser dashboard | `references/preview.md` |

## What this skill cannot do (be honest with the user)

- **Cannot auto-fire on session start** unless the user runs `scripts/install-hook.sh`
  to add a SessionStart hook to `~/.claude/settings.json`. Without that hook,
  the session-start protocol triggers only when the skill description matches
  the user's first message. Recommend the hook during `setup`.
- **Cannot atomically lock tasks across concurrent agents.** The `owner` field is
  advisory. If two agents touch the same task, last write wins.
- **Preview cannot edit files** — read-only by design.
- **Cannot sync tasks to GitHub Issues / Linear automatically.** Optional
  `external_ref:` frontmatter field is the only bridge.
