# `/ichie-content repurpose <source>`

Take one core idea and produce platform-native cuts. Source can be: a draft markdown file, a YT transcript bundle (`trending/<slug>/transcript.md`), or a paragraph the user pastes.

## Output

```
dev_content/content/drafts/<slug>/
├── source.md                    ← copy/link of the source, with normalized metadata
├── standard-pack.md             ← shared standard elements (example, history, quote, comic) all cuts pull from
├── instagram-carousel.md        ← 6–10 slides (must include comic slide)
├── tiktok-reel-script.md        ← 30–60s, two-column (on-screen text / voiceover)
├── x-thread.md                  ← 6–12 posts (must cite the verified quote)
├── youtube-short-script.md      ← 45–60s
├── youtube-long-outline.md      ← OPTIONAL, only if user opts in
├── hooks.md                     ← winners per platform (written/refreshed by /ichie-content hooks)
└── validation.md                ← verdict + fix-list from /ichie-content validate (written at gate-time)
```

## Inputs to gather before producing
- **Core message:** one-line takeaway the viewer leaves with
- **Audience slice:** juniors / shipping engineers / AI-builders / framework users / etc
- **Voice:** builder / sharp / teacher / hybrid (defaults to `voice` memory)
- **CTA:** follow + what next (save / share / link in bio)
If any are missing, ASK — don't guess. A wrong audience tag wrecks the cut.

## Step 0 — Build `standard-pack.md` first
Before producing any platform cut, lock in the four standard elements. Every cut pulls from this pack so they stay consistent.

```markdown
# Standard pack — <piece slug>

## 1. Real-world example
- Name: <real company / person / product / event>
- 1-line context: <what they did + when>
- Source: <URL — must be checkable>

## 2. Historical / contextual anchor
- Reference: <named event / paper / release / era>
- Year + 1-line context:
- Source: <URL>

## 3. Verified quote (from canonical software/CS book)
- Quote: "<verbatim — checked against the published source>"
- Author + Book + Edition + Chapter/Section:
- Verified-by: <YYYY-MM-DD>  (and append to book-references ledger)

## 4. Comic cue
- Style: xkcd-adjacent | New-Yorker-single-panel
- Panel description: <what's in the frame — 1–2 sentences>
- Caption: "<the line under the panel>"
- Production note: <Midjourney prompt / DALL-E prompt / hand-sketch>
```

If any of the four cannot be filled honestly, **stop and fix it** — either go back to `research` for more material, or drop the angle. The validator will catch missing or fake elements anyway; better to catch them here.

## Per-platform specs

### `instagram-carousel.md` (6–10 slides)
- Slide 1: hook + bold visual cue. No fluff.
- One slide must be the **comic** (the cue from `standard-pack.md` — panel description + caption).
- One slide must be the **verified quote** (with attribution shown — author, book).
- The real-world example anchors one of the body slides.
- The historical anchor lands in the body or the closer (one line).
- Final slide: follow + save CTA, plus one teaser ("part 2 next week" if applicable).
- Format slides as `## Slide N` blocks so the producer can paste straight into Canva / Figma.

### `tiktok-reel-script.md` (30–60s)
Body must surface: the real example (name it on-screen), the verified quote (text-overlay card with attribution), the historical anchor (one spoken line), and the comic cue (B-roll / cutaway frame description).

Two columns, written as a table:
```
| Time | On-screen text | Voiceover |
|------|----------------|-----------|
| 0:00–0:02 | <hook text> | <hook VO> |
| 0:02–0:08 | <payoff cue> | <payoff line> |
| ... | | |
| -0:03 | Follow @<handle> | "Follow for part 2." |
```
- Hook in 0–2s — non-negotiable.
- Payoff reveal by 0:08.
- End on a clear CTA + open loop where possible.

### `x-thread.md` (6–12 posts)
- **P1:** bold claim hook, ≤240 chars, NO link (links suppress reach).
- **P2–P(N-1):** evidence, concrete examples, one idea per post. Use line breaks generously.
  - At least one mid-thread post is the **real-world example** with the source link inline.
  - At least one mid-thread post is the **verified quote** with author + book + section.
  - At least one mid-thread post is the **historical anchor** (one-liner — "This isn't new; [X] showed this in [year].").
  - One post (image attachment) is the **comic** — describe the panel here so the asset can be produced.
- **Final post:** "Follow @<handle> for more on <niche>." + link to longer artifact if relevant.
- Number posts `1/`, `2/`, … only if it adds value (deep dives yes; quick threads no).

### `youtube-short-script.md` (45–60s)
- Same hook discipline as TikTok.
- Often a clean copy of the TikTok script — but YT tolerates slightly more depth in the payoff.
- End with subscribe CTA + tease the next short.

### `youtube-long-outline.md` (optional, only on opt-in)
- Cold open (30–45s) → hook → context → 3–5 numbered chapters → recap → CTA
- Note B-roll cues inline as `[b-roll: <what>]`

## Rules
- **Hook-first on every cut.** No exceptions.
- **Translate, don't paste.** Each cut must feel native to the platform.
- **Honor `voice` memory.** Tag the chosen mode at the top of each file: `> voice: builder`.
- **One promise, one payoff.** Multiple ideas → split into multiple slate pieces, not one bloated cut.
- **Handles.** Insert real handles from `project-goals` / `user-profile` memory; if missing, leave a `{{handle}}` token and ask the user.

## After producing
1. Run `/ichie-content hooks` over the drafts to lock the winners into `hooks.md`.
2. **Run `/ichie-content validate <slug>`** — independent subagent gate against the content-quality standard. Fix every issue it returns, re-run until PASS. No publish without PASS.
3. Update the matching `ideas/backlog.md` row → `🎬 producing`.
4. When publish-ready, run `/ichie-content log` at ship time.
