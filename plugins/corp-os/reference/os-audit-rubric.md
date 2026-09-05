# OS audit rubric

Reference for `corp-os-audit`. Used to assess any personal or team knowledge system — one built from this plugin, one built from a different model, or one that grew by accident — and to learn from it in both directions.

## Stance

This is a two-way audit and the second direction matters more. Anyone who has run a real system for months has solved problems the shipped model has not. Arriving to grade someone against Corp-OS and leaving without having learned anything means the audit was done wrong.

Say so out loud at the start: half of this is finding what is missing, half is finding what they invented.

## Dimension 1 — Is there a source of truth?

- Is there an append-only raw layer, or has everything been edited in place?
- Can any given conclusion be traced back to something someone actually said or wrote?
- Is the derived layer regenerable, or would losing it lose original material?

The single highest-value finding in most audits. A system with no raw layer cannot be corrected, only argued with, and every other dimension is downstream of this one.

## Dimension 2 — Is there a review gate?

- Does anything become "known" just by being captured?
- Is there a visible distinction between what was said and what was confirmed?
- Who or what performs the confirmation?

## Dimension 3 — Is provenance carried?

- Does each entry carry a source, a date, and a confidence?
- Are verbatim citations kept, or only paraphrases?
- Is there any distinction between fact, decision, and assumption?

A system that paraphrases everything degrades one generation per rewrite and nobody notices, because each individual rewrite looks reasonable.

## Dimension 4 — Is it queryable without loading everything?

- Is there an index that carries enough summary to answer from?
- Does answering a normal question require reading the whole corpus?
- Do the indexes match reality, or have counts and listings drifted?

## Dimension 5 — Does anything decay?

- Is there any mechanism that flags a stale entry?
- Has anything ever been retired, superseded, or marked disputed?
- Is contradictory evidence held visibly, or silently overwritten?

Most systems score zero here, and it is usually the finding that changes behavior fastest — because the owner can immediately name three things in there they no longer believe.

## Dimension 6 — Is it organized around outcomes or subjects?

**Run the test; do not assume the answer.** This dimension is where an auditor carrying a model is most likely to find what the model predicts. Cluster their open items into three to seven candidate outcomes without looking at their subject taxonomy first, then compare the two. If the clusters reproduce the taxonomy they already have, their material is subject-shaped and an outcome layer would duplicate working structure — report that, and score this dimension on whether *something* provides a priority signal and a removal rule, not on whether it looks like Corp-OS.

Then sort their open items by grammatical form, which is often more revealing than subject:

| Form | What it is | Where it belongs |
|---|---|---|
| **Finding** | a fact with an implied concern, no question attached | the subject file that already covers it |
| **Errand** | an imperative — book, get access, read, meet | a task tracker, not a knowledge base |
| **Decision** | a live fork the person picks between | a decision log with owner and date |
| **Question** | something genuinely open and re-asked | the open-items layer |

A layer that is mostly findings is a **status register** wearing a question queue's name. The fix is splitting by form, which is cheap, rather than adding a layer above it, which is not.

Two more checks worth running here, both of which surface things no dimension score would:

- **Misfiled entries.** Look at whatever their "resolved" or "closed" tier contains. If a large share of it was never actually an item of that kind — meeting logs filed as closed questions is the classic case — the counts everywhere are inflated and the tier is not measuring what it appears to.
- **A hidden recurring attribute.** Scan for a property that recurs across many entries but that nothing groups: entries whose real substance is "nobody owns this," or "this is blocked on one person," or "this depends on a decision above me." A recurring attribute scattered across an urgency-tiered layer is invisible by construction, and surfacing it is usually a one-page view rather than a restructure. This is frequently the single most useful finding an audit produces.

- Is there any representation of what the person is trying to accomplish?
- Can the system say what it still needs to know?
- Is there a stopping rule — anything that tells the owner what *not* to capture?

Subject-organized systems only grow. This is the dimension the Corp-OS model exists to address, so state the trade honestly rather than as a verdict: subject organization is genuinely simpler, and a small system may not need jobs at all.

## Dimension 7 — Are inputs registered?

- Is there a record of what feeds this and how?
- Is it written down anywhere what each source cannot see?
- When a source breaks or goes stale, does anyone find out?

## Dimension 8 — Does it produce anything?

- Does the system get read, or only written to?
- Is there a recurring moment where it is consulted?
- Does it produce output others see?

A system nobody reads is a diary. Usually the fix is a scheduled brief, not more structure.

## Dimension 9 — Does it improve itself?

- Is there any record of friction in using it?
- Has its structure changed in response to how it was actually used?
- Would the owner notice if part of it went unused for a quarter?

## Dimension 10 — Is the shape adjustable, and is it safe to adjust?

- Is the structure declared anywhere, or does it live only in convention and habit?
- If they wanted to rename something or add a category, is that an edit or a migration nobody would attempt?
- Does anything distinguish a folder that is **regenerable** from one that is **its own source of truth**?

That last question is the one to press on, because getting it wrong is the only failure mode in this whole rubric that destroys data rather than degrading it. A system with any regeneration step and no explicit marking of what is safe to regenerate is one careless pass away from overwriting hand-made material with nothing to restore from. Ask directly: *if you re-derived everything tomorrow, which folders would you lose?* If the answer takes thought, that is the finding.

## Scoring

For each dimension (all ten): `absent`, `informal`, `partial`, or `solid`. Four levels, no numeric score — a composite number invites arguing with the number instead of fixing the gap.

`informal` means the discipline exists in the person's head but not in the system, which is worth calling out separately from `absent`, because it is one write-down away from `solid` and does not need new structure.

## Missing capability, not just missing structure

Part of what someone reviews an audit for is what to *build* next — a new skill, a scheduled run, a step that should stop being manual. Look for these specifically, because they do not show up as a dimension score:

- **A step done by hand every time.** Anything repeated manually in more than a few sessions is a candidate for a skill.
- **A question asked repeatedly that the system cannot answer from its structure.** Points at a missing view or a missing field.
- **A recurring moment with no support** — a weekly review, a pre-meeting prep, a handoff, a monthly report someone assembles from scratch.
- **A layer written to but never read.** Either it needs an output that surfaces it, or it should not exist.
- **Debt tracked with a trigger instead of a date.** "Do this next time the file is touched" is a TODO that never fires; name it and give it a date.

Report each as a concrete proposal — what it would do, what triggers it, and roughly what it saves — not as an observation that something is missing.

## Both halves of the report

**Gaps** — dimensions scoring `absent` or `informal`, ordered by what unblocks the most. Each gap names the smallest change that moves it, not a rebuild. Nobody rebuilds a working system on an audit's advice, so a recommendation to rebuild is a wasted recommendation.

**What they have that the model lacks** — every structure, convention, field, or ritual in their system with no Corp-OS equivalent. For each: what it is, why it emerged, and whether it generalizes. Anything that generalizes goes into an improvement packet per `improvement-packet.md`.

Do not skip the second half because the first was long. An audit that only grades is half a skill.
