---
name: dashboard-job-board
kind: dashboard
pack: corp-os-shipped@0.13.0
requires:
  - role: derived
    label: jobs
    fields: [id, statement]
  - role: derived
    fields: [citation, confidence]
  - role: source
  - role: derived
    label: person
    fields: [aliases]
    optional: true
produces: one self-contained HTML file
target: local
shield: required
generator: scripts/build_dashboard_job_board.py
---

## What it answers

What am I working toward, which of those is blocked, and what is the evidence
underneath each one actually worth.

Build this one first when there are many jobs and unclear priorities. It is the
view that turns a list of intentions into an ordering.

## Composition

- **Jobs, by readiness.** One row per job: statement, status, horizon, readiness,
  and the count of open evidence items. Ordered by readiness ascending, so the
  least ready sits at the top where it can be acted on.
- **Blocked, and on what.** Every job whose status is blocked, with the decision
  or evidence item blocking it, and how long it has been that way.
- **Evidence health per job.** For each job, `N entries / M distinct sources`.
  Never entries alone — see the recurrence rule in `reference/patterns.md`.
- **Open evidence, oldest first.** Cited from the root index, which already
  computes it. Do not recompute.
- **Unjobbed material.** Entries carrying no job, grouped by their file. A job
  list with a blind spot mis-ranks that domain every time, and this is the panel
  that makes the blind spot visible rather than structural.

## Refuses

- Cross-file navigation links. In-page routing only.
- Any runtime `fetch()`. Data is embedded.
- Any count computed anywhere but at build time.
- Recomputing a headline figure a panel could cite from `meta.json`.
- Rendering an empty panel where an optional layer did not bind. Say it was
  dropped instead.

## Verification

The five checks in `reference/patterns.md`, plus the shield checks, since this
pattern declares `shield: required` and a job board names people in its
blocked-on column.
