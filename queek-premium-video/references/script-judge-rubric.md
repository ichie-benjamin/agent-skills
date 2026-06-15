# Script / copy judge (writing-quality gate)

Premium video is also *writing*. Validator B checks the plan is structurally
complete; it does not check whether the words are good. A film with perfect
composition and motion still falls short if the hook is weak, lines restate
each other, or the close doesn't land. This gate judges the writing — the VO
script (Plan §7), the on-screen text, and the captions (Plan §8).

A fresh-context judge subagent (`Agent`, `subagent_type: general-purpose`)
scores the copy. Floor, not ceiling (§Gate philosophy): it fails weak, padded,
jargon-heavy, or inaccurate writing — never a bold voice, an unconventional
structure, or a strong line that breaks a "rule."

## Cost discipline

- **Runs at the Plan gate, on text only** — the cheapest possible place. Catch
  weak writing *before* a single scene or VO render is paid for. A near-free
  gate that prevents the most expensive rework (building a film around a script
  that doesn't work).
- **One pass.** It returns a verdict + the single biggest lift; the author
  rewrites and re-judges only if it FAILED. No multi-agent panel — writing
  quality at this floor is a single-judge call.
- Reads the script + brand voice (`memories/brand.md`) + the Plan's
  creative-bet header. Nothing else.

## The dimensions (0 / 1 / 2 each — premium = no zeros AND ≥ 11/14)

1. **Hook strength.** The first spoken line (and first caption) earns the next
   3 seconds — concrete, specific, a thing the viewer has felt. A meta-opener
   ("Have you ever wondered…", "In today's world…"), a warm-up, or a vague
   abstraction = FAIL. Open on the seen thing.
2. **Line economy — each idea once.** Every line earns its place. No filler, no
   restatement of a prior line, no explaining one point three ways. If a line
   can be cut with no loss, it should be. Padding = FAIL.
3. **Plain language + real terms.** Real engineering/product terms used
   correctly, each with a one-line plain gloss the first time — no jargon for
   its own sake, no academic/heavy words, no vague hand-waving. Both extremes
   (impenetrable *and* dumbed-down-to-nothing) = FAIL.
4. **Concrete over abstract.** Claims are grounded in a real example, a real
   number, a real tool/surface — not asserted in the air. "It's powerful" with
   nothing behind it = FAIL.
5. **The close lands.** The final line / CTA pays off the hook and is a clear,
   earned ask — not a trail-off, not a generic sign-off, not a second new idea
   crammed into the end.
6. **Accuracy.** Every claim is literally true: no fabricated numbers,
   partners, features, or capabilities the product doesn't have. One invented
   fact = automatic FAIL (this item can zero the whole gate).
7. **Voice fit + clean copy.** Matches the brand voice in `memories/brand.md`;
   no banned filler, no banned hedges, no competitor names, correct product
   naming. (Standalone/other brands: judge against whatever voice spec resolved,
   else generic premium discipline.)

## Verdict format (return EXACTLY this)

```
SCRIPT VERDICT: PASS | FAIL
SCORE: <passed>/<applicable ×2>
FAILS:
- <item #/name> — <the weak line, quoted> — <concrete rewrite direction>
(omit FAILS block only when SCORE is full)
BIGGEST LIFT: <one line — the single change that most raises the writing>
```

PASS requires **no zeros AND ≥ 11/14**. Item 6 (Accuracy) zeros the gate on
any fabrication regardless of the rest.

Quote the actual weak line in every fail — a verdict the author can't locate
is not actionable. Judge the words on the page, never the author's intent.
