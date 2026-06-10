# Scene critic rubric (per-scene quality gate)

Fresh-context critic subagent scores each scene against the reference it was
built from. Builder cannot advance until critic returns PASS.

The critic sees only: reference image(s), the 5-frame sequence + contact
sheet, this rubric, the scene's Plan §6 block (standalone mode: the
project's scene spec if one exists; otherwise reference + rubric universal
items only — motion items judged from the frame sequence). Never the builder's
reasoning, effort, or request to be lenient. Judges the artifact, not the
journey.

## The loop (WIP = 1)

```
for each scene N in order:
  build scene N (static layout -> motion, per Plan)
  PRE-CRITIC MECHANICAL GATE (cheap, blocks visual critic):
      npx hyperframes lint --json       -> if errorCount > 0, auto-FAIL with findings
      npx hyperframes inspect --json    -> if overflow on hero element, auto-FAIL
      (no critic dispatched until both pass)
  snapshot 3 frames via HF: --at start, mid, settle
  ORCHESTRATOR verifies every frame exists AND is non-trivial in size:
      missing/blank -> re-snapshot
      still missing after 1 re-snapshot -> HARD-FAIL the gate (tooling broken)
  if REPLICA MODE (project cites a ref video):
      runtime auto-injects ref-<slug>-source/frames/scene-NN-{entry,mid,settle}.png
      into the critic prompt — Dara does NOT attach them manually
  --> dispatch CRITIC subagent (Agent tool, subagent_type=scene-critic)
        inputs: refs + 3-frame sequence + contact-sheet + this rubric + Plan §6
        output: VERDICT PASS|FAIL + score + anchor + fails + fixes
  if FAIL: apply fixes, re-snapshot, re-critic (max 5 rounds — server-enforced
           in mcp_server.py; 6th dispatch denied by policy)
  if convergence stalls (PASS-count flat/dropping 2 rounds in a row): escalate
                                                                       early
  if PASS: log to TASK.md, advance to N+1
```

**Never substitute frames.** If a listed frame is missing, re-snapshot — do
NOT judge a different frame. A verdict on the wrong frame is invalid.
HF overwrites the snapshots dir per run, so capture the whole sequence in
ONE command and re-snapshot the whole set together.

**Why a sequence not a still:** premium is in the motion. A settled frame
alone cannot prove things actually animated. Judge motion from how frames
change across the sequence; judge static qualities from the settle frame.

## Calibration anchors

- **GOLD pole:** HyperFrames launch thesis frame
  (`hyperframes-launches/hyperframes-launch/`) · `motion.mp4` study frames
  (`reference_motion_video_study`). Editorial type at scale, real depth,
  motion that registers at 1920×1080.
- **FLOOR pole:** flat Tailwind card grid · generic centered fade-in · UI
  invented from imagination ("looks-like-Queek" fake features) · OR a
  static replica of a real screenshot (accurate but flat, web-scale,
  motionless). All FLOOR shapes = FAIL even if mechanical checks pass.

A premium motion-rich elevation of a REAL Queek concept is GOLD direction,
not FLOOR — "elevated beyond the screenshot" ≠ "synthetic invented UI".

When the creative-repo gold poles aren't on disk (standalone mode outside
the repo), the scene's own cited reference is the GOLD pole.

## Universal items (every scene)

Score only what is **visible in the frame(s)**. "Feels premium" is not a
check.

1. **Background is a design.md token** — not `#fff`/`#000`/`#333`/framework
   default. State the hex you see.
2. **Type at video scale** — headline ≥ 60px-equivalent, body ≥ 20px, data
   labels ≥ 16px, AND ≥ the Plan's banded hero size. Web-UI type = FAIL.
3. **Depth where reference has it** — shadow, glow, layering, elevation.
   Flat color-blocked fills when the reference shows depth = FAIL.
4. **Motion registers across the 3-frame sequence (entry → mid → settle)**
   — compare frames in time order. The hero element must visibly change
   between entry and mid (first-half motion) AND between mid and settle
   (second-half motion or hold). If entry and mid look pixel-similar on the
   hero element when the Plan says motion happens in that window = FAIL.
   If mid and settle look identical when the Plan calls for ambient
   float / breathing / sustained motion = FAIL. Entrances stage rather
   than pop; accents/particles ≥ 24px. A still frame can NEVER prove
   this — if you were given fewer than 2 frames, FAIL this item and
   report sequence missing.
5. **Every element intentional + placed** — no clipped-off-frame, no
   overlap collision, no orphan default-styled box.
6. **Brand color discipline** — colors per the resolved brand/design spec
   (Queek default: light/neutral bg, green as accent only, no green section
   fills); no rogue palette colors. If no spec resolved, judge against the
   reference's own palette and say so.
7. **Not the FLOOR pole** — not a flat card grid, not a generic centered
   fade, not synthetic looks-like-Queek UI.

## UI-anchored scenes (🎨 / 📺) — add items 8-10

The screenshot anchors **CONCEPT, not pixels**. A UI-anchored scene is
judged on *concept fidelity + premium elevation*, never on how closely it
replicates the source screenshot. Two failure modes the critic keeps
separate:

- **Replication ≠ pass.** A frame that merely reproduces the screenshot
  (static table, web-UI type, flat chrome) is NOT a pass — it's just the
  screenshot. Apply items 2-4 the same as any other scene.
- **Elevation ≠ fail.** A frame that looks different from AND better than
  the screenshot (re-composed, enlarged, given depth + motion, columns
  dropped, pill turned into an animated tracker) is CORRECT.

8. **Concept fidelity (real, not invented)** — the surface represents a
   *real* Queek concept: real data/states/flow/features (orders, statuses,
   setup tasks, payments). FAIL only if it invents features, screens,
   states, or actions the product doesn't have — NOT if it re-composes or
   elevates the real ones.
9. **Premium elevation over the source** — items 2-4 applied to the UI:
   type at video scale, real depth, staged motion, cinematic composition.
   A pasted/replicated screenshot (flat, web-scale type, no motion) FAILS
   this even though "accurate."
10. **Real content** — real amounts + names from the resolved brand source
    (`memories/brand.md` in the creative repo; the project's design/brand
    spec elsewhere). No lorem, no placeholder.

## Motion-concept scenes (🟢 / 🔤) — add items 11-12

11. **Signature device present + central** — the film's signature device
    carries the beat in this scene.
12. **No UI chrome invented** — brand-real content without fabricated
    product surfaces.

## REPLICA MODE — add items 13-14 (only when ref video is cited)

13. **Composition relates to reference at matching timestamp.** Compare
    Dara's snapshot at t=X to the reference's frame at t=X (auto-injected).
    Same staging class, same element count + arrangement, same hero
    placement. "Looks premium but unrelated to reference" = FAIL.
14. **Text-animation pattern matches reference.** If the reference's entry
    frame shows partial text reveal (character-by-character build), Dara's
    +25% frame MUST show partial reveal too — NOT settled-full text.
    Count visible chars: if reference at t=0.2s shows ~N chars and Dara's
    matching frame shows all chars, FAIL (wrong animation primitive — fade
    or slide-in instead of type-on).
15. **SFX wired from library, not baked.** If `works/<slug>/sfx-picks.md`
    exists, `composition/index.html` MUST contain
    `<audio src="files/audio/<file>.mp3">` tags per picked onset — NOT a
    single baked `master.mp3`. Library citation is auditable; baked master
    isn't. Check by reading the composition source.

## Legibility vs the contrast linter (do NOT chase WCAG-AA on video)

`hyperframes validate` reports contrast against WCAG-AA 4.5:1 — the
standard for small interactive web body text, wrong bar for cinematic
video. False positives include white-on-color chips/monograms (measured
against page bg, not chip fill → ~1:1) and intentional muted secondary
text (designed low-contrast for hierarchy).

The scene critic, judging the frame sequence at video scale, is the
legibility authority — if hero/CTA text is illegible, item 2 catches it.
Treat contrast warnings as review-only; fix only text the *critic* flags
as illegible.

## Verdict format (return EXACTLY this — no preamble)

```
VERDICT: PASS | FAIL
SCENE: S<n>
SCORE: <passed>/<applicable>
ANCHOR: closer to GOLD | MID | closer to FLOOR
FAILS:
- <item #/name> — <what's wrong in the frame vs the reference> — <concrete fix>
(omit FAILS block only when SCORE is full)
NOTES: <one line — the single biggest lift toward GOLD>
```

PASS requires **all applicable items pass** AND anchor is GOLD or MID.
Any FLOOR anchor = FAIL regardless of item count.

If a frame is missing or unreadable, STOP and return exactly:
`FRAME MISSING: <path>`. Do NOT judge a different frame.

When you cannot see evidence for a check, mark it FAIL — absence of proof
is a fail, not a pass.

## TASK.md log (append per scene)

```markdown
### Scene critic log
| Scene | Rounds | Final verdict | Anchor | Note |
|---|---|---|---|---|
| S1 | 2 | PASS | GOLD | (human-confirmed: taste anchor for the film) |
| S2 | 1 | PASS | MID | |
| S3 | 5 | ESCALATED | FLOOR→MID | type still under reference scale — human reviewing |
```
