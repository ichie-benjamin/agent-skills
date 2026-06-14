# Scene design layer → `works/<slug>/scenes-design.md`

Written at **Flow step 4 (Scene design)**, AFTER the Plan gate, BEFORE Make.
It is the *visual realization* of the approved plan — how each beat looks and
moves — not a restatement of the plan's contract. Plan stays the source of
truth for timing / VO / scene intent; this layer adds archetype + layout +
motion + a 6-dim score per scene. `bin/scenes-to-html.py` renders it as
`SCENES.html` for the design gate.

Author one scene block per approved plan §6 scene. Read the scene's plan block
+ `memories/brand.md` + the project scene library + bundled archetypes first;
pick an archetype, never invent the layout cold. The layout is a **wireframe
spec, not built HTML** — boxes on a grid, cheap to redraw when the reviewer
corrects it.

```markdown
# Scene design — <film title>

**Signature device:** <the film's one device>
**Arc:** <peak Sx · quiet Sy · resolve Sz>

## S1 · <name> (<start>–<end>s)
- Archetype:  <name from scene library / bundled archetypes — e.g. "Term/Definition Card">
- Derives:    <screenshot path · archetype:<name> · ref:<brand>-<slug>#S2 — what this layout is built from>
- Focal:      <the one thing the eye lands on first>
- Motion:     <the one meaningful move + its primitive — e.g. "stamp-settle on card">
- Type:       <hero face/size · support · label>

​```layout
cols: 12 · rows: 8 · aspect: 16/9
hero "Ankara shirt ₦18,500" : c2-11 r3-5 focal
pill "WRONG ITEM" : c2-5 r6
label "ORDER #2841" : c2-6 r2
​```

Score: 1:2 2:2 3:2 4:1 5:2 6:2
Fix 4: hero ₦ amount should be 120px not 96 to clear the support line

## S2 · <name> (<start>–<end>s)
...
```

## Layout grammar (inside the `layout` fence)

- **Header line (optional):** `cols: <n> · rows: <n> · aspect: <w/h>`. Defaults
  `cols 12 · rows 8 · aspect 16/9`. Use `aspect: 9/16` for a mobile-frame scene.
- **Region line:** `<kind> "<label>" : <placement> [focal] [muted]`
  - `kind` — `hero` (big label) · `pill` (rounded chip) · `label` (small caps) ·
    `text` (body) · `media` (dashed, for a screenshot/clip region) · `box` (plain).
  - `placement` — `c<a>-<b> r<a>-<b>` (1-indexed, inclusive spans). Single cell:
    `c3 r2`. Column-only or row-only spans the other axis fully.
  - `focal` — accent outline; mark exactly one per scene (the eye's first stop).
  - `muted` — dimmed (de-emphasised / background element).
- A region with no parseable placement is listed below the wireframe as
  **unplaced** rather than dropped — fix the placement before the gate.

## Score line

`Score: <dim>:<0|1|2> …` for all six scene-design dimensions, in order:

1 focal idea · 2 motion meaning · 3 color discipline · 4 type hierarchy ·
5 composition & breath · 6 timing & energy fit.

The generator computes total + verdict (premium = **no zeros AND ≥ 10/12**);
don't hand-type a badge. Add `Fix <n>: <what to change>` lines for any dim < 2 —
they render under the scorecard and are what the builder fixes at Make.
