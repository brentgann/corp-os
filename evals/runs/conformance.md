# Conformance

Model `claude-opus-5` · 4 cases · each against a fresh copy of `examples/fixture-os`

**17/23 checks passed**

## `decide-open-fork` — corp-os-decide (5/5)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — no raw material was written
- PASS — the past-date decision was surfaced

  <sub>added 1, changed 5, removed 0</sub>

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

## `improve-thin-evidence` — corp-os-improve (3/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- **67%** — derived-layer writes have a proposal behind them · 2/3 runs
- PASS — no improvement packet written from one occurrence
- **67%** — no proposals written from one occurrence · 2/3 runs
- **67%** — improve wrote no claims · 2/3 runs

  <sub>added 0, changed 2, removed 0</sub>

  Why these matter:

  - **derived-layer writes have a proposal behind them** — a proposal that lives only in chat dies with the session and leaves no record of what the gate saw -- the declines especially, which are the only trace of what someone chose not to know
  - **no proposals written from one occurrence** — the bar is more than one real occurrence. Proposing from a single one is manufacturing findings from noise, and this skill is the most prone to it because a person who asked for changes wants changes
  - **improve wrote no claims** — this skill studies how the OS is used and proposes changes to it. Writing a claim means it answered a question nobody asked with material it was reviewing, and it is corp-os-claims that has the rules for doing that properly

## `jobs-artifact-as-motivation` — corp-os-jobs (6/6)

- PASS — raw stays append-only
- PASS — usage/log.md row appended
- PASS — derived-layer writes have a proposal behind them
- PASS — a job file was written
- PASS — the dashboard they asked for was not built
- PASS — the job written carries an outcome clause

  <sub>added 2, changed 6, removed 0</sub>

