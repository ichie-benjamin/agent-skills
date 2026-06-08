# `/ichie-content slate`

Plan the week's content slate. 3–4 core ideas, each repurposed across ≥2 platforms, hooks ready.

## Output

- `dev_content/content/drafts/<YYYY>-W<WW>-slate.md` (e.g. `2026-W22-slate.md`)
- Rows appended to `dev_content/ideas/backlog.md` with status `✍️ scripting`
- Memory: `current-slate.md` written/updated; `MEMORY.md` index updated

## Process

### 1. Load context (mandatory)
- `MEMORY.md` → at minimum: `project-goals`, `content-strategy`, `voice`, `current-slate` (if exists)
- Any active briefs in `dev_content/trending/`
- `analytics/performance.md` — last 1–2 weeks of results + any `feedback` memories

### 2. Pick 3–4 core ideas
Mix:
- **≥1 trend-rider** — current. Run `/ichie-content research` first if coverage is thin.
- **≥1 evergreen** — always-true insight, doesn't decay.
- Each idea must have a payoff that survives a 30-second cut.

### 3. Decide platform cuts
Default: every idea ships on ≥2 platforms. Strong pairings:
- IG carousel + X thread (text-heavy ideas)
- TikTok + IG Reel (motion / demo ideas)
- YT Short + X teaser (deep-dive teasers pointing to a longer piece later)

### 4. Hooks ready
For each piece, run `/ichie-content hooks` discipline mentally (3 candidates → winner) and write the winner into the slate file. Full pass happens at draft-lock time.

### 5. Write the slate file

```markdown
# Week of <YYYY-MM-DD> — slate

**Target context:** <where we are vs the 10k/90d goal — e.g. "Day 12 / 90, need ~110/day, currently tracking X">

## Piece 1 — <title>
- **Angle:** <one line — the wedge that makes it interesting>
- **Hook (winner):** <hook>
- **Voice:** builder | sharp | teacher | hybrid
- **Platforms:** IG carousel, X thread
- **Research:** trending/<slug>/ (or "none — evergreen")
- **Ship target:** <day, or "when ready">
- **Payoff:** <one line — what the viewer leaves with>

## Piece 2 — ...
```

### 6. Backlog rows
Append one row per piece to `dev_content/ideas/backlog.md`. Status: `✍️ scripting`.

### 7. Memory (hard-gate)
Create/update `current-slate.md` memory:
```
---
name: current-slate
description: Locked content slate for week of <YYYY-MM-DD>
metadata:
  type: project
---

Week of <YYYY-MM-DD>. Pieces:
- <title 1> → <platforms>
- <title 2> → <platforms>
- ...

See content/drafts/<YYYY>-W<WW>-slate.md for full angles + hooks.
```
Update `MEMORY.md` index.

## When to re-run the slate
- Beginning of each calendar week
- When a hot trend lands mid-week and an existing piece should be swapped out
- After a flop — re-evaluate remaining slate against the lesson
