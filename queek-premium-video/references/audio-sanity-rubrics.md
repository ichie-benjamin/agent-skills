# Audio Sanity Check Rubrics

`bin/audio-sanity-check.sh` — catches mechanical audio failures. **Does NOT predict premium quality.** Premium judgment stays with the ear.

## What it checks

Only 5 hard checks. No middle-range premium prediction. Each fires FAIL only at extremes.

| Check | FAIL threshold | What it catches |
|---|---|---|
| **loudness** | `LUFS < -25` OR `LUFS > -8` | Audio too quiet to use, or louder than any normal master |
| **clipping** | `true peak > +1.0 dBFS` | Real clipping (intersample peaks up to ~+0.5 dBFS are normal — relaxed from earlier) |
| **evenness** | `LRA > 3.5 LU` | Uneven delivery — quiet-then-loud (take3 was 4.0 — rejected) |
| **pace** | `WPM < 60` OR `WPM > 220` (only if `--script`/`--transcript` supplied) | Drag-speed or rushed reading |
| **pauses_present** | `0 pauses ≥ 300ms detected` | Single-take rushed read with no breath beats |

## `--profile master` (objective master-spec compliance — NOT premium prediction)

Default `--profile sanity` is the mechanical floor above (wide thresholds on raw VO). `--profile master` adds four checks that verify a **finished master** hit the published premium loudness spec from `pattern-premium-vo.md` — the numbers the master is *told* to hit, now enforced by tool instead of asserted:

| Check | FAIL threshold |
|---|---|
| `master_loudness` | LUFS outside `[-14, -11]` |
| `master_truepeak` | true peak > `0.0 dBFS` |
| `master_dynamics` | LRA > `3.0 LU` |
| `master_clean_stop` | outro silence < `0.10s` (hard cut mid-sound) |

This is **spec compliance, not feel prediction** — it does not repeat the v1 mistake of predicting premium from metrics. It only confirms the delivered master meets its own target; whether it *feels* premium stays the ear at Gate 1. Run it on the mastered file, not raw stems.

## What it does NOT check

- **Pause count bands.** 1 pause vs 9 pauses both PASS — premium feel varies.
- **Premium quality.** That's an ear judgment. Tool can't predict.
- **Pause distribution.** Where pauses land matters but isn't measured.
- **Pronunciation accuracy.** Whisper-based check would need adding (Phase 2).
- **Master-mode pause detection.** Pauses get masked by music beds — unreliable.

## Calibration anchors (2026-05-21)

Validated against 5 files:

| Anchor | Expected | Result |
|---|---|---|
| `shipper.mp4` audio (gold-standard launch reference) | PASS | ✓ PASS |
| `kokoro-heart-paragraph.wav` (user-preferred render) | PASS | ✓ PASS |
| `kokoro-heart.wav` (Kokoro blob, snappier) | PASS | ✓ PASS |
| `sarah-el.mp3` (EL eleven_v3 with audio tags) | PASS | ✓ PASS |
| `queek-laundry-demo-30s-vo-take3-rejected.mp3` (LRA 4.0, choppy) | FAIL | ✓ FAIL |

## Calibration history

- **2026-05-21 v1 (deprecated):** Pause-count rubric tried to predict premium. FAILED shipper.mp4 (gold standard). User-preferred render also FAILED for "too many pauses." Rubric was inverted relative to ear preference.
- **2026-05-21 v2 (current):** Dropped pause-count bands. Kept only metrics where extreme = real failure: loudness, clipping, evenness, pace, pauses-present. Pause counts now informational only.

## When to update the rubric

If a future render PASSES the tool but the ear rejects it → record the failure, identify the mechanical signal that should have caught it (or accept that the failure is taste-only and the tool can't catch it). Don't add bands back — that's how v1 went wrong.

If a future render FAILS the tool but the ear accepts it → record, check the metric that fired, decide whether to relax the threshold OR if the metric is now mis-calibrated. Add the audio file to the PASS anchors and re-test the tool.

## Usage

```bash
# SKILL_DIR = this skill's install directory (the dir holding SKILL.md). Never hardcode ~/.claude.
"$SKILL_DIR/bin/audio-sanity-check.sh" <audio.mp3> \
  [--script script.txt | --transcript transcript.json] \
  [--json]
```

WPM check only fires if `--script` or `--transcript` is supplied AND the script matches the audio. Don't pass an unrelated script — produces false rushed-pace fails.

## Integration with skill

At Make-phase Gate 1 (Audio), after VO renders:

```bash
"$SKILL_DIR/bin/audio-sanity-check.sh" \
  works/<slug>/deliverables/audition-<date>/kokoro-heart.wav \
  --script works/<slug>/voice-script.txt
```

PASS → forward to ear-test. FAIL → fix the specific mechanical issue. Document grader output in `works/<slug>/TASK.md` Notes.

**Important:** PASS does NOT mean premium. PASS means no mechanical extremes detected. The ear is still the deciding judge.
