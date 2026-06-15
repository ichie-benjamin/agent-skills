---
name: scene-design
description: DEPRECATED — folded into the queek-premium-video skill. Scene-layout recommendation, the archetype catalog, the visual layout library, and the design gate now live in queek-premium-video (which homes them alongside its own strong, independent gates). Do not invoke this skill; use queek-premium-video for any premium-video scene design.
license: proprietary
metadata:
  author: Ichie Benjamin
  version: "2.0.0-deprecated"
---

# Scene Design — deprecated (folded into queek-premium-video)

This standalone skill has been **consolidated into `queek-premium-video`** to
remove a cross-skill dependency and keep one home for premium-video scene work.
Nothing here is loaded anymore.

## Where everything went

| Was here | Now in `queek-premium-video` |
|---|---|
| `recommend` (pick an archetype, emit a layout spec) | Inlined in §Scene design (Flow step 4) — read the catalog + saved layout snapshots, pick, emit |
| `references/archetypes.md` (the catalog) | `queek-premium-video/references/archetypes.md` |
| the visual layout library | `queek-premium-video/references/scene-layouts.html` + pre-rendered `references/layout-snapshots/` |
| `validate` / `approve` (advisory 6-dim self-score) | **Dropped** — they were inline self-scores, which violate queek's gate philosophy (every verdict independent, never self-graded). queek's own gates (structural + scene-critic, both independent) cover the same ground harder |

## Why

- queek-premium-video already called only `recommend`; homing it removes the hop.
- The design artifact is now a **rendered snapshot the AI sees**, not a generated
  HTML page read as markup (a model misreads code under pressure — the snapshot
  is the truth). Saved template snapshots are reused, not re-rendered.
- queek has its own strong, independent validation, so scene-design's advisory
  self-scoring is redundant.

## What to do

Use **`queek-premium-video`** for any premium-video scene design — directly, or
it runs scene design as Flow step 4 of a full film. If a project still
references `/scene-design`, point it at queek-premium-video.
