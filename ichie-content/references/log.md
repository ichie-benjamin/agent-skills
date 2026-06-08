# `/ichie-content log`

Close the loop after a publish. **Mandatory** — never end a production session without at minimum the initial log row. This is the only mechanism that makes the studio compound.

## Two phases

### Pre-condition: validate PASS

Before any of this runs, the piece's `validation.md` must show a `VERDICT: PASS` from `/ichie-content validate`. No PASS, no publish. If the validator hasn't been run, STOP and run it first.

### A. At publish time (right when it ships)

1. **Append a row** to `dev_content/analytics/performance.md`:
   ```
   | <YYYY-MM-DD> | <title> | <platform(s)> | <format> | <hook used> | | | | | |
   ```
   Metrics blank for now — filled at follow-up.

2. **Snapshot followers.** Ask the user (or have them paste) current follower count on each of IG / TikTok / X / YouTube. Append a row to the "Follower count snapshots" table.

3. **Move the piece** from `dev_content/content/drafts/<slug>/` → `dev_content/content/published/<slug>/`.

4. **Update backlog.** Set the matching row in `dev_content/ideas/backlog.md` → status `✅ published`.

### B. Follow-up (24–72h after publish)

1. **Get metrics.** Ask user (or accept paste) for: views, likes, saves/shares, follows attributed (best estimate).

2. **Fill in the analytics row.**

3. **Write the lesson** (hard-gate). Create/update a memory:
   ```
   ---
   name: lessons-<topic-or-pattern>
   description: What we learned from <piece> on <platform>
   metadata:
     type: feedback
   ---
   
   <piece title> on <platform> got <metrics>.
   
   What worked: <one sentence>
   What flopped: <one sentence>
   Hypothesis why: <one sentence>
   Apply next time: <do this / avoid this>
   
   Related: [[hook-lesson-<pattern>]] [[content-strategy]]
   ```

4. **Update `MEMORY.md` index** with the new lesson.

5. **If the lesson contradicts an existing memory**, update or delete it. The hard-gate says: no duplicates, delete what's proven wrong.

## Why this can't be skipped
Every published piece without a logged lesson is a missed compounding event. After 30 pieces with `log`, you have 30 data points that bias the next slate toward what works. After 30 pieces without `log`, you have intuition that may or may not match reality. The whole studio architecture is built on this.
