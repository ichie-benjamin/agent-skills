# Scene design layer → `works/<slug>/scenes-design.md`

Written at **Flow step 4 (Scene design)**, AFTER the Plan gate, BEFORE Make.
Each scene's layout is authored as **real static HTML** — the literal frame —
which is then **rendered to a snapshot** that the AI and reviewer judge (never
read the markup and imagine it), and which Make lifts and adds motion to. The
HTML is the *static layout* (HF's "Layout Before Animation" step): no GSAP, no
HF wiring, no real data — just the composed frame. Read the plan §6 block +
`memories/brand.md` + the scene library first; derive from an archetype, never
invent cold. **Snapshot on change only** — a scene that uses a library template
as-is reuses the saved template snapshot (`references/layout-snapshots/`);
render a fresh `scene-shots/S<n>.png` only when the scene diverges (new
composition, or content that could break the frame).

```markdown
# Scene design — <film title>

**Signature device:** <the film's one device>
**Arc:** <peak Sx · quiet Sy · resolve Sz>
**Palette:** bg #FBF4E3 · ink #1C1A15 · accent #0E6B43
**Font:** Inter, sans-serif        (optional; defaults to Inter)

## S1 · <name> (<start>–<end>s)
- Archetype:  <name from scene library / bundled archetypes>
- Derives:    <screenshot path · archetype:<name> · ref:<brand>-<slug>#S2>
- Focal:      <the one thing the eye lands on first>
- Motion:     <the one meaningful move + primitive — added at Make, described here>
- Aspect:     16/9        (optional per scene: 16/9 · 9/16 · 1/1 · 4/5 · 4/3)

​```html
<div class="stagepad">
  <div class="card stack" style="align-items:flex-start;text-align:left">
    <p class="t-label">Order #2841</p>
    <h1 class="t-hero">Ankara shirt <span class="accent">₦18,500</span></h1>
    <span class="chip">⚠ Wrong item</span>
  </div>
</div>
​```

Score: 1:2 2:2 3:2 4:1 5:2 6:2
Fix 4: hero amount competes with the item name; push ₦18,500 to its own line

## S2 · <name> (<start>–<end>s)
...
```

## The HTML block (one per scene)

Self-contained static markup for a `<frame>` at the scene's resolution
(16/9 → 1280×720, 9/16 → 720×1280, etc.). The generator wraps it in an
isolated iframe with the palette tokens + a small helper stylesheet already
injected, so author only the scene's elements. The reviewer sees the real
frame; **the builder copies it verbatim** (the "Copy HTML" button) into the HF
composition and animates it — so keep it clean, real, and on-brand.

**Tokens available** (CSS variables, from `Palette:`): `--bg` · `--ink` ·
`--accent` · `--accent-soft` · `--muted`.

**Helper classes** (use them or roll your own):
`.stagepad` (full-frame centered padding) · `.stack` (vertical, gap) ·
`.t-hero` (serif display) · `.t-sub` · `.t-label` (tracked small-caps) ·
`.chip` (accent pill) · `.card` (white elevated panel) · `.accent` (accent text).

Rules: real brand content (real ₦, `brand.md` names), no lorem; static only
(no `<script>`, no animation — that's Make); derive the composition from the
scene's `Derives:` source, don't invent UI cold.

## Score line

`Score: <dim>:<0|1|2> …` for the six scene-design dimensions in order:
1 focal idea · 2 motion meaning · 3 color discipline · 4 type hierarchy ·
5 composition & breath · 6 timing & energy fit. The generator computes
total + verdict (premium = no zeros AND ≥ 10/12). Add `Fix <n>: <change>`
lines for any dim < 2 — they render under the scorecard and the builder fixes
them at Make.
