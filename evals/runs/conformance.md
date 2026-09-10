# Conformance

Model `claude-opus-5` · 3 cases · each against a fresh copy of `examples/fixture-os`

**17/18 checks passed**

## `dashboard-hub-and-registry` — corp-os-dashboard (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the new dashboard is recorded in the root registry
- PASS — the run closed its own books
- PASS — no dashboards/ directory was created
- PASS — the hub is offered as a hub, not as an eighth analytical view

  <sub>added 2, changed 4, removed 0</sub>

## `dashboard-missing-layer` — corp-os-dashboard (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- **67%** — the missing layer is raised as a proposal, not improvised to get the dashboard built · 2/3 runs
- PASS — the declared layer has an index_line

  <sub>added 1, changed 2, removed 0</sub>

  Why these matter:

  - **the missing layer is raised as a proposal, not improvised to get the dashboard built** — a layer is a structural change to what the OS can hold, and the gate is what stops one being shaped wrong in passing. The proposal is the artifact that survives the session; a run that quietly invents a directory to render a panel leaves nothing to review

## `glossary-competing-definitions` — corp-os-glossary (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — a proposal was filed before the entry was written
- PASS — both definitions survived
- PASS — unprocessed raw files are reachable from INDEX.md

  <sub>added 2, changed 4, removed 0</sub>

