# Video Layout Guide

> **Portable, reusable guide for building premium HTML-based video** (HyperFrames runtime). Distilled from hard-won production lessons across the dev_content + Queek video builds. **Read this before any video build** — by Claude or by another project. It is the single source of truth for *placement, animation, transitions, pacing, and render-safety*. Project-specific bits (palette, signature device) are marked **[INSTANCE]** — swap them per project; everything else is universal.
>
> Companion gates: a fresh-context **scene critic** scores each scene ≥9 before it ships; nothing reaches the client below that bar. The builder may never self-grade.

---

## 0. The bar (calibration — make it unambiguous)

| Pole | Score | Why |
|---|---|---|
| Abstract motion-graphics slideshow, human absent, decorative stock | **1/10** | "dull… PowerPoint." The failure to never repeat. |
| Sparse beats, long static holds, clean typography only | **0.5/10** | "8 components for 70+ seconds, too dull." |
| theMITmonk "7 Ways" (talking-head spine + real UI + literal b-roll + bold cards) | **8/10** | Balanced premium explainer grammar. |
| **Our target** | **10/10** | Better and more premium than mitmonk. |

**The one-line law:** a premium video is **a sequence of deliberately-chosen video treatments, one per beat, picked from that beat's content** — never a motion-graphics slideshow with a face in the corner.

---

## 1. PLACEMENT / LAYOUT GUIDE

### 1a. The first step (most-missed): read the beat, pick the treatment from its CONTENT
Map the treatment to **what the beat is about**:

| The beat is about… | Treatment |
|---|---|
| **Concept / explanation / the thesis** (how RAG works, "AI is confidently wrong", the signature idea) | **Premium motion design** (the signature device, animated diagram, particles) + supporting stock. NOT static text, NOT a talking head. |
| **Personal / first-person** ("I'd been…", "the playbook I wish I'd had") | **Talking-head** (face-cam). |
| **A real thing / product moment** (an error, a chat answer, a tool, code) | **Real UI / screen-recording.** Real software > abstract diagram. |
| **Stakes / world** (students, servers, production) | **Literal b-roll** — each clip illustrates ONE concrete thing. |

> Static on-screen text is the **last resort** — only a short punch line, never a 10s held block, never on a concept beat that should move.

### 1b. The four treatments (the layout vocabulary)
1. **Full-screen video** — footage fills the frame, text/motion overlaid.
2. **Wide centered card** — a wide ~16:9 card centered with margin on the background (NOT full-screen, NOT a small floating card).
3. **Split** — video on one side + motion-graphics/text on the other.
4. **Talking-head** — face-cam; for the personal / hand-explaining / demonstrating beats.

Rules:
- **Vary the talking-head treatments** across the piece (full-screen ↔ wide-centered-card ↔ split). Include **full-frame** talking-head, not only cards.
- **Prefer talking-head over long on-screen text** — convert first-person text-heavy beats to the person talking.
- **Motion-graphics is connective tissue**, woven between the others — never the whole film.
- All talking-head frames **properly aligned** (no off-center placeholders).

### 1c. Face-cam slot system (when the face is filmed later)
Reserve a **labelled, positioned, masked slot** in each scene's sub-composition (a `BENNY-CAM`-style placeholder div: rounded rect, dashed border, label = position + the exact VO line + duration). Build the motion *around* the slot so real footage drops into the same box later. Keep it **sparse** — ~1 short slot per scene, first-person lines only. Positions to rotate: right-third / left-third / bottom-third / centered-on-bg / straight-to-camera / hands-demo. **Apply all camera animation to the placeholder too** so the critic judges the *usage*, not a gradient.

### 1d. The visual grammar to match (5 pillars, from the 8/10 reference)
1. **Talking head = the spine** (~50%+), warmly lit, real hand gestures — not a corner inset.
2. **Real screen recordings** do the teaching.
3. **B-roll is literal + purposeful** — one concrete idea per clip.
4. **Bold clean text cards** — one big concept on a soft surface, not tiny crawling captions.
5. **Brand/logo cards + one recurring framework motif.**

---

## 2. ANIMATION GUIDE

### 2a. Every video element is camera-animated (non-negotiable)
A static clip is not premium. **Every** element (talking-head, b-roll, card, full-screen) gets a named camera move, matched to the beat:
- **zoom in · zoom out · move right · move to center** (Ken Burns / push-in / parallax).

### 2b. Use a NAMED motion vocabulary — never "generic fade-in"
Reach for these, not opacity fades:
- **cam-push** — slow camera push-in on the hero (scale 1 → 1.06 over the beat).
- **tilt-rake** — slight 3D tilt/rotate on entrance (rotateX/Y a few° → 0).
- **shimmer-sweep** — a light/gradient band sweeps across type/surface on reveal.
- **stamp-thunk** — element slams in (overshoot scale + an impact SFX 10–20ms early).
- **pulse-halo** — a glow/halo pulses behind the hero word/element.
- **shimmer** — multi-stop warm gradient shimmer on hero type.

### 2c. Motion must REGISTER at 1920×1080
Subtle motion reads as NO motion at video scale. Hard rules:
- Particles **≥24px head + ≥80px gradient tail** (4–10px = invisible).
- **≥3 simultaneous** moving packets per stream — not a lone drifter.
- **Ambient breathing** on otherwise-static elements (slow scale/opacity pulse) so nothing is dead-still.
- Accents ≥24px.

### 2d. Motion density (never a static slideshow)
- **Continuous motion under everything** — ambient drift, parallax, particle beds, camera moves, a signature element that never freezes.
- **No held static frame longer than ~1.5s.**
- Density target: a 65s VO should carry **~20–30 visual events**, not ~10.
- Real **stock clips** (classrooms, code-on-screen, servers, hands typing) graded/duotone to the palette so they read cohesive, not random.
- **Animated illustrations** (real animated marks), not static CSS shapes. ⚠ See §6 on Lottie — build the animated mark *natively* because Lottie does not render in HyperFrames.

### 2e. Entrances + eases
- **Entrances are dynamic** — overshoot / tilt / scale on `back.out`, parallax. Flat fades = "PowerPoint."
- **Eases are snappy** — `power3`/`power4`, `expo`, `back`. Not slow `sine` drifts. Movement with intent.

### 2f. Title reveal system (every scene opens on its title — vary the effect)
Open each scene on its title as a chapter card; **rotate the reveal, don't repeat**:
- **Typewriter / type-on** (mono + caret) — keep this for the intro/case-file titles; don't drop it when varying others.
- **Per-word kinetic reveal** (serif, breath-hold on the hero word).
- **Marker-sweep / underline highlight.**
- **Sketch / draw-on / distortion reveal.**

Pull exact effects from the `/hyperframes` references (`references/techniques.md`, `typography.md`, captions/dynamic-techniques, `references/transitions/`).

---

## 3. TRANSITIONS GUIDE

- **Use the HyperFrames transition catalog, NOT opacity crossfades.** Available families (`/hyperframes` → `references/transitions/`): **push · cover · dissolve · scale · 3d · light · distortion · radial · grid · blur · mechanical.**
- Each beat-to-beat cut uses a **real transition** (push-wipe, dissolve, scale-out, light-leak), chosen to fit the cut.
- **Transitions handle exits.** Rule: *"no exit animations except the final scene — transitions handle exits."* Don't hand-animate every element out; let the transition carry the cut.

---

## 4. PACING / TIMING GUIDE

Pacing is what separates premium from amateur. The #1 crime: *"text on screen staying longer than it reads."*
1. **Text leaves when read.** A line stays only ~**0.3s per word + ~0.5s**, then it's OUT. Same for titles/captions/labels. Lingering text is THE worst amateur tell.
2. **Nothing overstays.** No motion runs longer than its purpose; if a beat is done, cut.
3. **Fast cuts** — ~**2–3s** per beat, intercutting talking-head / b-roll / real-UI / motion. Not ~7s holds.
4. **Cut to the VO word-timing.** Transcribe the VO (Whisper → word timestamps) and sync every text in/out and every cut to the actual words/sentence boundaries. **Don't hand-guess timings.**
5. **Cut words FIRST, then slow the pace.** A dense script at a slow pace drags — trim the script before stretching beats.

---

## 5. AUDIO GUIDE

- **VO:** Kokoro local TTS via `hyperframes-media` (`npx hyperframes tts`). Voice by register — e.g. forceful/authority vs neutral; pick to fit the narrator, not a warm-commercial default. Paragraph-split + **0.5s gaps**; normalize **loudnorm `I=-16:LRA=3:TP=-1.5`**. Where real face-cam covers a line, the recorded audio replaces TTS for that slot (TTS = scratch until filmed).
- **Music bed:** one continuous low bed that never drops; a single **sub-bass impact at each peak**; a clean silent stop at the end.
- **SFX:** sparse + **semantic** only — e.g. a soft type-click under typewriter titles, a tone when the signature device completes, a chime/whoosh on a resolution beat, a dull thud at each "wall." Never gratuitous; give SFX events their own table in the plan.

---

## 6. RENDER GOTCHAS (HyperFrames — check BEFORE debugging a "missing element")

- **Lottie does NOT render in HyperFrames.** Tried every documented way (path + inlined `animationData`, GSAP proxy → `goToAndStop`, snapshot AND full MP4) — the container stays empty. **Build the animated mark natively instead:** a GSAP/CSS **stroke-draw on an inline `<svg>`** (`stroke-dasharray`/`dashoffset`), a drawn path, particles, the signature device. If a brief says "Lottie," deliver a real animated mark via a technique that renders, or STOP and flag — never ship an invisible Lottie container.
- **Masked-overflow text reveal does NOT render.** `.x{overflow:hidden}` + `translateY`/`yPercent` mask = invisible text. Use opacity + y fade-slide instead.
- **`<video>` cannot live inside a timed `.clip`.** Put the timed `<video>` in a NON-timed container (control its opacity via GSAP). Keep the video clip covering the whole on-screen window so it doesn't blank early.
- **GSAP transform conflict:** animating `x`/`scale` on an element with CSS `transform:translate(-50%)` wipes the centering. Use `xPercent`/`yPercent` or `fromTo`. (Lint flags `gsap_css_transform_conflict`.)
- **Judge the actual MP4, not snapshots.** Snapshots don't render Lottie/late-async reliably — extract frames from the real render (`ffmpeg`) for anything async.
- **Cloud render has a 32 MB upload cap** — unusable for asset-heavy episodes. **Render locally.**
- **`hyperframes transcribe` times out on long audio** (subprocess `ETIMEDOUT` on ~hour-long files). **Bypass the wrapper, run `whisper-cli` directly:** `yt-dlp -f bestaudio -x --audio-format m4a` → `ffmpeg -ar 16000 -ac 1 -c:a pcm_s16le audio.wav` → `whisper-cli -m ~/.cache/hyperframes/whisper/models/ggml-<model>.bin -f audio.wav -ojf -otxt -of <out>/transcript -t 8`. Models cached at `~/.cache/hyperframes/whisper/models/`. Prefer an already-cached model (mid-download of a new model can leave a partial `.bin`).

---

## 7. BUILD / RUNTIME RULES (HyperFrames — proven)

- **HTML is the source of truth.** GSAP timeline **paused + registered** on `window.__timelines["<id>"]`; **seek-deterministic** — no `Math.random`/`Date.now`, finite repeats, pre-split spans, no bare `gsap.set` on later-scene clips.
- Every timed element: `class="clip"` + `data-start` / `data-duration` / `data-track-index`. Sub-comps via `data-composition-src`.
- **Bundle every non-built-in font LOCAL** (`fonts/*.woff2` + local `@font-face`) — the render sandbox blocks CDN fonts (`fonts.googleapis.com` → `ERR_BLOCKED_BY_ORB`). (GSAP via CDN renders fine; only *fonts* must be local.)
- Run `npx hyperframes lint && validate && inspect` (or `npm run check`) after every edit; **snapshot before rendering**.
- One scene = one sub-composition (`compositions/sNN-<slug>.html`), assembled by a part-root composition.

---

## 8. WORKFLOW + GATES (scene-gated, no rush)

For EACH scene, in order — do not start the next until the current passes:
1. **Build** the scene as its own sub-composition.
2. **Generate VO** (TTS) → time visuals to it (VO-driven).
3. **Lint + validate + inspect** — fix all errors.
4. **Snapshot** key frames — eyeball layout, no overlap/bleed, color correct, motion reads.
5. **Fresh-context critic gate** — a separate subagent scores the scene from a **5–7 frame sequence** (entrance → settle) against the reference + a scene rubric. **The builder may not self-grade.** Rewrite until it passes.
6. **Log the gate** in the project's `TASK.md`. Move on.

Then assemble the part, render, present. **Render locally.**

- **Approval before production (binding):** TTS / transcribe / RENDER cost real resources — get an explicit go-ahead first. "Validate / review" ≠ "produce." Iterate cheaply (lint / snapshot / critic), report, then wait for "go."
- **Read the reference files before the first keyframe** — not from memory.

---

## 9. THE LITERAL-ASK RULE (binding — the #1 recurring failure)

**Deliver the EXACT thing asked, or STOP and flag it with options — never quietly ship an easier approximation.**
- "A stock video of someone **giving** a book" = a person handing a book to a person — NOT a book lying on a table.
- "**Advanced motion** on the right" = real animated motion-graphics — NOT a text list (01, 02, 03…).
- "**Lottie**" = an actual animated mark plays (built natively per §6) — NOT an invisible container.
- "**Read the text**" = use the ACTUAL script/VO words, design around them — NEVER a paraphrase.

Defaults to break: reaching for on-screen TEXT instead of motion/footage; a near-miss clip instead of the actual action; rewriting the words instead of using them. Check the deliverable against the exact words before showing it: *did I do THIS, or an easier cousin of this?*

---

## 10. SIGNATURE DEVICE (exactly one per episode)

Each episode/film gets **exactly ONE signature motion device that embodies its concept**, recurs across scenes, and pays off at the climax. One device = the whole thesis.
- **[INSTANCE]** *The Agentic Company E1* — **"The Missing Doubt":** the machine's output is one unbroken, perfectly confident stroke/block (it looks identical right or wrong); the engineering craft is the **doubt layer** the human adds back (a check, a second pass, a dotted verification line). Pays off at "fifty years of manufacturing that doubt by hand."
- **[INSTANCE]** *Engineering With AI E1* — **"The Moving Constraint Pinch":** particles flow through a bottleneck that dissolves at center and re-forms at the two ends (Specification + Verification).

---

## 11. ASSET SOURCING

- **Stock clips:** default to **Pixabay** (free, commercial-OK, no attribution); Pexels / Coverr also fine. Grade/duotone to the project palette so footage reads cohesive.
- **Destination editor** (e.g. CapCut Pro) is for assembly only — don't reuse its stock off-platform.

---

## 12. VISUAL SYSTEM **[INSTANCE — swap per project]**

Have **one** semantic palette + type system per project and use color *semantically* (a color only ever means one thing). Worked example (dev_content "Engineering With AI" / "The Agentic Company"):
- **Palette:** cream `#FBF4E3` (bg) · ink `#1A1714` · slate `#4A5568` (neutral/system) · **terracotta `#C2410C` = tension/constraint** · **sage `#5F7A5C` = flow/resolution**. Warm grain ~6–7% + radial vignette. No dark mode.
- **Type:** Instrument Serif (editorial hero, 130–220px, italic) · Inter (labels/body, built-in) · IBM Plex Mono (code/terminal).
- **Pipeline:** `queek-premium-video` discipline adapted own-brand + HyperFrames runtime; Direction → Plan → scene-by-scene Make (critic gates, WIP=1) → render → mobile re-author.

---

## 13. PRE-BUILD CHECKLIST

- [ ] Read this guide + the project's `PRODUCTION.md` + reference frames (not from memory).
- [ ] For each beat: treatment written (full / card / split / talking-head), chosen from its content.
- [ ] Each element has a named camera animation + a named motion-vocab entrance.
- [ ] Title reveal chosen (varied across scenes).
- [ ] Beat-to-beat transitions chosen from the HF catalog.
- [ ] VO transcribed → cuts + text in/out synced to word timing.
- [ ] Density check: ~20–30 events / 65s, nothing static >1.5s, motion registers at 1080p.
- [ ] No Lottie / masked-overflow / video-in-timed-clip; fonts local; seek-deterministic.
- [ ] One signature device, recurring.
- [ ] Literal-ask check: delivered the exact thing, or flagged.
- [ ] Scene passed the fresh-context critic ≥ target, from the real MP4. Logged.

---

## Provenance (source memories, dev_content)
`premium-video-section-treatments` · `premium-video-pacing` · `premium-video-motion-density` · `premium-motion-vocab` · `deliver-the-literal-ask` · `themitmonk-visual-style` · `premium-video-production` · `hyperframes-gotchas` · `render-pipeline-decision` · `stock-footage-licensing` · `approval-before-production` · `agentic-company-e1-video-build` + the episode `video/PRODUCTION.md`. Keep this guide in sync if any of those change.
