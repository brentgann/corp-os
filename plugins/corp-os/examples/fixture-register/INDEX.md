# corp-os — Index

Scan this first. Most questions should be answerable from this file alone; open a detail file only when the one-liners here are not enough.

_Regenerated 2026-09-10 by scripts/build_index.py (counts and listings only — no retagging)._

## Counts

- **Raw files**: 3 (1 unprocessed)
- **Entries**: 4
- **Open-Items**: 3
- **Patterns**: 1
- **Playbooks**: 2
- **Proposals**: 1
- **Unlisted Files**: 1
- **Dashboards**: 0

## Open-Items

- **[oi-001](open-items/meridian-replacement.md)** — What replaces the Meridian SLA tier after March? · now
- **[oi-002](open-items/attestation-scope.md)** — Does the Q2 attestation move change the evidence we have to collect? · soon
- **[oi-003](open-items/retention-figure.md)** — Is the seven-year retention figure actually right? · watching

## Playbooks

- **[Escalation ladder](playbooks/escalation.md)** — hand-maintained
- **Vendor offboarding** — hand-maintained

## Unlisted Files

- **connectors**

> **Paths follow the name.** An entry listed without a link lives at `<layer>/<its name, lowercased and hyphenated>.md` — 2 of them here. Spelling that out per entry restates the name in a form that costs more than the name. Anything whose filename does not follow the convention keeps its link.

> **Incomplete index.** These layers have no `index_line` in `config.json`, so their entries are listed as bare links and cannot be scanned without opening each file: `unlisted_files`. Run corp-os-configure to give each one a template.

## Unprocessed queue

Raw material not yet folded into the derived layer.

- [2026-08-25--note--meridian-call](raw/2026-08-25--note--meridian-call.md) — note

## Not in the scan path

- `usage/` — excluded by config. Open only when the task specifically requires it.
- `sensitive.md` — excluded by config. Open only when the task specifically requires it.
- `raw/` — source of truth, but never loaded wholesale. corp-os-rebuild is the sole exception.
