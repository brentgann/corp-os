# corp-os — Index

Scan this first. Most questions should be answerable from this file alone; open a detail file only when the one-liners here are not enough.

_Regenerated 2026-09-09 by scripts/build_index.py (counts and listings only — no retagging)._

## Counts

- **Jobs**: 2
- **Raw files**: 3 (1 unprocessed)
- **Findings**: 4
- **Decisions**: 2
- **Patterns**: 1
- **Proposals**: 1
- **Dashboards**: 2

## Jobs

- **[job-001](jobs/renewal-risk.md)** — When a renewal comes up, I want to know which churn risks are real, so I can decide what to concede.
- **[job-002](jobs/support-load.md)** — When support volume spikes, I want to know which product surface caused it, so I can decide what to fix first.

## Decisions

- **[dec-001](decisions/midmarket-pricing.md)** — Per-seat or usage pricing for the mid-market tier? · Priya Raman · by 2026-11-01
- **[dec-002](decisions/support-tooling.md)** — Keep the current helpdesk through renewal, or migrate before Q4? · Wren Adeyemi · by 2026-09-01

## Unprocessed queue

Raw material not yet folded into the derived layer.

- [2026-08-21--note--hallway](raw/2026-08-21--note--hallway.md) — note

## Open evidence

What the jobs still need, oldest first. One list, because the alternative is the same question spread across every job file.

- Whether the churn started before or after the price change — `signal exists` · job-001
- Which accounts are seat-capped rather than usage-capped — `open` · job-001
- Which surface generated the August ticket spike — `partial` · job-002

## Not in the scan path

- `usage/` — excluded by config. Open only when the task specifically requires it.
- `sensitive.md` — excluded by config. Open only when the task specifically requires it.
- `raw/` — source of truth, but never loaded wholesale. corp-os-rebuild is the sole exception.
