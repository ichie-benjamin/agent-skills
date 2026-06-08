# `/ichie-content hooks <draft>`

Generate, critique, and rank hooks for a piece. **Mandatory gate before any piece is locked for publish** — the hook decides reach.

## Output

`dev_content/content/drafts/<slug>/hooks.md` (or appended to the draft file directly if no `<slug>/` exists yet).

## Process

### 1. Read the payoff
One sentence: what does the viewer/reader actually leave with? If unclear, ASK the user — a hook that promises a payoff the piece doesn't deliver burns trust. This is non-negotiable.

**Honesty check before generating.** If the hook implies a stat ("X is costing you $Y" / "3× faster") or an authority claim ("companies are switching from X to Y"), that claim must be backed by a verified source in the piece's `standard-pack.md`. If it isn't, do NOT propose hooks that lean on it — propose ones that lean on what IS verified. The [[content-quality-standard]] makes every hook claim auditable.

### 2. Generate 8 candidates
Pull from these patterns. Mix and match — don't blindly use all 8.

| Pattern | Shape | Use when |
|---|---|---|
| Contrarian | "Stop doing X. Do Y." | You have a confident alternative |
| Callout | "You're using <tool> wrong." | Showing a common misuse |
| Curiosity gap | "The <N>-sec trick that <result>." | Quick, demonstrable win |
| First-person stake | "I tried <X> so you don't have to." | Personal experiment |
| News / edge | "<Framework> just shipped <feature> — here's why it matters." | Trending ecosystem update |
| Numbered | "3 <X> tricks I wish I knew sooner." | List-shaped piece |
| Loss aversion | "<X> is costing you <Y>." | Hidden tax / inefficiency |
| Identity | "If you ship code, you need to know this." | Universal-truth angle |

### 3. Critique each on 4 axes (score 1–5)

| Axis | Question |
|---|---|
| Scroll-stop power | Would *I* stop scrolling? |
| Payoff promise | Does the hook telegraph value? |
| Honesty | Does the piece deliver what the hook promises? |
| Platform fit | Does length / cadence / register match the surface? |

Output as a table so the trade-offs are visible.

### 4. Rank top 3 with rationale
One short line per pick on why it ranked above the others.

### 5. Winner per platform
IG and X often share a winner. TikTok and YT Short often diverge from text platforms (rhythm matters more, fewer words).

Write into `hooks.md`:
```markdown
# Hooks — <piece title>

**Payoff:** <one line>

## Winners
- Instagram: <hook>
- TikTok:    <hook>
- X:         <hook>
- YouTube:   <hook>

## Ranked candidates
1. <hook> — <why>
2. <hook> — <why>
3. <hook> — <why>

## All candidates + scores
| # | Hook | Scroll | Payoff | Honest | Fit | Total |
|---|------|--------|--------|--------|-----|-------|
| 1 | ... | 5 | 4 | 5 | 5 | 19 |
| ... |
```

### 6. After publish — capture the lesson (hard-gate)
If a hook overperforms or flops vs expectations, write/update a `feedback` memory:
```
---
name: hook-lesson-<pattern>
description: What we've learned about <pattern> hooks on <platform>
metadata:
  type: feedback
---

<hook used> on <platform> got <metrics>. Hypothesis: <why>. Apply next time by <what to repeat / avoid>.
```
This is how the studio gets sharper. Skipping it wastes the data.
