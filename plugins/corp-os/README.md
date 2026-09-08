# Corp-OS

A portable, configurable personal work OS.

Most personal knowledge systems are organized by subject: a folder per topic, a note per person. They only ever grow, nothing in them ever expires, and after a few months nobody trusts them enough to look. Corp-OS is a folder of markdown files plus twenty-one skills that operate on it, and its shape is declared rather than assumed — layer names, label vocabulary, decay windows, retention and gate strictness all live in a `config.json` that every skill reads first.

Its default organizing primitive is the **job** — the concrete outcome someone is trying to reach — with subjects hanging off jobs. That default is worth understanding before adopting it, and worth turning off when it does not fit; see "It is a default profile, not a schema" below.

Job-organization buys three things a subject-organized system cannot have:

- **Intake gets a priority signal.** A job declares what it still needs to know, which turns "capture everything" into "capture what is blocking this."
- **Recall gets a relevance signal.** "What do we know about pricing" is unanswerable in the abstract. "What do we know about pricing that bears on this renewal" has a real answer.
- **Pruning gets a stopping rule.** When a job retires, everything that existed only to serve it can retire with it.

## It is a default profile, not a schema

The shipped shape is a reasonable guess about a stranger's work, and guesses should be adjustable. `config.json` at the OS root declares everything: which layers exist, what they are called, the label vocabularies, decay windows per kind and per tag, how long source material is kept, and how strict the review gate is. A layer Corp-OS never imagined — `experiments/`, `matters/`, `properties/`, `readouts/` — is declared with its own field schema and its own one-line index template, and every skill then treats it like a shipped one.

Five properties are not configurable, because they are what the whole thing rests on: an **append-only source layer**, **provenance** on derived entries, a **review gate** in front of the derived layer, an **index that can be scanned** rather than loaded, and **something that removes things**. Everything else is yours — **including the jobs layer itself.**

That last point is worth stating plainly rather than burying. Job-organization is this model's default and its best idea, and it is wrong for some people. It pays off for a decision-heavy operator with a handful of recurring forks, where the same question gets re-asked and the same evidence re-gathered. It costs more than it returns when the work is mostly reference accumulation, or organized around long-lived subject areas that genuinely do not change. There is an empirical test for which case you are in — cluster your existing material into candidate jobs without looking at your subject taxonomy, then compare; if the clusters reproduce the taxonomy you already have, your material is subject-shaped and a jobs layer would duplicate something that already works. `corp-os-audit` and `corp-os-jobs` both run it and will tell you to leave jobs off if that is the answer.

Call claims "findings" if that is the right word in your field. Turn decay off for a three-month project. Set a TTL on raw material if a retention schedule requires it — though `archive` is what most people asking for that actually want, and it costs nothing.

## What it actually is

Two layers, deliberately separated:

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
| `corp-os-decide` | Track the forks you have not decided yet — owner, date, what they block |
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
| `corp-os-improve` | Mine your usage log for friction and unused structure; propose evidence-backed changes; export an anonymized improvement packet |
| `corp-os-audit` | Assess any knowledge system across ten dimensions, propose what to build next, and find what *it* has that Corp-OS lacks |
| `corp-os-upgrade` | Bring an OS in line with a newer plugin version — refresh its script copies, stamp the version, name the migrations |
| `corp-os-contribute` | Turn something already diagnosed into an apply-ready diff against the plugin's own source |

## Start here

Run `/corp-os` — it finds your OS, or offers to build one.

| | |
|---|---|
| `/corp-os` | Find your OS and say what is worth doing next |
| `/corp-os-capture` | File something — a transcript, a thread, a note |
| `/corp-os-recall` | Ask a question, or fold what it knows into what you are writing |
| `/corp-os-brief` | What moved, what needs a decision, what went stale |
| `/corp-os-catchup` | Pull what is new from your connected sources |
| `/corp-os-open` | The decisions you have open, worst date first |
| `/corp-os-check` | Sweep for stale, contradicted, and never-verified |
| `/corp-os-share` | Make something safe to send, with a private record of what came out |

Named for the moment rather than the skill: reaching for the export boundary, you are thinking "share this", not "redact". Everything else — setup, configure, rebuild, audit, improve — you ask for by name, because those are rare and deliberate and a command for every skill is surface area with no return.

Or just ask for Corp-OS setup. The interrogation takes fifteen to twenty minutes and covers your role and mandate, why you want this, your jobs to be done, which data actually earns its keep, how information reaches you, which tools you can connect and how, your company and market, your design and output needs, and your sensitivity boundaries.

The interrogation is the deliverable as much as the folder is. A scaffold built without it produces a generic notebook that gets abandoned in a month.

## Design principles

**The model argues against itself where the evidence says so.** `corp-os-audit` refuses to score outcome-orientation from the absence of a jobs layer without running the clustering test, and refuses to recommend decay without first checking whether entries can be re-verified at all. A model that only ever confirms itself is not measuring anything.

**Configurable by default.** The structure is declared, not assumed, and changing it is a supported operation rather than a hack. Layer roles (`source`, `derived`, `record`) are explicit, so a rebuild can never overwrite a folder you maintain by hand.

**Content agnostic.** No role templates, no domain vocabulary, no starter taxonomy. A job statement, a claim, a decay window, and a connector mean the same thing to a recruiter, a controller, a field engineer, and a product manager. Your vocabulary comes from your own glossary and your own job statements.

**Portable across companies and roles.** Sources are registered by category, not product. Change jobs, change stack, keep the OS.

**The review gate is load-bearing.** Skills write to `raw/` and the indexes autonomously. Everything entering the derived layer is proposed and waits for you. Not because any one entry is risky — because without the gate the derived layer stops being knowledge and becomes a second, messier copy of `raw/`.

**Nothing is deleted.** Retired, superseded, disputed — but kept. The record of having believed something is frequently the most useful thing in the file. `no source` is a legitimate citation value; a fabricated citation never is.

**Bookkeeping is separate from judgment.** `scripts/build_index.py` recounts what is on disk and rewrites the index. It reads nothing from `raw/` and retags nothing, which is what makes it safe to run after any manual edit — and makes "the index is stale" a thirty-second fix rather than a reason to schedule a rebuild.

**The OS improves from evidence, not opinion.** Every skill logs one line of friction per run. `corp-os-improve` reads those lines and proposes changes with counts attached. Structure that nobody uses gets retired; the same manual step appearing every run becomes a field.

## Extending it

Bind a design system by naming it in the OS's `design.md`, and every rendered output follows it.

The model itself is specified in `reference/data-model.md`. Improvement packets from `corp-os-improve` and `corp-os-audit` are the intended path for changing it — anonymized, evidence-backed, and applied deliberately rather than automatically.

## Reference

| File | Contents |
|---|---|
| `reference/data-model.md` | The canonical spec: structure, schemas, the scan contract |
| `reference/scheduling.md` | Which scheduler to use for a recurring run, and why the wrong one fails silently |
| `reference/configuration.md` | Everything adjustable: vocabulary, layers, custom layers, decay, retention/TTL, gate |
| `reference/interrogation.md` | The nine-area setup question bank |
| `reference/jtbd-patterns.md` | Job statement forms, malformed shapes and their repairs |
| `reference/dashboard-patterns.md` | Which views are worth building, and what makes them go stale |
| `reference/company-research.md` | What to establish about a company, and how to source it |
| `reference/improvement-packet.md` | The interchange format for improving the model |
| `reference/os-audit-rubric.md` | The ten audit dimensions |
| `CONNECTORS.md` | How tool categories work |
| `scripts/build_index.py` | Deterministic recount and drift check |
| `scripts/write_export.py` | Redaction's two outputs, written together — refuses one without the other |
| `scripts/log_run.py` | The usage-log row and the history entry, written together |
| `scripts/delete_source.py` | The five-step retention deletion — dry-run by default, refuses without an obligation |
| `scripts/upgrade_os.py` | Refreshes the script copies an OS carries, stamps the version, names the migrations it will not perform |
| `examples/fixture-os/` | A synthetic OS the build actually runs `build_index.py` against |
| `commands/` | Eight slash commands over the daily path — see below |
| `evals/` | Two harnesses — does the right skill get reached, and does it do what it says |

## Version history

**0.11.1** — the skill map ships with the repo, at `docs/skill-map.html`: every skill, what it does, what it refuses, and which of the five phases it belongs to, with the commands and scripts underneath. It is **generated**, not written. A page stating how many skills exist and what each one does is a set of facts already true elsewhere, and this project has now caught that same defect four times — "both shipped scripts" three releases after there were four, a hard-coded version stale within one release, `corpos_version` in six files with six values, and a registry that counted 1 for five releases. A hand-kept map would have been the fifth. Descriptions come from the frontmatter that already holds them, counts are `len()`, the invariants are parsed from the README so the page says five because it counted, and the eval figures are read from the committed run reports rather than typed in. The one thing declared by hand is which phase a skill belongs to, because nothing can derive that — and the generator refuses to run until a new skill has been placed, which is the only part a person is needed for.

**0.11.0** — updating the plugin never updated anyone's OS. Every Corp-OS carries its own copies of the shipped scripts, because an OS should keep working when the plugin is not loaded and because sixteen skills call them at the OS path. The cost was invisible until 0.10.1 fixed how `build_index.py` counts a single-file layer: every OS built before it kept the copy that counts wrong, and nothing anywhere would have said so. `upgrade_os.py` is the fifth shipped script — it compares each script by content rather than by date (a copy restored from a backup has a new date and old behavior), refreshes what drifted, and records the version the OS is now on. `corp-os-upgrade` runs it and does the part a script should not: it names the structural migrations the version gap implies and hands them to `corp-os-configure`, which enumerates and asks before moving anyone's files. The split is the point. Moving a registry file is one `mv`, which is exactly why a script that was allowed to do it would.

Two smaller things, both the same defect as the one being fixed. `scaffold.py` hard-coded the version string it stamped into every OS and it went stale within one release; it reads `plugin.json` now. And `corp-os-setup` carried a prose list of the scripts to copy, which said two for three releases after there were four — the list is gone rather than corrected, since `scaffold.py` already does the copying, and a validator check now keeps the two remaining copies of that list in step. A third fixture, `fixture-stale`, is an OS two releases behind, and the validator asserts it is still broken: repair it and the upgrade case passes against an OS with nothing to upgrade, which reads as coverage and is not.

Found while testing that upgrade path: **no shipped script had ever executed in a conformance run.** The harness ran with `acceptEdits`, which auto-approves file edits and nothing else, so every `python3 scripts/...` in every skill was answered with `This command requires approval`. The file-level results were real; what was never measured is what produced them, because a model told to run a script and blocked from doing so writes the row by hand. It cost the suite six runs and three instruction passes chasing a `corp-os-setup` failure that was the harness the whole time — with the fix, that case goes from 3/10 to 9/9 and the upgrade case from 5/10 to 10/10. Every other conformance figure in the record is now provisional until re-run.

One more gap, found in the same pass: `corp-os-improve`'s packet assumes a stranger maintains the plugin, which is the wrong assumption the moment the person running it is that maintainer. `corp-os-contribute` is the twenty-first skill — it starts from something `corp-os-improve` or `corp-os-audit` already diagnosed, applies a lower bar (one fully-traced mechanism is enough; frequency is what the local-improvement pass gates on, not this), and writes literal before/after diffs against the plugin's actual current files rather than an anonymized note. It never edits the plugin itself — the deliverable is a portable document, and applying it stays a separate, deliberate act wherever the plugin source actually lives. `corp-os-improve` Step 7 now asks which audience it is writing for and hands off rather than assuming.

**0.10.1** — the first defect found by using it rather than testing it. The dashboards registry shipped at `dashboards/registry.md`: a directory-shaped path over a single file of many entries, which `build_index.py` counts by file. With one dashboard registered both readings say 1, so it was invisible for five releases and surfaced only on the second. It now lives at `dashboards.md`, beside `glossary.md`, `connectors.md` and `design.md` — the bug existed because dashboards broke a convention the other three kept. Dashboards are counted by default too; the layer nobody counted is the layer nobody noticed was wrong. `build_index.py` also warns generically now when a declared directory path holds one file with many entry headers, because `corp-os-configure` walks people through declaring custom layers with their own paths and the class recurs where no layout fix reaches. A home/index dashboard joins the patterns as the eighth, gated on a second dashboard already existing. `corp-os-intake` and `corp-os-dashboard` now hand off to `corp-os-configure` when material implies a layer that has not been declared — a hand-off that lands 2 times in 5 and is on the record at that number rather than reworded a fourth time.

**0.10.0** — `delete_source.py`, the fourth shipped script and the third confirmation of the same rule: the retention-delete sequence held at 67% after two instruction passes, the second saying *never edit the original into a tombstone* in as many words, and one run in three still did. With the script, 8/8 at 100%. It was the last path in the suite whose failure destroyed source material rather than degrading quality. Eight slash commands now cover the daily path, named for the moment rather than the skill — and `evals/run_commands.py` makes them iterable: a full sweep in about a minute, against half an hour for conformance, which is the difference between a loop you stay inside and one you leave. That harness settled an open question with data rather than argument — seven cases give a person plain English and nothing but eight one-line descriptions to choose between, and they land at 100%. Eight commands are distinguishable. `validate.py` also lints the static half of a command: description length, no two opening alike, a real skill named, `$ARGUMENTS` handled, and the no-args path stated rather than left to chance.

**0.9.0** — Two more shipped scripts, both added because measurement demanded them. `write_export.py`: across five conformance runs `corp-os-redact` produced its private log under four different names and once not at all, while the instruction to write it was present, concrete, explained, and strengthened twice. Past a certain point more instruction stops buying reliability, so the step left the model's hands — the script writes the cleaned copy and the log together and refuses to write one without the other. `log_run.py` followed for the same reason from a different direction — `corp-os-brief` wrote its `meta.json` history entry in one run out of three — and now writes the log row and the history entry together for sixteen skills. The rule these establish, alongside `build_index.py`: a step that has to happen every time, that nothing else will catch if it is skipped, belongs in code. None of the three exercises judgment; that stays with the skill. Sensitivity also split into two axes, because one flag was making the OS quietly wrong. `sensitivity` is the export class — what must not leave, and to whom. `bearing` is whether the OS can reason correctly without it, and it is `bearing` that decides where an entry lives. Quarantining everything sensitive assumed sensitive material is never needed for the daily job; when that is false, the quarantine does not produce a gap, it produces a confidently wrong answer with nothing in it to signal the omission. So load-bearing sensitive material now stays in the scan path, marked, and is stripped at the export boundary by `corp-os-redact` — which is the only place confidentiality was ever really enforced. One operator is settled as the intended shape rather than a limitation: sharing is an export event, not a mode. Alongside that, a second fixture (`fixture-register`: jobs off, renamed vocabulary, a hand-maintained `source` layer planted as a rebuild trap) and conformance cases for the irreversible paths — rebuild refusing a non-`derived` layer, the retention-delete sequence, redaction never touching the original. Building the second fixture immediately caught the index rendering the plugin's vocabulary instead of the person's, and a retention-delete run invented the tombstone that is now in the spec.

**0.8.0** — The skills got run. `evals/run_conformance.py` puts one skill in front of a throwaway copy of the fixture OS and then reads the filesystem to see what it actually did — which found, in its first run, three things no amount of reading had: `corp-os-intake` writing the raw file, recounting `meta.json`, filing the proposal, appending the log row, and leaving out the index entry, four runs out of four; `corp-os-brief` skipping the dated history entry that is the only write a brief makes; and a four-release-old contradiction where `data-model.md` said raw files are never edited while three skills instructed flipping `processed: true` on them. All fixed, and `processed` is now named as the one sanctioned exception with the reason attached. It also answered a question open since 0.2.0 — the usage-log row does get written, in every case. Two of the harness's own assertions turned out to be wrong about the skills and were corrected on the record rather than quietly, because an eval that has never been wrong about what it measures has not been looked at hard enough. On the routing side, a third iteration added the categories a 100% score should make anyone suspicious of — renamed vocabulary, no Corp-OS words at all, mid-conversation fragments, two-skill sequences — and scored 100% across all of them, which is the evidence for saying plainly that routing is not this suite's risk and putting eval effort where the defects actually are.

**0.7.0** — Built out the things the 0.6.0 audit said were missing rather than wrong. `corp-os-decide` is the nineteenth skill and the one the model had been working around: a `decision` claim records a call that was made, and nothing held the ones that had not been. An open decision does not rot by going stale the way a claim does — it rots by going quiet — so the record requires an owner (a person, never a team) and a `decide_by` date, past which the choice is being made by default and the log says which option is winning by inaction. `examples/fixture-os/` is a synthetic OS that `validate.py` now *executes* `build_index.py` against, asserting the rendered index and its idempotence; parsing the script only ever proved it imports, which was never the failure mode. Building it immediately caught a silent config fallback, now a warning. `reference/scheduling.md` names the mechanism the five scheduling skills were vague about — the failure there is silent, and a brief that never fires looks exactly like a brief that fired and found nothing. Four slash commands cover the daily path. And `evals/` holds a routing harness that measures which of the nineteen skills a real query actually reaches, which is the question eighteen similar descriptions raise and nobody had answered.

**0.6.0** — A conformance pass: the shipped files now obey the rules the architecture said were cross-cutting, and the validator enforces them so they cannot drift again. Root detection no longer tests for `jobs/` — an OS running with the jobs layer disabled was reading as no OS at all, which pointed its owner at a re-scaffold of a working system, the only data-destroying path in the suite. The pre-flight and config-first rules moved from six scattered skills into a single identical block in all eighteen, with `corp-os-audit` carrying the variant that fits auditing someone else's system. `people/` and `topics/` left the default scaffold under a new rule — **no layer is enabled without a declared `entry_schema` and `index_line`** — because both were being created, indexed and read while nothing specified what one entry contains; the `relationship` profile now carries a full `people` declaration for anyone who wants it. `improve-corp-os` became `corp-os-improve`, so all eighteen share the prefix that makes the suite guessable. The private-identifier denylist moved out of `validate.py` into an untracked file, since a hardcoded list of real names in a public repo publishes exactly what it was written to protect.

**0.4.0** — Made the jobs layer genuinely optional and added the empirical test for whether it fits: cluster existing material into candidate jobs without looking at the subject taxonomy, and if the clusters reproduce it, the material is subject-shaped and jobs is overhead. Added the grammatical-form diagnostic that catches an open-items layer drifting into a status register (findings and errands crowding out real questions), plus checks for misfiled entries in a resolved tier and for a recurring attribute nothing groups. Added `decay.applies_to` — decay assumes re-verification is possible, so on a corpus where a large share has no retrievable source, applying it to everything produces a backlog nobody can clear; the default now scopes to sourced entries with a one-time disposition pass for the rest. `corp-os-audit` gained a tenth dimension (adjustability, including whether it is safe to regenerate), a step that proposes new skills and workflow changes rather than only scoring, and explicit instructions to resist finding what the model predicts.

**0.3.0** — Made the model configurable. Added `config.json` as the authority every skill reads first; custom layers with their own field schemas and index-line templates; explicit layer roles (`source` / `derived` / `record`) so a rebuild can never overwrite hand-maintained material; renameable vocabulary; per-kind and per-tag decay; retention policy on raw material with four options, where `delete` is handled as a claim-integrity event rather than file management; three gate modes; five structural starter profiles; and the new `corp-os-configure` skill. `build_index.py` became config-driven and now flags layers missing an index template and directories missing from config.

**0.2.0** — Folded in structures learned from auditing a mature real-world knowledge system built independently of this model (~215 sources accumulated over four months). Added: persisted proposal files so the review gate leaves an audit trail; `sensitive.md` quarantine outside the scan path; the five-state answer-status ladder on evidence items; `no source` as a sanctioned citation value; cohort-level confidence ceilings for migrations and bulk imports; dated update blocks on claims; diagnoses attached to conflicts rather than bare `disputed` flags; identity claims for entity ambiguity; reclassification logged as a decision; the pre-flight and files-beat-memory rules; an explicit graduation bar for a top tier; and `scripts/build_index.py`.

**0.1.0** — Initial suite: 17 skills, jobs-to-be-done as the organizing primitive, claims with decay windows.
