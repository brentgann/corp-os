# Corp-OS

A portable personal work OS, organized around jobs to be done.

Most personal knowledge systems are organized by subject: a folder per topic, a note per person. They only ever grow, nothing in them ever expires, and after a few months nobody trusts them enough to look. Corp-OS inverts the organizing principle. The primitive is the **job** — the concrete outcome someone is trying to reach — and subjects hang off jobs.

That inversion buys three things a subject-organized system cannot have:

- **Intake gets a priority signal.** A job declares what it still needs to know, which turns "capture everything" into "capture what is blocking this."
- **Recall gets a relevance signal.** "What do we know about pricing" is unanswerable in the abstract. "What do we know about pricing that bears on this renewal" has a real answer.
- **Pruning gets a stopping rule.** When a job retires, everything that existed only to serve it can retire with it.

## It is a default profile, not a schema

The shipped shape is a reasonable guess about a stranger's work, and guesses should be adjustable. `config.json` at the OS root declares everything: which layers exist, what they are called, the label vocabularies, decay windows per kind and per tag, how long source material is kept, and how strict the review gate is. A layer Corp-OS never imagined — `experiments/`, `matters/`, `properties/`, `readouts/` — is declared with its own field schema and its own one-line index template, and every skill then treats it like a shipped one.

Five properties are not configurable, because they are what the whole thing rests on: an **append-only source layer**, **provenance** on derived entries, a **review gate** in front of the derived layer, an **index that can be scanned** rather than loaded, and **something that removes things**. Everything else is yours — **including the jobs layer itself.**

That last point is worth stating plainly rather than burying. Job-organization is this model's default and its best idea, and it is wrong for some people. It pays off for a decision-heavy operator with a handful of recurring forks, where the same question gets re-asked and the same evidence re-gathered. It costs more than it returns when the work is mostly reference accumulation, or organized around long-lived subject areas that genuinely do not change. There is an empirical test for which case you are in — cluster your existing material into candidate jobs without looking at your subject taxonomy, then compare; if the clusters reproduce the taxonomy you already have, your material is subject-shaped and a jobs layer would duplicate something that already works. `corp-os-audit` and `corp-os-jobs` both run it and will tell you to leave jobs off if that is the answer.

Call claims "findings" if that is the right word in your field. Turn decay off for a three-month project. Set a TTL on raw material if a retention schedule requires it — though `archive` is what most people asking for that actually want, and it costs nothing.

## What it actually is

A folder of markdown files plus eighteen skills that operate on it. Two layers, deliberately separated:

- **`raw/`** — append-only source archive. Transcripts, threads, documents, notes. Never edited, never deleted. Existing here means *said*, not *true*.
- **the derived layer** — jobs, claims, people, topics, glossary, company records. Fully regenerable from `raw/`. Nothing lands here without a person confirming it, and every proposal is written to `proposals/` before it is presented, so the gate leaves a record rather than a chat exchange.

Alongside both sits `sensitive.md`, a quarantine file deliberately outside the scan path. A sensitivity *flag* is not enough on its own — a flagged entry sitting inline still loads on every scan and still travels when that file gets shared. Content nobody needs for the daily job stops being in the daily path. Captured, never suppressed.

The unit of knowledge is a **claim**: one short statement carrying its kind (fact, decision, theme, assumption, constraint, metric, preference), a confidence level, a verbatim citation with speaker and date, the jobs it serves, and a **decay window** saying when it needs re-checking.

That last field is what makes drift correctable on a schedule instead of by accident. A pricing claim rots in a quarter; a claim about someone's role rots in a year; "our fiscal year starts in February" never does. Without decay, a knowledge base ages into confident fiction and nobody notices, because each individual entry still looks reasonable.

## The skills

**Get started**

| Skill | What it does |
|---|---|
| `corp-os-guide` | Explains the system and routes to the right skill |
| `corp-os-setup` | Interrogates you across nine areas, then scaffolds an OS shaped to the answers |
| `corp-os-configure` | Reshape it later — rename vocabulary, add a custom layer, set decay or retention, tune the gate |

**Define the work**

| Skill | What it does |
|---|---|
| `corp-os-jobs` | Add, sharpen, split, or retire jobs; keep evidence lists current |
| `corp-os-connect` | Register a source: protocol, cadence, what it feeds, what it is blind to |

**Get information in**

| Skill | What it does |
|---|---|
| `corp-os-pull` | Retrieve what is new from registered sources, with dedupe |
| `corp-os-intake` | File a pasted transcript, thread, document, or note |

**Build knowledge**

| Skill | What it does |
|---|---|
| `corp-os-claims` | Turn raw material into reviewed, citable claims |
| `corp-os-reality-check` | Sweep for stale, unverified, contradicted, and untested-assumption claims — then interrogate to resolve them |
| `corp-os-glossary` | Internal jargon, acronyms, and especially metric definitions |
| `corp-os-company` | Research employers, counterparties, and competitors from the web plus what you already know |

**Get value out**

| Skill | What it does |
|---|---|
| `corp-os-recall` | Answer with citations, and enrich whatever you are working on |
| `corp-os-dashboard` | Publish views of what the OS actually holds |
| `corp-os-brief` | The recurring operating brief; schedulable |

**Keep it honest**

| Skill | What it does |
|---|---|
| `corp-os-rebuild` | Re-derive the whole derived layer from `raw/` |
| `corp-os-redact` | Make something safe to share, with a private log of every removal |

**Improve the model**

| Skill | What it does |
|---|---|
| `improve-corp-os` | Mine your usage log for friction and unused structure; propose evidence-backed changes; export an anonymized improvement packet |
| `corp-os-audit` | Assess any knowledge system across ten dimensions, propose what to build next, and find what *it* has that Corp-OS lacks |

## Start here

Ask for Corp-OS setup. The interrogation takes fifteen to twenty minutes and covers your role and mandate, why you want this, your jobs to be done, which data actually earns its keep, how information reaches you, which tools you can connect and how, your company and market, your design and output needs, and your sensitivity boundaries.

The interrogation is the deliverable as much as the folder is. A scaffold built without it produces a generic notebook that gets abandoned in a month.

## Design principles

**The model argues against itself where the evidence says so.** `corp-os-audit` refuses to score outcome-orientation from the absence of a jobs layer without running the clustering test, and refuses to recommend decay without first checking whether entries can be re-verified at all. A model that only ever confirms itself is not measuring anything.

**Configurable by default.** The structure is declared, not assumed, and changing it is a supported operation rather than a hack. Layer roles (`source`, `derived`, `record`) are explicit, so a rebuild can never overwrite a folder you maintain by hand.

**Content agnostic.** No role templates, no domain vocabulary, no starter taxonomy. A job statement, a claim, a decay window, and a connector mean the same thing to a recruiter, a controller, a field engineer, and a product manager. Your vocabulary comes from your own glossary and your own job statements.

**Portable across companies and roles.** Sources are registered by category, not product. Change jobs, change stack, keep the OS.

**The review gate is load-bearing.** Skills write to `raw/` and the indexes autonomously. Everything entering the derived layer is proposed and waits for you. Not because any one entry is risky — because without the gate the derived layer stops being knowledge and becomes a second, messier copy of `raw/`.

**Nothing is deleted.** Retired, superseded, disputed — but kept. The record of having believed something is frequently the most useful thing in the file. `no source` is a legitimate citation value; a fabricated citation never is.

**Bookkeeping is separate from judgment.** `scripts/build_index.py` recounts what is on disk and rewrites the index. It reads nothing from `raw/` and retags nothing, which is what makes it safe to run after any manual edit — and makes "the index is stale" a thirty-second fix rather than a reason to schedule a rebuild.

**The OS improves from evidence, not opinion.** Every skill logs one line of friction per run. `improve-corp-os` reads those lines and proposes changes with counts attached. Structure that nobody uses gets retired; the same manual step appearing every run becomes a field.

## Extending it

Bind a design system by naming it in the OS's `design.md`, and every rendered output follows it.

The model itself is specified in `reference/data-model.md`. Improvement packets from `improve-corp-os` and `corp-os-audit` are the intended path for changing it — anonymized, evidence-backed, and applied deliberately rather than automatically.

## Reference

| File | Contents |
|---|---|
| `reference/data-model.md` | The canonical spec: structure, schemas, the scan contract |
| `reference/configuration.md` | Everything adjustable: vocabulary, layers, custom layers, decay, retention/TTL, gate |
| `reference/interrogation.md` | The nine-area setup question bank |
| `reference/jtbd-patterns.md` | Job statement forms, malformed shapes and their repairs |
| `reference/dashboard-patterns.md` | Which views are worth building, and what makes them go stale |
| `reference/company-research.md` | What to establish about a company, and how to source it |
| `reference/improvement-packet.md` | The interchange format for improving the model |
| `reference/os-audit-rubric.md` | The nine audit dimensions |
| `CONNECTORS.md` | How tool categories work |
| `scripts/build_index.py` | Deterministic recount and drift check |

## Version history

**0.4.0** — Made the jobs layer genuinely optional and added the empirical test for whether it fits: cluster existing material into candidate jobs without looking at the subject taxonomy, and if the clusters reproduce it, the material is subject-shaped and jobs is overhead. Added the grammatical-form diagnostic that catches an open-items layer drifting into a status register (findings and errands crowding out real questions), plus checks for misfiled entries in a resolved tier and for a recurring attribute nothing groups. Added `decay.applies_to` — decay assumes re-verification is possible, so on a corpus where a large share has no retrievable source, applying it to everything produces a backlog nobody can clear; the default now scopes to sourced entries with a one-time disposition pass for the rest. `corp-os-audit` gained a tenth dimension (adjustability, including whether it is safe to regenerate), a step that proposes new skills and workflow changes rather than only scoring, and explicit instructions to resist finding what the model predicts.

**0.3.0** — Made the model configurable. Added `config.json` as the authority every skill reads first; custom layers with their own field schemas and index-line templates; explicit layer roles (`source` / `derived` / `record`) so a rebuild can never overwrite hand-maintained material; renameable vocabulary; per-kind and per-tag decay; retention policy on raw material with four options, where `delete` is handled as a claim-integrity event rather than file management; three gate modes; five structural starter profiles; and the new `corp-os-configure` skill. `build_index.py` became config-driven and now flags layers missing an index template and directories missing from config.

**0.2.0** — Folded in structures learned from auditing a mature real-world knowledge system built independently of this model (~215 sources accumulated over four months). Added: persisted proposal files so the review gate leaves an audit trail; `sensitive.md` quarantine outside the scan path; the five-state answer-status ladder on evidence items; `no source` as a sanctioned citation value; cohort-level confidence ceilings for migrations and bulk imports; dated update blocks on claims; diagnoses attached to conflicts rather than bare `disputed` flags; identity claims for entity ambiguity; reclassification logged as a decision; the pre-flight and files-beat-memory rules; an explicit graduation bar for a top tier; and `scripts/build_index.py`.

**0.1.0** — Initial suite: 17 skills, jobs-to-be-done as the organizing primitive, claims with decay windows.
