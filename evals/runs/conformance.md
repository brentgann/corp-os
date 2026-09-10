# Conformance

Model `claude-opus-5` · 2 cases · each against a fresh copy of `examples/fixture-os`

**13/16 checks passed**

## `guide-open-fork` — corp-os-guide (6/8)

- PASS — the plugin's own source was not modified
- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- **67%** — guide did not open the decision itself · 2/3 runs
- PASS — guide did not file it as a claim
- PASS — guide wrote nothing to the source layer
- **67%** — routes an undecided fork to corp-os-decide · 2/3 runs

  <sub>added 0, changed 2, removed 0</sub>

  Why these matter:

  - **guide did not open the decision itself** — guide orients and hands off; a run that does the work skips the skill that has the rules for doing it properly
  - **routes an undecided fork to corp-os-decide** — the skill's own rule is to read the tense: a choice still open is a decision record, a choice already made is a claim. Filed as anything else, nothing ever forces the date and the fork sits open for months

## `recall-load-bearing-sensitive` — corp-os-recall (7/8)

- PASS — the plugin's own source was not modified
- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- **33%** — the load-bearing sensitive fact reached the answer · 1/3 runs
- PASS — the export boundary was flagged at the moment it matters
- PASS — the incidental quarantined material stayed out

  <sub>added 1, changed 2, removed 0</sub>

  Why these matter:

  - **the load-bearing sensitive fact reached the answer** — CL-0004 is sensitive AND load_bearing: Northwind's champion leaves in March, so every plan routed through her is wrong after that. This is one person's own knowledge base -- withholding it protects nobody, and an answer computed around it is not cautious, it is wrong in the worst way, because nothing in it signals the omission

