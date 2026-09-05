# Conformance

Model `claude-opus-5` · 12 cases · each against a fresh copy of `examples/fixture-os`, `examples/fixture-register`

**73/75 checks passed**

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

## `configure-delete-sequence` — corp-os-configure (6/7)

- PASS — raw deletion happened under the retention path
- **67%** — raw stays append-only · 2/3 runs
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — entries citing the deleted source were re-cited
- PASS — config.json records the policy and the obligation
- PASS — meta.json logs what was destroyed and under what obligation

  <sub>added 1, changed 9, removed 1</sub>

  Why these matter:

  - **raw stays append-only** — an edited raw file destroys the only thing a rebuild can restore from; flipping `processed` is the one sanctioned edit, and deletion only under a declared retention obligation

## `decide-open-fork` — corp-os-decide (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- PASS — the past-date decision was surfaced

  <sub>added 2, changed 4, removed 0</sub>

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

## `reality-check-sweep` — corp-os-reality-check (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- PASS — the unsourced entry was handled as its own bucket

  <sub>added 1, changed 7, removed 0</sub>

## `rebuild-respects-roles` — corp-os-rebuild (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — meta.json carries a dated history entry for the rebuild
- PASS — the hand-maintained source layer survived
- PASS — the raw archive was not rewritten
- PASS — the existing proposals record was not rewritten

  <sub>added 1, changed 5, removed 0</sub>

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
- PASS — the load-bearing sensitive fact reached the answer
- PASS — the export boundary was flagged at the moment it matters
- **67%** — the incidental quarantined material stayed out · 2/3 runs

  <sub>added 0, changed 1, removed 0</sub>

  Why these matter:

  - **the incidental quarantined material stayed out** — sensitive.md holds incidental material and sits outside the scan path; pulling it in unasked is the opposite error and just as wrong

## `recall-read-only` — corp-os-recall (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — no raw material was written

  <sub>added 0, changed 1, removed 0</sub>

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

