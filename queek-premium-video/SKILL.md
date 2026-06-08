---
name: queek-premium-video
description: Produce premium Queek videos — launch films, industry films, feature spotlights, customer-side films, reels/TikToks, brand stings. Trigger whenever the user asks for any Queek video, ad, social cut, brand sting, hook reel, motion graphic, demo film, or anything that lands as a moving image under the Queek name, even if they don't say "video" explicitly. Also trigger for face-cam edits (founder talking-head + B-roll) and mobile recuts of existing masters.
---

# Queek premium video

Build Queek videos that match the team's premium bar. Flow has three human approvals: Direction, Plan, each Make gate. Everything else runs without interruption.

This file is the entry point. Pull templates and project files as you go.

**Invoke `/hyperframes` at the start of Make.** HF is the build runtime — every composition, every animation, every render goes through it. The skill never bypasses HF or hand-rolls equivalents. See §Make for the full toolchain + skill load list.

## Root resolution

**The brand-knowledge root is the current working directory (cwd) — the directory the skill is invoked from.** Every "working project" path below (`memories/`, `research/`, `hyperframes-launches/`, `works/`, `files/`) resolves relative to cwd. The skill never hardcodes an absolute path or assumes a specific repo name.

Run the skill from the brand-KB root. Interactively that's the creative repo; under an autonomous runtime, the caller `cd`s into the brand-KB root before dispatching. Skill-bundled files (templates, `bin/`) resolve relative to the skill's own install directory, not cwd — see §Make audio-sanity for the pattern.

## Files

| File | Where it lives | Use when |
|---|---|---|
| `SKILL.md` | this skill | Entry. Read first. |
| `references/direction-template.md` | this skill | Filling Direction for a project |
| `references/plan-template.md` | this skill | Filling Plan for a project |
| `references/postmortem-template.md` | this skill | Writing the Close-phase postmortem |
| `references/reference-template.md` | this skill | Distilling an approved film into a reusable reference |
| `references/scene-critic-rubric.md` | this skill | Per-scene quality gate in Make §2 Video — critic rubric + subagent prompt |
| `references/asset-sourcing.md` | this skill | Sourcing any asset |
| `research/REFERENCES.md` | working project | Pre-flight reference scan; picking refs to cite |
| `research/patterns/pattern-failures.md` | working project | Pre-flight failures scan |
| `memories/brand.md` | working project | Loading brand at Intake |
| `memories/asset-libraries.md` | working project | Resolving library paths |
| `memories/voice-options.md` | working project | Picking a voice + TTS rules |

## Project layout

Each project lives at `works/<slug>/`:

```
brief.md · direction.md · plan.md · postmortem.md · TASK.md
assets/                       raw originals
deliverables/                 audio: stems + master + audio-timeline.json + README
composition/                  desktop HF project (renders/ lives inside per HF convention)
composition-mobile/           9:16 surgical clone (renders/ inside)
```

HF owns the composition **and the render output** — codec, bitrate, and where the `.mp4` lands are HF's call, not the skill's. By convention HF writes a `renders/` folder inside each composition (so you'll typically find masters at `works/<slug>/composition/renders/` and `works/<slug>/composition-mobile/renders/`), but treat that as where-to-look, not a path the skill pins. The skill owns the `works/<slug>/` project folder (briefs, plan, TASK.md, audio deliverables, composition source); HF owns what happens inside the composition at render time.

At Close, the approved project also writes:

```
research/references/ref-queek-<slug>.md      new reference
research/REFERENCES.md                        updated index
memories/<topic>.md                           updated if new insight
```

---

## Flow

Seven steps. Approvals at Direction, Plan, each Make gate.

1. **Intake** — Load brand + asset libraries + REFERENCES + voice-options. Run pre-flight (below). Pick type. Ask for missing brief fields in one consolidated message; never infer. When the brief is complete: `mkdir works/<slug>/`, write `brief.md`, initialise `TASK.md` with phase skeleton. The project exists from this moment so any session cut can resume.
2. **Direction** — Write `works/<slug>/direction.md` (creative commitment: signature device · look · sound · references). Self-grade against Validator A. Rewrite until pass. Submit.
3. **Plan** — Write `works/<slug>/plan.md` (per-scene contract). Source assets per `references/asset-sourcing.md`. Self-grade against Validator B. Rewrite until pass. Submit.
4. **Make** — Audio · Video · Mobile, with three gates (below).
5. **Render** — Wire stems, render both masters.
6. **Review** — Three axes: technical · brand · story · reference diff. Fail routes to the phase that owns the gap.
7. **Close** — Run close-gate (below). Write postmortem + new reference + index update. Project is not done until the gate passes.

---

## Gate protocol (durable, single source of truth)

Every human-decision point — Intake missing-brief questions, Direction submit, Plan submit, Gate 1 (audio), Gate 2 (desktop), Gate 3 (mobile), and any "block until supplied" / hero-frame sign-off — is a **durable gate**, not a synchronous conversation pause. The decision is always recorded in `works/<slug>/TASK.md`, so a run can pause and resume across sessions (or across an autonomous runtime's turn budget) without losing the question.

**Every gate, both interactive and autonomous, does the same thing:**

1. Finish and save the gate's artifact (e.g. `direction.md`, `audio-cue-sheet.md`, the Gate 2 deck).
2. Write one durable line into `works/<slug>/TASK.md` Notes:
   ```
   - [!] AWAITING <gate> — <the question / what to decide> · artifacts: <paths to review>
   ```
3. **Interactive use:** also ask the question in conversation. When the human answers, update the line to `[x] <gate> — <resolution>` and proceed in the same session.
4. **Autonomous use:** stop cleanly after writing the line — the worker has emitted everything the human needs. On the next session, read the resolution and proceed.

**On resume** (per §Task tracking): read TASK.md, find the `[!] AWAITING` line, read the human's resolution (written back on the same line, or appended below it), flip it to `[x]`, and continue from there. The answer lives in the same durable place the question did — never only in conversation.

This means no gate ever depends on the human being reachable *right now*. Interactive answers are a convenience; the TASK.md line is the contract.

---

## Types

Six. Every type ships desktop + mobile aspects. Mobile is re-authored per scene, not cropped — frame is too different. Brand sting is the only single-aspect type.

| Type | Duration | Desktop | Mobile | VO | Real captures | Cap | Tone |
|---|---|---|---|---|---|---|---|
| Launch film | 60–90s | 16:9 | 9:16 | 2-variant | yes | 10 | commercial |
| Industry film | 30–50s | 16:9 | 9:16 | 1-variant | yes | 8 | commercial |
| Feature spotlight | 15–30s | 16:9 / 1:1 | 9:16 | 1-variant | yes | 5 | commercial |
| Customer-side film | 15–30s | 1:1 | 9:16 | 1-variant | optional | 5 | warmer |
| Reel / TikTok | 6–15s | 1:1 opt | 9:16 primary | optional | optional | 3 | match channel |
| Brand sting | 3–7s | 1:1 | (covers both) | none | none | 1 | brand |

Face-cam mode: a flag on Launch / Industry / Customer when the human supplies face footage. Skill adds B-roll, lower-thirds, captions around it. Not a separate type.

### Section requirements matrix

`✓` required · `opt` validated if present · `–` skip.

| Section | Launch | Industry | Feature | Customer | Reel | Sting |
|---|---|---|---|---|---|---|
| Story skeleton | ✓ | ✓ | ✓ | ✓ | opt | – |
| Energy arc (peak/quiet/resolve) | ✓ | ✓ | peak | peak | – | – |
| Audio path (§7) — A (VO-driven) · B (music/sound-driven) | A default · B by exception | A default · B by exception | A or B | A default · B by exception | A or B | – (uses §7-sting micro-spec) |
| §7-A · VO 2-variant | ✓ (Path A) | – | – | – | – | – |
| §7-A · VO 1-variant | (above) | ✓ (Path A) | ✓ (Path A) | ✓ (Path A) | opt (Path A) | – |
| §7-A · Continuous VO assembly + audio math + word-anchored cue sheet (§7.A.4) | required when Path A | required when Path A | required when Path A | required when Path A | required when Path A if VO | – |
| §7-B · Music architecture + SFX events table + captions (carries meaning) | required when Path B | required when Path B | required when Path B | required when Path B | required when Path B | – |
| Captions track | ✓ | ✓ | ✓ | ✓ | ✓ | – |
| Real product source anchor (screenshot · screen rec · mockup · registered component) | ✓ | ✓ | ✓ | opt | opt | – |
| Motion vocabulary block | ✓ | ✓ | ✓ | ✓ | opt | – |
| Tokens block | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Rhythm pattern | ✓ | ✓ | ✓ | ✓ | ✓ | – |
| Visual signature moves | 2–4 | 2–3 | 1–2 | 1–2 | 1–2 | 1 |
| Audio signature elements | 3–5 | 3 | 2–3 | 2–3 | 2–3 | 1–2 |
| Sub-comp/inline reason | ✓ | ✓ | ✓ | ✓ | opt | – |
| Per-scene risk + fallback | ✓ | ✓ | ✓ | ✓ | opt | – |
| Production budget | ✓ | ✓ | ✓ | ✓ | ✓ | – |
| Mobile surgical re-author | ✓ | ✓ | ✓ | ✓ | n/a | – |
| Scene cap | 10 | 8 | 5 | 5 | 3 | 1 |

---

## Validators

Binary checklists. Type-aware via the matrix. Score as `<passed>/<applicable>` with fails listed (or `none`). Rewrite until pass before submitting to human.

The validator exists because films review badly when a structural piece is missing. Catching it before the human review is cheaper than catching it after.

### A · Direction

**Header**
1. Type is one of the six.
2. Duration is exact and in band (or override has a one-line reason).
3. Desktop + mobile aspects specified (mobile N/A only for Brand sting).
4. Channels named concretely (no "social" — name them).
5. CTA verbatim (no "standard CTA").
6. Approval gate names a human.

**Concept + signature**
7. Concept is one sentence, one idea.
8. Exactly one signature device.
9. Visual moves count matches type minimum; each cites a reference.
10. Audio elements count matches type minimum + music character described.
11. Story skeleton named (skip Sting; opt Reel).

**Look**
12. Palette has bg / ink / accent / supporting hex.
13. Type: hero/body/UI fonts named, sizes banded, files declared (built-in or `fonts/*.woff2`).
14. Corners + depth declared.
15. Motion feel: eases + duration band.

**Energy + refs**
16. Peak / quiet / resolve per matrix (Launch + Industry all three; Feature + Customer peak only; Reel + Sting skip).
17. At least one reference is a local file path.
18. Each reference declares what's lifted.

**Brand-fit**
19. No banned filler in the Direction text itself.
20. No banned hedges.
21. No banned competitors.
22. Naming: "Queek AI" / "AI Agent" — never "bot", "Qee", "chatbot".
23. Light bg, green accent only (no green fills).
24. No fabricated numbers / partners / features.

**Production resources**
25. Screen-cap availability declared.
26. Face-cam declared yes/no.
27. Banned-for-project list present (even if empty).

**Type-specific**
28. Real product source anchors (screenshot · screen recording · designed mockup · registered reusable component) listed for every UI-anchored scene the type requires. Motion-concept scenes are exempt.
29. Scene cap acknowledged.

### B · Plan

**Structure**
1. Direction recap full (no drift from approved Direction).
2. Signature card lines per matrix filled.
3. Motion vocab ≥ 3 primitives (skip Sting; opt Reel).
4. Tokens block present.
5. Rhythm pattern named (skip Sting).

**Scenes** — every scene must pass every applicable row, or the whole group fails.

6. Every scene has id, start, duration.
7. Host (inline or sub:) + sub-comp reason if sub.
8. Hero frame described.
9. Layers checked.
10. Transition-in named (skip Sting).
11. Entrance contract per visible element.
12. No exit animations except the final scene — transitions handle exits.
13. Technique from HF's 11 catalog.
14. VO anchor times absolute (from t=0), inside scene window.
15. Caption present (skip Sting).
16. SFX cues or `silent` declared.
17. Risk + fallback (skip Sting; opt Reel).
18. Director's note.

**HF safety**
19. HF safety contract block all checked. See `references/plan-template.md` §5.

**Audio**
**Audio** — path-aware (Path A and Path B are peer-gated; Brand sting uses §7-sting only)

20. Audio path declared (A or B) in §7 with one-line reason if non-default for type per matrix.
21. **If Path A:** §7.A.2 TTS rules complete — "Kweek" spelling, "and"-rule, voice IDs verified via `/v1/voices`, variants per type matrix.
    **If Path B:** §7.B.1 music architecture complete — bed source, continuity, peak + quiet moments, LUFS target.
22. **If Path A:** Acceptable WPM band stated for this film with a one-line reason (matched to type reference band · derived from §7.A.1 architecture · first-of-type derivation lock).
    **If Path B:** Captions-as-narrator declaration in §7.B.3 — every meaning-bearing scene listed in §8 captions table.

**Captions**
23. Captions table present (skip Sting).
24. ≤ 60 chars/line, ≤ 2 lines.

**Mobile cut**
25. Mobile cut spec present per scene. Depth scales with film length:
    - **For films ≥ 30s (Launch · Industry):** full per-scene block required — (a) mobile hero frame description, (b) entrance contract deltas from desktop (which elements re-position, re-size, or re-flow), (c) mobile safe-area verification (no element crossing top 220 / bottom 380 on 1080×1920 unless justified).
    - **For films < 30s (Feature · Customer):** a compact recut row per scene is sufficient if it names (a) the layout shift and (b) any element that moves into mobile safe area. Element-level entrance deltas can be condensed.
    - **Skip Sting; n/a Reel** (mobile IS master).
26. No element crosses safe area (top 220 / bottom 380 on 1080×1920) unless justified.

**Assets**
27. Every asset has G/D/R status + concrete path/link/request.
28. No assumed-available assets.
29. Adaptation noted for any unavailable asset.
30. UI-anchored scenes name a real source anchor (screenshot, design file, or registered component). Motion-concept scenes are exempt. No UI invented from imagination ("looks-like-Queek" CSS from intuition remains the documented fail mode).

**Quality gates**
31. Snapshot frames listed for desktop + mobile.
32. Inspect samples count chosen; intentional overflows marked.
33. Render targets table filled.
34. Production budget filled (skip Sting).

**Type + submission**
35. Scene count ≤ type cap.
36. Duration + aspects match Direction.
37. Validator score line at bottom of submission.

**Audio architecture pass (1 item, path-branching)**

38. Audio architecture pass per declared path. *(Skip only if Brand sting — uses §7-sting micro-spec, no gate.)*

    **If Path A:** §7.A.1 audio math table is complete AND Pass = ✅. Specifically:
    - Sum of VO anchor windows calculated (matches §6 within ±10%)
    - Derived WPM calculated (words ÷ windows × 60)
    - Acceptable band stated with a one-line reason
    - Derived WPM falls inside band
    - No per-scene VO window exceeds 220 WPM (physically un-deliverable)
    - §7.A.4 word-anchored cue sheet present: VO script line-by-line + cue-by-cue table (one row per SFX event, cue column = word/moment not seconds), with the single peak and quiet beat marked. This is what the human approves the sound design from at plan time.

    **If Path B:** §7.B.4 pass table is ✅. Specifically:
    - §7.B.1 music architecture: all 5 fields filled
    - §7.B.2 SFX events table: ≥ 1 row per scene that needs sound-design punctuation
    - §7.B.3 captions cover every meaning-bearing scene in §8

    Mixed paths within a film are not permitted — one path per master.

---

## Checks

Pre-flight flags low-readiness — surface and ask before proceeding. Close gate blocks completion — fix or waive in postmortem with reason.

### Pre-flight (project start)

| # | Check | If fails |
|---|---|---|
| 1 | `CLAUDE.md` loads at cwd (project-instructions layer) | FLAG — not load-bearing; `memories/brand.md` (#2) is the portable brand source. Absent when run outside the creative repo, which is fine. |
| 2 | `memories/brand.md` loads at cwd | HARD STOP — this is the brand source of truth |
| 3 | `memories/asset-libraries.md` loads | NOTE + flag |
| 4 | `research/REFERENCES.md` exists | FLAG — library missing, partially blind |
| 5 | References for this type ≥ 2 (mature) · ≥ 1 (developing) · = 0 (first-of-type — allowed; carries Close item 11 obligation) | FLAG — name the count; if first-of-type, surface the Close item 11 lock |
| 6 | `memories/voice-options.md` exists (if VO needed) | FLAG — request direction |
| 7 | Voice path resolves (MCP or API key in `<repo>/.env`) | FLAG — request setup |
| 8 | Asset wrappers in `bin/` present | FLAG — note missing ones |
| 9 | Failures-register scan against brief | FLAG any F-class match (see `research/patterns/pattern-failures.md`); propose avoidance |

Output format:

```
Pre-flight for <slug> (<type>)
✓ <passed>
⚠ <flagged> — <reason>
✗ <hard-stopped> — <reason>

Proceed? [Y/N]
```

### Close gate (before "done")

| # | Check | Pass condition |
|---|---|---|
| 1 | `works/<slug>/postmortem.md` exists | Every required section per template non-empty |
| 2 | `research/references/ref-queek-<slug>.md` exists | Follows `references/reference-template.md` |
| 3 | `research/REFERENCES.md` index updated | New entry under the right type |
| 4 | Renders saved | Desktop + (if applicable) mobile mp4 |
| 5 | Audio deliverables saved | Stems + master + audio-timeline.json |
| 6 | Plan was followed | Shipped matches Plan within documented adaptations |
| 7 | Research/memory diff filed | Update applied, OR postmortem says "no new insight" with reason |
| 8 | Read-back verified | Items 1, 2, 3, 7 re-read after write |
| 9 | Three-axis review green | Technical · brand · story all pass |
| 10 | `TASK.md` in closed state | Only `[x]` or `[-]` items remain |
| 11 | First-of-type reference obligation (only when pre-flight #5 = 0) | New entry seeded under this type in `research/REFERENCES.md` AND `research/references/ref-queek-<slug>.md` written from `references/reference-template.md`. |

Output:

```
Close gate for <slug>
✓ <passed>
✗ <failed> — <missing>

Result: <DONE | BLOCKED>
```

### Read-back rule

Every required write follows: write → read back → confirm content → if missing or malformed, rewrite and re-read. Disk-write success is not content present.

### Waivers

Items 2, 3, 7 can be waived in the postmortem. Items 1, 4, 5, 6, 8, 9, 10, 11 cannot — the postmortem, renders, audio, plan-fidelity, read-back, review, task closure, AND first-of-type reference seeding (when applicable) are non-negotiable. Item 11 only fires when pre-flight #5 = 0, but when it does, it's non-waivable: a first-of-type project must seed the type's first reference at Close, else the next film of that type re-enters the same first-of-type loop indefinitely. Waiver format:

```
- Item <n> (<name>) — <reason>. Date: <YYYY-MM-DD>. Approved by: <human>.
```

Missing any of the four fields invalidates the waiver.

---

## Make phase

Plan locks the contract; Make builds against it. Make doesn't re-pick durations, rewrite VO, choose colors, invent UI, or change story beats. If Make hits a decision that isn't in Plan, route back to Plan with the gap.

| Plan delivers | Make builds |
|---|---|
| Direction · signature · tokens · scene script · per-scene UI specs · audio plan · captions · asset checklist · render targets · approval | Composition skeleton · component HTML · timeline animation · VO audio · audio mix · snapshots · linted/validated/inspected output · final renders |

Three sub-phases, one gate each. Audio first (it's the timing source), then video to audio, then mobile to approved desktop. Within Video, each scene clears a per-scene quality gate (HF suite + fresh-context critic) before the next begins — WIP=1, so quality is enforced scene-by-scene, not rushed across all at once. See §2 Video.

### Pre-flight reference scan

Read `research/REFERENCES.md`. Pull the 3–5 refs cited in the approved Plan. Read each fully before authoring — patterns drift in memory.

### Toolchain + skills to load

| Tool | Why | How |
|---|---|---|
| Tailwind v4 browser runtime | Utility classes let you match screenshot tokens precisely (`bg-[#FBF4E3] gap-[14px]`) without magic numbers | `npx hyperframes init --tailwind` |
| Lucide icons | The Queek vendor portal uses Lucide-style line icons throughout | CDN inline SVG from `lucide-static` / `unpkg.com/lucide-static` |
| Inter font | Queek vendor portal type — built into HF, no `.woff2` work | Reference in CSS directly |
| GSAP | All HF animation — already loaded by HF runtime | Available globally |

NOT in toolchain: shadcn React (HF is vanilla HTML — lift shadcn's *visual patterns* into your own components, never install React/Next), custom font hosting (unless `design.md` names a non-built-in font), additional icon libraries (Lucide alone).

**Bundle every non-built-in font locally — never load from a CDN.** The render sandbox blocks external requests (`fonts.googleapis.com` → `ERR_BLOCKED_BY_ORB`), which surfaces as a **validate error** and silently falls back to the wrong font in the render. For any family beyond HF's built-ins (e.g. Fraunces, Instrument Serif, Caveat): fetch the `.woff2` files into `composition/fonts/`, write local `@font-face` (one `fonts.css`), and link that — not a `<link href="fonts.googleapis.com/...">`. The HF lint also warns `google_fonts_import`; treat it as a must-fix before render, not a warning to ignore. (Tip: fetch the Google Fonts CSS with a desktop browser User-Agent to get the woff2 URLs, keep the `latin`/`latin-ext` subsets.)

Skills to load alongside `queek-premium-video`:

| Skill | When |
|---|---|
| `hyperframes` | Always (every comp) |
| `hyperframes-cli` | Setup onward (init, lint, validate, inspect, snapshot, render) |
| `tailwind` | While authoring component HTML |
| `gsap` | While wiring scene timelines |
| `emil-design-eng` | While building each component (polish discipline) |
| `frontend-design` | While building components (distinctive aesthetic) |
| `impeccable` | Pre-render review pass |
| `lottie` · `three` · `typegpu` | Only if the scene uses them |

### Layer tags (use in scene specs)

| Tag | Meaning |
|---|---|
| 🟢 Motion | HF + GSAP animations · motion graphics · signature device in motion |
| 🔤 Text | Kinetic typography · on-screen text · captions |
| 🎨 UI Mockup | HTML mockup, anchored to a real screenshot / design / reusable component |
| 📺 Platform Capture | Literal screen recording placed in the comp (bronze path — reads fuzzier at video scale) |
| 🎞️ Stock | Third-party clips (Pixabay, Pexels) |
| 🎥 Manual Film | Live-action filmed by the human |

### Scene buckets (decided in Plan, executed in Make)

Two buckets. Same product, different production approach.

**UI-anchored** — scene's purpose is to *show* a real product concept (a surface that exists), elevated into premium motion design. Viewer should recognise the product *and* feel it's premium — not see a pasted screenshot. Layer: 🎨 UI Mockup (or 📺 Platform Capture). The screenshot anchors concept (real data/states/features), not appearance. Two failure modes: (a) inventing UI from imagination → "looks-like-Queek" fake features; (b) flatly replicating the screenshot → accurate but not premium. The win is real-concept + premium-elevation.

**Motion-concept** — scene's purpose is to *convey a lifecycle moment* through motion graphics anchored to the film's signature device. Layer: 🟢 Motion · 🔤 Text (no 🎨, no 📺). Uses brand-real content (real names, real ₦ amounts) but no platform UI chrome. Failure mode: forcing literal UI where motion would land cleaner.

Rule of thumb: UI-anchored buys credibility; motion-concept buys clarity. The Plan picks per scene; Make doesn't re-decide.

### 1 · Audio

Read `memories/voice-options.md`. Render the VO variants per type matrix. Build the FX bed and SFX from the Plan's cue list — every SFX lands 10–20ms before its visual lock because the ear processes sound faster than the eye; leading audio makes motion feel intentional.

Master per `research/patterns/pattern-premium-vo.md`: -11 to -14 LUFS, true peak ≤ 0, LRA ≤ 3, one intentional peak, one quiet beat, clean silent stop.

**Face-cam mode audio rules** (applies when brief has `face-cam: true`)

| Face-cam supplied with… | Audio path |
|---|---|
| Sync audio (human spoke on camera) | VO = the face footage's own audio track. No TTS render. §7.a math runs on the **actual** words spoken / duration spoken — measure with Whisper (`hyperframes-media` skill), don't estimate. Mix VO with the bed at -16 LUFS as usual; do NOT re-EQ or re-pace. |
| Video only (no usable audio) | VO = separate TTS render OR new VO recording. §7.a math applies normally. Treat as standard VO film. |

**Music architecture under face-cam:**
- Default: quiet bed (-26 to -28 LUFS) so the face's audio sits forward; no peak hits over a face speaking.
- One-line declaration in §7.a: `"bed runs at -26 LUFS continuous; one drop at <s> for landing moment <name>; no hits during face-speech windows"`.

**SFX under face-cam:**
- Avoid SFX during face-speech windows; SFX cues belong in non-speech transitions, B-roll inserts, and the close.

Mix targets: bed -22 LUFS · VO -16 · SFX -14 · big impacts -10 to -12. Music architecture is **layered, not composed** — bed runs continuous, stems (cello sustain, piano notes, closing sustain) trigger at scene moments, SFX fire on visual events.

Save audio + timeline alongside stems. The timeline lets the video phase wire anchors directly:

```json
{
  "duration_s": 50.0,
  "anchors": [
    { "scene": "S1", "vo_start_s": 0.0, "vo_end_s": 2.8, "sfx_cues": [{"name":"paper-tear","at_s":0.4}] }
  ]
}
```

Deliverables → `works/<slug>/deliverables/`:
- `<slug>-master.mp3` (winner audition)
- `<slug>-vo.mp3` · `<slug>-fx-bed.mp3` (stems — kept separate so they re-render independently)
- `<slug>-master-<loser>.mp3` (2-variant types)
- `<slug>-audio-timeline.json` (if applicable)
- `README.md` (scene-anchor handoff table)

Plus the human-approval artifact at `works/<slug>/audio-cue-sheet.md` (see below).

#### Audio cue sheet (HARD — the Gate 1 approval artifact)

Before Gate 1, generate `works/<slug>/audio-cue-sheet.md` per [references/audio-cue-sheet-template.md](references/audio-cue-sheet-template.md) and submit it to the human alongside the audio. JSON timelines are for the video phase; the human approving audio needs a legible cut-to-cut sheet.

The cue sheet MUST contain:
1. **Header** — bed file + character, continuous range + level, master LUFS/TP.
2. **VO script line by line** — numbered 1..N, no "S" prefix, just the spoken lines as one readable block.
3. **Cue-by-cue table** — one row per SFX event: `# · Scene<br>(range) · VO words · Effect · Character · Start · Dur · Tracks(motion)`. Scene label+range stacked, shown on the scene's first row; sub-rows (↳) for additional cues in the same scene.
4. **Totals** — SFX count, the single peak, the quiet beat, recurring motifs.
5. **Approval checklist.**

All timings transcript-derived (`hyperframes transcribe` on the rendered VO — scene start = first word onset, end = last word offset). Never estimate; state "transcript-derived" in the header.

#### Audio sanity check (HARD — runs before Gate 1)

Every VO stem rendered at this phase MUST clear the bundled `bin/audio-sanity-check.sh` before reaching the human ear-test. **The tool only catches mechanical extremes** — clipping, wildly off loudness, uneven delivery (LRA > 3.5), drag/rush pace, single-take reads with zero pauses. **It does NOT predict premium quality.** Premium = ear judgment.

The script ships *inside this skill*, not in the brand-KB repo. Resolve it relative to the skill's own install directory (`SKILL_DIR` = the directory containing this `SKILL.md`, which the runtime reports at invocation) — never a hardcoded `~/.claude` path, since the skill may be installed project-locally elsewhere.

```bash
# SKILL_DIR = this skill's install directory (the dir holding SKILL.md)
"$SKILL_DIR/bin/audio-sanity-check.sh" \
  works/<slug>/deliverables/audition-<date>/kokoro-heart.wav \
  --script works/<slug>/voice-script.txt
```

See [references/audio-sanity-rubrics.md](references/audio-sanity-rubrics.md) for the 5 checks + calibration anchors.

- **PASS** → forward to Gate 1 human ear-test. PASS does not mean premium; PASS means no mechanical issue detected.
- **FAIL** → fix the specific failure (typically LRA > 3.5 = re-render with different voice/speed/script; or clipping = lower peak via loudnorm). Re-render, re-check. Don't surface a FAIL to the human.

Surface the check output in `works/<slug>/TASK.md` Notes. Gate 1 cannot sign off without an audio-sanity-check entry showing PASS on every audition surfaced.

**Why narrow scope:** prior v1 of this tool tried to predict premium via pause-count bands. FAILED the gold-standard shipper.mp4 reference AND user-preferred Kokoro renders. Calibration was inverted. Current v2 only catches mechanical extremes (validated 2026-05-21 against 5 calibration anchors). Premium-feel can't be automated yet.

**Gate 1** — human reviews the `audio-cue-sheet.md` + ear-tests the audio, then picks the winning variant and approves the cue sheet (or marks rows to change). The sanity check is upstream — the human only ear-tests renders that already cleared it. Gate 1 cannot sign off without an approved cue sheet. Durable gate — write the `[!] AWAITING Gate 1` line per §Gate protocol.

**On audio re-lock, regenerate the timeline.** Whenever the audio changes after first lock (new master version, retimed cue, added/removed SFX, different VO take), regenerate `<slug>-audio-timeline.json` from the approved `audio-cue-sheet.md` in the same commit. The cue sheet is the human-approved truth; the JSON is its machine mirror. A stale timeline silently desyncs the video — it must always describe the master that actually shipped (duration, scene windows, every cue at its real second).

### 2 · Video

#### Audio is the spine (HARD — reconcile before authoring)

The video syncs to the **locked per-project audio timeline** (`works/<slug>/deliverables/<slug>-audio-timeline.json`), not to the Plan. Audio is built first and gets iterated at Gate 1; by the time video starts, the Plan's timing — and sometimes its scene count, VO lines, or duration — can be stale. The audio that shipped is the spine; the video lands on it.

Before any HTML, reconcile Plan ↔ locked timeline:

1. Read the locked timeline JSON. Compare its `duration_s`, `scenes[]`, and `vo.lines[]` against the Plan's §1 duration and §6 scene script.
2. **If they match** — proceed; the Plan's scene intents drive content, the timeline drives every anchor time.
3. **If they diverge** (different duration, scene count, or VO script — e.g. the audio was re-cut tighter than the Plan) — the **timeline wins on structure and timing**; re-align the Plan's scene grid onto the locked timeline (same number of scenes, same windows, same VO lines) before authoring. The Plan still governs *visual* intent (signature device, tokens, technique) per scene — but it owns no timing the locked audio contradicts.
4. Record the reconciliation outcome (`matched` or `re-aligned: <what changed>`) in `works/<slug>/TASK.md` Notes.

Routing a structural divergence back to "just follow the Plan" is the failure this gate prevents — it produces a video cut to a film the audio no longer is.


> **Note:** Skipping the Pre-Gate-2 reference scan below is **F21** in `research/patterns/pattern-failures.md`. Manifests as flat Tailwind cards, generic fade-in motion, and synthetic UI surfaces. The scan block in TASK.md Notes is the hard gate — no HTML before it lands.

#### Pre-Gate-2 reference scan (HARD — blocks all HTML authoring)

**No `.html` file is created in `composition/` until a `Reference scan — <YYYY-MM-DD>` block exists in `works/<slug>/TASK.md` Notes section.**

Make MUST read, before any HTML:

1. **Every reference cited in PLAN §1 References table** — open the actual file (or fetch the URL), not just the reference card. For local file paths, `Read` the file. For external links, `WebFetch` or note the read-source.
2. **Queek mockups v1** — resolve path via `memories/asset-libraries.md`. Look at the actual designs.
3. **Queek Vendor portal screenshots** — resolve path via `memories/asset-libraries.md`. Real production surfaces (includes POS as `pos.png`).
4. **Queek WhatsApp components** — resolve path via `memories/asset-libraries.md`. Premium reusable components for any chat-scene clone-and-adapt.
5. **Premium-video feedback memories** — `feedback_read_refs_before_first_keyframe` · `feedback_creative_ambition` · `feedback_amplify_motion` · `feedback_premium_video_standard`. These are the bars prior films failed against; read them before authoring.
6. **Prior-shipped HF references** — for any cited HF launch / promo / kinetic-type reference, open the actual `.html` in `hyperframes-launches/` or `research/references/`. The composition IS the spec — extract tokens, motion vocab, layout decisions.

Confirmation format — append this block to TASK.md Notes:

```markdown
### Reference scan — <YYYY-MM-DD>

| Ref | What I'm lifting |
|---|---|
| `hyperframes-launches/hyperframes-launch/compositions/thesis.html` | editorial Instrument Serif italic 132–220px on cream + dot-grid at 16% alpha |
| `ref-queek-os-launch-film-60s` | tokens (warm cream `#fbf4e3`, motion vocab cam-push / tilt-rake / shimmer-sweep), STAR skeleton |
| `feedback_amplify_motion` | particles ≥24px, dense streams, ambient breathing — register at video scale |
| ... | one row per cited reference + each Queek library opened + each feedback memory read |
```

Authoring HTML without this block is a process failure — same shape as F19 (audio math without derivation) and F5 (UI without source anchor). See F21 in `research/patterns/pattern-failures.md`.

#### Authoring (after the scan block lands)

Initialise the composition via `/hyperframes`. Write `design.md` from Plan tokens before any composition HTML.

Build static layout first (HF's *Layout Before Animation*) — overlaps are invisible until render unless the end state is built first.

**Author one scene at a time, fully, in order — never batch all scenes in one pass.** Batching is the rush: effort front-loads and the tail coasts until the human corrects it. The per-scene quality gate below makes WIP=1 a hard rule.

Per scene:
- Read the cited reference for the technique. Don't rely on memory.
- Decide host (inline / sub:) per Plan; if sub, justify (sub-comps using `tl.call` / `onUpdate` / bare `gsap.set` outside the timeline won't seek deterministically — see F1/F2 in `research/patterns/pattern-failures.md`).
- Build entrances per contract.
- Build transition-in.
- Wire to audio anchors from the timeline JSON.
- Snapshot the peak frame (via HF) and `Read` the PNG. Black or empty means the timeline didn't seek — fix before continuing. Inline a sub-comp that fails repeatedly.

#### Per-scene quality gate (HARD — WIP=1 + fresh critic)

The agent may not start scene N+1 until scene N passes this gate. Two checks, in order:

1. **HF gate suite** (mechanical — *is it broken?*): lint · inspect · validate · animation-map. Three failed snapshots on the same scene means the reference doesn't match the Plan's intent, or the technique doesn't seek — stop iterating motion, inline the scene, swap the technique, or route back to Plan.
2. **Scene critic** (premium — *is it good?*): a **fresh-context critic subagent** scores the scene against the reference it was built from, on the observable rubric in `references/scene-critic-rubric.md`. **Judge a frame SEQUENCE across the scene window (entrance→settle), not one still** — premium lives in the motion, and a single frozen frame can't show whether it animated well or just popped in. Snapshot ~5–7 frames in one HF command (HF overwrites the dir per run). **Re-snapshot on any missing frame; never let the critic judge a substitute frame** (a verdict about the wrong frame is invalid). Self-grading is banned — the builder is primed to declare "done" (see the vo-grade lesson). Invoke `Agent` (`subagent_type: general-purpose`), fresh each scene, with the prompt template in the rubric. The critic returns `PASS | FAIL + fails list`.

Loop: **FAIL → apply the critic's fixes → re-render → re-critic, max 3 rounds.** Still FAIL after 3 → escalate to the human with the gap list (not a pass; the scene stays open). PASS → log the verdict to the TASK.md *Scene critic log* (format in the rubric) → advance.

The human only ever sees critic-passed scenes — that is the point of the gate. Human eyes are reserved for: the **first scene's** hero frame (taste anchor — confirms the critic is calibrated to this film) and the **peak scene** (the money shot). Every other scene is critic-gated, then shown in the Gate 2 deck.

#### Per-Platform-UI-scene workflow

For every 🎨 UI Mockup scene:

1. Confirm which surface (Orders, Setup, Customer profile…) and which design / screenshot is the **concept** source — what data/states/flow/features are real. The screenshot tells you *what's true*, not *how it should look*.
2. Verify the screenshot is in a registered library. If missing, request it and block until supplied.
3. Search L0–L3 (below) for an existing reusable component. Building from scratch when a reusable exists is a process failure.
4. Build a **premium, motion-ready version of that concept** in HTML — Tailwind + Lucide + Inter. Take the real data/states/flow from the screenshot; elevate the *design* well beyond it (type at video scale, depth, cinematic composition). The goal is a frame that looks better than the screenshot, never a pixel copy. Don't bitmap; build so it scales at 4K and animates.
5. Iterate toward **premium**, not toward the screenshot. Use the screenshot to check concept fidelity (right data, no invented features); use the gold-pole references (HF launch, motion.mp4) to push design quality. A frame that merely replicates the screenshot has failed — that's just the screenshot, not premium video.
6. Add the animation contract from the scene spec.
7. Snapshot animated key timestamps; verify motion lands.
8. Resolve any overflow or contrast failure flagged by the HF gate suite.
9. Clear the **Per-scene quality gate** above (HF suite + scene critic). Human sign-off on the static hero frame is required only for the **first scene** and the **peak scene** — every other UI scene is gated by the critic, not the human.

Bitmap a screenshot literally into the comp **only** when the human explicitly asked, OR the screenshot is too complex to faithfully replicate AND its visual already fits the film's design language. Default = build the HTML.

#### Screenshot anchor — concept source, not a replication target

The screenshot is source-of-truth for **what's real** (data, states, flow, features) — NOT for how the scene looks. Replicating it is a non-goal; **elevating it into premium motion design is the goal.** If matching the screenshot were the bar, the AI could paste the screenshot — and that fails the premium bar. So the scene must look *more premium than the screenshot*, while staying conceptually true to the product.

- ✅ Expected (and rewarded): re-compose for the frame · enlarge to video scale · add depth, motion, cinematic staging · turn a static element into an animated one (status pill → animated stepper; setup list → live build queue) · cut columns that are noise · use brand-real content (real ₦, `brand.md` names).
- ❌ Forbidden (concept violations only): features/screens/states/actions the product doesn't have · colors outside the palette · copy outside the product's vocabulary.
- ❌ Also a fail: a **static, faithful replica** of the screenshot (accurate but flat/web-scale/motionless). Accuracy is not the bar; premium is.

Rule of thumb: keep what's *true* (real data/states/features), elevate how it *looks* (premium, motion, scale). Never pass a scene for matching the screenshot; never fail it for surpassing the screenshot.

#### Component graduation (L0–L3)

Build components once, reuse forever. Graduation grows the library only as components prove themselves.

| Level | Location | Graduation trigger |
|---|---|---|
| L0 — embedded | inline in `composition/index.html` | only ever in one scene of one film |
| L1 — project-local | `composition/components/<name>.html` | used in 2+ scenes of the same film |
| L2 — shared candidate | `works/_components/<name>.html` | cloned to a 2nd film. Move at the moment of clone — both films then read from L2 |
| L3 — org library | `files/components/<name>.html` (registered in `memories/asset-libraries.md`) | proven in 3+ films · token API stable |

Each component declares (top-of-file comment): concept source (which real surface/screenshot it draws its data + states from — not "replicates") · tokens consumed · variants · animation hooks.

Build-time rule: search L0–L3 first before authoring any new component.

**Gate 2** — human approves desktop preview. Durable gate — write the `[!] AWAITING Gate 2` line per §Gate protocol.

### 3 · Mobile

Clone the composition (`cp -r composition/ composition-mobile/`). Edit only the clone.

Per scene, re-author for 9:16: reposition elements for the vertical canvas, re-size hero/body type for thumb distance, reframe the hero subject for portrait, respect the safe area (top 220px, bottom 380px on 1080×1920). The mobile cut is not a crop — the frame is too different and content would clip.

Audio reuses desktop stems by default. Re-anchor only if a scene's beat moved.

Snapshot-verify mobile. Re-run the gate suite.

**Gate 3** — human approves mobile preview. Durable gate — write the `[!] AWAITING Gate 3` line per §Gate protocol.

### 4 · Integrate + render

Wire VO + FX as separate audio tracks on both compositions. No mastering at this step — stems ship pre-mastered. No new SFX — sound design happens at the Audio phase.

Render via `/hyperframes` per the render targets in the Plan. HF owns codec, bitrate, and output locations. By convention renders land inside each composition (`works/<slug>/composition/renders/` and `works/<slug>/composition-mobile/renders/`) — where-to-look, not a path the skill pins. Skip mobile render for Brand sting and Reel (mobile IS the master).

### 5 · Three-axis review

**Technical** — Lint, validate, inspect all clean · animation-map: no unintended `paced-fast` / `paced-slow` / `collision` / `offscreen` · dimensions match Plan · sync ≤ 50ms (captions within ±100ms) · no drops or crackle.

**Brand** — First frame holds muted (would a viewer scroll past?) · color discipline per scene · "Queek AI" / "AI Agent" naming everywhere · no banned filler · approved copy verbatim · CTA legible at thumbnail muted.

**Story** — Final 1s holds the close · hook → payoff under 3s for short-form, under 8s for long-form · energy arc actually lands · no competitors · no fabricated numbers.

**Reference diff** — Compare against cited refs. Honour, don't copy. Flag any place where a reference's pattern was attempted but missed.

All green → Close. Any fail → route back to the phase that owns the gap. Don't patch a story-fail at render time.

---

## Task tracking

Each project keeps `works/<slug>/TASK.md`. Granularity is your call — five tasks for a Brand sting, eighty for a Launch film, both fine.

Required: file exists · consistent statuses · read first on session resume · update as work happens · closed state at close (no `[ ]`, `[~]`, or `[!]` items remaining).

**Statuses:** `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked (reason inline) · `[-]` waived (reason inline). A `[!] AWAITING <gate>` line is the durable-gate marker (see §Gate protocol) — it carries the question + artifact paths and is resolved to `[x]` when the human answers, in the same session or a later one.

**Skeleton:**

```markdown
# TASK · <slug>
Type: <type> · Status: <phase | DONE>
Last: <timestamp>

## <phase>
- [x] done
- [~] in progress
- [ ] todo
- [!] blocked — <reason>

## Notes
<scratchpad for next session>
```

On resume: read TASK.md → pick up at the first non-`[x]` item → check `[!]` items and Notes before continuing. If the first open item is a `[!] AWAITING <gate>` line, read the human's resolution from that line (or appended below it); if no resolution is present yet, the gate is still pending — stop cleanly. Sessions cut; persistent task state keeps the next agent from re-deriving where you were.
