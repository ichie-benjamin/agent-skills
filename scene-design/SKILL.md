---
name: scene-design
description: Recommend, validate, and approve premium video SCENE designs before they are built. Use when designing a video scene-by-scene, choosing how a beat should look and move, scoring a proposed scene against a premium rubric, or locking a scene design for build. Sits between storyboard/Plan and HyperFrames build — outputs a design spec (+ minimal HF skeleton), never a finished render. Works for dev_content episodes and Queek brand video. Advisory: it scores and recommends fixes, it does not hard-block.
license: proprietary
metadata:
  author: Ichie Benjamin
  version: "1.0.0"
---

# Scene Design

A lightweight judge + recommender for **premium video scene design**. One scene = one idea. The skill decides (or scores) *how a beat should look and move* before any HTML exists. It produces a compact **design spec**, hands the build to the `hyperframes` family, and never renders anything itself.

**It is advisory.** It always returns a score and a fix-list; it never blocks. The human approves. The *hard* per-scene gates (structural soundness, render-safety, premium-motion) live in `queek-premium-video` — this skill supplies the starting vocabulary and a recommendation, it does not gate.

**The layout samples are a starter palette, never a cap on concept.** `references/scene-layouts.html` is a visual library of proven scene layouts (talking-head placements, splits, number/quote/illustration frames, b-roll). Use them to skip the blank page — but creativity is limitless: a beat that needs a layout not in the library is welcome, not a deviation. The samples seed ideas; they never bound them.

## Token discipline (read this first)

- `validate` and `approve` are **self-contained in this file** — do NOT load `references/archetypes.md` for them.
- Load `references/archetypes.md` **only for `recommend`** (it's the scene library + HF skeletons).
- **Score inline.** Do not spawn a subagent. The rubric is six lines; judge directly.
- Output the scorecard table + fixes. No essays.

## Modes

Invoked as `/scene-design <mode>`:

| Mode | Input | Output |
|---|---|---|
| `recommend` | a script beat + its role in the energy arc (and the episode's signature device, if any) | chosen archetype, treatment spec, minimal HF skeleton, self-scored preview |
| `validate` | a proposed scene design (spec or built scene) | scorecard (0/1/2 ×6), hard-gate checks, total /12, verdict, fix-list |
| `approve` | a validated scene | confirms the lock checklist, notes the locked spec |

## The rubric — 6 dimensions, 0 / 1 / 2 each

Premium = **no zeros AND total ≥ 10/12**. Below that → advise fixes (don't block).

| # | Dimension | 2 — premium | 1 — passable | 0 — reject |
|---|---|---|---|---|
| 1 | **One focal idea** | exactly one idea, one focal point, instantly read | one idea but a weak second element competes | cluttered / multiple focal points |
| 2 | **Motion with meaning** | every motion maps to the idea (semantic) | mostly purposeful, one decorative move | animation for its own sake |
| 3 | **Color discipline** | semantic palette honored, restraint (in Eng-With-AI: terracotta=constraint, sage=flow ONLY) | minor off-palette tint | color used decoratively / off-system |
| 4 | **Type hierarchy** | clear hero / support / label tiers; editorial face used deliberately | tiers present but soft | flat sizing / wrong face |
| 5 | **Composition & breath** | grid-aligned, generous negative space, hero gets air | a little tight or slightly off-grid | cramped / edge-crowded / misaligned |
| 6 | **Timing & energy fit** | pacing fits the beat's slot in the arc; entrance · hold · exit; breath-hold on hero word | timing fine but no deliberate hold | uniform pacing / fights the arc |

### Hard gates (binary — note them, but still advisory)

These don't change the score; they're flagged loudly when failed because a build will break or the episode will feel incoherent:

- **Render-safe (HF):** seek-deterministic — no `Math.random` / `Date.now`, finite repeats, pre-split spans, fonts bundled local (CDN is blocked in the render sandbox). Fail → the scene won't render correctly.
- **Signature-device coherence:** if the episode has its ONE signature device, this scene either *is* that device or stays out of its way — it must not introduce a competing hero motion.

## Output format

### `validate` / preview after `recommend`

```
SCENE: <name / beat>
1 Focal idea ........ 2
2 Motion meaning .... 1   → fix: parallax on bg is decorative; cut it
3 Color discipline .. 2
4 Type hierarchy .... 2
5 Composition ....... 1   → fix: hero is 40px from top edge; drop to baseline grid
6 Timing & energy ... 2
TOTAL 10/12   VERDICT: premium ✓
HARD GATES: render-safe ✓ · signature-device ✓
```

### `recommend` adds, above the preview:

```
ARCHETYPE: <from catalog>
LAYOUT: <where elements sit on the grid>
MOTION DEVICE: <the one meaningful move>
COLOR ROLE: <which semantic colors, why>
TYPE: <hero face/size · support · label>
TIMING: <entrance / hold / exit in seconds; hero-word hold>
```
…then a **minimal HF skeleton** (adapt the archetype's template from `references/archetypes.md` — keep it to structure + the one motion, not a finished scene).

## Where it fits the pipeline

`Direction → Plan/storyboard → [scene-design recommend → validate → approve] → hyperframes build → render`

It replaces ad-hoc "what should this scene look like" guessing with a named choice + a score. For dev_content, the visual system (palette, fonts, signature device) comes from the `premium-video-production` memory; for Queek, from the brand KB.

## After locking (dev_content only)

If an approved scene establishes a reusable pattern (a new archetype variant, a signature-device treatment), write a memory and update `MEMORY.md` per the studio hard-gate. Don't let the decision die in chat.
