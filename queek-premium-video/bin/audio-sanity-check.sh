#!/usr/bin/env bash
# audio-sanity-check.sh — catches mechanical audio failures only
# Does NOT predict premium quality. Premium = ear judgment.
#
# Usage: audio-sanity-check.sh <audio.mp3> [--script script.txt | --transcript transcript.json] [--json]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$SCRIPT_DIR/_audio_sanity.py"

if [ ! -f "$PY" ]; then
  echo "ERROR: _audio_sanity.py not found at $PY" >&2
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg not installed. brew install ffmpeg" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not installed" >&2
  exit 1
fi

exec python3 "$PY" "$@"
