#!/usr/bin/env python3
"""
Audio sanity check for Queek VO renders.

Catches MECHANICAL failures only — clipping, wildly off loudness, completely
uneven delivery, single-take rushed reads, extreme pace. Does NOT predict
"premium" quality. Premium judgment stays human.

Calibrated 2026-05-21 against:
  PASS anchor: shipper.mp4 (gold-standard launch reference)
  PASS anchor: kokoro-heart-paragraph (user-preferred Kokoro render)
  PASS anchor: sarah-el (EL eleven_v3 with audio tags)
  FAIL anchor: queek-laundry-demo-30s-vo-take3-rejected (LRA 4.0, choppy)

Usage:
  _audio_sanity.py <audio> [--script <txt> | --transcript <json>] [--json]
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


# Only the checks the tool can reliably verify — no middle-range premium prediction.
# Each threshold is a hard failure (not a band). Below threshold = sanity issue.
THRESHOLDS = {
    "lufs_min": -25.0,          # below this = audio is too quiet to be useful at any mix level
    "lufs_max": -8.0,            # above this = audio is louder than any normal master
    "true_peak_max": 1.0,        # above this = real clipping (intersample peaks up to ~+0.5 dBFS are normal)
    "lra_max": 3.5,              # above this = uneven delivery (take3 was 4.0; clean stems are 1.5-3.0)
    "wpm_min": 60,               # below this = drag-speed reading
    "wpm_max": 220,              # above this = rushed read
    "min_pauses_300ms": 1,       # must have ≥1 pause ≥300ms — zero pauses = single-take rush
    "silence_db_stem": -50,      # for VO stems (no music)
}

# Objective master-target spec (pattern-premium-vo). NOT feel prediction —
# these are the loudness/dynamics numbers a premium master is *told* to hit;
# --profile master verifies the finished master actually hit them. Premium
# FEEL remains the ear at Gate 1; this only enforces the published spec.
MASTER_PROFILE = {
    "lufs_lo": -14.0,            # integrated loudness band
    "lufs_hi": -11.0,
    "true_peak_max": 0.0,        # ceiling for a delivered master (tighter than sanity's +1.0)
    "lra_max": 3.0,             # premium dynamic-range ceiling (tighter than sanity's 3.5)
    "min_outro_silence": 0.10,   # ends on a clean silent stop, not a hard mid-sound cut
}


def run_ebur128(audio_path):
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(audio_path),
         "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True
    )
    out = result.stderr[-4000:]
    m_i = re.search(r"I:\s+(-?\d+\.\d+)\s+LUFS", out)
    m_lra = re.search(r"LRA:\s+(-?\d+\.\d+)\s+LU", out)
    m_peak = re.search(r"Peak:\s+(-?\d+\.\d+)\s+dBFS", out)
    return (
        float(m_i.group(1)) if m_i else None,
        float(m_lra.group(1)) if m_lra else None,
        float(m_peak.group(1)) if m_peak else None,
    )


def run_silencedetect(audio_path, threshold_db=-50, min_silence_s=0.3):
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(audio_path),
         "-af", f"silencedetect=noise={threshold_db}dB:d={min_silence_s}",
         "-f", "null", "-"],
        capture_output=True, text=True
    )
    out = result.stderr
    starts = [float(s) for s in re.findall(r"silence_start:\s*(-?\d+\.?\d*)", out)]
    end_matches = re.findall(
        r"silence_end:\s*(-?\d+\.?\d*)\s*\|\s*silence_duration:\s*(\d+\.?\d*)", out
    )
    silences = []
    for i, (e, dur) in enumerate(end_matches):
        if i < len(starts):
            silences.append((starts[i], float(e), float(dur)))
    return silences


def get_duration(audio_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def count_words(text):
    text = re.sub(r"\[[^\]]+\]", "", text)
    words = re.findall(r"\b[\w'₦]+\b", text, re.UNICODE)
    return len(words)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("audio", help="audio file path (mp3/wav)")
    ap.add_argument("--script", help="text file of VO script (for WPM)")
    ap.add_argument("--transcript", help="hyperframes transcript.json (for WPM)")
    ap.add_argument("--json", action="store_true", help="structured JSON output")
    ap.add_argument("--profile", choices=["sanity", "master"], default="sanity",
                    help="sanity (default, mechanical floor) or master (objective premium loudness spec)")
    args = ap.parse_args()

    audio = Path(args.audio)
    if not audio.exists():
        print(f"ERROR: audio not found: {audio}", file=sys.stderr)
        sys.exit(2)

    duration = get_duration(audio)
    lufs, lra, true_peak = run_ebur128(audio)
    silences = run_silencedetect(audio)
    pauses_300 = [s for s in silences if s[2] >= 0.3]
    pauses_600 = [s for s in silences if s[2] >= 0.6]
    outro_silence = 0.0
    for s in silences:
        if s[1] >= duration - 0.15:
            outro_silence = s[2]
            break
    speech_duration = duration - sum(s[2] for s in silences if s[1] < duration - 0.15)

    wpm = None
    word_count = None
    if args.transcript and Path(args.transcript).exists():
        transcript = json.loads(Path(args.transcript).read_text())
        words = transcript if isinstance(transcript, list) else transcript.get("words", [])
        word_count = len(words)
        if words:
            word_speech_time = sum(w.get("end", 0) - w.get("start", 0) for w in words)
            if word_speech_time > 0:
                wpm = round(word_count / word_speech_time * 60)
    elif args.script and Path(args.script).exists():
        script_text = Path(args.script).read_text()
        word_count = count_words(script_text)
        if speech_duration > 0:
            wpm = round(word_count / speech_duration * 60)

    # Each check is binary: pass or fail. No middle bands.
    checks = []

    # LUFS extreme check (only fires at extremes)
    if lufs is None:
        checks.append(("loudness", "SKIP", "ffmpeg could not measure"))
    elif lufs < THRESHOLDS["lufs_min"]:
        checks.append(("loudness", "FAIL", f"{lufs:.1f} LUFS — too quiet (extreme < {THRESHOLDS['lufs_min']})"))
    elif lufs > THRESHOLDS["lufs_max"]:
        checks.append(("loudness", "FAIL", f"{lufs:.1f} LUFS — too loud (extreme > {THRESHOLDS['lufs_max']})"))
    else:
        checks.append(("loudness", "PASS", f"{lufs:.1f} LUFS"))

    # True peak (real clipping only — not intersample)
    if true_peak is None:
        checks.append(("clipping", "SKIP", "ffmpeg could not measure"))
    elif true_peak > THRESHOLDS["true_peak_max"]:
        checks.append(("clipping", "FAIL", f"{true_peak:.1f} dBFS — true clipping (> {THRESHOLDS['true_peak_max']} dBFS)"))
    else:
        checks.append(("clipping", "PASS", f"{true_peak:.1f} dBFS"))

    # LRA uneven delivery
    if lra is None:
        checks.append(("evenness", "SKIP", "ffmpeg could not measure"))
    elif lra > THRESHOLDS["lra_max"]:
        checks.append(("evenness", "FAIL", f"{lra:.1f} LU — uneven delivery (> {THRESHOLDS['lra_max']} LU)"))
    else:
        checks.append(("evenness", "PASS", f"{lra:.1f} LU"))

    # WPM extreme check (only when script/transcript supplied)
    if wpm is None:
        checks.append(("pace", "SKIP", "supply --script or --transcript"))
    elif wpm < THRESHOLDS["wpm_min"]:
        checks.append(("pace", "FAIL", f"{wpm} WPM — drag-speed (extreme < {THRESHOLDS['wpm_min']})"))
    elif wpm > THRESHOLDS["wpm_max"]:
        checks.append(("pace", "FAIL", f"{wpm} WPM — rushed (extreme > {THRESHOLDS['wpm_max']})"))
    else:
        checks.append(("pace", "PASS", f"{wpm} WPM"))

    # Pauses present (zero = rushed single-take)
    if len(pauses_300) >= THRESHOLDS["min_pauses_300ms"]:
        checks.append(("pauses_present", "PASS", f"{len(pauses_300)} pauses ≥ 300ms"))
    else:
        checks.append(("pauses_present", "FAIL", f"0 pauses detected — single-take rushed read"))

    # Master profile (objective spec compliance — only with --profile master).
    # Verifies the finished master hit the published loudness/dynamics target;
    # NOT a premium-feel predictor (that's the ear at Gate 1).
    if args.profile == "master":
        mp = MASTER_PROFILE
        if lufs is None:
            checks.append(("master_loudness", "SKIP", "ffmpeg could not measure"))
        elif not (mp["lufs_lo"] <= lufs <= mp["lufs_hi"]):
            checks.append(("master_loudness", "FAIL",
                           f"{lufs:.1f} LUFS — outside master band [{mp['lufs_lo']}, {mp['lufs_hi']}]"))
        else:
            checks.append(("master_loudness", "PASS", f"{lufs:.1f} LUFS in band"))

        if true_peak is None:
            checks.append(("master_truepeak", "SKIP", "ffmpeg could not measure"))
        elif true_peak > mp["true_peak_max"]:
            checks.append(("master_truepeak", "FAIL",
                           f"{true_peak:.1f} dBFS — over master ceiling {mp['true_peak_max']} dBFS"))
        else:
            checks.append(("master_truepeak", "PASS", f"{true_peak:.1f} dBFS"))

        if lra is None:
            checks.append(("master_dynamics", "SKIP", "ffmpeg could not measure"))
        elif lra > mp["lra_max"]:
            checks.append(("master_dynamics", "FAIL",
                           f"{lra:.1f} LU — over premium LRA ceiling {mp['lra_max']} LU"))
        else:
            checks.append(("master_dynamics", "PASS", f"{lra:.1f} LU"))

        if outro_silence >= mp["min_outro_silence"]:
            checks.append(("master_clean_stop", "PASS", f"{outro_silence:.2f}s clean tail"))
        else:
            checks.append(("master_clean_stop", "FAIL",
                           f"{outro_silence:.2f}s — no clean silent stop (hard cut mid-sound)"))

    # Verdict
    fails = [c for c in checks if c[1] == "FAIL"]
    if fails:
        verdict = "FAIL"
    else:
        verdict = "PASS"

    if args.json:
        out = {
            "audio": str(audio),
            "profile": args.profile,
            "verdict": verdict,
            "duration_s": round(duration, 2),
            "metrics": {
                "lufs": lufs, "lra": lra, "true_peak_dbfs": true_peak,
                "wpm": wpm, "word_count": word_count,
                "pauses_300ms_count": len(pauses_300),
                "pauses_600ms_count": len(pauses_600),
                "outro_silence_s": round(outro_silence, 2),
                "speech_duration_s": round(speech_duration, 2),
            },
            "checks": [{"name": c[0], "status": c[1], "detail": c[2]} for c in checks],
        }
        print(json.dumps(out, indent=2))
        return

    sym = {"PASS": "✓", "FAIL": "✗", "SKIP": "·"}
    print()
    print("Audio Sanity Check")
    print("═" * 56)
    print(f"File:      {audio.name}")
    print(f"Duration:  {duration:.2f}s"
          + (f"  ·  Words: {word_count}" if word_count else ""))
    print()
    print("Sanity checks (FAIL = mechanical extreme; PASS = within reason)")
    for name, status, detail in checks:
        print(f"  {sym[status]} {name:18} {detail}")
    print()
    print("Informational (no gating — for context)")
    print(f"    pauses ≥ 300ms:  {len(pauses_300)}")
    print(f"    pauses ≥ 600ms:  {len(pauses_600)}")
    print(f"    outro silence:   {outro_silence:.2f}s")
    if wpm is not None:
        print(f"    speech ratio:    {speech_duration/duration*100:.0f}%")
    print()
    print(f"Verdict: {verdict}")
    if verdict == "FAIL":
        for c in fails:
            print(f"  → {c[0]}: {c[2]}")
    else:
        print("  → no mechanical issues detected. Premium judgment is ear's call.")
    print()


if __name__ == "__main__":
    main()
