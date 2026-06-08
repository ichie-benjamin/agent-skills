# Postmortem

One-page learning note. Required by close gate. Every section non-empty or marked `none` with reason. Keep it tight — three pages is performative.

## Frontmatter
```yaml
---
slug: <slug>
type: <one of 6>
duration_s: <number>
shipped_on: <YYYY-MM-DD>
approver: <named human>
---
```

## What worked
2–4 concrete techniques that landed. Name specific catalog blocks or moves if they were the win.

## What broke
1–3 things that went wrong + the fix applied. Cross-link `feedback_*` memories if it's a documented gotcha.

## What surprised
Insights that weren't in any existing doc. This is where the library grows. `none` is valid if honest — don't fabricate.

## References used + scoring
How each cited reference served the film, scored 1–10. Low scores signal the reference may be misleading and should be down-weighted next time.

| Reference | What was lifted | Score 1–10 |
|---|---|---|

## Diffs filed
Actual files updated or created. Or `no new insight` with a one-line reason.

| File | Change | Action |
|---|---|---|

## Verified writes
- [ ] `works/<slug>/postmortem.md` — written + read back
- [ ] `research/references/ref-queek-<slug>.md` — written + read back
- [ ] `research/REFERENCES.md` — updated + read back
- [ ] Other diffs read back

## Waivers
Format: `- Item <n> (<name>) — <reason>. Date: <YYYY-MM-DD>. Approved by: <human>.`

Items 2, 3, 7 of the close gate can be waived. Items 1, 4, 5, 6, 8, 9, 10 cannot. Or `none`.

---

`Close gate: <passed>/<applicable> · <DONE | BLOCKED>`
