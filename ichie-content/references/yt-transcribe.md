# `/ichie-content yt-transcribe <youtube-url>`

Fetch YouTube audio, transcribe it with Whisper, save as clean markdown. No broader web research — that's `/ichie-content research`.

**Naming:** The action is `yt-transcribe` (source-scoped) to leave room for future siblings like `audio-transcribe` or `podcast-transcribe`. The output artifact is still named `transcript.md` (the noun — it *is* a transcript).

**Engine:** Delegates the actual Whisper run to the **`hyperframes-media`** skill (`npx hyperframes transcribe`). One Whisper wrapper, shared across skills. ichie-content stays thin — `scripts/yt-transcribe.py` is just an orchestrator that handles audio extraction (via `yt-dlp`), invokes hyperframes, and converts the resulting word-level `transcript.json` into paragraphed markdown.

## Output

```
/Users/benny/Documents/dev_content/trending/<YYYY-MM-DD>-<slug>/
└── transcript.md
```

Slug derived from the video title (or user-supplied), lowercase-kebab, prefixed with today's date.

## Steps

### 1. Resolve slug
- If the user supplied a slug, use it.
- Else fetch the video title with `yt-dlp --get-title <url>` and slugify (lowercase, non-alnum → `-`, collapse repeats, trim).
- Prefix with today's date in `YYYY-MM-DD`.

### 2. Run the helper script
```bash
scripts/yt-transcribe.py <youtube-url> [slug] \
  [--model small.en|medium.en|large-v3|...] \
  [--language en|es|...] \
  [--keep-json] [--root PATH]
```
The script:
- Creates `dev_content/trending/<slug>/`
- Downloads audio with `yt-dlp -x --audio-format m4a` into the slug dir
- Runs `npx hyperframes transcribe audio.m4a -m <model>` (the hyperframes-media skill)
- Reads the resulting word-level `transcript.json`, groups it into ~80-word paragraphs, and writes `transcript.md`
- Deletes the audio + the JSON (pass `--keep-json` if you'll feed the same video into a captioned hyperframes video later)

### Model selection
- `large-v3` (~3.1GB) — **default (2026-05-29).** Best accuracy, already cached locally, handles any language correctly. Local + free, so the only cost is transcription time (unattended) — nothing to lose on accuracy.
- `medium.en` (~1.5GB) — opt-in faster pass; good on clearly-English audio.
- `small.en` (~466MB) — opt-in fastest pass for a quick gist. Sometimes mishears proper nouns ("Claude" → "Clot").
- `*.en` variants are English-only and silently *translate* non-English audio. The `large-v3` default avoids this trap; only reach for `.en` models when you know the audio is English and want speed. For a specific non-English language, pass `--language <code>` with `large-v3`.

### 3. Add a header
Top of `transcript.md` should include:
```markdown
# <Video title>

- Source: <youtube-url>
- Channel: <author>
- Duration: <hh:mm:ss>
- Fetched: <YYYY-MM-DD>

---

<transcript paragraphs>
```
(Get title/author/duration via `yt-dlp --print '%(title)s|%(uploader)s|%(duration_string)s' <url>`.)

### 4. Fallbacks / troubleshooting
- **Wrong proper nouns** (e.g. "Clot" instead of "Claude") → re-run with `--model medium.en` or `--model large-v3`.
- **Non-English audio** → drop the `.en` suffix and pass `--language <code>` (e.g. `--model small --language es`).
- **hyperframes not installed** → first run auto-installs via `npx --yes`. If that fails, ensure `node` + `npx` are on PATH.
- **First run is slow** → expected; the model downloads to `~/.cache/hyperframes/` and is cached for subsequent runs.

### 5. Memory hook (only if the transcript informs a locked decision)
If a transcript feeds a slate piece, add a `reference` memory pointer per the project hard-gate.

## Why a script
The orchestration (audio extract → Whisper → markdown) is repetitive and benefits from a single source of truth. Keep the logic in `scripts/yt-transcribe.py`. This reference describes *when* to run it; the script is *how*.

## Why delegate to hyperframes-media
Every Python "transcribe" library you'll find (`openai-whisper`, `faster-whisper`, `mlx-whisper`, `whisperx`, `whisper.cpp`) is a Whisper wrapper. `hyperframes-media transcribe` is also a Whisper wrapper — and it's already installed and maintained as part of Benny's skill set. Delegating keeps Whisper concerns in one place: model cache, version updates, format support, language handling. ichie-content just orchestrates around it.
