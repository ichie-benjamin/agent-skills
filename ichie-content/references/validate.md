# `/ichie-content validate <draft-path>`

Independent quality validator. Mandatory gate before any piece is published. Runs as a **subagent with a fresh context** so the producer's biases (yours, the model that drafted the piece) don't leak into the review.

## When to invoke

- After `repurpose` produces platform cuts — validate each cut, OR validate them as a bundle if they share a source.
- Before `log` — no publish without a PASS.
- On demand whenever a piece is being polished and you want a clean second opinion.

## How to run — the independent-subagent protocol

This is the critical part. **Do not "self-review" inline.** Spawn a fresh-context subagent via the `Agent` tool with `subagent_type: "general-purpose"`. The subagent only sees the inputs you pass — no chat history, no producer rationalizations. That's what makes the review independent.

Invocation template:
```
Agent({
  description: "Validate dev_content draft",
  subagent_type: "general-purpose",
  prompt: <see below>,
})
```

Prompt template the parent passes to the subagent:
```
You are an independent content-quality validator for Benny's dev_content
studio. You have NOT seen any prior discussion — only the materials below.
Apply the standard verbatim; PASS or FAIL with specifics. Be a hard reviewer.

## The standard (binding)

Every piece must satisfy:
1. Real-world example — at least one concrete, named (real company, real
   person, real shipped product, real event). No "Acme Corp," no hypotheticals.
2. Historical or contextual anchor — a precedent (famous bug, software era
   moment, named release/outage/paper). One sentence ok.
3. One verified quote from a canonical software/CS book — exact wording, with
   author + book + chapter/section. (See book-references memory for the
   canonical list.)
4. One intelligent comic cue — single-panel concept with caption, smart not
   slapstick (xkcd-adjacent or New-Yorker-single-panel style).
5. Zero unverified claims — every stat, fact, or assertion must be traceable
   to a source. Flag anything not sourced.

## What to check on EACH numbered point

1. Is the example real and checkable? (Search if needed; do not assume.)
2. Is the historical anchor real, correctly named, and dated correctly?
3. Is the quote VERBATIM (not paraphrased), correctly attributed (author,
   book, edition, chapter/section)? Reject "Steve McConnell once said…" with
   no source.
4. Is the comic cue specified clearly enough that an illustrator could
   produce it? Is it on-topic and intelligent (not corny, not offensive)?
5. List every claim that is NOT sourced. If any unsourced claim is a load-
   bearing assertion (carries the piece's argument), it is an automatic FAIL.

Additional checks:
6. Does the hook deliver on its promise in the body?
7. Is the voice tag at the top of the draft honored throughout?
8. Is the platform-correct CTA present?
9. Is there one promise, one payoff — or is the piece stuffed with multiple
   ideas? Stuffed = FAIL.
10. Coherence: does the argument actually hold? Walk through the logic.

## Materials provided to you

[paste each of: the draft file(s), the source transcript/research bundle
links, the chosen voice mode, and the relevant book-references ledger entry]

## Required output format

VERDICT: PASS | FAIL

If FAIL, list every issue under one of these headings:
- Missing standard element
- Unsourced / unverified claim
- Incorrect attribution
- Hook ↔ payoff mismatch
- Voice mismatch
- Stuffed (multiple ideas)
- Other

For each issue, give:
- Exactly where (slide N / post N / time-range)
- What's wrong
- The minimum fix

Do not soften. Producer wants a hard pass-or-fix list, not encouragement.
```

## Output handling

The subagent returns a verdict + issues list. The parent (your current Claude session) then:

1. **PASS** → the piece is cleared. Proceed to `/ichie-content log` when published.
2. **FAIL** → fix every listed issue. Re-run `validate` — do **not** skip the re-validation. Repeat until PASS.

## What goes into the studio after PASS

- The verdict + the prompt + the input materials should be archived next to the draft as `validation.md` in `content/drafts/<slug>/`. After publish, this file moves with the draft into `content/published/<slug>/`. That creates a paper trail and trains the studio's intuition for what passes vs fails.
- If a new quote was used and verified during the validation pass, append it to the [[book-references]] approved-quotes ledger (memory hard-gate).

## Why an independent subagent (and not just self-review)

Self-review by the producing model has a known bias: it tends to ratify what it just produced. A fresh-context subagent has no investment in the draft, no rationalization to protect. That's the only way to actually catch unsourced claims you'd otherwise wave through. This isn't optional — the architecture *is* the quality guarantee.

## Edge cases

- **Short pieces (X single-post, sub-30s video)**: standard still applies, but condense — the verified quote can be implied via a screenshot/citation card rather than spoken. The example + comic still required.
- **Pure-meme pieces**: extremely rare in this studio. If the slate has one, mark it explicitly (`type: meme` at the top of the draft) and the validator relaxes points 2–3 but still enforces points 1, 4, 5.
- **Series / part-N pieces**: standard applies per piece. Don't smuggle "we covered the quote in part 1" — the new piece must stand alone.

Related: [[content-quality-standard]] [[book-references]] [[themitmonk-style]] [[memory-discipline]] (project memory files).
