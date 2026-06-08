#!/usr/bin/env python3
"""yt-transcribe.py — fetch YouTube audio and transcribe via hyperframes-media.

This script orchestrates:
  1. yt-dlp        → extract audio from a YouTube URL
  2. hyperframes   → transcribe audio to word-level transcript.json (Whisper)
  3. this script   → group words into paragraphs and write transcript.md

We delegate the actual speech-to-text to hyperframes-media (`npx hyperframes
transcribe`) so model management, caching, and Whisper updates stay in one
place. ichie-content stays thin.

Usage:
  yt-transcribe.py <youtube-url> [slug]
                   [--model MODEL] [--language CODE] [--keep-json] [--root PATH]

Examples:
  yt-transcribe.py 'https://youtu.be/xxxx'
  yt-transcribe.py 'https://youtu.be/xxxx' my-slug --model large-v3
  yt-transcribe.py 'https://youtu.be/xxxx' --language en --model medium.en

Output: <root>/trending/<slug>/transcript.md
  (root defaults to $DEV_CONTENT_ROOT or /Users/benny/Documents/dev_content)

External deps (must be installed):
  - yt-dlp        (brew install yt-dlp)
  - node + npx    (for npx hyperframes)
  - hyperframes   (auto-installed by npx on first run)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

DEFAULT_ROOT = "/Users/benny/Documents/dev_content"
# large-v3 (~3.1GB) is the default: best accuracy, already cached locally, and
# (unlike .en models) it does NOT silently translate non-English audio. It's
# local/free, so the only cost is transcription time (unattended). Override with
# --model small.en / medium.en for a faster pass when you only need the gist.
DEFAULT_MODEL = "large-v3"


def slugify(text: str, max_len: int = 60) -> str:
    body = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:max_len]
    return f"{date.today().isoformat()}-{body}"


def require(tool: str) -> None:
    if shutil.which(tool) is None:
        sys.exit(f"missing required tool: {tool}")


def get_metadata(url: str) -> dict:
    out = subprocess.run(
        ["yt-dlp", "--print",
         "%(title)s|%(uploader)s|%(duration_string)s|%(id)s", url],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    title, uploader, duration, vid = out.split("|", 3)
    return {"title": title, "uploader": uploader,
            "duration": duration, "id": vid}


def download_audio(url: str, out_dir: Path) -> Path:
    template = str(out_dir / "audio.%(ext)s")
    subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "m4a", "--audio-quality", "0",
         "--quiet", "--no-warnings", "-o", template, url],
        check=True,
    )
    matches = sorted(out_dir.glob("audio.*"))
    if not matches:
        raise RuntimeError("audio download produced no file")
    return matches[0]


def transcribe_via_hyperframes(audio_path: Path, model: str,
                               language: str | None) -> tuple[list, Path]:
    """Invoke `npx hyperframes transcribe` and return (words, json_path).

    hyperframes writes `transcript.json` into the project dir (`-d`).
    First run downloads the requested Whisper model into ~/.cache/hyperframes/.
    """
    work_dir = audio_path.parent
    # Run hyperframes with cwd=work_dir so it writes transcript.json there.
    # Do NOT also pass -d <work_dir> — combining them caused exit-1 in testing.
    cmd = [
        "npx", "--yes", "hyperframes", "transcribe", audio_path.name,
        "-m", model,
    ]
    if language:
        cmd += ["-l", language]
    print(f"  → npx hyperframes transcribe (model: {model})", file=sys.stderr)
    # Let hyperframes' stdout/stderr stream straight through so failures
    # surface immediately instead of being swallowed by the spinner.
    subprocess.run(cmd, check=True, cwd=work_dir)

    json_path = work_dir / "transcript.json"
    if not json_path.exists():
        # Fall back to any *.json written into the work dir.
        candidates = [p for p in work_dir.glob("*.json")
                      if p.name != "package.json"]
        if not candidates:
            raise RuntimeError(
                "hyperframes transcribe produced no JSON output")
        json_path = candidates[0]
    words = json.loads(json_path.read_text())
    if not isinstance(words, list):
        raise RuntimeError(
            f"unexpected hyperframes output shape: {type(words).__name__}")
    return words, json_path


def words_to_prose(words: list, words_per_para: int = 80) -> str:
    """Convert [{text, start, end, ...}] word objects into paragraphed prose.

    Whisper word tokens already include trailing punctuation/whitespace on
    each word, so naive join gives readable prose. We just collapse stray
    multi-spaces and chunk by ~N words at sentence boundaries.
    """
    raw = "".join(
        (w.get("text") if w.get("text", "").startswith((" ", "\n"))
         else " " + w.get("text", ""))
        for w in words
    ).strip()
    # Collapse whitespace; tidy space-before-punctuation
    raw = re.sub(r"\s+", " ", raw)
    raw = re.sub(r"\s+([.!?,;:])", r"\1", raw)

    sentences = re.findall(r"[^.!?]+[.!?]?", raw)
    sentences = [s.strip() for s in sentences if s.strip()]
    paragraphs, buf, count = [], [], 0
    for s in sentences:
        buf.append(s)
        count += len(s.split())
        if count >= words_per_para:
            paragraphs.append(" ".join(buf))
            buf, count = [], 0
    if buf:
        paragraphs.append(" ".join(buf))
    return "\n\n".join(paragraphs)


def write_transcript(out_path: Path, meta: dict, url: str,
                     body: str, info: dict) -> None:
    info_line = " · ".join(f"{k}: {v}" for k, v in info.items())
    out_path.write_text(
        f"# {meta['title']}\n\n"
        f"- Source: {url}\n"
        f"- Channel: {meta['uploader']}\n"
        f"- Duration: {meta['duration']}\n"
        f"- Fetched: {date.today().isoformat()}\n"
        f"- Transcription: {info_line}\n\n"
        f"---\n\n"
        f"{body}\n"
    )


def main() -> int:
    p = argparse.ArgumentParser(
        description=(
            "Transcribe a YouTube video by delegating to hyperframes-media."),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("url", help="YouTube video URL")
    p.add_argument("slug", nargs="?", default=None,
                   help="Output slug (default: <date>-<title-slug>)")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help=("Whisper model — passed to hyperframes. "
                         "Options: tiny.en, base.en, small.en, medium.en, "
                         "large-v3. Default: large-v3."))
    p.add_argument("--language", default=None,
                   help=("ISO code (e.g. en, es, ja). Omit for auto-detect. "
                         "If your audio is not English, do NOT use *.en "
                         "models — they translate instead of transcribing."))
    p.add_argument("--keep-json", action="store_true",
                   help=("Keep transcript.json (word timestamps) alongside "
                         "transcript.md. Useful if you'll feed the same "
                         "video into hyperframes for captioned video later."))
    p.add_argument("--root",
                   default=os.environ.get("DEV_CONTENT_ROOT", DEFAULT_ROOT),
                   help="Studio root (default: $DEV_CONTENT_ROOT or built-in)")
    args = p.parse_args()

    require("yt-dlp")
    require("npx")

    print("→ fetching metadata", file=sys.stderr)
    meta = get_metadata(args.url)
    slug = args.slug or slugify(meta["title"])
    out_dir = Path(args.root) / "trending" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"→ downloading audio: {meta['title']}", file=sys.stderr)
    audio = download_audio(args.url, out_dir)

    print("→ transcribing (delegating to hyperframes-media)", file=sys.stderr)
    try:
        words, json_path = transcribe_via_hyperframes(
            audio, args.model, args.language)
    finally:
        audio.unlink(missing_ok=True)

    body = words_to_prose(words)
    info = {
        "engine": "hyperframes-media (Whisper)",
        "model": args.model,
        "words": len(words),
    }
    if args.language:
        info["language"] = args.language

    transcript_path = out_dir / "transcript.md"
    write_transcript(transcript_path, meta, args.url, body, info)

    if not args.keep_json and json_path.exists():
        json_path.unlink()

    print(f"✓ {transcript_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
