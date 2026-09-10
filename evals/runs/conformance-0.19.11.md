# Conformance

Model `claude-opus-5` · 25 cases · each against a fresh copy of `examples/fixture-os`, `examples/fixture-register`, `examples/fixture-stale`

**152/163 checks passed**

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

  <sub>added 1, changed 6, removed 1</sub>

## `connect-blind-spots` — corp-os-connect (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the registry gained the source
- PASS — the blind spots question was actually asked

  <sub>added 0, changed 3, removed 0</sub>

## `dashboard-hub-and-registry` — corp-os-dashboard (6/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the new dashboard is recorded in the root registry
- PASS — the run closed its own books
- **FAIL** — no dashboards/ directory was created · touched: ['dashboards/hub.html']
- PASS — the hub is offered as a hub, not as an eighth analytical view

  <sub>added 2, changed 4, removed 0</sub>

  Why these matter:

  - **no dashboards/ directory was created** — the registry was a directory holding one file for five releases, and that shape made the index report 1 no matter how many dashboards were in it. A run that recreates the directory has reintroduced the bug the layout fix removed

## `dashboard-missing-layer` — corp-os-dashboard (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- **FAIL** — the missing layer is raised as a proposal, not improvised to get the dashboard built · added 0, needed 1: []
- PASS — the declared layer has an index_line

  <sub>added 1, changed 2, removed 0</sub>

  Why these matter:

  - **the missing layer is raised as a proposal, not improvised to get the dashboard built** — a layer is a structural change to what the OS can hold, and the gate is what stops one being shaped wrong in passing. The proposal is the artifact that survives the session; a run that quietly invents a directory to render a panel leaves nothing to review

## `decide-open-fork` — corp-os-decide (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **FAIL** — derived-layer writes have a proposal behind them · wrote ['claims/support.md', 'decisions/midmarket-pricing.md', 'decisions/support-tooling.md', 'jobs/renewal-risk.md'] with no proposal file
- PASS — no raw material was written
- PASS — the past-date decision was surfaced

  <sub>added 0, changed 9, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know

## `fidelity-backlog` — corp-os-reality-check (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the run closed its own books
- PASS — unrecoverable entries are separated from decay candidates
- PASS — nothing was promoted without an actual fetch

  <sub>added 1, changed 14, removed 0</sub>

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

## `guide-open-fork` — corp-os-guide (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — guide did not open the decision itself
- PASS — guide did not file it as a claim
- PASS — guide wrote nothing to the source layer
- PASS — routes an undecided fork to corp-os-decide

  <sub>added 0, changed 1, removed 0</sub>

## `improve-thin-evidence` — corp-os-improve (3/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **FAIL** — derived-layer writes have a proposal behind them · wrote ['claims/pricing.md'] with no proposal file
- PASS — no improvement packet written from one occurrence
- **FAIL** — no proposals written from one occurrence · touched: ['usage/proposals.md']
- **FAIL** — improve wrote no claims · touched: ['claims/pricing.md']

  <sub>added 0, changed 4, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know
  - **no proposals written from one occurrence** — the bar is more than one real occurrence. Proposing from a single one is manufacturing findings from noise, and this skill is the most prone to it because a person who asked for changes wants changes
  - **improve wrote no claims** — this skill studies how the OS is used and proposes changes to it. Writing a claim means it answered a question nobody asked with material it was reviewing, and it is corp-os-claims that has the rules for doing that properly

## `intake-transcript` — corp-os-intake (8/8)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — raw file written for the pasted material
- PASS — proposal file written before claims were presented
- PASS — INDEX.md updated in the same pass
- PASS — meta.json recounted
- PASS — unprocessed raw files are reachable from INDEX.md

  <sub>added 2, changed 8, removed 0</sub>

## `jobs-artifact-as-motivation` — corp-os-jobs (5/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **FAIL** — derived-layer writes have a proposal behind them · wrote ['jobs/renewal-early-warning.md', 'jobs/renewal-risk.md', 'jobs/support-load.md'] with no proposal file
- PASS — a job file was written
- PASS — the dashboard they asked for was not built
- PASS — the job written carries an outcome clause

  <sub>added 1, changed 7, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know

## `migrate-cohort-and-cliff` — corp-os-migrate (10/10)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — raw files written for the material that should come across
- PASS — the disposition record exists
- PASS — the batch went through the gate as a persisted proposal
- PASS — a cohort ceiling was recorded before minting
- PASS — the run closed its own books
- PASS — unprocessed raw files are reachable from INDEX.md
- PASS — the calendar log is declined rather than filed

  <sub>added 14, changed 6, removed 0</sub>

## `pattern-adopt-refusal` — corp-os-pattern (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the run closed its own books
- PASS — the teammate's pattern was not edited to make it bind
- PASS — the refusal is reported rather than worked around

  <sub>added 1, changed 3, removed 0</sub>

## `pull-broken-connector` — corp-os-pull (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the broken connector was recorded as broken, not silently skipped
- PASS — the hand-maintained source layer was not touched

  <sub>added 1, changed 4, removed 0</sub>

## `reality-check-sweep` — corp-os-reality-check (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- PASS — the unsourced entry was handled as its own bucket

  <sub>added 1, changed 12, removed 0</sub>

## `rebuild-respects-roles` — corp-os-rebuild (6/7)

> run error: timed out

- PASS — raw stays append-only
- **FAIL** — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — meta.json carries a dated history entry for the rebuild
- PASS — the hand-maintained source layer survived
- PASS — the raw archive was not rewritten
- PASS — the existing proposals record was not rewritten

  <sub>added 0, changed 2, removed 0</sub>

  Why these matter:

  - **usage/log.md row appended** — the friction field is the whole improvement flywheel; a skill that skips it under pressure makes corp-os-improve blind

## `recall-jobs-off` — corp-os-recall (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — the hand-maintained source layer was not touched
- PASS — no raw material was written
- PASS — the run completed against an OS with no jobs layer

  <sub>added 0, changed 1, removed 0</sub>

## `recall-load-bearing-sensitive` — corp-os-recall (6/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- **FAIL** — the load-bearing sensitive fact reached the answer · 'march' absent from the answer
- PASS — the export boundary was flagged at the moment it matters
- PASS — the incidental quarantined material stayed out

  <sub>added 1, changed 1, removed 0</sub>

  Why these matter:

  - **the load-bearing sensitive fact reached the answer** — CL-0004 is sensitive AND load_bearing: Northwind's champion leaves in March, so every plan routed through her is wrong after that. This is one person's own knowledge base -- withholding it protects nobody, and an answer computed around it is not cautious, it is wrong in the worst way, because nothing in it signals the omission

## `recall-read-only` — corp-os-recall (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — no raw material was written

  <sub>added 1, changed 1, removed 0</sub>

## `redact-external` — corp-os-redact (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — two outputs, not one — a cleaned copy and its private log
- PASS — the originals were not modified in place
- PASS — raw was not touched

  <sub>added 2, changed 2, removed 0</sub>

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

  <sub>added 37, changed 0, removed 0</sub>

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

  <sub>added 10, changed 6, removed 0</sub>

