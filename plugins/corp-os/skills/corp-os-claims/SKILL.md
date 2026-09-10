---
name: corp-os-claims
description: Turns raw material in a Corp-OS knowledge base into reviewed, citable claims — each with a kind, a confidence level, a verbatim citation, the jobs it serves, and a decay window — and promotes, edits, merges, supersedes, or retires existing claims. Use when someone says "turn this into claims", "process my unprocessed queue", "what do we actually know", "promote this claim", "this claim is wrong", "mark this confirmed", or wants raw notes converted into knowledge. Not for capturing new source material (use corp-os-intake or corp-os-pull) and not for the systematic staleness and contradiction sweep (use corp-os-reality-check).
---

# Corp-OS claims

> **Judgment pass** — the reasoning is the product here. Run it on your best model, and do not economise by skipping the questions it asks.

The claims layer is what separates a Corp-OS from a tagged archive. A claim is a short statement that has been looked at by a person and carries enough provenance that a future reader — including a future version of the person who wrote it — can tell how much to trust it and when to re-check it.

Read `${CLAUDE_PLUGIN_ROOT}/reference/claim-record.md` before writing anything. The layer rules and the scan contract are in `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md`; you do not need them to mint a claim.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

A `claim` renamed `finding` is still a claim: same fields, same gate, the person's word.

## Step 0 — scan

Read `INDEX.md`, `jobs/INDEX.md`, `claims/INDEX.md`, and the `next_claim_id` in `meta.json`. Read the specific raw files in scope — only those. Never load `raw/` wholesale.

If there is no `claims/` layer yet, offer to create it and explain what it buys: a place where reviewed knowledge lives separately from what was merely said. Do not create it silently.

## Step 1 — pick the scope

Common asks and what each means:

- **"Process my queue"** — the unprocessed raw files in `INDEX.md`, oldest first. If the queue is long, work the files that serve open evidence lists first and say that is what you are doing.
- **"Turn this into claims"** — the specific material just discussed.
- **"What do we know about X"** — this is recall, not claims. Hand to `corp-os-recall`.
- **A choice nobody has made yet** — a `decision` claim records a call that *was* made. A live fork belongs in the decision layer via `corp-os-decide`, because it needs an owner and a date, and a claim has neither. Filing one as a claim is how a fork goes quiet.

## Step 2 — extract candidates

Read for statements that would matter to someone who was not in the room. Then apply two filters, in this order:

**Is it claim-shaped?** A claim is a single assertion, checkable in principle, that someone could disagree with. "Pricing came up" is not a claim. "Acme's CFO will block a renewal above current per-seat cost" is.

**Does it serve a job?** A claim serving no job is a claim nobody will ever look up. Say so and leave it in `raw/`. This filter is the reason job-organization exists, and skipping it is how a claims layer grows to 800 entries nobody reads.

**The graduation bar.** A handful of claims are worth more than a claim — the ones that change what someone does. If the OS keeps a top tier (`insights/`, or whatever the person called it), it needs an explicit bar, or everything drifts into it. A useful one: the entry has to be *informative* (says something true), *instructive* (says what to do about it), *insightful* (not obvious from the underlying facts), and *immediate* (actionable now, with the timing named). Four tests, all of them, or it stays a claim. Without a stated bar the top tier fills with interesting facts and stops being read.

## Step 3 — get the fields right

The fields are where this skill earns its keep. The three that go wrong most often:

**Kind.** Separate what was observed (`fact`), what was chosen (`decision`), what recurs across sources (`theme`), what is being taken on faith (`assumption`), what limits options (`constraint`), what is measured (`metric`), and what someone wants (`preference`).

Filing an assumption as a fact is the single most damaging error available here, because an assumption promoted to fact stops being questioned. When someone says "customers won't pay for that," ask whether that is something a customer said or something the person believes. The first is a `fact` with a citation; the second is an `assumption` with the person as its source. Both are worth keeping. Conflating them is not.

**Confidence.** Evidentiary standing, not importance:

- `confirmed` — verbatim from a primary source, or corroborated by two genuinely independent sources. Two people's notes on the same call are one source.
- `needs_review` — inferred, single ambiguous mention, or heard secondhand. The correct default. Most claims should start here.
- `reconstructed` — backfilled from a summary or from memory rather than a real source. Never promote to `confirmed` without a real citation appearing.
- `disputed` — live evidence points both ways. Keep both citations visible; do not pick a winner to tidy the record.
- `retired` — no longer true. Kept, never deleted, with what superseded it.

**Sensitivity and bearing.** Two fields, not one, and they answer different questions. `sensitivity` is the export class — what must not leave. `bearing` is whether the OS can reason correctly without it: `incidental` if removing it makes an answer thinner, `load_bearing` if removing it makes an answer *wrong*.

Set both at proposal time. **When bearing is genuinely unclear, write `load_bearing`** — a wrongly quarantined fact produces confidently wrong answers with nothing to signal the omission, while a wrongly retained one just gives `corp-os-redact` more to strip. Full reasoning in `${CLAUDE_PLUGIN_ROOT}/reference/claim-record.md`; the short version is that sensitivity governs what leaves, not what the person is allowed to know.

**Decay.** Ask "when would this need re-checking?" and write the interval. Pricing, headcount, org structure, roadmap, competitive positioning: 30 to 90 days. Someone's role or a customer's architecture: a year. A stated principle, a contract term, a fiscal calendar: `none`.

This field is what makes drift correctable on a schedule instead of by accident, and a claims layer without it silently ages into fiction. Do not default everything to 90 days to move faster — a wrong decay window is worse than an honest `none`.

**Citation.** Verbatim, always, with speaker and date. A paraphrase in the citation field defeats the entire mechanism, because the next reader cannot separate the source from the summarizer.

When no retrievable original exists — the claim traces to a summary, a migration, or someone's recollection — write the literal `no source`. That value is sanctioned and correct. Never invent a plausible-looking citation to fill the field: an unsourced claim that says so is honest and fixable, while a fabricated citation is the single most corrosive thing that can enter a claims layer, because nothing downstream can detect it.

If the batch being processed comes from a structurally weaker source than verbatim — a bulk migration, a set of AI-generated meeting summaries, a backfill from memory — apply a **cohort ceiling** rather than judging each claim alone. Record it once in `meta.json` under `confidence_ceilings` and mark the raw frontmatter, so a future rebuild rediscovers the ceiling instead of promoting the whole cohort to `confirmed` in one careless pass.

## Step 4 — check against what already exists

Before writing a new claim, scan `claims/INDEX.md` for:

- **A near-duplicate.** Enrich the existing claim with the new citation and raise its confidence if this is genuine independent corroboration. Do not create a second claim.
- **A contradiction.** Do not overwrite. Either mark the old claim `disputed` and keep both citations, or — if the new evidence clearly supersedes it — set the old to `retired` with `Relations: superseded by CL-NNNN`. Say which you are doing and why. Silently replacing a claim destroys the record of having believed it, which is often the most useful thing in the file.

  Then **write the diagnosis into the conflict**, not just the flag. "Either two distinct initiatives share a name, or one source is stale — not resolved here." "Could be two different offers rather than a real contradiction; needs a direct check." A named hypothesis about the shape of a conflict lets someone resolve it in one question; a bare `disputed` pair gets skipped every time it is read.

- **Something the new evidence extends rather than contradicts.** Append a dated update block inside the existing claim, carrying its own confidence and citation, instead of minting a second claim. Use an update block when the claim is still true and now known in more detail; mint a new claim only when the old one stopped being true. A reader following one claim's update blocks can see how understanding developed — a chain of superseded atomic claims makes that nearly unreadable.

- **An identity ambiguity.** Two spellings of a name, one first name shared by several people, someone referred to by role. File as kind `identity` and never merge on resemblance — a new mention with a fuller name is a candidate, not a confirmation. When one resolves, record the resolution *and* where it propagated, including any sensitivity change that follows from it.
- **An assumption this claim tests.** If a `fact` now confirms or refutes a standing `assumption`, link them and flag the assumption for review. This is where a claims layer starts paying for itself.

## Step 5 — write the proposal to disk, then present it

Write `proposals/PROPOSAL-<date>-<slug>.md` **before** presenting anything. Shape it like a briefing, not a diff:

- **Headline** — the one thing in this batch that actually matters. If a board mandate landed, or a number moved, or two sources now conflict, that goes first.
- **Per item**: the proposed claim with all fields, and an explicit recommendation — *enrich* an existing claim, *create* a new one, *flag* as a conflict, or *decline*. "Update the existing Takeoff gap with these specifics rather than duplicate" is a recommendation; "here are five claims" is not.
- **What is deliberately not being proposed**, and why.

Then present it in conversation. A proposal that exists only in chat dies with the session, leaves no record of what the gate saw, and cannot be reviewed the next morning when the person has time to think.

Present the candidate claims with all fields visible and wait for confirmation. Every one, including the obvious ones. The gate is not about individual risk — it is that skipping it turns the derived layer into a second unreviewed copy of `raw/`.

On confirmation: append the outcome per item to the proposal file — confirmed, declined, deferred, modified. The declines matter most: they are the only record of what the person chose not to know. Then assign sequential IDs from `next_claim_id`, write into `claims/<topic-slug>.md`, add the one-line `claims/INDEX.md` entry, flip `processed: true` on the source raw files, update affected job evidence lists and `What I know` links, recount `meta.json`.

Group by topic, not by source or date. A claim's home is its subject; its provenance is in its fields.

## Editing an existing claim

Statements can be sharpened, citations added, decay adjusted, jobs re-linked. Two rules:

- **Never edit a citation.** It is a quotation. If it was wrong, the claim was wrong — retire and replace.
- **Log any confidence change** in the claim's `Verified` field with the date and what changed it. A claim that quietly became `confirmed` is indistinguishable from one that was always guessed at.

## Source fidelity is read, not judged

Set `Source fidelity` — `verbatim | summary | reconstructed | absent` — from the **source's** record in `connectors.md`, not from an assessment of the entry. It is a property of the medium, which is why it can be read rather than decided, and why deciding it per entry would be wrong.

`absent` when the citation is the sanctioned `no source` literal. Nothing can ever re-confirm those, so they are a one-time disposition pass rather than decay candidates, and `corp-os-reality-check` handles them as their own bucket.

This is not confidence. Confidence is evidentiary standing; fidelity is how faithful the recording is. Keeping them separate is what makes *"summary, and the transcript is still fetchable"* expressible — and that sentence is the difference between a ceiling people work through and one they treat as permanent.

Where a confidence value needs a reason, write `Confidence reason` as its own field. Never inside the value: everything downstream equality-tests that string.

## Stamp the proposal with its outcome

After review, write the result back into the proposal file as a header — what was accepted, what was declined, what changed during the conversation, and the date. Then say plainly in the file that it is a record rather than a live list.

Without the stamp, a proposal nobody reviewed and a proposal reviewed and accepted are the same artifact on disk. The declines are the valuable part of the gate, and a decline is only legible if the outcome was written down: in an audited OS the gate had produced two empty placeholders where the prior system had three stamped records, and no one could tell whether the gate had run.

**A bulk pass sets its ceiling first.** If this batch comes from a structurally weaker source — a migration, a set of AI-generated summaries, a backfill from memory — record the cohort ceiling in `meta.json` before minting, and give it an escape route if one exists. A ceiling that reads as permanent gets treated as permanent: in one corpus, 599 entries sat one connector call from promotion with zero having taken it.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-claims --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

It also refuses to close a run that put something in a derived layer with no proposal file behind it, and names the files and the `propose.py` call that repairs the record. The gate is checked here because this is the step that never gets skipped — three attempts at stating it nearer the write got it to one run in three.

- Programmatic recount of claims and `next_claim_id`, cross-checked against actual header counts.
- A `usage/log.md` row with real friction — "person could not tell whether three items were facts or assumptions" is exactly what `corp-os-improve` needs.
- A summary: claims added, claims enriched, contradictions found, jobs moved, and how much of the queue is still waiting.
