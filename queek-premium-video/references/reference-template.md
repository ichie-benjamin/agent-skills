# Reference

Distills an approved film into 2 pages that let the next agent lift patterns without opening the comp HTML. Lives at `research/references/ref-queek-<slug>.md`. Written at Close, auto-indexed into REFERENCES.md.

## Frontmatter
```yaml
---
name: queek-<slug>
kind: reference
status: active
last_updated: <YYYY-MM-DD>
type: <one of 6>
duration_s: <number>
sources:
  - works/<slug>/composition/index.html
  - works/<slug>/plan.md
  - works/<slug>/audio-cue-sheet.md
  - works/<slug>/postmortem.md
---
```

## What this film is
Two sentences. Audience · what it sells · ship date.

## Signature card
```
Device:    <signature device>
Sounds:    <audio elements>
Moves:     <visual moves>
Skeleton:  <one of 5>
Arc:       <peak Sx · quiet Sy · resolve Sz>
Format:    <duration · desktop · mobile · fps>
Rhythm:    <pattern>
```

## Tokens used
| Token | Value | Use |
|---|---|---|

## Motion vocabulary used
| Name | Duration | Ease | Use |
|---|---|---|---|

## HF catalog / registry blocks used
| Block | Source | Used in | Notes |
|---|---|---|---|

## Track layout
Top-level track plan. Audio + overlays + scene-hosts.

| Track | Role |
|---|---|

## Per-scene breakdown
One block per scene. Pulled from the actual comp source, not memory.

```
### S<n> · <name> (<start s>–<end s>)
Track:       <integer>
Hero:        <most-visible moment>
Layers:      🟢 · 🔤 · 📺 · 🎞️ · 🎥
Host:        <inline | sub:>
Technique:   <HF 11 / named primitive>
GSAP:        <specific tween shape — e.g. tl.fromTo opacity+y, stagger 0.08s, power3.out>
Catalog:     <block id or custom>
Transition:  <named>
VO:          "<words>" @ <abs s>
On-screen:   <text>
SFX:         <cues>
Reusable:    <yes pattern X | partly | no project-specific>
```

## Sound design (reusable)
The next agent should be able to lift the audio approach without opening the project. Capture the *reasoning*, not the per-second timings (those are project-specific and live in `audio-cue-sheet.md`).

```
Path:        <A VO-driven | B music-driven>
Bed:         <file> — <character> — WHY it fit this film's aesthetic (e.g. warm-piano matched warm-cream visual; a dark-tech bed would have fought it)
VO voice:    <Kokoro af_heart 1.0 paragraph-split | EL Sarah eleven_v3 | ...> — why
SFX palette: <which real sources for which job — e.g. real sub = impact, soft pop = ticks; note any synth-vs-real lessons>
Motifs:      <recurring SFX threads that carried meaning — e.g. ascending build ticks = "progress/each stage", channel pops → whoosh = "many channels, one system">
Peak/quiet:  <the one peak + the one quiet beat, and what made the peak read>
```

## Reusable across projects
Bullets. Patterns to lift into future films.

## Project-specific
Bullets. Things that worked here but won't transfer.

## Gotchas hit
Concrete issues + the fix. Cross-link `feedback_*` memories where applicable.

## Source paths
| What | Path |
|---|---|
| Composition | `works/<slug>/composition/index.html` |
| Sub-comps | `works/<slug>/composition/compositions/` |
| Plan | `works/<slug>/plan.md` |
| Audio cue sheet | `works/<slug>/audio-cue-sheet.md` |
| Postmortem | `works/<slug>/postmortem.md` |
| Desktop renders | `works/<slug>/composition/renders/` |
| Mobile renders | `works/<slug>/composition-mobile/renders/` |

## Index entry
Append to `research/REFERENCES.md` under the type's section:
```
- [queek-<slug>](references/ref-queek-<slug>.md) — <signature device> · <duration>s · <skeleton> · reusable: <one line>
```
