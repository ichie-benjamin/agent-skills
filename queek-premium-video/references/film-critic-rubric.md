# Film critic rubric (whole-film quality gate)

The scene gates prove each scene is sound and premium *in isolation*. They
cannot see what only exists across the whole film: does the arc build, does it
drag, do scenes flow, does the hook hold, does it read as a top-studio product
end to end. This gate is that watch — the last gate before Close, on the
**finished rendered master**.

A fresh-context critic subagent (`Agent`, `subagent_type: general-purpose`)
watches the film as an experience and returns a verdict. Floor, not ceiling
(§Gate philosophy): it fails only films that are weak, that drag, that don't
land — never films that are bold or unconventional.

## Cost discipline (read first — this is the most expensive gate)

- **Runs ONCE, on the finished master** — never iteratively, never on drafts.
  A FAIL routes back to the phase that owns the gap (story → Plan, motion →
  the scene, audio → Audio); it does not loop here.
- **Inputs are sampled, not the raw video.** Feed the critic:
  - a **frame strip** sampled at ~2 fps across the whole film (one `ffmpeg`
    call: `-vf fps=2` → a numbered sequence; ~120 frames for a 60s film),
  - the **rendered audio track** (or its transcript + the `audio-cue-sheet`
    if audio is judged separately at Gate 1),
  - the Plan's **creative-bet header + arc** (the intent it's judged against).
  A 2 fps strip + audio is enough to judge pacing, flow, hook, and sync;
  it is a fraction of the tokens of frame-by-frame, and catches everything
  this gate exists for. Do not send the full-rate render.
- **Don't re-judge scenes.** Per-scene premium was already settled by the
  scene-critic. This gate judges *the film*, not the scenes — if it finds a
  single-scene defect, that's a scene-critic miss to note, not this gate's job.

## The dimensions (0 / 1 / 2 each — premium = no zeros AND ≥ 12/16)

Judge from the frame strip + audio, against the Plan's arc. Score only what is
observable across the sequence.

1. **Hook holds in 3s, muted.** First ~3s (first ~6 frames) — would a viewer
   scrolling MUTED stop? A cold, slow, or text-only-explained open = FAIL.
2. **Energy arc lands.** The peak beat reads as the peak (biggest, loudest,
   most motion); the quiet beat actually drops. A flat film with no build,
   or a peak that doesn't out-scale its neighbours, = FAIL. Compare against
   the Plan's declared `Arc`.
3. **No drag.** No stretch where nothing changes for too long, no beat held
   past its read, no dead air that isn't a deliberate quiet beat. Pacing
   matches the type (short-form: payoff < 3s; long-form < 8s).
4. **Scene flow.** Cuts/transitions connect — no jarring tonal jump, no two
   adjacent scenes that look like different films, no transition that fights
   the motion. The film reads as one piece.
5. **Sync feels tight.** Sound and motion land together across the film (the
   objective check is `bin/sync-check.py`; this is the felt-rhythm read on
   top of it). Visible drift between a hit and its visual = FAIL.
6. **Consistency.** One type system, one motion vocabulary, one palette
   across all scenes — not eight designers. Token/scale drift = FAIL.
7. **The close lands.** Final ~1s holds; the CTA is legible muted at
   thumbnail; it doesn't trail off or cut dead early.
8. **Top-studio bar (gestalt).** Watched end to end, would this pass as a
   top-studio product? This is the one holistic item — if 1–7 pass but the
   whole still feels amateur, that's a real FAIL; say why in one line.

## Verdict format (return EXACTLY this)

```
FILM VERDICT: PASS | FAIL
SCORE: <passed>/<applicable ×2>
FAILS:
- <item #/name> — <what's wrong across the film> — <which phase owns the fix: Plan/scene/Audio>
(omit FAILS block only when SCORE is full)
BIGGEST LIFT: <one line — the single change that most raises the whole film>
```

PASS requires **no zeros AND ≥ 12/16**. A FAIL names the owning phase so the
fix routes there — this gate diagnoses, it does not patch.

If the frame strip or audio is missing/unreadable, STOP and return
`INPUT MISSING: <what>`. Do not judge a partial film.

## Where it sits

Flow step 7 (Review), after both masters render, before Close. It is the
film-level sibling of the per-scene scene-critic: scene-critic = is each scene
premium; film-critic = is the *film* premium. Human eyes are still the final
backstop, but they are now spent on a film the critic already cleared — taste
on the ceiling, not floor-catching.
