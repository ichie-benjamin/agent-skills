# `/ichie-content research [topic]`

Pull research material for content ideation. Two modes:

- **Targeted:** topic given → gather supporting YT + X links, news, recent discourse.
- **Sweep:** no topic → scan dev/AI trending across HN, X, YouTube, major changelogs, cluster into 2–3 themes.

If the input is a single YouTube URL, prefer `/ichie-content yt-transcribe <url>` — `research` is for breadth, `yt-transcribe` is for one video.

## Output location

All artifacts saved to:
```
/Users/benny/Documents/dev_content/trending/<YYYY-MM-DD>-<slug>/
├── brief.md      ← topic summary, why now, hook angles, suggested platforms
├── links.md      ← supporting YT + X + HN links with one-line context each
└── transcript.md ← only if a YT source was also fed in
```

Slug = `<YYYY-MM-DD>-<lowercase-kebab-of-topic>`.

## Steps

### 1. Identify topic + slug
If the user gave a topic, use it. Otherwise sweep first (step 4) and create one bundle per theme.

### 2. Web sweep (targeted)

**Sweep the curated source list FIRST.** Open `dev_content/sources.md` (memory: [[sources]]) and check whether any of the channels/accounts/newsletters/blogs have published on this topic recently. Those hits are higher-signal than open web search because the credibility is pre-vetted.

Then broaden via `WebSearch` (load via ToolSearch if deferred):
- `"<topic> 2026"` — recency
- `"<topic> latest"` — fresh discourse
- `site:x.com <topic>` or `site:twitter.com <topic>` — X conversation
- `site:youtube.com <topic>` — related videos
- `site:news.ycombinator.com <topic>` — HN signal
- `site:github.com <topic>` — repos + releases (useful for framework topics)

Capture top 3–5 per channel into `links.md` with a one-line "why it's relevant". Mark which links came from the curated source list (e.g. tag with `[curated]`) so we can later measure which surfaces produce hit pieces.

### 3. Optional supporting transcript
If a specific YT video is the anchor, call `/ichie-content yt-transcribe <url>` and place the resulting `transcript.md` in the same bundle folder.

### 4. Sweep mode (no topic given)
Hit these in order, cluster results into 2–3 themes, then produce a brief per theme:
- **The curated source list first** (`dev_content/sources.md`) — scan recent posts from the YouTube channels, X accounts, and newsletters. This is the highest-signal surface.
- Hacker News front page (`https://news.ycombinator.com/`)
- X dev discourse — search "AI agents", framework names, "shipped today"
- YouTube dev trending
- Major changelogs: Vercel, Anthropic, OpenAI, Next.js, React, Node, big LLM releases

### 5. Verify every claim
Before writing the brief, **walk through every fact the research surfaced and mark each one as verified or unverified.** A claim is verified only when:
- The source is named (specific article, repo, release notes, paper, talk — not "people are saying")
- A second independent source confirms it (different author or org), OR the source is the primary (e.g. Anthropic's own release notes for an Anthropic feature)
- Dates and numbers cross-check

Unverified claims do **not** enter the brief. Either chase them down or drop them. The [[content-quality-standard]] makes this binding — anything not verified here will fail at `/ichie-content validate` later.

### 6. Hunt for the standard's required elements
For each promising angle, look for:
- **A real, named example** to anchor the piece (a real company that shipped this, a real outage, a real codebase). Note it in the brief.
- **A historical anchor** — when did this idea first surface? Who proposed it? What earlier system did it replace? (e.g. for "MCP," reference earlier protocols like LSP.)
- **A canonical-book quote candidate** — search [[book-references]] for relevant principles, mark which book/section to verify.
- **A comic angle** — what's the dry, smart, single-panel joke that captures the contradiction or insight? (xkcd-adjacent or New-Yorker-single-panel.)

If any of the four can't be found from the available material, note it as a gap — `repurpose` will need to do more digging or the piece needs another research pass.

### 7. Write `brief.md`
```markdown
# <Topic>

**Why now:** <one paragraph — what changed, what's hot, the wedge>

**Verified claims:**
- <claim> — source: <URL/citation>
- <claim> — source: <URL/citation> (+ cross-check: <2nd URL>)

**Unverified — DROP or chase:** <none, or list>

**Hook angles:**
1. <contrarian / news / curiosity / etc — see hooks reference for patterns>
2. ...
3. ...

**Standard-elements scouted:**
- Real example: <name + 1-line context, or "GAP — needs more research">
- Historical anchor: <name + year + 1-line context, or "GAP">
- Canonical-book candidate: <book + chapter — needs verification at use-time, or "GAP">
- Comic angle: <one-line concept + caption draft, or "GAP">

**Suggested platforms:** <which of IG / TikTok / X / YouTube and why>

**Supporting research:** see links.md (and transcript.md if present)
```

### 6. Memory hook (hard-gate)
If a brief gets promoted into the slate, write a `reference` memory:
```
---
name: research-<slug>
description: Research bundle on <topic> — see trending/<slug>/
metadata:
  type: reference
---

<one-paragraph context + link back to trending/<slug>/>
```
Add a pointer to `MEMORY.md`. This prevents re-researching the same topic next session.
