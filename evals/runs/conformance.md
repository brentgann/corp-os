# Conformance

Model `claude-sonnet-4-5` · 5 cases · each against a fresh copy of `examples/fixture-os`, `examples/fixture-register`

**22/32 checks passed**

## `pull-broken-connector` — corp-os-pull (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- **67%** — the broken connector was recorded as broken, not silently skipped · 2/3 runs
- PASS — the hand-maintained source layer was not touched

  <sub>added 0, changed 3, removed 0</sub>

  Why these matter:

  - **the broken connector was recorded as broken, not silently skipped** — the meeting-notes connector has been dead since July. A run that quietly pulls from email and reports success leaves the person believing they are covered on a source that has returned nothing for six weeks -- which is the specific way an OS starts mistaking silence for absence

## `rebuild-respects-roles` — corp-os-rebuild (5/8)

- **0%** — the plugin's own source was not modified · 0/3 runs
- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **67%** — derived-layer writes have a proposal behind them · 2/3 runs
- PASS — meta.json carries a dated history entry for the rebuild
- PASS — the hand-maintained source layer survived
- **33%** — the raw archive was not rewritten · 1/3 runs
- PASS — the existing proposals record was not rewritten

  <sub>added 0, changed 7, removed 0</sub>

  Why these matter:

  - **the plugin's own source was not modified** — a run works on a throwaway copy of an OS; the plugin is readable so skills can follow ${CLAUDE_PLUGIN_ROOT}, not so they can edit it. corp-os-contribute writes diffs and applies nothing, and this is what makes that testable rather than asserted
  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know
  - **the raw archive was not rewritten** — a rebuild reads raw/ wholesale; that is the one operation licensed to. It is never licensed to write there

## `recall-jobs-off` — corp-os-recall (5/7)

- PASS — raw stays append-only
- **33%** — usage/log.md row appended · 1/3 runs
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — the hand-maintained source layer was not touched
- PASS — no raw material was written
- **33%** — the run completed against an OS with no jobs layer · 1/3 runs

  <sub>added 0, changed 0, removed 0</sub>

  Why these matter:

  - **usage/log.md row appended** — the friction field is the whole improvement flywheel; a skill that skips it under pressure makes corp-os-improve blind
  - **the run completed against an OS with no jobs layer** — jobs is disabled here and an urgency-tiered open-items layer carries the priority signal instead. A skill that treats a missing jobs/ as a broken OS fails on this fixture -- which is the failure v0.6.0 actually shipped

## `recall-load-bearing-sensitive` — corp-os-recall (4/7)

- PASS — raw stays append-only
- **67%** — usage/log.md row appended · 2/3 runs
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- **67%** — the load-bearing sensitive fact reached the answer · 2/3 runs
- **67%** — the export boundary was flagged at the moment it matters · 2/3 runs
- PASS — the incidental quarantined material stayed out

  <sub>added 0, changed 2, removed 0</sub>

  Why these matter:

  - **usage/log.md row appended** — the friction field is the whole improvement flywheel; a skill that skips it under pressure makes corp-os-improve blind
  - **the load-bearing sensitive fact reached the answer** — CL-0004 is sensitive AND load_bearing: Northwind's champion leaves in March, so every plan routed through her is wrong after that. This is one person's own knowledge base -- withholding it protects nobody, and an answer computed around it is not cautious, it is wrong in the worst way, because nothing in it signals the omission
  - **the export boundary was flagged at the moment it matters** — the person is mid-draft and will copy the paragraph, not a closing caveat; the inline marking is what makes the boundary visible before it gets crossed rather than after

## `recall-read-only` — corp-os-recall (4/5)

- PASS — raw stays append-only
- **33%** — usage/log.md row appended · 1/3 runs
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — no raw material was written

  <sub>added 0, changed 0, removed 0</sub>

  Why these matter:

  - **usage/log.md row appended** — the friction field is the whole improvement flywheel; a skill that skips it under pressure makes corp-os-improve blind

