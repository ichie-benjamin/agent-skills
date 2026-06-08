# Plan

Copy this template, fill it, run Validator B (README §Validators), submit when it passes. Skip sections marked `–` in README §Section requirements matrix for the type.

All times are absolute from `t=0` unless marked scene-relative.

## 1 · Direction recap
Copy the approved Direction fields here in full. Plans stand alone — don't link.

## 2 · Signature card
```
Device:    <signature device>
Sounds:    <audio signature elements>
Moves:     <visual signature moves>
Skeleton:  <one of 5>
Arc:       <peak Sx · quiet Sy · resolve Sz>
Format:    <duration · desktop · mobile · fps>
Rhythm:    <e.g. fast-fast-SLOW-fast-HOLD>
```

## 3 · Motion vocabulary
At least 3 named primitives. Scenes reference by name; don't redefine moves in scene blocks.

| Name | Duration | Ease | Use |
|---|---|---|---|

## 4 · Tokens
| Token | Value | Use |
|---|---|---|

## 5 · HF safety contract
Check every box. An unchecked box means that scene needs redesign before the Plan ships.

- [ ] No `tl.call` / `onUpdate` / bare `gsap.set` outside timeline for seek-critical motion (use `tl.fromTo`, `tl.set`, clip-path, opacity).
- [ ] No `Math.random` / `Date.now` (seeded PRNG if randomness needed).
- [ ] No `repeat: -1` (finite repeats derived from duration).
- [ ] No animating `visibility` / `display` / media `.play()`/`.pause()`.
- [ ] Sub-comps use `<template>` wrapper; root composition does not.
- [ ] No exit animations except the final scene — transitions handle exits.
- [ ] Every visible element has an entrance tween.

These rules exist because HF's deterministic seek-and-render engine can't capture state changes that happen outside the timeline.

## 6 · Scene script
One block per scene. Fields apply per matrix.

```
### S<n> · <name> (<start s>–<end s>)
- Track:        <integer — data-track-index>
- Start:        <abs s>
- Duration:     <s>
- Bucket:       <UI-anchored | motion-concept>
- Host:         <inline | sub:<file>>  (if sub, say why this can seek)
- Hero frame:   <one line — the most-visible moment, the static layout HF builds first>
- Layers:       🟢 Motion · 🔤 Text · 🎨 UI Mockup · 📺 Platform Capture · 🎞️ Stock · 🎥 Manual
- UI source:    <screenshot path | L1/L2/L3 component to clone>  (only for UI-anchored)
- Transition:   <named>
- Entrances:    <element: tween shape>
- Technique:    <from HF 11 + named primitive>
- VO:           "<words>" @ <abs s>–<abs s>
- On-screen:    <text rendered on the frame>
- SFX:          <name>@<abs s>, ... (10–20ms before visual lock)
- Risk:         <what could break | fallback>
- Note:         <why these choices>
```

Bucket guidance (README §Make): **UI-anchored** = scene shows a real product surface (uses 🎨 or 📺). **Motion-concept** = scene conveys a lifecycle moment via the signature device (uses 🟢 🔤 only, no UI chrome).

Captions belong in §8, not in scene blocks.

## 7 · Audio architecture

Declare path first. Required for all types except Brand sting (which uses §7-sting micro-spec — see end of section).

**Path declaration (one line, mandatory):**
`Audio path: A — VO-driven  OR  B — music/sound-driven  (with one-line reason if non-default for this type per matrix)`

Both paths require equivalent rigor — different fields, same gate weight. Pick one.

---

### Path A — VO-driven (default for Launch / Industry / Feature / Customer / Reel with VO)

#### 7.A.1 · Audio math (required when Path A)

Lock the math BEFORE writing the prose. WPM is a *consequence* of script density + scene anchor windows — not a target you bolt on. See `patterns/pattern-premium-vo.md`.

| Field | Value | How derived |
|---|---|---|
| Total film duration | `<s>` | from §1 |
| Sum of VO anchor windows | `<s>` | sum across §6 scene VO times |
| Active speech ratio | `<%>` | windows ÷ duration |
| Total words in continuous VO | `<n>` | count from prose below |
| Derived target WPM | `<n>` | words ÷ windows × 60 |
| Acceptable band for this film | `<low–high>` | per type reference band in `pattern-premium-vo.md` · derived from architecture · with one-line reason |
| Pass | ✅ / ❌ | derived WPM inside band? AND no per-scene window exceeds 220 WPM? |

If Pass is ❌, either widen scene VO windows, cut words, or accept a faster band honestly. **Don't lock the plan with ❌.**

#### 7.A.2 · TTS rules
- "Kweek" spelling for TTS input
- "and" before final list item (except deliberate stamp-sequences of 2–4 words)
- VO variants per type matrix (2-variant Launch · 1-variant others)
- Voice ID(s) declared and verified live via `/v1/voices` (per F11 in pattern-failures)

#### 7.A.3 · Continuous prose

```
<continuous prose, riding scene cuts>
```

#### 7.A.4 · Audio cue sheet — word-anchored (the plan-approval artifact)

The human approving the plan needs to *read* the sound design, not reassemble it from scattered §6 scene lines. This table is that view — every effect with its character, intended length, and the word it lands on. It's the same cut-to-cut format the Make phase produces; the only difference is the anchor: **at plan time you anchor to the word** (you know the impact lands on "missing shirt" before you know that's 0.2s), **at Make it gets a real second-timestamp** from the rendered-VO transcript. Word-anchoring avoids inventing precise seconds the render hasn't earned yet.

Path B already has its sound-design events table (§7.B.2); this gives Path A the same single-table parity.

```markdown
### VO script (line by line)
1. <line 1 verbatim>
2. <line 2 verbatim>
...
N. <final line verbatim>

### Cue-by-cue (word-anchored)
| # | Scene | VO words | Effect | Character | Dur | Cue (word/moment it lands on) |
|---|---|---|---|---|---|---|
| — | all | (full track) | <bed> | <bed character> | full | continuous under voice |
| 1 | S1 | <line 1> | <effect> | <real/synth source> | 0.6s | on "<word>" |
| 2 | S2 | <line 2> | — bed only — | — | — | let it breathe |
| 3 | S4 | ↳ <sub-moment> | <effect> | <source> | 0.13s | as "<word>" appears |
...
Peak = #<n> (<scene> — <what>) · Quietest = <scene> · Motifs: <recurring SFX threads>
```

Rules:
- **One row per SFX event.** Scene label on the scene's first row; sub-rows (`↳`) for additional cues in the same scene.
- **Cue column = the word or on-screen moment**, never a guessed second. Durations are intended lengths (a design choice you own now).
- **Mark the single peak and the quiet beat** — restraint is what makes the peak read (see `ref-shipper-mp4-scenes.md`: one big hit, the rest functional ticks).
- Effects should fit the film's bed/aesthetic — name the bed in the header so SFX character is judged against it (warm-piano bed ≠ dark-tech SFX).

Full template + the Make-phase second-anchored version: `<skill>/references/audio-cue-sheet-template.md`.

---

### Path B — Music/sound-driven (no VO; e.g. premium motion-driven film, no-speech Reel)

Use when the film has no VO. Captions + visual + music + sound design carry the story. Reference: `ref-motion-mp4.md` (35s premium no-VO film at -14.8 LUFS).

#### 7.B.1 · Music architecture (required when Path B)

| Field | Value | Notes |
|---|---|---|
| Bed source | `<file path or library entry>` | name the file |
| Bed continuity | `<continuous · scene-changing · none>` | most premium = continuous |
| Peak moments | `<timestamp · level · what the visual is doing>` | e.g. `13s · -5 dB · brand reveal` |
| Quiet beats | `<timestamp · level drop · purpose>` | breath beats before phase changes |
| Music LUFS target | `<integrated LUFS>` | shipper-style premium = -11 to -14; motion-driven typically -14 to -16 |

#### 7.B.2 · Sound design events table (required when Path B)

One table for the whole film. Dense — sound design carries what VO would.

| Time (s) | Event | SFX source | Visual it punctuates |
|---|---|---|---|

#### 7.B.3 · Captions-as-narrator (required when Path B)

When VO is absent, captions carry brand-naming, story beats, and CTA. Section §8 captions table becomes mandatory across every scene that conveys meaning (not just sound-off-affordance).

#### 7.B.4 · Pass check (required when Path B)

| Field | Value | Pass? |
|---|---|---|
| §7.B.1 music architecture all 5 fields filled | | ✅/❌ |
| §7.B.2 SFX events table has ≥ 1 row per scene that needs punctuation | | ✅/❌ |
| §7.B.3 captions cover every meaning-bearing scene in §8 | | ✅/❌ |
| Pass | | ✅ (all three) / ❌ |

If Pass is ❌, complete the missing field(s) before locking.

---

### §7-sting micro-spec (Brand sting only)

Brand sting (3–7s) uses freeform audio per matrix. One block, no math gate:

```
- Sting sound:    <file or generated · one-line description>
- Music sting:    <one-shot sustained note · or none>
- Visual sync:    <how audio aligns with the 1-scene logo reveal>
```

## 8 · Captions track
Burned-in lines for sound-off viewing — separate from on-screen text. ≤ 60 chars/line, ≤ 2 lines.

| Scene | Caption |
|---|---|

## 9 · Mobile (9:16) surgical cut
Safe area on 1080×1920: top 220px (chrome / clock), bottom 380px (action bar / caption). Hero lives in the middle 1320px.

One block per desktop scene. Skip this section for Brand sting; for Reel, mobile IS the master, so no separate cut.

```
### S<n> · <name> · mobile
- Layout shift:   <what moves where in 9:16>
- Type re-size:   <hero/body adjustments>
- Hero reframe:   <how the focal element is centred for portrait>
- Safe area:      <elements crossing 0–220 or 1700–1920 — should be none>
- Audio:          <same as desktop | re-anchored>
```

## 10 · Asset checklist
Status: **G** gathered · **D** downloadable · **R** requested from human.

| Asset | Used in | Status | Path / Link / Request |
|---|---|---|---|

If an asset can't be sourced, adapt the Plan to use what's available; never fake. See ASSET_SOURCING §"If not available" rule.

## 11 · Quality gates

- Snapshot frames (desktop): `<t1, t2, …>`
- Snapshot frames (mobile): `<t1, t2, …>`
- Inspect samples: `<n>` — intentional overflows marked `data-layout-allow-overflow`
- Lint · validate · animation-map clean

### Render targets

HF owns codec, bitrate, and output paths. Specify only project-level deviations from HF defaults (e.g. resolution, fps, file-size cap for a specific channel).

| Cut | Resolution | fps | Notes / channel overrides |
|---|---|---|---|
| Desktop master | 1920×1080 | 30 | |
| Mobile master | 1080×1920 | 30 | IG Reel ≤ 100 MB · X autoplay ~9 Mbps |

## 12 · Production budget

| Layer | Scene count | Effort |
|---|---|---|
| 🟢 Motion | | AI authors |
| 🔤 Text | | AI authors |
| 📺 Platform | | Human screen-recs |
| 🎞️ Stock | | AI sources |
| 🎥 Manual | | 0 unless Face-cam |

---

`Plan validator: <passed>/<applicable> ✓ [fails: <list> | none]`
