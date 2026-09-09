# Corp-OS data model

The canonical spec — and a **default profile, not a schema.**

Every skill reads this file for the shapes, but reads the OS's own `config.json` for which of them apply. Layer names, label vocabularies, decay windows, retention and TTL policy, gate strictness, and any layer the model never imagined are all declared there; see `configuration.md`. Precedence is `config.json`, then the OS's own `README.md`, then this file.

What is *not* configurable is the short list this whole thing rests on: an append-only source layer, provenance on derived entries, a review gate in front of the derived layer, an index that can be scanned instead of loaded, and something that removes things. Everything else is a reasonable guess about a stranger's work, and guesses should be adjustable.

> **This file is the spine.** Two record specs live beside it so a skill reads only
> what it needs — `data-model.md` was one 6,900-word file that seventeen skills
> loaded in full, most of them for one section of it.
>
> - **`reference/claim-record.md`** — the claim: every field, what each one is for,
>   and the failures that shaped them.
> - **`reference/records.md`** — the job, decision, raw file, connector, usage log
>   and `meta.json` shapes.

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
├── sensitive.md            # quarantine for *incidental* sensitive material only
├── raw/
│   ├── README.md           # append-only convention + frontmatter shape
│   └── YYYY-MM-DD--<source>--<slug>.md
├── company/
│   ├── <company-slug>.md   # own employer, plus accounts / prospects / competitors
│   └── market.md
├── glossary.md
├── connectors.md           # what is connected, by what protocol, feeding what
├── design.md               # which design system governs rendered output
├── dashboards.md           # registry of published dashboards: name, URL, source files, cadence, owning job
├── scripts/
│   └── build_index.py      # deterministic recount — bookkeeping, not judgment
└── usage/
    ├── log.md              # what the OS was asked to do, and where it hurt
    └── proposals.md        # improvement backlog
```

Only `raw/`, `INDEX.md`, `meta.json`, `proposals/` and `usage/` are mandatory. **`jobs/` is not** — see below. Everything else gets created when the person actually wants it. An empty `glossary.md` nobody fills for six months is worse than not having one.

A layer that is not in this tree — `people/`, `topics/`, `experiments/`, `matters/` — is not thereby unavailable. It is declared in `config.json` with its own `entry_schema` and `index_line`, and every skill then treats it exactly like a shipped one. What no layer may do is exist without that declaration: see "No layer is enabled without a schema" in `configuration.md`.
## The two layers, and the gate between them

- **raw/** is the source of truth. Append-only. Never edited, never summarized in place, never deleted. Existing in raw/ does not make something true — only said.

  **One sanctioned exception:** the `processed` flag in a raw file's frontmatter gets flipped to `true` once the derived layer has drawn from it. That flag is bookkeeping *about* the file, not part of what was said, and it has to live on the file so that a rebuild reading `raw/` wholesale can tell what was already worked. Nothing else in a raw file — body, speaker, date, source, citationable content — is ever edited. Stated explicitly because "append-only" and "flip `processed: true`" both appear in this suite, and an instruction that looks like it contradicts an invariant is one a future session will resolve in whichever direction it happens to read first.
- **Everything else** is the derived layer. Fully regenerable from raw/ (that is what `corp-os-rebuild` does). Nothing lands here without a human confirming it.

Skills may write to `raw/`, `INDEX.md`, `meta.json`, and `usage/log.md` autonomously. Skills must **propose, not write** anything entering `claims/`, `jobs/`, `glossary.md`, `company/`, or any declared layer whose role is `derived`.

The gate is not there because any single entry is risky. It is there because without it the derived layer stops being knowledge and becomes just a second, messier copy of raw/.

### The same rules, stated outward

Those three sentences are also the contract for **a skill set built by someone else on top of this one** — a team's own plugin that operates on a Corp-OS. It is written here rather than assumed, because the internal version is enforced by this repo's validator running over this repo's skills, and a companion has nothing checking it.

- **Append to `raw/`, never edit it.** The one sanctioned exception is `processed`, and it is not a companion's to flip unless the companion is what did the processing.
- **Propose into any layer whose role is `derived`; never write.** Whatever the companion's own gate looks like, entries arriving in the derived layer went past a person or the invariant is gone.
- **Own your own `record` layers outright.** A companion that needs a place to keep what it produces declares a layer with its own `entry_schema` and `index_line`, and writes there freely. That is the extension point, and it is the whole reason layer roles are explicit.
- **Do not take the `corp-os-` prefix.** It is what makes this suite guessable, and one exception costs that for every skill in it.

A companion that keeps to those four can be installed alongside without the audit having to ask what it has been doing. One that cannot should say so in its own description, because the failure it produces — a derived layer nobody confirmed — is indistinguishable afterward from a corpus that was curated properly.

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
## Content agnosticism

Structure is configurable; content is never shipped. Nothing in this model assumes a domain. A job statement, a claim, a connector, and a decay window mean the same thing to a recruiter, a controller, a field engineer, and a product manager. The *vocabulary* a given OS uses comes from that person's `glossary.md` and their own job statements — never from a template shipped with this plugin. When a skill in this suite is tempted to suggest a category, it suggests the shape (`a job needs a definition of done`) and lets the person supply the content.
