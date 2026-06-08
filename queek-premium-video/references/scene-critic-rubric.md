# Scene critic rubric (per-scene quality gate)

The per-scene gate that lets the agent author one premium scene at a time instead of rushing all of them. A **fresh-context critic subagent** scores each scene's hero frame against the reference it was built from. The builder cannot advance to the next scene until the critic returns PASS.

## Why a separate critic, not self-grading

The agent that just authored a scene is the worst judge of it — it's primed to declare "done" and move on (this is the rush this gate exists to stop). A self-score from the same context inflates: the vo-grade tool taught us a grader that *predicts* quality from inside the work gets gamed. So the critic runs as a **separate agent with clean context** that sees only the reference image, the rendered frame, and this rubric — never the builder's reasoning, effort, or a request to be lenient. It judges the artifact, not the journey.

## The loop (WIP = 1)

```
for each scene N in order:
  build scene N (static layout -> motion, per Plan)
  run HF gate suite (lint · inspect · validate · animation-map)   # mechanical: is it broken?
  snapshot a SEQUENCE across the scene window via HF (NOT one still):
      ~5-7 frames evenly from scene start..end, INCLUDING the entrance and the settle,
      e.g. snapshot --at start, +20%, +40%, +60%, +80%, settle   (HF also writes a contact-sheet)
  ORCHESTRATOR verifies every listed frame BEFORE dispatching the critic:
      each path must exist AND be non-trivial in size (a blank/failed render is a tiny file — size-check it)
      a wrong/typo'd path or a blank frame -> RE-SNAPSHOT (do not dispatch the critic on it)
      after one re-snapshot still missing/blank -> HARD-FAIL the gate (tooling broken); never substitute another frame
      (the critic ALSO halts with "FRAME MISSING" if handed a bad path — but catching it here, before dispatch, is the orchestrator's job; a typo'd path that still returns a verdict is an integrity failure)
  --> CRITIC subagent (fresh context)
        inputs: reference image(s) + the FRAME SEQUENCE (+ contact-sheet) + this rubric + scene's Plan block
        output: VERDICT PASS|FAIL + fails list + fixes
  if FAIL: apply fixes, re-snapshot the sequence, re-critic   (max 3 rounds)
  if still FAIL after 3: escalate to human with the gap list — do NOT pass, do NOT loop
  if PASS: log verdict to TASK.md, advance to N+1
```

**Why a sequence, not a still:** premium lives in the *motion* — a single frozen frame strips out the animation entirely, and a settled frame looks identical whether it animated beautifully or just popped in. You cannot judge motion quality from one still. The sequence lets the critic see the arc: does it actually animate, do entrances stage, does motion register, does it settle cleanly. A still can only verify static qualities (composition, type scale, color, depth, concept) — never motion. (For the highest-stakes scenes, a short rendered clip of the segment beats even a sequence; use it when a sequence is ambiguous.)

**Re-snapshot on fail; never substitute.** If the expected frame isn't there, the gate re-snapshots. It must never judge a *different* frame than the one under test — a verdict about the wrong frame is worse than no verdict. If re-snapshot still fails, the gate hard-fails as a tooling problem, not a scene FAIL. (Note: `hyperframes snapshot` overwrites the snapshots dir each run — capture the whole sequence in ONE command, and re-snapshot the whole set together.)

The human only ever sees scenes that already passed the critic. That is where human intervention drops.

## Invoking the critic

Use the `Agent` tool, `subagent_type: general-purpose`, **fresh each scene** (no shared memory between scenes — a worn-down critic drifts lenient). Hand it a self-contained prompt:

```
You are a premium-video scene critic. Judge ONE scene, shown as a SEQUENCE of frames across
its time window (entrance -> mid -> settle), against the reference it was built from. You did
not build it; you owe it no benefit of the doubt. Be specific and evidence-based. When you
cannot see evidence for a check, mark it FAIL — absence of proof is a fail, not a pass.

Read these files:
- Reference image(s): <paths from the scene's Plan §1 / §6 cited reference>
- Scene frame SEQUENCE (in time order): <list every frame path start..settle> (+ contact-sheet if present)
- Rubric: references/scene-critic-rubric.md
- This scene's intent (Plan §6 block): <paste the scene block — hero frame, technique, layers, on-screen text>

Judge MOTION from how the frames change across the sequence (does it animate, do entrances
stage, does motion register, does it settle cleanly) — NOT from any single frame. Judge static
qualities (composition, type scale, color, depth, concept) from the settle frame.

If any listed frame is missing or unreadable, STOP and report "FRAME MISSING: <path>" — do NOT
judge a different frame, do NOT hunt for a substitute. A verdict about the wrong frame is invalid.

Score every applicable rubric item. Calibrate against the two anchors named in the rubric
(gold pole vs floor pole). Output EXACTLY the verdict format in the rubric. No preamble.
```

The critic reads the images itself — never describe the frames for it. If it reports FRAME MISSING, the gate re-snapshots and re-invokes (per the loop) — it does not accept a verdict built on a substitute frame.

## Calibration anchors (the two poles)

The critic must place the frame between these, not judge in a vacuum:

- **Gold pole (premium):** HyperFrames launch thesis frame (`hyperframes-launches/hyperframes-launch/`) · the `motion.mp4` study frames (`reference_motion_video_study`). Editorial type at scale, real depth, motion that registers at 1920×1080.
- **Floor pole (reject):** a flat Tailwind card grid · a generic centered fade-in · UI **invented from imagination** ("looks-like-Queek" — fake features/screens the product doesn't have) · OR a **static replica of a real screenshot** (accurate but flat, web-scale, motionless — that's just the screenshot, not premium video). This is the F21/F5 failure shape. Note: a *premium, motion-rich elevation of a REAL Queek concept* is the GOLD direction, not the floor — don't confuse "elevated beyond the screenshot" with "synthetic".

A frame closer to the floor than the gold is a FAIL even if every mechanical check passes.

## Rubric — observable, binary, no taste words

Score only what is **visible in the frame**. "Feels premium" is not a check; the items below are.

### Universal (every scene)
1. **Background is a design.md token** — not `#fff`/`#000`/`#333`/framework default. State the hex you see.
2. **Type at video scale** — headline ≥ 60px-equivalent, body ≥ 20px, data labels ≥ 16px, and ≥ the Plan's banded hero size. Tiny web-UI type = FAIL.
3. **Depth where the reference has it** — shadow, glow, layering, or elevation present; not flat color-blocked fills.
4. **Motion registers at scale — judged across the SEQUENCE, never one frame** (per `feedback_amplify_motion`). Compare the frames in time order: things must visibly move/enter/build between them; entrances stage rather than pop; accents/particles ≥ 24px; the scene settles cleanly. If the frames are nearly identical across the window (nothing animates) for a beat that should move = FAIL. A single settled frame can NEVER prove this — if you were given only one frame, FAIL this item and report the sequence is missing.
5. **Every visible element is intentional & placed** — no element clipped off-frame, no overlap collision, no orphan default-styled box.
6. **Brand color discipline** — light/neutral bg, green as accent only (no green section fills), no rogue palette colors.
7. **Not the floor pole** — not a flat card grid, not a generic centered fade, not synthetic looks-like-Queek UI.

### UI-anchored scenes (🎨 / 📺) — add

> **The screenshot anchors CONCEPT, not pixels.** A UI-anchored scene is judged on *concept fidelity + premium elevation*, never on how closely it replicates the source screenshot. The screenshot exists so the AI doesn't invent fake features — it does **not** dictate how the scene should look. The video version is **expected to be a more premium, motion-rich design than the screenshot.** Two failure modes the critic must keep separate:
> - **Replication ≠ pass.** A frame that merely reproduces the screenshot (static table, web-UI type, flat chrome) is NOT a pass — that's just the screenshot, and the screenshot is not premium video. Hold it to the same scale/depth/motion bar (items 2–4) as everything else.
> - **Elevation ≠ fail.** A frame that looks *different from and better than* the screenshot — re-composed, enlarged, given depth and motion, columns dropped, a pill turned into an animated tracker — is CORRECT, not a deviation to penalize. Do not fail a scene for not matching the screenshot's layout.

8. **Concept fidelity (real, not invented)** — the surface represents a *real* Queek concept: real data/states/flow/features that exist in the product (orders, statuses, setup tasks, payments). FAIL only if it invents features, screens, states, or actions the product doesn't have — NOT if it re-composes or elevates the real ones. "Doesn't match the screenshot layout" is not a fail; "shows a feature Queek doesn't have" is.
9. **Premium elevation over the source** — the scene is more premium than a static screenshot would be: type at video scale, real depth, staged motion, cinematic composition (items 2–4 applied to the UI). A frame that looks like a pasted/replicated screenshot (flat, web-scale type, no motion) FAILS this even though it's "accurate".
10. **Real content** — real ₦ amounts and `brand.md` names; no lorem, no placeholder.

### Motion-concept scenes (🟢 / 🔤) — add
11. **Signature device present and central** — the film's signature device carries the beat.
12. **No UI chrome invented** — brand-real content without fabricated product surfaces.

## Legibility vs the contrast linter (do NOT chase WCAG-AA on video)

`hyperframes validate` reports contrast against **WCAG-AA 4.5:1** — the standard for small interactive *web body text*. It is the wrong bar for cinematic video and massively over-flags:
- **White-on-color chips/monograms** (white "OVERDUE" on red, "MO" on a green avatar) get measured against the *page* background, not the chip's own fill → reported as ~1:1. False positives.
- **Intentional muted secondary text** (eyebrows, meta labels, dashboard sub-labels) is *designed* low-contrast for hierarchy and is legible at video scale + brief on-screen time.

A real film commonly shows 500+ such warnings; chasing them to 4.5:1 flattens the muted hierarchy and is impossible for white-on-color. **The scene critic, judging the frame sequence at video scale, is the legibility authority** — if hero/CTA text were genuinely illegible the critic catches it (item 2 type-at-scale). So: treat contrast warnings as **review-only**, fix only text the *critic* flags as illegible, and record in the postmortem "contrast warnings reviewed — N decorative/muted, 0 illegible hero text" rather than driving the count to zero.

## Verdict format (the critic returns exactly this)

```
VERDICT: PASS | FAIL
SCENE: S<n>
SCORE: <passed>/<applicable>
ANCHOR: closer to GOLD | MID | closer to FLOOR
FAILS:
- <item #/name> — <what's wrong in the frame vs the reference> — <concrete fix>
(omit FAILS block only when SCORE is full)
NOTES: <one line — the single biggest lift toward the gold pole>
```

PASS requires **all applicable items pass** AND anchor is GOLD or MID. Any FLOOR anchor = FAIL regardless of item count.

## Iteration cap

3 critic rounds per scene. If still FAIL, stop iterating motion (more attempts won't converge — same lesson as the "three failed snapshots" rule) and escalate to the human with the latest fails list. Escalation is not a pass; the scene stays open.

## TASK.md log (one block, appended as scenes clear)

```markdown
### Scene critic log
| Scene | Rounds | Final verdict | Anchor | Note |
|---|---|---|---|---|
| S1 | 2 | PASS | GOLD | (human-confirmed: taste anchor for the film) |
| S2 | 1 | PASS | MID | |
| S3 | 3 | ESCALATED | FLOOR→MID | type still under reference scale — human reviewing |
```
