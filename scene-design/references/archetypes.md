# Scene Archetype Catalog

The `recommend` library. Pick the archetype that fits the beat, adapt its treatment, emit its skeleton. **Don't invent cold** — start from one of these. Each entry: *when · layout · motion device · color role · timing · HF skeleton seed.*

Skeletons are **seeds, not finished scenes** — structure + the one meaningful motion. Keep them seek-deterministic (no `Math.random`/`Date.now`, finite repeats, pre-split spans, local fonts). Build-out belongs to the `hyperframes` skill.

---

## 1. Hero Statement
The thesis line. Used at openings, turns, and the closing punch.
- **When:** a single sentence carries the whole beat.
- **Layout:** centered or lower-third, big negative space above.
- **Motion device:** per-word reveal with a **breath-hold on the hero word** (the word the line pivots on).
- **Color:** ink on bg; one semantic accent on the hero word only.
- **Timing:** 0.4s in · 1.5–2.5s hold · 0.4s out.
- **Seed:** `<h1>` of `<span>` per word; stagger opacity/`translateY`; longer hold tween on the accent word's span.

## 2. Term / Definition Card
Introduce a named concept.
- **When:** a term must land before the argument uses it.
- **Layout:** term as hero (serif), definition as support line beneath, label/tag above.
- **Motion device:** term sets first, definition fades up after a beat (sequence = "name, then explain").
- **Color:** neutral; accent only if the term IS the constraint/flow concept.
- **Timing:** term 0.3s in, 0.6s hold, then definition 0.4s in, hold to read.
- **Seed:** stacked `<div>`s: `.label` `.term` `.def`; timeline reveals top→down.

## 3. Contrast Split
This vs that. The workhorse for "before/after", "vibe-coder vs engineer", "workflow vs agent".
- **When:** the beat is a comparison or tension between two things.
- **Layout:** vertical or diagonal split; each side labeled; a seam down the middle.
- **Motion device:** sides enter from opposite edges and **meet at the seam** (the tension is the seam).
- **Color:** one side neutral/system, the other the tension accent — semantic, never decorative.
- **Timing:** 0.5s in (both sides together), hold, optional seam pulse on the key word.
- **Seed:** two half-width columns + center rule; mirror `translateX` from ±100%.

## 4. Enumerated Reveal
A short list (3–5 items).
- **When:** steps, reasons, or a count — and the count itself matters.
- **Layout:** left-aligned list on a baseline grid, generous line-height, index numerals.
- **Motion device:** items reveal one-by-one in rhythm with narration (sync to TTS beats).
- **Color:** neutral list; accent the one item the beat emphasizes.
- **Timing:** ~0.25s per item in, staggered to voice; whole list holds at end.
- **Seed:** `<ol>`/rows; stagger each row's opacity+`translateX`; finite, pre-split.

## 5. System Diagram
Nodes and flow — an architecture, a pipeline, a loop.
- **When:** the beat describes how parts connect or data moves.
- **Layout:** nodes on an implicit grid; connectors as thin rules/paths; one focal node.
- **Motion device:** **flow along the connectors** (a dot/dash traveling the path) — motion = the data/control moving.
- **Color:** system nodes neutral; the constrained path terracotta, the resolved path sage (or brand equivalents).
- **Timing:** nodes set first (0.5s), then flow animates once per cycle, finite repeats.
- **Seed:** absolutely-positioned nodes + SVG `<path>`; animate `stroke-dashoffset` (finite) for flow.

## 6. Code / Terminal Focus
Real code or command output on screen.
- **When:** a concrete, checkable example (the quality standard's "real example").
- **Layout:** mono block, dim chrome, one highlighted line/token as focal.
- **Motion device:** **focus pull** — block dims, the key line brightens/scales slightly (typing reveal only if the act of typing is the point).
- **Color:** mono on near-bg; accent the one line that proves the beat.
- **Timing:** block in 0.4s, hold to read, highlight pulse on the key line.
- **Seed:** `<pre>` with per-line spans; lower opacity on non-focal lines, animate the focal span.

## 7. Number Punch
A single statistic or figure.
- **When:** one number is the whole point.
- **Layout:** giant numeral centered, tiny caption beneath.
- **Motion device:** count-up to the value (finite, deterministic — precompute frames, not `Math.random`) OR a hard scale-in snap.
- **Color:** ink numeral; accent if the number marks the tension.
- **Timing:** 0.6s count/snap, 1.5s hold.
- **Seed:** `<div class="num">`; drive value off the seekable timeline progress, not a live counter.

## 8. Book-Quote Card
The canonical CS/software quote (quality-standard requirement).
- **When:** the verified quote from `book-references`.
- **Layout:** quote as hero (serif italic), attribution small beneath (author · book · chapter).
- **Motion device:** quote fades up as one block (let the words breathe); attribution sets last.
- **Color:** ink; no accent — restraint signals authority.
- **Timing:** slow — 0.8s in, long hold (it's a read-aloud moment).
- **Seed:** `<blockquote>` + `<cite>`; single fade+`translateY`, attribution delayed.

## 9. Signature-Device Moment
The episode's ONE signature device (e.g. Eng-With-AI's *Moving Constraint Pinch*).
- **When:** the beat that embodies the episode's core concept. **Exactly one per episode.**
- **Layout / motion / color:** defined by the device itself — pull from the episode's spec, don't reinvent.
- **Timing:** the peak of the energy arc; give it room before and after.
- **Seed:** reference the device's existing POC; this scene IS it. No competing hero motion anywhere near it.

## 10. Breather / Transition
The connective tissue between dense scenes.
- **When:** after a peak, before a shift; the eye needs rest.
- **Layout:** near-empty — bg, grain, maybe one small mark or the continuous motion bed.
- **Motion device:** ambient only (slow bloom, drift) or a clean match-cut into the next scene.
- **Color:** bg + texture; no accent.
- **Timing:** short, 0.5–1s; its job is rhythm, not information.
- **Seed:** bg layer + vignette/grain; optional crossfade hook to the next scene.

---

## Choosing fast

| The beat is… | Archetype |
|---|---|
| a thesis / punch line | Hero Statement |
| introducing a term | Term / Definition Card |
| a comparison or tension | Contrast Split |
| a list or count | Enumerated Reveal |
| how things connect | System Diagram |
| a concrete example | Code / Terminal Focus |
| one striking number | Number Punch |
| the canonical quote | Book-Quote Card |
| THE core concept | Signature-Device Moment |
| a pause between scenes | Breather / Transition |

If a beat seems to need two archetypes, it's probably two beats — split it (rubric dimension 1: one focal idea).
