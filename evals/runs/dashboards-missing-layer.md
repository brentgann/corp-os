# Conformance

Model `claude-opus-5` · 1 cases · each against a fresh copy of `examples/fixture-os`

**4/5 checks passed**

## `dashboard-missing-layer` — corp-os-dashboard (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- **0%** — the missing layer is raised as a proposal, not improvised to get the dashboard built · 0/2 runs
- PASS — the declared layer has an index_line

  <sub>added 1, changed 4, removed 0</sub>

  Why these matter:

  - **the missing layer is raised as a proposal, not improvised to get the dashboard built** — a layer is a structural change to what the OS can hold, and the gate is what stops one being shaped wrong in passing. The proposal is the artifact that survives the session; a run that quietly invents a directory to render a panel leaves nothing to review

