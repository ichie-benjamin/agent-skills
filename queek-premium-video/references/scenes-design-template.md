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

- Snapshot:   reuse (template <name> as-is) · OR scene-shots/S1.png (diverges)

​```html
<div class="stagepad">
  <div class="card stack" style="align-items:flex-start;text-align:left">
    <p class="t-label">Order #2841</p>
    <h1 class="t-hero">Ankara shirt <span class="accent">₦18,500</span></h1>
    <span class="chip">⚠ Wrong item</span>
  </div>
</div>
​```

## S2 · <name> (<start>–<end>s)
...
```

## The HTML block (one per scene)

Self-contained static markup for the frame at the scene's resolution
(16/9 → 1280×720, 9/16 → 720×1280, etc.), composed against the `Palette:`
tokens + the helper classes below. It is build-ready: at Make the builder
lifts this exact markup into the HF composition and adds the motion.

**Tokens** (CSS variables, from `Palette:`): `--bg` · `--ink` · `--accent` ·
`--accent-soft` · `--muted`. **Helper classes** (use them or roll your own):
`.stagepad` (full-frame centered padding) · `.stack` (vertical, gap) ·
`.t-hero` (serif display) · `.t-sub` · `.t-label` (tracked small-caps) ·
`.chip` (accent pill) · `.card` (white elevated panel) · `.accent` (accent text).

Rules: real brand content (real ₦, `brand.md` names), no lorem; static only
(no `<script>`, no animation — that's Make); derive the composition from the
scene's `Derives:` source, don't invent UI cold.

## Review by snapshot (no score line)

There is **no self-score** in this layer — scoring a scene against a rubric is
done post-build by the independent scene-critic (§Gate philosophy: verdicts
are never the author's own). The design gate is the human approving the
**rendered frame**:

- **Snapshot on change only.** A scene that uses a library template as-is
  reuses the saved template snapshot (`references/layout-snapshots/`) — mark
  `Snapshot: reuse (template <name>)` and don't re-render it. A scene that
  diverges (new composition, or content that could break the frame) gets a
  fresh `works/<slug>/scene-shots/S<n>.png`; `Read` it to confirm the frame
  matches intent.
- Submit the snapshot set (fresh PNGs + the reused template snapshots) as the
  durable Design gate. The reviewer judges the images, not this markup.
