---
name: ichie-content
description: Benny's dev-tech content studio workflow for Instagram, TikTok, X, and YouTube. Use for any operation in the dev_content studio — researching trending dev/AI topics, transcribing a YouTube video, planning the weekly publishing slate, repurposing one idea into platform-native cuts (IG carousel + TikTok/Reel + X thread + YT Short), generating and ranking hooks, or logging a publish + capturing the lesson. Subcommands are invoked as `/ichie-content <action>`. Designed around the self-learning hard-gate in dev_content/CLAUDE.md — every locked decision becomes a memory file.
license: proprietary
metadata:
  author: Ichie Benjamin
  version: "1.0.0"
---

# Ichie Content

A single skill that runs the full dev-content production loop for Benny's studio at `/Users/benny/Documents/dev_content`. Each action is a small, focused step in the loop. Load the action reference for the step you're on — don't load all of them.

## Studio at a glance

- **Target:** 10,000 combined new followers across IG / TikTok / X / YouTube in 90 days (deadline 2026-08-22 — set 2026-05-24)
- **Cadence:** 3–4 publishes/week, flexible (ship when ready)
- **Voice:** hybrid — builder-in-public (default), sharp/contrarian when warranted, friendly teacher for tutorials. Picked per piece, tagged at top of every draft.
- **Hard-gate:** the studio is self-learning. Any new decision/idea/result/preference/template/target → write a memory file in `/Users/benny/.claude/projects/-Users-benny-Documents-dev-content/memory/` and pointer in `MEMORY.md`. Never let knowledge die in chat. Full rules in `dev_content/CLAUDE.md`.

## Subcommands

Invoked by the user as `/ichie-content <action> [args]`. Always load the matching reference before producing output.

| Action | When to invoke | Reference |
|---|---|---|
| `research [topic]` | "what's trending in <topic>", proactive sweep before slate, or gathering supporting YT/X links | `references/research.md` |
| `yt-transcribe <youtube-url>` | User pastes a YT link and wants the transcript (no broader research). Source-scoped name leaves room for future `audio-transcribe`, `podcast-transcribe`, etc. | `references/yt-transcribe.md` |
| `slate` | "plan this week" / start of week / after research surfaces a hot trend | `references/slate.md` |
| `repurpose <source>` | A draft is locked and needs IG carousel + TikTok + X thread + YT Short | `references/repurpose.md` |
| `hooks <draft>` | "give me hooks for X" — also a **mandatory** gate before any piece is locked for publish | `references/hooks.md` |
| `validate <draft>` | **Mandatory** independent quality gate. Spawns a fresh-context subagent to check the content-quality standard (real example, historical anchor, verified quote, comic cue, zero unsourced claims). Runs before `log`. | `references/validate.md` |
| `log` | "just posted X" / closing step of any production session — requires a `validate` PASS first | `references/log.md` |

## Video production — READ before any video build

Producing video (HyperFrames)? **Read [`references/video-layout-guide.md`](references/video-layout-guide.md) first.** It is the portable, project-agnostic guide for **placement/layout, animation, transitions, pacing, audio, signature device, render-safety gotchas, and the scene-gated workflow + critic gate** — distilled from every hard-won lesson. Reusable by this project or any other. Project-specific bits (palette, signature device) are marked `[INSTANCE]` — swap per project.

## Session-start protocol (when working in dev_content)

1. **Read `MEMORY.md` first** (the index at `/Users/benny/.claude/projects/-Users-benny-Documents-dev-content/MEMORY.md`). Open relevant memory files based on the task.
2. **Confirm or advance the current target** — check `project-goals` memory.
3. **Do the work** via the matching subcommand.
4. **Write memories** for anything new, then update `MEMORY.md`.
5. **Close with `/ichie-content log`** if anything shipped.

## Studio directory map

```
/Users/benny/Documents/dev_content/
├── CLAUDE.md                  ← studio rules + memory hard-gate
├── ideas/backlog.md           ← idea pipeline (status-tagged rows)
├── content/drafts/<slug>/     ← in-progress pieces (platform cuts here)
├── content/published/<slug>/  ← shipped archive
├── trending/<YYYY-MM-DD>-<slug>/  ← research bundles (transcript.md, brief.md, links.md)
├── analytics/performance.md   ← the learning loop
├── templates/                 ← reusable hooks/formats/hashtag sets
├── scripts/                   ← any video/post scripts
└── assets/                    ← raw + exported media
```

## External deps

- `yt-dlp` (Homebrew) — used by `yt-transcribe` and `research`. Install: `brew install yt-dlp`.
- `node` + `npx` — required by `yt-transcribe` (which delegates Whisper to the `hyperframes-media` skill via `npx hyperframes transcribe`).
- `ffmpeg`, `jq` — present in this environment.
- `WebSearch` / `WebFetch` — used by `research` (load via ToolSearch if deferred).

The `yt-transcribe` action is a thin Python orchestrator (`scripts/yt-transcribe.py`, pure stdlib) that:
1. Downloads audio with `yt-dlp`
2. Delegates Whisper to `hyperframes-media` (one Whisper wrapper, shared across skills)
3. Converts word-level `transcript.json` into paragraphed `transcript.md`

## Authoring rules (apply to every cut)

- **Hook-first.** First slide / first second / first post earns the scroll-stop or the piece fails.
- **One promise, one payoff.** Don't stuff multiple ideas; that's what the slate is for.
- **Translate, don't paste.** Carousel pacing ≠ thread pacing ≠ video pacing.
- **Platform-correct CTA.** IG: "Follow + save". X: "Follow @ for more on <niche>". TikTok: "Follow for part 2". YouTube: "Subscribe — new ones every week".
- **Honor `voice` memory.** Tag the mode at the top of each draft.
- **Hooks are gated.** No publish without `/ichie-content hooks` first.
- **Quality standard is gated.** Every piece must include: (1) real-world example, (2) historical/contextual anchor, (3) one verified quote from a canonical software/CS book, (4) one intelligent comic cue, (5) zero unverified claims. Enforced by `/ichie-content validate`. See the `content-quality-standard` memory + [[themitmonk-style]] reference.
- **No publish without a `validate` PASS.** Independent subagent gate — not optional, not skippable.
- **No publish without `/ichie-content log`.** That's how the studio compounds.
