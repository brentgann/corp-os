# Conformance

Model `claude-opus-5` · 5 cases · each against a fresh copy of `examples/fixture-os`, `examples/fixture-register`

**22/29 checks passed**

## `decide-open-fork` — corp-os-decide (4/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **0%** — derived-layer writes have a proposal behind them · 0/3 runs
- PASS — no raw material was written
- PASS — the past-date decision was surfaced

  <sub>added 0, changed 6, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know

## `glossary-competing-definitions` — corp-os-glossary (3/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **33%** — derived-layer writes have a proposal behind them · 1/3 runs
- **33%** — a proposal was filed before the entry was written · 1/3 runs
- PASS — both definitions survived

  <sub>added 1, changed 4, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know
  - **a proposal was filed before the entry was written** — glossary entries are derived-layer like anything else

## `improve-thin-evidence` — corp-os-improve (3/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **67%** — derived-layer writes have a proposal behind them · 2/3 runs
- PASS — no improvement packet written from one occurrence
- **33%** — no proposals written from one occurrence · 1/3 runs
- **67%** — improve wrote no claims · 2/3 runs

  <sub>added 0, changed 4, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know
  - **no proposals written from one occurrence** — the bar is more than one real occurrence. Proposing from a single one is manufacturing findings from noise, and this skill is the most prone to it because a person who asked for changes wants changes
  - **improve wrote no claims** — this skill studies how the OS is used and proposes changes to it. Writing a claim means it answered a question nobody asked with material it was reviewing, and it is corp-os-claims that has the rules for doing that properly

## `jobs-artifact-as-motivation` — corp-os-jobs (5/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **0%** — derived-layer writes have a proposal behind them · 0/3 runs
- PASS — a job file was written
- PASS — the dashboard they asked for was not built
- PASS — the job written carries an outcome clause

  <sub>added 1, changed 5, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know

## `recall-jobs-off` — corp-os-recall (7/7)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — nothing entered the derived layer
- PASS — the hand-maintained source layer was not touched
- PASS — no raw material was written
- PASS — the run completed against an OS with no jobs layer

  <sub>added 0, changed 1, removed 0</sub>

