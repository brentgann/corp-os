# Conformance

Model `claude-opus-5` · 3 cases · each against a fresh copy of `examples/fixture-os`

**14/18 checks passed**

## `dashboard-hub-and-registry` — corp-os-dashboard (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the new dashboard is recorded in the root registry
- PASS — the run closed its own books
- PASS — no dashboards/ directory was created
- PASS — the hub is offered as a hub, not as an eighth analytical view

  <sub>added 2, changed 3, removed 0</sub>

## `dashboard-missing-layer` — corp-os-dashboard (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the missing layer is raised as a proposal, not improvised to get the dashboard built
- **67%** — the declared layer has an index_line · 2/3 runs

  <sub>added 2, changed 2, removed 0</sub>

  Why these matter:

  - **the declared layer has an index_line** — build_index.py renders this banner for any layer declared without an index_line, and lists its entries as bare links. It is the exact machine-visible signature of a layer declared without the configure interrogation -- the shape mistake this check exists to catch, made once already in this repo

## `glossary-competing-definitions` — corp-os-glossary (3/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **67%** — derived-layer writes have a proposal behind them · 2/3 runs
- **67%** — a proposal was filed before the entry was written · 2/3 runs
- PASS — both definitions survived
- **33%** — unprocessed raw files are reachable from INDEX.md · 1/3 runs

  <sub>added 2, changed 4, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know
  - **a proposal was filed before the entry was written** — glossary entries are derived-layer like anything else
  - **unprocessed raw files are reachable from INDEX.md** — a file that exists but is missing from the queue is invisible to every later run's scan, and the person's queue silently under-reports

