#!/usr/bin/env python3
"""sync-check.py — objectively measure audio/visual sync on a rendered master.

Sound-to-motion tightness is a top premium signal, and it is *measurable* — so
it must never cost a paid agent's tokens (§Gate philosophy: tool before agent).
This tool reads facts (ffprobe on the render + the audio-timeline JSON) and
returns PASS/FAIL + a drift table. The agent reads the verdict, not the video.

What it catches:
  1. A/V container desync — audio vs video stream duration + start-time offset
     on the render (the classic "audio drifts from picture" bug).
  2. Duration mismatch — render length vs the locked timeline's duration_s.
  3. Timeline self-consistency — SFX cues / VO windows in-bounds and ordered.
  4. (optional) SFX-leads-visual — with a --visual-events JSON mapping each cue
     to its visual-lock time, verify sound leads vision by ~10-20ms (the ear
     beats the eye; leading audio makes motion feel intentional).

Usage:
  sync-check.py --render master.mp4 --timeline <slug>-audio-timeline.json
  sync-check.py --render master.mp4 --timeline t.json --visual-events ve.json
  sync-check.py --timeline t.json            # timeline self-consistency only

Stdlib + ffprobe (degrades to timeline-only if ffprobe is absent).
Exit 0 = PASS, 1 = FAIL, 2 = could not run.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# tolerances (seconds)
DUR_TOL = 0.15        # render vs timeline duration
AV_OFFSET_TOL = 0.050  # audio/video container offset (50ms)
LEAD_MIN = 0.005      # sound should lead vision by at least 5ms
LEAD_MAX = 0.060      # ...and at most 60ms (beyond = feels detached / late)


def ffprobe_streams(path: Path):
    exe = shutil.which("ffprobe")
    if not exe:
        return None
    try:
        out = subprocess.run(
            [exe, "-v", "error", "-show_entries",
             "stream=codec_type,duration,start_time", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=60,
        )
        data = json.loads(out.stdout or "{}")
    except (subprocess.SubprocessError, json.JSONDecodeError):
        return None
    streams = {}
    for s in data.get("streams", []):
        t = s.get("codec_type")
        if t in ("video", "audio") and t not in streams:
            streams[t] = {
                "duration": float(s.get("duration", 0) or 0),
                "start": float(s.get("start_time", 0) or 0),
            }
    return streams


def main():
    ap = argparse.ArgumentParser(description="Measure A/V sync on a rendered master")
    ap.add_argument("--render", help="path to the rendered .mp4")
    ap.add_argument("--timeline", required=True, help="path to <slug>-audio-timeline.json")
    ap.add_argument("--visual-events", help="optional JSON: {cue_or_scene: visual_lock_at_s}")
    ap.add_argument("--strict", action="store_true", help="treat NOTE-level items as fails")
    args = ap.parse_args()

    tl_path = Path(args.timeline)
    if not tl_path.is_file():
        print(f"sync-check: no such timeline: {tl_path}")
        sys.exit(2)
    try:
        tl = json.loads(tl_path.read_text())
    except json.JSONDecodeError as e:
        print(f"sync-check: bad timeline JSON: {e}")
        sys.exit(2)

    fails, notes, rows = [], [], []
    dur = float(tl.get("duration_s", 0) or 0)
    anchors = tl.get("anchors", []) or []

    # --- 1+2: render container + duration (needs ffprobe + --render) ---
    if args.render:
        rp = Path(args.render)
        if not rp.is_file():
            print(f"sync-check: no such render: {rp}")
            sys.exit(2)
        streams = ffprobe_streams(rp)
        if streams is None:
            notes.append("ffprobe unavailable or failed — skipped container checks")
        else:
            v, a = streams.get("video"), streams.get("audio")
            if not a:
                fails.append("render has no audio stream")
            if v and a:
                offset = abs(v["start"] - a["start"])
                ddiff = abs(v["duration"] - a["duration"])
                rows.append(f"  A/V start offset   {offset*1000:6.0f} ms   "
                            f"(tol {AV_OFFSET_TOL*1000:.0f})")
                rows.append(f"  A/V duration diff  {ddiff*1000:6.0f} ms")
                if offset > AV_OFFSET_TOL:
                    fails.append(f"audio/video start offset {offset*1000:.0f}ms "
                                 f"> {AV_OFFSET_TOL*1000:.0f}ms (container desync)")
                if ddiff > DUR_TOL:
                    fails.append(f"audio/video duration diff {ddiff*1000:.0f}ms")
            if v and dur:
                rdiff = abs(v["duration"] - dur)
                rows.append(f"  render vs timeline {rdiff*1000:6.0f} ms   "
                            f"(render {v['duration']:.2f}s · timeline {dur:.2f}s)")
                if rdiff > DUR_TOL:
                    fails.append(f"render duration {v['duration']:.2f}s != "
                                 f"timeline {dur:.2f}s")
    else:
        notes.append("no --render given — timeline self-consistency only")

    # --- 3: timeline self-consistency ---
    last_end = -1.0
    cue_index = {}
    for an in anchors:
        sc = an.get("scene", "?")
        vs, ve = an.get("vo_start_s"), an.get("vo_end_s")
        if vs is not None and ve is not None:
            if ve < vs:
                fails.append(f"{sc}: vo_end {ve} < vo_start {vs}")
            if dur and ve > dur + 0.01:
                fails.append(f"{sc}: vo_end {ve} past film duration {dur}")
            if vs + 1e-6 < last_end:
                notes.append(f"{sc}: vo_start {vs} overlaps prior window end {last_end:.2f}")
            last_end = max(last_end, ve)
        for cue in an.get("sfx_cues", []) or []:
            at = cue.get("at_s")
            nm = cue.get("name", "?")
            cue_index[(sc, nm)] = at
            if at is None:
                fails.append(f"{sc}: SFX '{nm}' has no at_s")
            elif dur and (at < 0 or at > dur + 0.01):
                fails.append(f"{sc}: SFX '{nm}' at {at}s out of [0,{dur}]")

    # --- 4: SFX leads visual lock (optional) ---
    if args.visual_events:
        vp = Path(args.visual_events)
        if not vp.is_file():
            notes.append(f"--visual-events not found: {vp}")
        else:
            try:
                ve_map = json.loads(vp.read_text())
            except json.JSONDecodeError:
                ve_map = {}
                notes.append("visual-events JSON unreadable — skipped lead check")
            for (sc, nm), at in cue_index.items():
                lock = ve_map.get(nm, ve_map.get(sc))
                if at is None or lock is None:
                    continue
                lead = float(lock) - float(at)  # >0 = sound before vision
                rows.append(f"  {sc} {nm}: lead {lead*1000:+5.0f} ms")
                if lead < LEAD_MIN:
                    fails.append(f"{sc} SFX '{nm}' lands {(-lead)*1000:.0f}ms "
                                 f"AFTER its visual lock (should lead)")
                elif lead > LEAD_MAX:
                    notes.append(f"{sc} SFX '{nm}' leads {lead*1000:.0f}ms "
                                 f"(>{LEAD_MAX*1000:.0f}ms — may feel detached)")

    if args.strict:
        fails.extend(notes)
        notes = []

    print(f"sync-check · {tl_path.name}" + (f" · {Path(args.render).name}" if args.render else ""))
    for r in rows:
        print(r)
    for n in notes:
        print(f"  NOTE  {n}")
    if fails:
        print("\nRESULT: FAIL")
        for f in fails:
            print(f"  ✗ {f}")
        sys.exit(1)
    print("\nRESULT: PASS" + (f"  ({len(notes)} note(s))" if notes else ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
