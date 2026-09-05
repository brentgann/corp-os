# Company research brief

Reference for `corp-os-company`. What to establish about a company, in what order, and how to keep it honest.

## Scope: three kinds of company record

- **Employer** — where the operator works. The deepest record, and the one whose staleness hurts most, because everyone assumes they already know it.
- **Counterparty** — a customer, prospect, partner, or candidate employer. Built on demand, scoped to the job that needs it.
- **Competitor** — built comparatively; the useful content is the delta, not a second full profile.

Ask which kind before researching. The questions overlap but the depth and decay windows do not.

## What to establish

Work down this list. Stop when the job being served is satisfied — a full profile for a company that touches one job is waste.

1. **What they sell, in one sentence a customer would recognize.** Not the tagline. If the marketing copy and the pricing page disagree about what the product is, that disagreement is itself a finding worth recording.
2. **Users versus buyers.** Whether they are the same people, and if not, who holds budget. This distinction drives more misunderstanding than any other single fact.
3. **Use cases, ranked.** What people actually do with it, in what proportion, if that is discoverable.
4. **Pricing shape.** The mechanism — per seat, usage, tiered, flat, take-rate, hybrid — matters more than the numbers, because the mechanism is what constrains their strategy. Record the numbers if public, and mark them `Decay: 90d` because they move.
5. **Monetization beyond the list price.** Expansion path, services, marketplace or take-rate revenue, upsell motion.
6. **Funding and ownership.** Stage, most recent round with date and amount, notable investors, or bootstrapped, PE-owned, public. Ownership shape predicts behavior better than headcount does.
7. **Current status.** Growing, flat, raising, post-raise, hiring or cutting, recently reorganized, being acquired. The most decision-relevant field and the fastest to rot — `Decay: 30d`.
8. **Stated goals.** What leadership says publicly they are trying to do. Record as kind `preference` or `decision`, not `fact` — a stated goal is a claim about intent.
9. **Competitors and the honest delta.** Where they genuinely win, where they lose. A competitor record with no losses recorded is marketing, not research.

## Sourcing discipline

Search before answering, always, on every one of these fields. Company facts are exactly the category where recalled knowledge is confidently wrong: funding rounds close, pricing pages get rewritten, leaders leave.

Source tiers, and how each lands as a claim:

- **Primary** — the company's own site, pricing page, docs, filings, official announcements. `confidence: confirmed`.
- **Credible secondary** — established trade press, funding databases, analyst coverage. `confidence: confirmed` when two independent ones agree, `needs_review` on a single source.
- **Weak** — aggregator pages, SEO listicles, undated summaries, competitor comparison pages written by a competitor. `confidence: needs_review` at best, and say which source it was so the reader can discount it.
- **The operator's own knowledge** — often the best source for an employer record, and it should be captured, but as a claim with `Source: <person>, <date>` and `needs_review` until corroborated. Insider knowledge is not self-verifying.

When sources conflict, record both as `disputed` with each citation. Do not average them and do not pick the more recent one without saying why.

## Output shape

Write `company/<slug>.md` with frontmatter and the numbered areas above as sections. Every substantive line becomes a claim in `claims/` with a source and a decay window — the company file is a readable view, and `claims/` is where correctness is enforced. Do not let a fact exist in the company file without a matching claim, or reality-check cannot see it.

```markdown
---
company: acme-corp
relationship: counterparty     # employer | counterparty | competitor
serves_jobs: [job-004]
researched: 2026-09-04
next_review: 2026-10-04
---
```

`next_review` is set from the shortest decay window in the record — usually the 30-day status field. That is what makes a company record self-maintaining rather than a snapshot that silently ages.

## What not to do

- Do not produce a profile nobody asked for because the company was mentioned once.
- Do not assert headcount, revenue, or valuation from a data aggregator as fact. Attribute it.
- Do not record anything about named individuals beyond their public professional role.
- Do not let a competitor record become a pitch. If it reads like sales copy, the research has not happened yet.
