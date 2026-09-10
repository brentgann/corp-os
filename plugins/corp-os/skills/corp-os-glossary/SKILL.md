---
name: corp-os-glossary
description: Builds and maintains the glossary in a Corp-OS knowledge base — internal jargon, product terms, acronyms, role names, and especially metric definitions — extracted from captured material and confirmed by the person. Use when someone says "add this term", "what does X mean here", "build my glossary", "define this metric", "I keep having to look up what this stands for", or when captured material uses vocabulary the OS has never resolved. Not for company-level facts like pricing or funding (use corp-os-company) and not for general claims (use corp-os-claims).
---

# Corp-OS glossary

> **Judgment pass** — the reasoning is the product here. Run it on your best model, and do not economise by skipping the questions it asks.

The fastest-paying part of a work OS, and the most neglected. Every organization runs on vocabulary that is nowhere written down: an acronym three teams define differently, a metric whose formula lives in one analyst's head, a role name that means something specific here and something else everywhere else.

The glossary is also what makes the rest of the OS portable across roles. This suite ships no domain vocabulary on purpose — the terms come entirely from the person's own captured material.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — scan

Read `config.json`, the OS `README.md`, `INDEX.md`, and the existing glossary. If `layers.glossary` is disabled, offer to enable it via `corp-os-configure` and explain what it is for. Do not enable it unasked.

## Step 1 — find the terms worth defining

Two paths, depending on the ask.

**Someone hands over a term.** Define that term. Also check whether it is already in there under a different spelling or expansion — duplicate entries under `ARR` and `Annual Recurring Revenue` is how a glossary becomes unreliable.

**Someone wants the glossary built or extended.** Extract candidates from what the OS already holds, prioritizing in this order:

1. **Metrics** — anything counted, measured, or reported. Highest value by a wide margin, because a metric with an ambiguous definition produces confident disagreement rather than visible confusion.
2. **Acronyms and initialisms** used without expansion.
3. **Terms used differently here than in the wider industry.** These are the ones that burn a new person, and the ones a veteran no longer notices.
4. **Internal names** — systems, processes, rituals, tiers, segments, codenames.
5. **Role and team names** that do not mean what they appear to mean.

Do not extract every capitalized noun. A glossary of 300 obvious terms is unusable; forty load-bearing ones is a real asset.

## Step 2 — the metric interrogation

Metrics get more questions than other terms, because a metric is a definition plus a set of decisions nobody wrote down:

- What exactly is in the numerator and denominator?
- What is excluded, and why? The exclusions are usually where the disagreement lives.
- What time window, and is it trailing, calendar, or cohort-based?
- Who owns the number, and where is it computed?
- Is there a competing definition in use elsewhere in the company?

That last question is the one worth asking every time. When the answer is yes, record **both** definitions with who uses which. A glossary that flattens a real disagreement into one authoritative-looking entry makes things worse — it gives two teams the same word and the confidence that they agree.

## Step 3 — write the proposal, then the entry

1. **Write the proposal to disk before anything is written to `glossary/`.** Not a proposal made in the conversation — a file, because the conversation ends and the file is what the gate leaves behind:

```bash
python3 scripts/propose.py --root <the OS> --layer glossary --slug <batch> \
  --headline "<the one thing here that matters>" \
  --item "<create|enrich|flag|decline> · <id> · <what>" \
  --not-proposing "<what is being held back, and why>"
```

Present it, wait, then record the answer per item — the declines are the half that matters:

```bash
python3 scripts/propose.py --root <the OS> --record <the file it wrote> \
  --outcome "<item>: confirmed" --outcome "<item>: declined"
```

2. Only then, compose the entry:


```markdown
### ARR
- **Expansion**: Annual Recurring Revenue
- **Definition**: Contracted subscription revenue normalized to a twelve-month
  basis, excluding one-time services and usage overage.
- **Also called**: annualized revenue (informally, in board material)
- **Not to be confused with**: run-rate revenue, which includes overage here
- **Owner**: Finance — computed in the warehouse, not the CRM
- **Competing definition**: Sales quota reporting includes first-year services,
  which runs roughly 8% higher
- **Source**: raw/2026-08-11--note--finance-definitions.md — Priya, 2026-08-11
- **Confidence**: confirmed
- **Decay**: 180d
```

`Not to be confused with` and `Competing definition` are the two fields that make a glossary worth consulting rather than skimming. Fill them when they apply and leave them out when they do not — do not pad entries with empty fields.

Terms carry provenance and decay like any other derived entry. Definitions change, and a glossary nobody re-checks is a glossary that teaches yesterday's vocabulary with full confidence.

## Step 4 — on confirmation

Batch the confirmations when proposing many, then record them with `propose.py --record`.

Write to `glossary.md` alphabetically, add the term count to `meta.json`, and note in `INDEX.md` that the glossary exists with its count.

For a term the person cannot confidently define, write it with `confidence: needs_review` and a note on who to ask. A recorded unknown is more useful than an absent entry, because it stops the same question being re-asked and names the person who can settle it.

## Step 5 — connect it back

A glossary is not a standalone artifact. Two links to maintain:

- When a term's definition **is** the substance of a claim — a metric definition that a decision rests on — the claim and the glossary entry should cite the same source. Do not let them drift into two different definitions.
- When a job's evidence list contains "figure out what X actually means," resolving the term answers the job. Strike it from the evidence list in the same pass.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-glossary --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

- Recounted term count in `meta.json`, verified against actual entries.
- A `usage/log.md` row.
- A short report: terms added, competing definitions surfaced, and any term nobody could define — that last list is often the most actionable output of the run.
