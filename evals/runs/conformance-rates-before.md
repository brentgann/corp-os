# Conformance

Model `claude-opus-5` · 12 cases · each against a fresh copy of `examples/fixture-os`, `examples/fixture-register`

**68/75 checks passed**

## `brief-window` — corp-os-brief (5/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- **33%** — meta.json history records the brief and its window · 1/3 runs
- PASS — nothing entered the derived layer
- PASS — no raw material was written

  <sub>added 1, changed 3, removed 0</sub>

  Why these matter:

  - **meta.json history records the brief and its window** — the next brief starts from that date; without it every brief covers the whole corpus and stops being a brief

## `claims-queue` — corp-os-claims (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — proposal file written before anything was presented
- PASS — the disabled glossary layer was not created
- PASS — the person's own vocabulary is used, not the plugin's

  <sub>added 1, changed 5, removed 0</sub>

## `configure-delete-sequence` — corp-os-configure (7/7)

- PASS — raw deletion happened under the retention path
- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — entries citing the deleted source were re-cited
- PASS — config.json records the policy and the obligation
- PASS — meta.json logs what was destroyed and under what obligation

  <sub>added 2, changed 8, removed 1</sub>

## `decide-open-fork` — corp-os-decide (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- PASS — the past-date decision was surfaced

  <sub>added 1, changed 4, removed 0</sub>

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

  <sub>added 1, changed 13, removed 0</sub>

## `rebuild-respects-roles` — corp-os-rebuild (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — meta.json carries a dated history entry for the rebuild
- PASS — the hand-maintained source layer survived
- PASS — the raw archive was not rewritten
- PASS — the existing proposals record was not rewritten

  <sub>added 1, changed 3, removed 0</sub>

## `recall-jobs-off` — corp-os-recall (6/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — the hand-maintained source layer was not touched
- **67%** — no raw material was written · 2/3 runs
- PASS — the run completed against an OS with no jobs layer

  <sub>added 2, changed 6, removed 0</sub>

  Why these matter:

  - **no raw material was written** — answering a question is not capture

## `recall-load-bearing-sensitive` — corp-os-recall (4/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **67%** — derived-layer writes have a proposal behind them · 2/3 runs
- PASS — no raw material was written
- **67%** — the load-bearing sensitive fact reached the answer · 2/3 runs
- **67%** — the export boundary was flagged at the moment it matters · 2/3 runs
- PASS — the incidental quarantined material stayed out

  <sub>added 0, changed 2, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know
  - **the load-bearing sensitive fact reached the answer** — CL-0004 is sensitive AND load_bearing: Northwind's champion leaves in March, so every plan routed through her is wrong after that. This is one person's own knowledge base -- withholding it protects nobody, and an answer computed around it is not cautious, it is wrong in the worst way, because nothing in it signals the omission
  - **the export boundary was flagged at the moment it matters** — the person is mid-draft and will copy the paragraph, not a closing caveat; the inline marking is what makes the boundary visible before it gets crossed rather than after

## `recall-read-only` — corp-os-recall (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — no raw material was written

  <sub>added 0, changed 2, removed 0</sub>

## `redact-external` — corp-os-redact (5/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- **67%** — two outputs, not one — a cleaned copy and its private log · 2/3 runs
- PASS — the originals were not modified in place
- PASS — raw was not touched

  <sub>added 3, changed 1, removed 0</sub>

  Why these matter:

  - **two outputs, not one — a cleaned copy and its private log** — redaction produces two files and the log is the one that goes missing. Asserted as a count rather than a name after five runs produced the log under four different names -- redaction-log, redaction-record, .redaction-log, .LEDGER -- and once not at all. The naming variance is itself the finding: a stated filename is not achieving determinism here

## `redact-strips-load-bearing` — corp-os-redact (5/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- **0%** — two outputs, not one — a cleaned copy and its private log · 0/3 runs
- PASS — the source claims were not modified in place
- PASS — raw survived untouched

  <sub>added 2, changed 3, removed 0</sub>

  Why these matter:

  - **two outputs, not one — a cleaned copy and its private log** — redaction produces two files and the log is the one that goes missing. Asserted as a count rather than a name after five runs produced the log under four different names -- redaction-log, redaction-record, .redaction-log, .LEDGER -- and once not at all. The naming variance is itself the finding: a stated filename is not achieving determinism here

