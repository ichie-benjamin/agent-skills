# MIGRATION — ichie-content v1.0.0

## What changed

Replaces the per-project skills installed at `/Users/benny/Documents/dev_content/.claude/skills/` on 2026-05-24:

| Old per-project skill | New action |
|---|---|
| `research`        | `/ichie-content research [topic]` |
| (new)             | `/ichie-content yt-transcribe <youtube-url>` (carved out of research as its own action; source-scoped verb leaves room for future `audio-transcribe`, `podcast-transcribe`, etc.) |
| `weekly-slate`    | `/ichie-content slate` |
| `repurpose`       | `/ichie-content repurpose <source>` |
| `hook-lab`        | `/ichie-content hooks <draft>` |
| `publish-log`     | `/ichie-content log` |

The 5 per-project skill directories were deleted; `ichie-content` lives canonically at `/Users/benny/Documents/agents/skills/ichie-content/` and is symlinked into `~/.claude/skills/`, `~/.codex/skills/`, `~/.cursor/skills/` by `sync-skills.sh`.

## Why one skill instead of five

- Single discoverable verb (`/ichie-content`) instead of five fragmented entry points.
- Shared studio context (target, voice, hard-gate) declared once in `SKILL.md`.
- Per-action references via progressive disclosure — load only the step you're on.
- New actions slot in without re-installing.
- Mirrors the convention already used by `dev-guideline` and Hyperframes (subcommand-style).

## New capability

`yt-transcribe` is now its own action with a real helper script (`scripts/yt-transcribe.py`, pure-stdlib Python orchestrator) that:
1. Downloads audio with `yt-dlp`
2. Delegates the Whisper run to the `hyperframes-media` skill (`npx hyperframes transcribe`)
3. Converts the word-level `transcript.json` into paragraphed `transcript.md`

Previously transcription was a step inside `research` using YouTube's auto-captions (mediocre accuracy — got "Claude" as "Clot", "Higgsfield" as "Hicksfield", etc.). Carving it out + upgrading to Whisper via hyperframes-media is a massive quality jump.

The output file is `transcript.md` — source-scoped verb for the action, noun for the artifact. Source-scoping (`yt-` prefix) leaves room for `audio-transcribe`, `podcast-transcribe`, etc. without ambiguity.

## Migration steps performed

1. `rm -rf /Users/benny/Documents/dev_content/.claude/skills/{research,weekly-slate,repurpose,hook-lab,publish-log}`
2. Built `ichie-content/` at the canonical path with `SKILL.md`, 6 `references/`, and `scripts/yt-transcribe.py`.
3. Ran `./sync-skills.sh` from `/Users/benny/Documents/agents/skills/` — symlinks created in all three tool dirs.
4. Updated `skills-installed` memory in `/Users/benny/.claude/projects/-Users-benny-Documents-dev-content/memory/` to point at the consolidated skill.

## Backwards compatibility

The old per-project skills are deleted. Any old `MEMORY.md` index entries referencing them are updated to point at the consolidated skill.
