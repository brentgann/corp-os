---
name: corp-os-company
description: Researches and maintains company context in a Corp-OS knowledge base — what a company sells, users versus buyers, use cases, pricing mechanism, monetization, funding, current status, stated goals, and competitors — combining web research with what the person already knows, and recording each finding as a sourced claim with a decay window. Use when someone says "research this company", "what do we know about Acme", "build out my company context", "who are our competitors", "look up their pricing or funding", or is preparing for a meeting with a company. Not for defining internal vocabulary (use corp-os-glossary) and not for filing a call transcript (use corp-os-intake).
---

# Corp-OS company

> **Judgment pass** — the reasoning is the product here. Run it on your best model, and do not economise by skipping the questions it asks.

Company context is the material people re-explain and re-look-up more than anything else, and it is also the category where recalled knowledge is most confidently wrong. Funding rounds close, pricing pages get rewritten, leadership turns over, strategies reverse.

Read `${CLAUDE_PLUGIN_ROOT}/reference/company-research.md` before starting.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — establish the kind and the job

Two questions before any research:

**Which kind of record is this?** Employer, counterparty (customer, prospect, partner, candidate employer), or competitor. The nine research areas are the same; the depth, decay windows, and framing are not. A competitor record is built as a delta, not a second full profile.

**Which job does this serve?** A profile serving no job is one nobody reads. If a company came up once in passing, say that a full profile is probably not worth building and offer to record the one relevant fact as a claim instead.

Then read `INDEX.md`, `jobs/INDEX.md`, and any existing `company/<slug>.md`. If a record exists, this is an update, not a rebuild — check `next_review` and refresh what has decayed rather than starting over.

## Step 1 — harvest what the person already knows, first

Before searching, ask what they know. For an employer record this is usually the best source available, and doing it in this order matters: research first and you displace their knowledge with whatever the web says, losing the insider detail that was the valuable part.

Capture their answers as claims with them as the source, dated, at `needs_review` until corroborated. Insider knowledge is not self-verifying — but it is often right where public sources are wrong, so when a search later contradicts them, that is a `disputed` pair worth surfacing, not an automatic correction.

## Step 2 — research, searching every time

Search the web for every one of the nine areas. Do not answer any of them from recalled knowledge, and do not present recalled knowledge as a finding and then offer to verify it.

Work down the list in `company-research.md`, stopping when the job is served: what they sell, users versus buyers, ranked use cases, pricing mechanism, monetization beyond list price, funding and ownership, current status, stated goals, competitors and the honest delta.

Two areas deserve extra attention:

**Users versus buyers.** Whether the people who use it are the people who pay drives more misunderstanding than any other single fact, and most public material blurs it deliberately.

**Pricing mechanism over pricing numbers.** Per-seat versus usage versus take-rate constrains what a company can strategically do. The mechanism is durable and the numbers are not, so record both but weight the mechanism.

When the marketing copy and the pricing or docs pages disagree about what the product actually is, that disagreement is a finding. Record it rather than resolving it in favor of whichever is cleaner.

If a source cannot be retrieved, say so and move on. Never work around a blocked source by other means.

## Step 3 — grade every source

Per the tiers in the reference: primary company sources are `confirmed`; credible secondary is `confirmed` when two independent ones agree and `needs_review` on one; aggregators, undated summaries, and competitor-written comparisons are `needs_review` at best and must name the source so the reader can discount it.

Never assert headcount, revenue, or valuation from a data aggregator as fact. Attribute it.

When sources conflict, record `disputed` with both citations. Do not average them, and do not pick the more recent one without saying why the more recent one is better.

## Step 4 — write the proposal, then the record and the claims

1. **Write the proposal to disk before anything is written to `company/` or `claims/`.** Not a proposal made in the conversation — a file, because the conversation ends and the file is what the gate leaves behind:

```bash
python3 scripts/propose.py --root <the OS> --layer company --slug <name> \
  --headline "<what this research settled>" \
  --item "<create|enrich|flag|decline> · <id> · <what>" \
  --not-proposing "<what is being held back, and why>"
```

Present it, wait, then record the answer per item with `propose.py --record` — the declines are the half that matters.

2. Only then, write `company/<slug>.md` with the frontmatter from the reference — `relationship`, `serves_jobs`, `researched`, `next_review` — and the nine areas as sections.

Then write each substantive line as a claim in `claims/` with source, citation, and decay. This matters more than it looks: the company file is a **readable view**, and `claims/` is where correctness is enforced. A fact living only in the company file is invisible to `corp-os-reality-check` and will silently rot.

Set `next_review` from the shortest decay window in the record — usually the 30-day status field. That is what makes the record self-maintaining rather than a snapshot that ages without anyone noticing.

Both the record and the claims are derived-layer: propose, confirm, write.

## Step 5 — answer the job

Close by answering the job that motivated the research, not by narrating the profile. If this was renewal prep, say what the record implies about the renewal: which pricing pressure is real, what their status suggests about budget, where the competitive threat actually is.

Then update the job's evidence list — strike what is answered, and add what the research revealed as unknown. A research run that surfaces a new gap has done useful work even if it answered nothing.

## Refreshing an existing record

- Re-check only what is past decay, plus the status field.
- Diff against what was there and **state the changes explicitly**: "they raised a Series C in March, which the record didn't have; the pricing page moved from per-seat to hybrid usage." The delta is the deliverable on a refresh.
- Retire superseded claims with `Relations` links rather than editing them in place. The history of what a company used to be is frequently the most useful thing in the file.

## What not to do

- Do not build a profile nobody asked for.
- Do not record anything about named individuals beyond their public professional role.
- Do not let a competitor record read like sales copy. If there are no recorded losses, the research has not happened yet.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-company --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

It also refuses to close a run that put something in a derived layer with no proposal file behind it, and names the files and the `propose.py` call that repairs the record. The gate is checked here because this is the step that never gets skipped — three attempts at stating it nearer the write got it to one run in three.

- Recounted `meta.json`, dated `history` entry.
- A `usage/log.md` row.
- The answer to the job, the source-quality caveats worth knowing, and what is still unknown.
