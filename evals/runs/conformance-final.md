# Conformance

Model `claude-opus-5` · 6 cases · each against a fresh copy of `examples/fixture-os`

**35/35 checks passed**

## `brief-window` — corp-os-brief (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — meta.json history records the brief and its window
- PASS — nothing entered the derived layer
- PASS — no raw material was written

  <sub>added 1, changed 2, removed 0</sub>

## `claims-queue` — corp-os-claims (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — proposal file written before anything was presented
- PASS — the disabled glossary layer was not created
- PASS — the person's own vocabulary is used, not the plugin's

  <sub>added 1, changed 5, removed 0</sub>

## `decide-open-fork` — corp-os-decide (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- PASS — the past-date decision was surfaced

  <sub>added 1, changed 6, removed 0</sub>

## `intake-transcript` — corp-os-intake (8/8)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — raw file written for the pasted material
- PASS — proposal file written before claims were presented
- PASS — INDEX.md updated in the same pass
- PASS — meta.json recounted
- PASS — unprocessed raw files are reachable from INDEX.md

  <sub>added 2, changed 7, removed 0</sub>

## `reality-check-sweep` — corp-os-reality-check (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- PASS — the unsourced entry was handled as its own bucket

  <sub>added 1, changed 5, removed 0</sub>

## `recall-read-only` — corp-os-recall (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — no raw material was written

  <sub>added 1, changed 2, removed 0</sub>

