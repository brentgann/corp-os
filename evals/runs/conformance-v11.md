# Conformance

Model `claude-opus-5` · 19 cases · each against a fresh copy of `examples/fixture-os`, `examples/fixture-register`, `examples/fixture-stale`

**114/122 checks passed**

## `brief-window` — corp-os-brief (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — meta.json history records the brief and its window
- PASS — nothing entered the derived layer
- PASS — no raw material was written

  <sub>added 0, changed 2, removed 0</sub>

## `claims-queue` — corp-os-claims (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — proposal file written before anything was presented
- PASS — the disabled glossary layer was not created
- PASS — the person's own vocabulary is used, not the plugin's

  <sub>added 1, changed 4, removed 0</sub>

## `configure-delete-sequence` — corp-os-configure (8/8)

- PASS — raw deletion happened under the retention path
- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — entries citing the deleted source were re-cited
- PASS — config.json records the policy and the obligation
- PASS — meta.json logs what was destroyed and under what obligation
- PASS — unprocessed raw files are reachable from INDEX.md

  <sub>added 1, changed 7, removed 1</sub>

## `connect-blind-spots` — corp-os-connect (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the registry gained the source
- PASS — the blind spots question was actually asked

  <sub>added 1, changed 4, removed 0</sub>

## `dashboard-hub-and-registry` — corp-os-dashboard (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the new dashboard is recorded in the root registry
- PASS — the run closed its own books
- PASS — no dashboards/ directory was created
- PASS — the hub is offered as a hub, not as an eighth analytical view

  <sub>added 1, changed 4, removed 0</sub>

## `dashboard-missing-layer` — corp-os-dashboard (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- **FAIL** — the missing layer is raised as a proposal, not improvised to get the dashboard built · added 0, needed 1: []
- PASS — the declared layer has an index_line

  <sub>added 1, changed 3, removed 0</sub>

  Why these matter:

  - **the missing layer is raised as a proposal, not improvised to get the dashboard built** — a layer is a structural change to what the OS can hold, and the gate is what stops one being shaped wrong in passing. The proposal is the artifact that survives the session; a run that quietly invents a directory to render a panel leaves nothing to review

## `decide-open-fork` — corp-os-decide (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **FAIL** — derived-layer writes have a proposal behind them · wrote ['claims/support.md', 'decisions/midmarket-pricing.md', 'decisions/support-tooling.md'] with no proposal file
- PASS — no raw material was written
- PASS — the past-date decision was surfaced

  <sub>added 0, changed 6, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know

## `glossary-competing-definitions` — corp-os-glossary (3/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **FAIL** — derived-layer writes have a proposal behind them · wrote ['glossary.md'] with no proposal file
- **FAIL** — a proposal was filed before the entry was written · added 0, needed 1: []
- PASS — both definitions survived

  <sub>added 1, changed 4, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know
  - **a proposal was filed before the entry was written** — glossary entries are derived-layer like anything else

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

## `pull-broken-connector` — corp-os-pull (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the broken connector was recorded as broken, not silently skipped
- PASS — the hand-maintained source layer was not touched

  <sub>added 1, changed 6, removed 0</sub>

## `reality-check-sweep` — corp-os-reality-check (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **FAIL** — derived-layer writes have a proposal behind them · wrote ['claims/pricing.md', 'claims/support.md', 'decisions/midmarket-pricing.md', 'decisions/support-tooling.md', 'jobs/renewal-risk.md', 'jobs/support-load.md'] with no proposal file
- PASS — no raw material was written
- PASS — the unsourced entry was handled as its own bucket

  <sub>added 0, changed 14, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know

## `rebuild-respects-roles` — corp-os-rebuild (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — meta.json carries a dated history entry for the rebuild
- PASS — the hand-maintained source layer survived
- PASS — the raw archive was not rewritten
- PASS — the existing proposals record was not rewritten

  <sub>added 1, changed 10, removed 0</sub>

## `recall-jobs-off` — corp-os-recall (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — the hand-maintained source layer was not touched
- PASS — no raw material was written
- PASS — the run completed against an OS with no jobs layer

  <sub>added 0, changed 1, removed 0</sub>

## `recall-load-bearing-sensitive` — corp-os-recall (5/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- **FAIL** — the load-bearing sensitive fact reached the answer · 'march' absent from the answer
- **FAIL** — the export boundary was flagged at the moment it matters · 'sensitive' absent from the answer
- PASS — the incidental quarantined material stayed out

  <sub>added 0, changed 1, removed 0</sub>

  Why these matter:

  - **the load-bearing sensitive fact reached the answer** — CL-0004 is sensitive AND load_bearing: Northwind's champion leaves in March, so every plan routed through her is wrong after that. This is one person's own knowledge base -- withholding it protects nobody, and an answer computed around it is not cautious, it is wrong in the worst way, because nothing in it signals the omission
  - **the export boundary was flagged at the moment it matters** — the person is mid-draft and will copy the paragraph, not a closing caveat; the inline marking is what makes the boundary visible before it gets crossed rather than after

## `recall-read-only` — corp-os-recall (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — no raw material was written

  <sub>added 1, changed 1, removed 0</sub>

## `redact-external` — corp-os-redact (5/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — two outputs, not one — a cleaned copy and its private log
- **FAIL** — the originals were not modified in place · touched: ['claims/pricing.md']
- PASS — raw was not touched

  <sub>added 3, changed 4, removed 0</sub>

  Why these matter:

  - **the originals were not modified in place** — redaction produces a copy; a redaction skill that edits the source has quietly destroyed the unredacted version, and the person will not find out until they need it

## `redact-strips-load-bearing` — corp-os-redact (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — two outputs, not one — a cleaned copy and its private log
- PASS — the source claims were not modified in place
- PASS — raw survived untouched

  <sub>added 2, changed 2, removed 0</sub>

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

  <sub>added 26, changed 0, removed 0</sub>

## `upgrade-stale-os` — corp-os-upgrade (10/10)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the shipped script this OS predates is installed
- PASS — the stale counter copy was replaced
- PASS — the recorded version moved
- PASS — the run closed its own books
- PASS — the registry migration was NOT performed
- PASS — no source material was touched
- PASS — the outstanding migration is named rather than silently left

  <sub>added 1, changed 5, removed 0</sub>

