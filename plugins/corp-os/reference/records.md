# The other record shapes

Everything that is not a claim: the job, the open decision, the raw file, the connector registry, the usage log and `meta.json`. The claim is in `reference/claim-record.md`; the layer rules and the scan contract are in `reference/data-model.md`.

## Job record

`jobs/<job-slug>.md`:

```markdown
---
id: job-004
statement: "When a renewal comes up, I want to know which churn risks are real, so I can decide what to concede."
kind: recurring          # recurring | milestone | exploratory
status: active           # active | blocked | paused | done | retired
horizon: this-quarter    # this-week | this-quarter | this-year | ongoing
readiness: medium        # high | medium | low — how equipped am I to do this today
stakeholders: [alex-r, jordan-k]
opened: 2026-09-04
last_touched: 2026-09-04
---

## Definition of done
What has to be true for this job to be considered handled. For a recurring job,
what a single good instance looks like.

## Success signals
The observable evidence, and the metric if there is one. Not aspirations —
things that can be checked.

## What I still need to know
The open evidence list, each item carrying its answer-status. This is the field
that drives intake priority, so keep items specific: "whether Acme's usage
dipped before or after the pricing change," not "more info on Acme."

- `open` — nothing on it yet.
- `signal exists` — something points at an answer but does not establish it.
- `partial` — answered in part; name what is still missing.
- `answered` — resolved, with the claim ID that resolved it. Kept briefly, then
  moved to History.
- `in motion` — being answered by work already underway, not by research.

## What I know
Linked claim IDs with their one-line statements. Never restate a claim's body
here — link it, so there is exactly one place it can be corrected.

## Blockers
What is stopping this, and who owns each blocker.

## Sources that serve this job
Connector or source names from connectors.md, with a one-line note on what each
can and cannot tell me.

## Deliverables
Things produced in service of this job, and where they live.

## History
Dated log of status changes and why.
```
## Decision record

Optional layer, declared as `layers.decisions`. It holds decisions that have **not been made yet** — the live forks. A decision that has been made is a `decision` claim, and closing a record here produces one.

The split is worth stating because it decides where things go. A claim rots by going stale, and a sweep catches it. An open decision rots by going quiet, and nothing catches that except a date, which is why `decide_by` is required here and has no equivalent on a claim.

`decisions/<slug>.md`:

```markdown
---
id: dec-007
statement: "Per-seat or usage pricing for the mid-market tier?"
owner: "Priya Raman"        # a person, never a team
status: open                # open | blocked | decided | lapsed | moot
decide_by: 2026-11-01
reversibility: costly       # reversible | costly | one-way
blocks: [job-004, dec-009]
opened: 2026-09-12
---

## Options
- **Per-seat** — predictable revenue; caps expansion in accounts that add read-only users.
- **Usage** — expands with adoption; unpredictable, and finance has said forecasting is the constraint.

## What would settle it
Whether the accounts that churned last year were seat-capped or usage-capped. Filed as an evidence item on job-004.

## Rests on
- CL-0042 (fact) — Acme named per-seat cost as the renewal obstacle.
- CL-0061 (assumption, untested) — mid-market buyers prefer predictable billing.

## History
Dated log: opened, blocked, owner changed, decided or lapsed, and the reasoning at the time.
```

**`decide_by` is what makes the layer work.** Past that date the choice is being made by default, and the record should say which option is winning by inaction. A decision layer without dates is a list of things someone feels vaguely bad about.

**`reversibility` sets how much evidence is worth gathering.** A reversible call made quickly and corrected beats a one-way call made slowly on the same information. Recording which kind this is stops both errors — the month spent on something that could have been tried in an afternoon, and the one-way door walked through casually.

On closure, the record keeps **the reasoning at the time**, not the reasoning that looks best afterward. Whether a call was wrong or merely unlucky is the single most useful thing this layer can answer a year later, and it is unrecoverable if the record was written to flatter.
## Raw file

```markdown
---
source: granola          # granola | slack | email | doc | transcript | note | web | tool
person: dana-chen        # primary other party, or `self` for a personal note
also_present: [alex-r]
date: 2026-09-02
type: meeting            # meeting | thread | document | note | call | research
jobs: [job-004]          # which jobs this was captured in service of
tags: [pricing, renewal]
external_id: granola:abc123   # for dedupe on connector pulls; omit if none
processed: false         # flipped true once the derived layer has taken from it
---

> Source: pulled from meeting notes connector, 2026-09-02

<content, essentially as given — placed and tagged, not rewritten>
```
## Connector registry

`connectors.md`, one block per source:

```markdown
### Meeting notes — Granola
- **Category**: meeting notes
- **Protocol**: MCP
- **Auth**: OAuth via connector, no local credentials
- **Feeds**: raw/ as `source: granola`, `type: meeting`
- **Serves jobs**: job-001, job-004
- **Cadence**: daily
- **Last pull**: 2026-09-03 — cursor `granola:abc123`
- **Status**: healthy       # healthy | stale | broken | not-connected | manual-only
- **List call**: `list_meetings(since, limit)` — id, title, date, participants. No bodies.
- **Fetch call**: `get_transcript(id)` — the body, verbatim
- **Verbatim fetch**: yes
- **Blind spots**: only captures calls I actually joined; nothing from Alex's own calls.
```

**`List call` and `Fetch call` are what make triage possible at all.** Almost every source has two shapes of read — one that enumerates and one that returns a body — and they differ in cost by two orders of magnitude. A registry that records only *"Protocol: MCP"* tells a skill it can reach the source and nothing about how to reach it cheaply, so the skill does the only thing it knows how to do and fetches everything.

Record the narrowing arguments too, in the call itself: the parameter that caps results, the one that takes a date, the one that selects fields. An unnarrowed call is the difference between reading a week and reading a year.

Where a source can be reached by a script rather than through a model — an export on disk, an API with a token in the environment — record that instead and the bytes never enter a context at all:

```markdown
- **Fetch command**: `python3 scripts/fetch_granola.py --since {cursor} --out raw/`
- **Credential**: env `GRANOLA_TOKEN` — never the value, and never in this file
```

A credential is named here, never written here. The OS folder gets synced, shared, and handed to an audit; a secret in it is a secret published.

The **blind spots** field earns its keep. A connector registry that only lists what a source provides quietly implies full coverage. Writing down what each source cannot see is what stops the OS from mistaking silence for absence.
## Usage log

`usage/log.md` is an append-only table. Every skill in this plugin adds exactly one row per run, at the end of the run:

```markdown
| date | skill | jobs | asked for | outcome | friction |
|---|---|---|---|---|---|
| 2026-09-04 | corp-os-recall | job-004 | churn risk evidence for Acme | answered from 3 claims | 2 of 3 claims were past decay |
```

`friction` is the field `corp-os-improve` mines. Leave it blank when a run was clean; write the specific annoyance when it was not. "Had to ask the person which job this belonged to because nothing in the index made it obvious" is a useful row. "Went fine" is noise.
## meta.json

```json
{
  "corpos_version": "0.1.0",
  "created": "2026-09-04",
  "operator": "Brent Gann",
  "counts": { "raw": 0, "unprocessed": 0, "jobs": 0, "claims": 0, "people": 0, "topics": 0, "glossary_terms": 0 },
  "next_claim_id": 1,
  "next_job_id": 1,
  "cutoff": { "granola": null, "slack": null },
  "history": [
    { "date": "2026-09-04", "skill": "corp-os-setup", "change": "scaffolded OS with jobs, claims, raw, usage" }
  ]
}
```

Counts are always **recounted programmatically** (count files, count matching headers) rather than incremented by hand. Hand-incrementing is exactly where these numbers drift wrong over dozens of runs, and a wrong count in INDEX.md silently poisons the scan contract.

`scripts/build_index.py` ships with this plugin and does exactly this: it recounts files and headers, rewrites INDEX.md's listings and counts, and reports drift. It reads nothing from `raw/` and retags nothing — **bookkeeping, not judgment.** Keeping the deterministic half separate from the semantic half is what makes it safe to run after any manual edit, and it means "the index is stale" is a thirty-second fix rather than a reason to schedule a rebuild.

Add `confidence_ceilings` to `meta.json` per the cohort section above, and a `proposals` count alongside the rest.
