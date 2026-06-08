# Tasks — schema, lifecycle, self-review gate

## Folder layout

```
.agent/TASKS/
  active/      <slug>.md   open work
  completed/   <slug>.md   done, kept for history
  archived/    <slug>.md   auto-rotated from completed/ after 90 days
```

Filenames never carry dates. All dates live in frontmatter.

## Schema

Every task file MUST have this structure:

```markdown
---
title: Add OTP login
slug: add-otp-login
created: 2026-05-23
updated: 2026-05-23
status: in_progress         # pending | in_progress | blocked | completed
owner: claude-opus-4-7      # who last touched it (advisory)
external_ref:               # optional: linear ticket, GH issue, etc
---

## Description
One paragraph. Why this exists. What problem it solves.
Maximum 5 lines. If you need more, the task is too big — split it.

## Checklist
- [x] Wire SMS provider
- [ ] Build OTP UI
- [ ] Add rate limit

## Resume
**Last touched:** 2026-05-23 14:22
**Next step:** Implement rate limit in `auth/rate.ts:42`
**Context:** Using Twilio. Verified credentials in `.agent/.tmp/twilio-test`.
Decision to use sliding-window rate limiter — see MEMORY entry 2026-05-23.
**Files in flight:** `auth/otp.ts`, `components/OTPForm.tsx`

## Notes
(optional, free-form implementation notes. Keep tight.)
```

## Hard limits (skill-enforced)

| Section | Max | Why |
|---|---|---|
| Description | 5 lines | If longer, split the task |
| Resume → Context | 8 lines | Resume snapshots are for re-entry, not full state |
| Notes | 40 lines | If longer, promote learnings to MEMORY.md |
| Whole file | 200 lines | Anything bigger is a sub-project — split |

On overflow, warn the user and suggest a split. Don't silently truncate.

## The Resume block is the session snapshot

There is no separate `SESSIONS/` folder. Every task carries its own Resume.
When you stop working, leave Resume in a state where any agent can pick up
without reading the entire conversation.

Resume MUST contain:
- **Last touched** — ISO date + time
- **Next step** — exactly one concrete action with a file:line if applicable
- **Context** — only what's not visible from code (decisions, blockers, gotchas)
- **Files in flight** — paths currently being edited

Don't write Resume as a diary. It is a re-entry note.

## Lifecycle

```
pending → in_progress → completed     (happy path)
              ↓
           blocked → in_progress → completed
```

State transitions:
- **pending → in_progress**: agent commits to working on it now; updates `owner`, bumps `updated`
- **in_progress → blocked**: external dependency missing; update Resume with the blocker
- **any → completed**: self-review gate PASSES, file moves to `completed/`

## Session-start protocol

See SKILL.md for the full protocol. Summary:

1. `ls .agent/TASKS/active/`
2. If any active → list them (one line each: `slug • status • next_step`) and ask user which to resume
3. NEVER start new work while active tasks exist without explicit user approval
4. Capture this session's intent in one paragraph before any code change

## Self-review gate (before closing any task)

Run this every time, no exceptions:

```
1. List relevant project rules (max 5 bullets). Examples:
   - .agent/MEMORY.md entries that touched this work
   - CLAUDE.md conventions
   - Linting / type / test rules

2. PASS/FAIL with one-line evidence per rule:
   ✓ MEMORY: timestamps stored UTC — evidence: created_at uses .toISOString()
   ✗ MEMORY: no DB mocks in integration — evidence: tests/otp.test.ts mocks Drizzle
   ✓ CLAUDE: use Zod for input validation — evidence: routes/otp.ts:12

3. Fix every FAIL. Re-evaluate.

4. Conclude: GATE: PASS or GATE: FAIL

5. Update task: check final Checklist boxes, fill Resume one last time
   (Next step: "closed"), set status: completed, bump updated.

6. Move file from active/ to completed/.

7. Update .agent/PROGRESS.md — check the matching box, add ship date.
```

A task with `GATE: FAIL` does NOT close. Fix or convert to `blocked` with a
new task created for the remediation work.

## Multi-agent advisory locking

The `owner` field is advisory. Before claiming a task:

1. Read the file, note current `owner` and `updated`
2. If `updated` is within the last 30 minutes AND `owner` is not you →
   ask the user before claiming
3. If you proceed, set `owner` to your model ID and bump `updated`

This is not atomic. Two agents that race will both think they got the lock.
For real concurrent work, coordinate through the user.

## Anti-patterns

- Don't keep notes in chat that should be in Resume — chats are ephemeral
- Don't write "in progress on X" — write the exact next file:line
- Don't expand Description after the task starts; new context goes in Notes or MEMORY
- Don't reopen completed tasks — create a new task that references the old slug
- Don't leave the checklist blank; if you can't list 2+ concrete steps, the task isn't defined yet
