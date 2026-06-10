# Brand spec template → `memories/brand.md`

Written by §Brand setup on the skill's first production run in a project
(or by hand). Lives at `memories/brand.md` at the project root and is the
brand source of truth the validators and scene critic score against —
every field maps to a Validator A row or a critic item, so a blank field
is a check that can't run. Fill every field; write `none` where a rule
genuinely doesn't exist rather than leaving it blank.

Setup order: distill what the project's own design docs already answer,
then ask the human ONLY the gaps (in the consolidated Intake message).
Never infer palette hex, naming rules, banned terms, or voice.

```markdown
# Brand — <brand/product name>

Source: distilled from <files> + human answers, <YYYY-MM-DD>.

## Identity + naming                          (→ Validator A.22)
- Product name, exact on-screen spelling:
- One-line product truth (what it actually does — anything beyond this
  is a fabricated feature, A.24):
- Naming rules — required forms / banned forms (e.g. Queek: "Queek AI" /
  "AI Agent"; never "bot", "chatbot", "Qee"):
- TTS spellings (words VO must spell phonetically, e.g. "Kweek"):

## Palette                                    (→ A.12, A.23, critic 1/6)
- bg:          #
- ink:         #
- accent:      #
- supporting:  #
- Usage rules (e.g. light bg only; accent never as a section fill):

## Type                                       (→ A.13, critic 2)
- Hero font (+ file or built-in):
- Body font:
- UI font:
- Size bands at 1080p (hero / body / data labels):

## Shape + depth                              (→ A.14, critic 3)
- Corners:
- Depth character (shadow / glow / elevation):

## Motion feel                                (→ A.15, critic 4)
- Eases:
- Duration band:
- Character (one line, e.g. confident, settled, no bounce):

## Voice + copy                               (→ A.19–21, A.5)
- Tone:
- Banned filler:
- Banned hedges:
- Competitors policy (banned list, or "never named"):
- CTA conventions (verbatim forms):

## Content truth                              (→ A.24, critic 8/10)
- Real data sources (where real names / amounts / screens come from):
- Currency / locale:
- Always on: no fabricated numbers, partners, features, screens, states.

## Production resources                       (optional — FLAG-class)
- Screenshot / mockup library:
- Reusable component library:
- Voice options file:
```
