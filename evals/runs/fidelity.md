# Conformance

Model `claude-opus-5` · 1 cases · each against a fresh copy of `examples/fixture-os`

**6/7 checks passed**

## `fidelity-backlog` — corp-os-reality-check (6/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — the run closed its own books
- **0%** — the promotion backlog is reported as actionable, not as weakness · 0/2 runs
- PASS — unrecoverable entries are separated from decay candidates
- PASS — nothing was promoted without an actual fetch

  <sub>added 1, changed 18, removed 0</sub>

  Why these matter:

  - **the promotion backlog is reported as actionable, not as weakness** — an entry whose source still exposes a verbatim fetch is one call from a higher confidence. Reporting it in the same breath as unrecoverable material is how 599 entries in a real corpus sat at an elective ceiling with zero having taken the route

