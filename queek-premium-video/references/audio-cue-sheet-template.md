# Audio Cue Sheet Template (cut-to-cut approval artifact)

The same cut-to-cut sheet serves **both approval gates** — only the anchor changes:

| Gate | When | Anchor | Why |
|---|---|---|---|
| **Plan approval** | before build, in `plan-template.md` §7.A.4 | **word** ("on 'missing shirt'") | no VO rendered yet — anchoring to seconds would invent precision the render hasn't earned. You're approving the *design*: which effect, what character, what word it hits. |
| **Make Gate 1** | after VO renders + clears `audio-sanity-check` | **second** (`@0.15 · 0.6s`) | the rendered-VO transcript locks real timings. You're confirming the *timing* the design predicted. |

Both are the same table; the plan version's "Cue (word/moment)" column becomes a real "Start" timestamp at Make. This gives one consistent format across the whole flow — the human never has to re-learn the layout.

This Make-phase version is the human-readable companion to `<slug>-audio-timeline.json` (the machine format the video phase consumes). Save to `works/<slug>/audio-cue-sheet.md`.

**Rules for filling the Make version:**
- **All timings transcript-derived.** Run `hyperframes transcribe` on the rendered VO; scene start = first word onset, scene end = last word offset. Never estimate — state "transcript-derived" in the header.
- **VO script first, line by line** — numbered 1..N, no "S" prefix, just the spoken lines, so the human reads the script as one block before the cue breakdown.
- **One row per SFX event** in the cue table. Scene label + range stacked (`S1<br>(0.0–2.8)`) on the scene's first row only; sub-rows (↳) for additional cues within the same scene.
- Mark the **single peak** and the **quiet beat** explicitly.

---

## Template

```markdown
# <Project> — Audio Cue Sheet (for approval)

Bed: `<bed-file>` (<character>), continuous 0–<N>s at ~<X> LUFS under voice. Master: <Y> LUFS · TP <Z> · voice in front.

**Timings are transcript-derived (Whisper word-level on the rendered VO), not guesses.**

## VO script (line by line)

1. <line 1 verbatim>
2. <line 2 verbatim>
3. <line 3 verbatim>
...
N. <final line verbatim>

## Cue-by-cue

| # | Scene<br>(range) | VO words | Effect | Character | Start | Dur | Tracks (on-screen motion) |
|---|---|---|---|---|---|---|---|
| — | all<br>(0.0–<N>) | (full track) | <bed> | <bed character> | 0.00 | <N>s | continuous under voice |
| 1 | S1<br>(0.0–2.8) | <line 1> | <effect> | <character> | 0.15 | 1.2s | <what it tracks> |
| 2 | S2<br>(2.8–7.0) | <line 2> | — bed only — | — | — | — | <why no SFX> |
| 3 | S3<br>(7.1–10.3) | <line 3> | <effect> | <character> | 6.95 | 1.5s | <tracks> |
| 4 | S4<br>(10.3–15.0) | <line 4> | <effect> | <character> | 10.30 | 0.3s | <tracks> |
| 5 | S4 | ↳ <sub-moment> | <effect> | <character> | 12.05 | 0.13s | <tracks> |
| ... | | | | | | | |

**Totals:** <count> SFX events + continuous bed · Peak = #<n> (<scene>, <time>) · Quietest = <scene>
**Motifs:** <name the recurring SFX threads, e.g. progress ticks, channel pops>

## Approval checklist
- [ ] VO wording correct per scene
- [ ] Effect choices fit each scene's motion
- [ ] Timings land on the right words
- [ ] Recurring motifs (build/progress/channel) feel right
- [ ] Peak loudest, rest restrained
- [ ] Bed character right for the film's aesthetic
```

---

## Why this artifact exists

JSON timelines are for the video phase to wire anchors. The human approving the audio needs to *read* what they're signing off — the script as prose, then every effect with its character, length, and the on-screen moment it tracks. Without this, "confirm anchors" is opaque. With it, the human approves a legible cut-to-cut sheet.

Worked example: `works/queek-laundry-demo-30s/audio-cue-sheet.md` (laundry-demo, 2026-05-22).
