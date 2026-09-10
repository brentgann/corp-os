# Conformance

Model `claude-opus-5` · 7 cases · each against a fresh copy of `examples/fixture-os`, `examples/fixture-register`

**36/40 checks passed**

## `dashboard-hub-and-registry` — corp-os-dashboard (6/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the new dashboard is recorded in the root registry
- PASS — the run closed its own books
- **67%** — no dashboards/ directory was created · 2/3 runs
- PASS — the hub is offered as a hub, not as an eighth analytical view

  <sub>added 2, changed 3, removed 0</sub>

  Why these matter:

  - **no dashboards/ directory was created** — the registry was a directory holding one file for five releases, and that shape made the index report 1 no matter how many dashboards were in it. A run that recreates the directory has reintroduced the bug the layout fix removed

## `dashboard-missing-layer` — corp-os-dashboard (3/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- **33%** — the missing layer is raised as a proposal, not improvised to get the dashboard built · 1/3 runs
- **67%** — the declared layer has an index_line · 2/3 runs

  <sub>added 1, changed 3, removed 0</sub>

  Why these matter:

  - **the missing layer is raised as a proposal, not improvised to get the dashboard built** — a layer is a structural change to what the OS can hold, and the gate is what stops one being shaped wrong in passing. The proposal is the artifact that survives the session; a run that quietly invents a directory to render a panel leaves nothing to review
  - **the declared layer has an index_line** — build_index.py renders this banner for any layer declared without an index_line, and lists its entries as bare links. It is the exact machine-visible signature of a layer declared without the configure interrogation -- the shape mistake this check exists to catch, made once already in this repo

## `decide-open-fork` — corp-os-decide (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- PASS — the past-date decision was surfaced

  <sub>added 1, changed 6, removed 0</sub>

## `glossary-competing-definitions` — corp-os-glossary (5/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — a proposal was filed before the entry was written
- PASS — both definitions survived
- **33%** — unprocessed raw files are reachable from INDEX.md · 1/3 runs

  <sub>added 2, changed 4, removed 0</sub>

  Why these matter:

  - **unprocessed raw files are reachable from INDEX.md** — a file that exists but is missing from the queue is invisible to every later run's scan, and the person's queue silently under-reports

## `improve-thin-evidence` — corp-os-improve (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no improvement packet written from one occurrence
- PASS — no proposals written from one occurrence
- PASS — improve wrote no claims

  <sub>added 0, changed 2, removed 0</sub>

## `jobs-artifact-as-motivation` — corp-os-jobs (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — a job file was written
- PASS — the dashboard they asked for was not built
- PASS — the job written carries an outcome clause

  <sub>added 2, changed 7, removed 0</sub>

## `pull-broken-connector` — corp-os-pull (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the broken connector was recorded as broken, not silently skipped
- PASS — the hand-maintained source layer was not touched

  <sub>added 0, changed 4, removed 0</sub>

