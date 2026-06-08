# Asset sourcing

Status codes: **G** gathered on disk · **D** downloadable · **R** request from human.

Library paths and API keys live in `memories/asset-libraries.md` — consult it for exact locations. This file describes *which* libraries exist and *how* to use them; the memory file is the source of truth for *where* they are. Path drift updates only the memory file.

All paths below are relative to the working directory (the creative project root). External libraries are referenced by name; resolve to absolute paths via the memory file.

## Sources

| Kind | Library name (resolve via memory) | How to fetch | Code |
|---|---|---|---|
| Real product source anchor (dashboard, POS, app, settings) | Human-supplied screenshot · screen-rec · designed mockup · registered reusable component | Request — never invent from imagination | R |
| POS frames | "Queek POS screenshots" | Read + copy into `composition/assets/pos/` | G |
| Queek mockups v1 | "Queek mockups v1" | Read | G |
| Queek Vendor portal screenshots | "Queek Vendor portal screenshots" | Read | G |
| Queek logo / brand kit | `files/logo/queek.png` · Canva brand kit (manual) | Read PNG; request Canva exports | G/R |
| Theme captures (incl. `paralax.png`) | `files/refs/queek-website-themes/` | Read | G |
| Stock photos | Pixabay | `bin/pixabay-search.sh` → `bin/pixabay-download.sh` | D |
| Stock video | Pixabay (videos) · Pexels (manual pick) | Pixabay via wrapper; Pexels via search URL for human pick | D/R |
| Lottie | LottieFiles GraphQL | `bin/lottie-search.sh` → `bin/lottie-get.sh` | D |
| Music / bed | Pixabay music · royalty-free libraries | Provide links; human confirms pick | D/R |
| SFX bursts (on demand) | ElevenLabs Sound Effects API | `bin/elevenlabs-sfx.sh "<prompt>" <duration_s> <output>` | D |
| SFX library (curated) | "SFX library" | Read + copy into `composition/assets/sfx/` | G |
| Fonts | HF built-in · `fonts/*.woff2` | Built-in named in CSS; request `.woff2` from human for custom | G/R |
| HF references | `research/references/` + `works/_reference-hyperframes/` + `hyperframes-launches/` | Read before lifting | G |
| Face-cam footage | Human filming | Request (Face-cam mode only) | R |

## Wrappers

```
bin/pixabay-search.sh "<query>" [per_page] [orientation]
bin/pixabay-download.sh <largeImageURL> <output_path>
bin/lottie-search.sh "<query>" [limit]
bin/lottie-get.sh <json_url> <output_path>
bin/elevenlabs-sfx.sh "<prompt>" <duration_s|0> <output_path>
```

Keys live in `<repo>/.env`. Pixabay rate limit: 100 req/60s.

## "If not available" rule

When an asset can't be sourced (not in libraries, not downloadable, human can't supply this round), adapt the Plan to use what is available. Direction stays; the Plan flexes.

**Allowed:**
- Swap the scene's approach to one using available assets (e.g. illustrated Motion instead of a missing stock clip).
- Drop the scene if it isn't load-bearing; reflect the duration change everywhere.
- Merge the beat into an adjacent scene.

**Forbidden:**
- UI invented from imagination ("looks-like-Queek" CSS built from intuition, with no screenshot · design · or registered component as anchor) — reads as graphics, not software, and breaks the premium bar. HTML mockups anchored to a real source are the gold path; imagined UI is the fail mode.
- Generic stock pretending to be the Queek product.
- Placeholder or lorem stand-ins in the final composition.
- Proceeding with an unresolved gap.

Re-run Validator B after any adaptation.

## Pre-flight gather order

1. Inventory libraries on disk (mockups, POS, themes, SFX library).
2. Run stock searches per scene; save candidate URLs to the Plan's asset table.
3. List requests-from-human separately.
4. Adapt the Plan for any gap that 1–3 can't close.
5. Re-run Validator B.

## Licensing

- Pixabay · LottieFiles public · Pexels: free for commercial and editorial, no attribution required.
- ElevenLabs SFX: per EL terms; included on the project's API key.
- Music / SFX library tracks: verify per track; request from human if unclear.
- Queek-internal assets (mockups, POS shots, logo): use freely within Queek output.
