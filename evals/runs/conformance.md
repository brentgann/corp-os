# Conformance

Model `claude-opus-5` · 12 cases · each against a fresh copy of `examples/fixture-os`, `examples/fixture-register`

**69/79 checks passed**

## `configure-delete-sequence` — corp-os-configure (8/8)

- PASS — raw deletion happened under the retention path
- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — entries citing the deleted source were re-cited
- PASS — config.json records the policy and the obligation
- PASS — meta.json logs what was destroyed and under what obligation
- PASS — unprocessed raw files are reachable from INDEX.md

  <sub>added 3, changed 6, removed 1</sub>

## `dashboard-hub-and-registry` — corp-os-dashboard (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the new dashboard is recorded in the root registry
- PASS — the run closed its own books
- PASS — no dashboards/ directory was created
- PASS — the hub is offered as a hub, not as an eighth analytical view

  <sub>added 3, changed 5, removed 0</sub>

## `dashboard-missing-layer` — corp-os-dashboard (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- **FAIL** — the missing layer is raised as a proposal, not improvised to get the dashboard built · added 0, needed 1: []
- PASS — the declared layer has an index_line

  <sub>added 3, changed 5, removed 0</sub>

  Why these matter:

  - **the missing layer is raised as a proposal, not improvised to get the dashboard built** — a layer is a structural change to what the OS can hold, and the gate is what stops one being shaped wrong in passing. The proposal is the artifact that survives the session; a run that quietly invents a directory to render a panel leaves nothing to review

## `guide-open-fork` — corp-os-guide (4/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **FAIL** — derived-layer writes have a proposal behind them · wrote ['decisions/legacy-importer.md', 'jobs/support-load.md'] with no proposal file
- **FAIL** — guide did not open the decision itself · touched: ['decisions/legacy-importer.md']
- PASS — guide did not file it as a claim
- PASS — guide wrote nothing to the source layer
- **FAIL** — routes an undecided fork to corp-os-decide · 'corp-os-decide' absent from the answer

  <sub>added 1, changed 4, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know
  - **guide did not open the decision itself** — guide orients and hands off; a run that does the work skips the skill that has the rules for doing it properly
  - **routes an undecided fork to corp-os-decide** — the skill's own rule is to read the tense: a choice still open is a decision record, a choice already made is a claim. Filed as anything else, nothing ever forces the date and the fork sits open for months

## `improve-thin-evidence` — corp-os-improve (3/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **FAIL** — derived-layer writes have a proposal behind them · wrote ['claims/pricing.md'] with no proposal file
- PASS — no improvement packet written from one occurrence
- **FAIL** — says the evidence is too thin to propose from · 'once' absent from the answer

  <sub>added 1, changed 10, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know
  - **says the evidence is too thin to propose from** — this fixture's log holds two rows and one friction note. The bar is more than one real occurrence, and a run that proposes changes from a single one is manufacturing findings from noise -- the failure this skill is most prone to, because a person who asked for changes wants changes

## `intake-transcript` — corp-os-intake (8/8)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — raw file written for the pasted material
- PASS — proposal file written before claims were presented
- PASS — INDEX.md updated in the same pass
- PASS — meta.json recounted
- PASS — unprocessed raw files are reachable from INDEX.md

  <sub>added 2, changed 6, removed 0</sub>

## `jobs-artifact-as-motivation` — corp-os-jobs (4/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **FAIL** — derived-layer writes have a proposal behind them · wrote ['jobs/renewal-early-warning.md', 'jobs/renewal-risk.md'] with no proposal file
- PASS — a job file was written
- PASS — the dashboard they asked for was not built
- **FAIL** — the repaired job carries an outcome clause · 'so I can' absent from the answer

  <sub>added 1, changed 5, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know
  - **the repaired job carries an outcome clause** — artifact-as-motivation is the most common malformation: 'I want a dashboard' names a thing, not a motivation, and a job with no outcome cannot be closed. The repair is the skill's job

## `pull-broken-connector` — corp-os-pull (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **FAIL** — derived-layer writes have a proposal behind them · wrote ['connectors.md'] with no proposal file
- PASS — the broken connector was recorded as broken, not silently skipped
- PASS — the hand-maintained source layer was not touched

  <sub>added 0, changed 4, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know

## `recall-jobs-off` — corp-os-recall (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — the hand-maintained source layer was not touched
- PASS — no raw material was written
- PASS — the run completed against an OS with no jobs layer

  <sub>added 1, changed 2, removed 0</sub>

## `recall-load-bearing-sensitive` — corp-os-recall (6/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- **FAIL** — the load-bearing sensitive fact reached the answer · 'march' absent from the answer
- PASS — the export boundary was flagged at the moment it matters
- PASS — the incidental quarantined material stayed out

  <sub>added 2, changed 1, removed 0</sub>

  Why these matter:

  - **the load-bearing sensitive fact reached the answer** — CL-0004 is sensitive AND load_bearing: Northwind's champion leaves in March, so every plan routed through her is wrong after that. This is one person's own knowledge base -- withholding it protects nobody, and an answer computed around it is not cautious, it is wrong in the worst way, because nothing in it signals the omission

## `recall-read-only` — corp-os-recall (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — no raw material was written

  <sub>added 1, changed 1, removed 0</sub>

## `setup-from-empty` — corp-os-setup (9/9)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — an INDEX.md was written
- PASS — meta.json was written
- PASS — config.json was written
- PASS — the append-only source layer exists
- PASS — the review gate has somewhere to write
- PASS — the shipped scripts were copied in

  <sub>added 35, changed 0, removed 0</sub>

