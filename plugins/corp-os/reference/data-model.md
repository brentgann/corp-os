# Corp-OS data model

The canonical spec — and a **default profile, not a schema.**

Every skill reads this file for the shapes, but reads the OS's own `config.json` for which of them apply. Layer names, label vocabularies, decay windows, retention and TTL policy, gate strictness, and any layer the model never imagined are all declared there; see `configuration.md`. Precedence is `config.json`, then the OS's own `README.md`, then this file.

What is *not* configurable is the short list this whole thing rests on: an append-only source layer, provenance on derived entries, a review gate in front of the derived layer, an index that can be scanned instead of loaded, and something that removes things. Everything else is a reasonable guess about a stranger's work, and guesses should be adjustable.

## The organizing idea

Most personal knowledge bases are organized by *subject* — a folder per topic, a note per person. Corp-OS is organized by **job to be done**: the concrete outcome the person is trying to reach. Subjects still exist, but they hang off jobs.

This inversion is the whole point, and it buys three things:

1. **Intake gets a priority signal.** A job declares what it still needs to know. That turns "capture everything" into "capture what's blocking job-004."
2. **Recall gets a relevance signal.** "What do we know about pricing" is unanswerable in the abstract; "what do we know about pricing that bears on the renewal job" has a real answer.
3. **Pruning gets a stopping rule.** When a job retires, everything that existed only to serve it can retire with it. Without this, a personal OS only ever grows.

A job is not a task. A task is "send Alex the deck." A job is "when a renewal comes up, I want to know which risks are real, so I can decide what to concede." Jobs recur; tasks complete.

### When a jobs layer is the wrong answer

Job-organization is this model's default, not its requirement, and it is worth being direct about when it does not pay. `layers.jobs.enabled: false` is a supported, sometimes correct configuration.

Before building or recommending a jobs layer, run this test on whatever open-items layer already exists:

> Attempt to cluster the existing material into three to seven candidate jobs — **without looking at the subject files first**. Then compare the clusters against the topic, category, or subject taxonomy already in use.

If the clusters largely reproduce that existing taxonomy, the material is **subject-shaped**, and a jobs layer will duplicate a structure that already works rather than adding a priority signal. Two further tells:

- **High cross-assignment.** If a quarter or more of entries fit two clusters equally well, the taxonomy needs arbitration on every write, and it will not survive contact with a busy week.
- **Clusters that are really subject areas.** A cluster named for a domain ("integrations," "retention," "data quality") groups things that share a topic but have different triggers, different deciders, and different evidence. Calling that one job destroys information rather than organizing it.

Jobs pay off for a **decision-heavy** operator with a modest number of recurring forks, where the same question gets re-asked and the same evidence gets re-gathered. They cost more than they return for work that is mostly reference accumulation, mostly execution against an already-clear objective, or organized around long-lived subject areas that genuinely do not change.

When jobs are disabled, something else has to carry the two functions they provide — an intake priority signal and a rule that removes things. Say which: urgency tiering plus a decay policy is the usual substitute, and it is a legitimate one.

## Authority and pre-flight

Two rules that come before every operation, because getting them wrong silently invalidates everything downstream.

**Pre-flight.** Before doing any work in a Corp-OS, confirm it is actually accessible — mounted, current, and readable right now — not recalled from a previous session. A stale export, a folder that did not mount, a sync that has not landed: stop and ask rather than working from memory of what the OS probably contains. An operation performed against a remembered OS produces confident output about files that may not exist.

**The OS beats memory.** These files outrank an agent's own memory of past sessions. When something recalled about a person, a claim, or a decision conflicts with what is written in the OS, the files win, and the memory is what gets corrected. Memory is continuity between sessions, not a source of truth.

## Directory structure

```
<corp-os-root>/
├── README.md               # this OS's own operating manual (generated at setup)
├── INDEX.md                # scan-first entry point — the one file every skill reads
├── meta.json               # counts, cutoffs, dated history log
├── profile.md              # the operator: role, mandate, intent, horizon, working style
├── jobs/
│   ├── INDEX.md            # one line per job
│   └── <job-slug>.md       # full job record
├── claims/
│   ├── INDEX.md            # one line per claim
│   └── <topic-slug>.md     # claims grouped by topic
├── proposals/
│   └── PROPOSAL-YYYY-MM-DD-<slug>.md   # the review gate, persisted
├── sensitive.md            # quarantine — deliberately outside the scan path
├── raw/
│   ├── README.md           # append-only convention + frontmatter shape
│   └── YYYY-MM-DD--<source>--<slug>.md
├── company/
│   ├── <company-slug>.md   # own employer, plus accounts / prospects / competitors
│   └── market.md
├── people/<slug>.md
├── topics/<slug>.md
├── glossary.md
├── connectors.md           # what is connected, by what protocol, feeding what
├── design.md               # which design system governs rendered output
├── dashboards/
│   └── registry.md         # name, URL, source files, cadence, owning job
├── scripts/
│   └── build_index.py      # deterministic recount — bookkeeping, not judgment
└── usage/
    ├── log.md              # what the OS was asked to do, and where it hurt
    └── proposals.md        # improvement backlog
```

Only `raw/`, `INDEX.md`, `meta.json`, `proposals/` and `usage/` are mandatory. **`jobs/` is not** — see below. Everything else gets created when the person actually wants it. An empty `glossary.md` nobody fills for six months is worse than not having one.

## The two layers, and the gate between them

- **raw/** is the source of truth. Append-only. Never edited, never summarized in place, never deleted. Existing in raw/ does not make something true — only said.
- **Everything else** is the derived layer. Fully regenerable from raw/ (that is what `corp-os-rebuild` does). Nothing lands here without a human confirming it.

Skills may write to `raw/`, `INDEX.md`, `meta.json`, and `usage/log.md` autonomously. Skills must **propose, not write** anything entering `claims/`, `jobs/`, `people/`, `topics/`, `glossary.md`, or `company/`.

The gate is not there because any single entry is risky. It is there because without it the derived layer stops being knowledge and becomes just a second, messier copy of raw/.

**The gate is persisted, not conversational.** Every proposal is written to `proposals/PROPOSAL-YYYY-MM-DD-<slug>.md` before it is presented — headline first, then the specific additions and edits with their provenance, then an explicit recommendation per item (enrich an existing entry, create a new one, flag as a conflict, decline). A proposal that lives only in a chat exchange dies when the session does, leaves no audit trail of what the gate actually saw, and cannot be reviewed by the person the next morning when they have time to think about it. The file is the deliverable of a propose step; the conversation is just how it gets discussed.

A proposal file records what was **recommended**, not what was accepted. Once acted on, append the outcome per item — confirmed, declined, deferred, modified. The declines are the valuable part: they are the only record of what the person deliberately chose not to know.

## The scan contract

Before doing anything, a skill reads, in this order, and stops as soon as it has enough:

1. `INDEX.md`
2. `jobs/INDEX.md`
3. `claims/INDEX.md`
4. only then, specific detail files

Never load `raw/` wholesale. The single exception is `corp-os-rebuild`, whose entire purpose is a full re-derivation.

This is why every INDEX carries a one-line descriptor per entry rather than a bare link. A bare link forces a second read; a one-liner answers most questions outright. An entry that exists as a file but is missing from its INDEX is a broken contract, not a minor omission.

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

## Claim record

Claims live grouped by topic in `claims/<topic-slug>.md`, one block each:

```markdown
### CL-0042 — Acme flagged pricing as their top renewal concern
- **Statement**: Acme's economic buyer named per-seat pricing as the primary obstacle to renewing at current volume.
- **Kind**: fact          # fact | decision | theme | assumption | constraint | metric | preference
- **Jobs**: job-004
- **Confidence**: confirmed   # confirmed | needs_review | reconstructed | disputed | retired
- **Sensitivity**: internal   # public | internal | sensitive
- **Source**: raw/2026-09-02--granola--acme-qbr.md — Dana Chen (Acme), 2026-09-02
- **Citation**: "Honestly the seat math is the only thing my CFO is going to push back on."
- **Verified**: 2026-09-02 — heard first-hand on the call
- **Decay**: 90d              # re-verify after this long, or `none` for durable facts
- **Relations**: supersedes CL-0031
```

Field notes that matter:

- **Kind** separates what is observed from what is chosen from what is guessed. Conflating a `fact` with an `assumption` is the single most common way one of these systems starts lying to its owner.
- **Confidence** is about evidentiary standing, not importance. `confirmed` means verbatim or corroborated. `needs_review` means inferred, single-mention, or ambiguous. `reconstructed` means backfilled from a summary rather than a real source. `disputed` means live evidence points both ways — keep both sides visible rather than picking a winner. `retired` means no longer true; kept, not deleted, so the record of having believed it survives.
- **Decay** is what makes "refine data that has drifted from reality" mechanical instead of a vibe. A pricing claim rots in a quarter; a claim about a person's job title rots in a year; "our fiscal year starts in February" is `none`. `corp-os-reality-check` works this field.
- **Citation** is a verbatim excerpt, always. A paraphrase in the citation field defeats the purpose, because the next reader cannot tell how much of the claim is the source and how much is the summarizer.

Claim IDs are globally sequential (`CL-0001` up), never reused, tracked in `meta.json`. A rebuild never renumbers them — external references (dashboards, sent documents, prior briefs) depend on them holding still.

### When a citation does not exist

`no source` is a **sanctioned literal value** for the citation field. Use it when a claim traces to a summary, a migration, or someone's recollection with no retrievable original.

This exists because the alternative is worse in both directions: omitting the field makes an unsourced claim indistinguishable from a sourced one, and inventing a plausible-looking citation is the single most corrosive thing that can happen to a claims layer. A claim reading `Citation: no source` is honest and correctable. Nothing should ever be repaired by manufacturing a citation for it.

### Update blocks

A claim that develops does not always need to be superseded. When new evidence extends or qualifies a claim without contradicting it, append a dated update block inside the claim, carrying its own confidence and citation:

```markdown
- **Update (2026-08-25)**: the mitigation shipped and has early numbers —
  roughly two thirds of new arrivals now land in the cheaper tier. The
  underlying problem is not resolved; this is the response, not the fix.
  _(confirmed · raw/2026-08-25--monthly-review.md)_
```

Use an update block when the claim is still true and now known in more detail. Mint a new claim and retire the old one when the claim is no longer true. The distinction matters: a reader following a claim's update blocks can see how understanding developed, which a chain of superseded atomic claims makes almost unreadable.

### Conflicts get a diagnosis, not just a flag

Marking two claims `disputed` records that they disagree. It does not record *why*, and the why is usually what resolves it. Write the diagnosis into the conflict:

> Either two distinct initiatives share a name, or one source is stale. Not resolved here.

> Could be two different offers — a basic partnership versus a full connector-exchange tier — rather than a genuine contradiction. Needs a direct check rather than a guess.

A named hypothesis about the *shape* of a conflict is what lets someone resolve it in one question instead of re-deriving the confusion from scratch. A bare `disputed` pair gets skipped every time it is read.

### Identity claims

Any corpus with people in it accumulates identity ambiguity: two spellings of one name, one first name shared by four people, someone referred to by a role rather than a name, a person who "left" a project but not the company.

These get tracked as claims of kind `identity` and resolved deliberately, never merged on resemblance. Two rules:

- **Do not merge on similarity.** A fourth person appearing under a shared first name, now with a surname attached, is a new candidate — not confirmation that they are one of the three already on file. Record it as a candidate and say so. The pull toward tidying an ambiguity into a single entry is strong and almost always wrong.
- **When resolved, record the resolution and every place it propagated.** Not just "these two names are one person," but which files were corrected and whether the resolution changed anything else — an alias that turns out to describe someone leaving a *role* rather than the organization may also mean an entry was over-flagged as sensitive.

`people/<slug>.md` carries an `aliases` list for this. An unresolved identity question is a normal state and belongs on a job's evidence list.

### Corpus-level confidence ceilings

Per-claim confidence is not sufficient on its own. When a batch of material enters the OS from a source that is structurally weaker than verbatim — a migration from a previous system, a bulk import of AI-generated meeting summaries, a backfill from someone's memory — that whole cohort gets a **ceiling**, recorded once in `meta.json` and in the OS's README:

```json
"confidence_ceilings": [
  { "cohort": "2026-07-08 migration from prior system",
    "ceiling": "reconstructed",
    "raw_marker": "reconstructed: true in frontmatter",
    "count": 32,
    "note": "summaries, not verbatim source; cannot reach confirmed without new material" }
]
```

Without a ceiling, one careless pass promotes a whole cohort of summaries to `confirmed` and there is no way afterward to tell which claims were ever really sourced. Mark the cohort in the raw frontmatter too, so a rebuild rediscovers the ceiling rather than depending on the README being read.

### Sensitivity: quarantine, not just a flag

The `sensitivity` field marks an entry. That is not enough on its own, because a `sensitive` entry sitting inline in a topic file still gets loaded on every scan, still gets read over someone's shoulder, and still travels when that file is shared.

`sensitive.md` is a quarantine file, deliberately **outside the scan path** — `INDEX.md` does not link to it, and skills do not open it unless the task specifically requires it. Sensitive content is moved there, and a one-line pointer is left in the original file so continuity is not lost:

> Personnel context on this exists — see `sensitive.md`.

Captured, never suppressed. The point is that content nobody needs for the daily job stops being in the daily path, not that it disappears.

### Reclassification is logged, never silent

When something's confidence, sensitivity, or kind is changed on review, record the change and its reasoning as an entry — not as an edit.

An over-cautious `sensitive` flag downgraded to `internal` because the content turned out to be business signal rather than personnel signal is a **decision about the schema's application**, and the next person to look (including a future rebuild) needs to see that it was reviewed rather than assume it was never flagged. The same applies in reverse.

This is provenance for the classification, distinct from provenance for the content. Systems that skip it develop a slow, invisible drift in what their own labels mean.


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
- **Blind spots**: only captures calls I actually joined; nothing from Alex's own calls.
```

The **blind spots** field earns its keep. A connector registry that only lists what a source provides quietly implies full coverage. Writing down what each source cannot see is what stops the OS from mistaking silence for absence.

## Usage log

`usage/log.md` is an append-only table. Every skill in this plugin adds exactly one row per run, at the end of the run:

```markdown
| date | skill | jobs | asked for | outcome | friction |
|---|---|---|---|---|---|
| 2026-09-04 | corp-os-recall | job-004 | churn risk evidence for Acme | answered from 3 claims | 2 of 3 claims were past decay |
```

`friction` is the field `improve-corp-os` mines. Leave it blank when a run was clean; write the specific annoyance when it was not. "Had to ask the person which job this belonged to because nothing in the index made it obvious" is a useful row. "Went fine" is noise.

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

## Content agnosticism

Structure is configurable; content is never shipped. Nothing in this model assumes a domain. A job statement, a claim, a connector, and a decay window mean the same thing to a recruiter, a controller, a field engineer, and a product manager. The *vocabulary* a given OS uses comes from that person's `glossary.md` and their own job statements — never from a template shipped with this plugin. When a skill in this suite is tempted to suggest a category, it suggests the shape (`a job needs a definition of done`) and lets the person supply the content.
