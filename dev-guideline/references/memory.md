# Memory — `.agent/MEMORY.md`

Project decisions and lessons that a future agent would NOT be able to infer
from reading the code, git log, or CLAUDE.md.

## What belongs here

- **Decisions with a "why"**: "Chose Drizzle over Prisma because edge bundle size"
- **Non-obvious invariants**: "All timestamps stored UTC, converted at the edge"
- **Lessons from incidents**: "Do NOT mock DB in integration tests — Q4 prod-mock divergence"
- **Refused approaches**: "Tried Redis pub/sub for X, abandoned because Y"
- **External context**: "Stripe webhook ordering is not guaranteed; we dedupe by event.id"

## What does NOT belong here

- Anything in CLAUDE.md or AGENTS.md (project spec, stack, commands)
- File paths or function names (use git/grep)
- Recent changes (use git log)
- Task-specific state (use the task's Resume block)
- "I implemented X" (use PROGRESS.md or git log)
- Conversational context from the current session

If a fact is derivable from `git log` or `grep`, it does not belong in MEMORY.

## Format

```markdown
---
last_updated: 2026-05-23
entries: 12
---

# Project Memory

## 2026-05-23 — Drizzle over Prisma
Edge runtime + bundle size. Prisma's query engine is 14MB.
Trade-off accepted: more manual relation handling.

## 2026-05-20 — Timestamps UTC at rest
All DB columns store UTC ISO strings. UI converts via browser tz.
Reason: multi-region deployment confusion in Q1.

## 2026-05-15 — No DB mocks in integration tests
Q4 incident: mocked tests passed, prod migration broke. Always hit a real DB
(via testcontainers).
```

Each entry: ISO date, dash, terse title. Body is 1–4 lines. The why is
mandatory — if you can't articulate why, the entry isn't worth saving.

## Append protocol (run this every time you write)

1. **"Worth saving?" gate**: Could a future agent infer this from code or git?
   - If yes → don't save.
   - If derived from current session noise → don't save.
   - If you can't state the "why" in one sentence → don't save.
2. **Check duplicates**: search MEMORY.md for related entries. Update an existing
   entry rather than appending a near-duplicate.
3. **Append** with today's date and a `## YYYY-MM-DD — Title` heading.
4. **Read back** the file. Confirm the entry landed and the file structure is intact.
5. **Bump `last_updated`** and `entries` in the frontmatter.
6. **Check thresholds** (see below). If exceeded, run compaction.

## Compaction thresholds

Trigger compaction when EITHER:
- File exceeds **150 lines**, OR
- Entry count exceeds **40**

Compaction is run via `scripts/compact-memory.py` for the mechanical parts
(line and entry counting, frontmatter rewrite) plus an agent review pass for
the judgment parts (merge similar entries, drop obsolete ones, sharpen wording).

### Compaction algorithm

```
1. Read MEMORY.md
2. Group entries by topic (auth, db, deploy, ...)
3. Within each group:
   - merge near-duplicates into one entry; date = most recent date
   - drop entries that are now codified in CLAUDE.md or the code itself
   - drop entries about decisions that have been reversed
4. Re-sort by date (newest first)
5. Rewrite frontmatter: last_updated = today, entries = new count
6. Show user a diff and ask: keep / revise / abort
7. On keep → write file, confirm with read-back
```

Never silently drop entries. Always present the diff for approval.

## "Update your memory" / "Remember this" / "Note this"

When the user says any of these, write to project `.agent/MEMORY.md`. NEVER
write to `~/.claude/` user-level memory unless the user explicitly says "save
this to my user memory" or "global memory".

## Read-back is mandatory

After ANY append:
1. Read the file back
2. Summarize what's now in MEMORY (entry count, total lines)
3. If past thresholds, immediately offer compaction

This catches: silent write failures, frontmatter corruption, accidental
duplication, drift past limits.

## When MEMORY conflicts with current code

Trust the code. Update or remove the stale memory rather than acting on it.
A memory dated three months ago that names a function may be referring to
something that has been renamed or deleted.
