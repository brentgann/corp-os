# Corp-OS

A portable, configurable personal work OS.

Most personal knowledge systems are organized by subject: a folder per topic, a note per person. They only ever grow, nothing in them ever expires, and after a few months nobody trusts them enough to look. Corp-OS is a folder of markdown files plus twenty-three skills that operate on it, and its shape is declared rather than assumed — layer names, label vocabulary, decay windows, retention and gate strictness all live in a `config.json` that every skill reads first.

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
| `corp-os-migrate` | Bring an existing body of work across — cohort ceiling, original dates, staggered decay, a record of what was left behind |

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
| `corp-os-pattern` | Turn an output you built into a portable spec, or adopt a teammate's pack, so five people's dashboards stop being five dashboards |

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

## Installing, and the two things called "update"

```
/plugin marketplace add brentgann/corp-os
/plugin install corp-os@brentgann
```

Then ask for Corp-OS setup. In the desktop app, use the plugin browser rather than the slash command.

Updating has two halves and doing the first does nothing to the second:

```
/plugin marketplace update brentgann     # replaces the skills
ask for corp-os-upgrade                  # brings your OS in line with them
```

Every Corp-OS carries its own copies of the shipped scripts, so that it keeps working when the plugin is not loaded and because sixteen skills call them at the OS path. That is why updating the plugin has never updated anyone's OS, and why `corp-os-upgrade` exists: it refreshes those copies by comparing content rather than dates, records the version, and names the structural migrations it deliberately refuses to perform.

One thing that surprises people, including maintainers: the client caches an installed plugin **by version string**. New commits without a bump in `plugin.json` reach nobody, with no error and no way to tell from the inside. Full detail, including the release procedure, is in the repository's `docs/INSTALL.md`.

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
| `reference/patterns.md` | The pattern shape, the binding contract, the screen-share shield, and the composition rules every rendering pattern inherits |
| `reference/company-research.md` | What to establish about a company, and how to source it |
| `reference/improvement-packet.md` | The interchange format for improving the model |
| `reference/os-audit-rubric.md` | The ten audit dimensions |
| `CONNECTORS.md` | How tool categories work |
| `scripts/build_index.py` | Deterministic recount and drift check |
| `scripts/write_export.py` | Redaction's two outputs, written together — refuses one without the other |
| `scripts/log_run.py` | The usage-log row and the history entry, written together |
| `scripts/delete_source.py` | The five-step retention deletion — dry-run by default, refuses without an obligation |
| `scripts/migrate_schema.py` | Adds a schema field, filling only what can be derived and counting what cannot |
| `scripts/bind_pattern.py` | Resolves a pattern's requirements against an OS, or names exactly what is missing |
| `scripts/check_shield.py` | The JS-off leak test: proves a screen-share shield is real rather than decorative |
| `scripts/check_citations.py` | Clusters entries by citation; refuses an export whose members disagree on sensitivity |
| `scripts/stagger_decay.py` | Spreads a migrated corpus's decay windows so the first sweep is clearable |
| `scripts/upgrade_os.py` | Refreshes the script copies an OS carries, stamps the version, names the migrations it will not perform |
| `scripts/scaffold.py` | Builds an OS from the interrogation's answers, and copies the nine scripts an OS carries |
| `examples/fixture-os/` | A synthetic OS the build actually runs `build_index.py` against |
| `commands/` | Eight slash commands over the daily path — see below |
| `evals/` | Three harnesses — do the commands read distinctly, does the right skill get reached, and does it do what it says |

## Version history

**0.18.1** — three defects the cost work introduced, found by asking whether any of it reduced quality. Two were mine and one was silent.

**A capped or triaged pull was losing material permanently.** Step 4 advanced the source cutoff unconditionally, written long before triage existed. So an item skipped by triage, and an item the batch cap never reached, both fell behind the cutoff and were never offered again — while 0.17's own release note said *"skipping is deferring, not losing."* That was false the moment it shipped.

The cutoff now moves differently for the two cases, because they are not the same case. **A triage skip is a decision**: the ids are recorded in the connector block with a reason and the cutoff passes them, so they are written down rather than merely gone. **A batch remainder is not a decision**: the cutoff does not move past it, and it is the first thing the next pass offers.

**`corp-os-rebuild` lost the spec for the thing it rebuilds.** The 0.16 split moved the claim record into its own file and rebuild kept pointing only at the spine — so the skill whose entire job is re-deriving claims from `raw/` no longer read the definition of a claim. It re-derives against whatever it remembers, which is exactly the failure the reference files exist to prevent.

**`corp-os-intake` was classified as mechanical and is not.** It infers which jobs a piece of material serves and draws tags from the vocabulary already in use — and the skill itself warns that inventing categories is how a tag vocabulary fragments into uselessness. Bad tagging is invisible on the day and degrades every recall afterwards. It is a mixed pass; the distribution is now 3 mechanical, 6 mixed, 14 judgment.

All three are checked now, so none can come back quietly.

**0.18.0** — the other half of the cost problem, for sources a script cannot reach. 0.17 stopped fetching bodies nobody wanted. This stops paying three times for the ones you do.

**When a source is behind MCP, the read is unavoidable and the write is not.** The body enters a context because a model has to call the tool — that cost is real and there is no way around it. What was avoidable was everything after: the model re-emitting the whole body as output to write the file, and then re-opening that file to propose claims from it. The same content, three times, and two of those passes bought nothing.

**`capture.body`** decides how much of a kept item lands: `full` (a complete archive, and a rebuild can find what the first pass missed), `excerpt` (frontmatter, the passages actually cited, and a retrieval pointer — cost proportional to what the material was *used for*), or `stub` (the pointer alone). `excerpt` and `stub` are **refused** on a source with no verbatim fetch, because a pointer at something unretrievable is not a source. Neither mode summarizes: an excerpt is a verbatim span, and a summary is the different object Step 3 has always refused.

Under `excerpt` the order inverts — **propose from the body while it is still in front of you, then write the file carrying what you cited.** And `corp-os-pull` now forbids re-opening a file the same run just wrote, in every mode. It is the same bytes at full price for a file nothing has changed since.

**The connector registry learned the shape of a cheap read.** Almost every source has two: one that enumerates and one that returns a body, differing in cost by two orders of magnitude. The registry recorded `Protocol: MCP` — enough for a skill to know it can reach the source, nothing about reaching it cheaply, so it fetched everything. `List call`, `Fetch call` and their narrowing arguments are now recorded, and `corp-os-connect` asks for them; the list call is the single highest-value fact in the record.

`Fetch command` and `Credential` are there for sources a script can reach, where bytes never enter a context at all. **A credential is named, never written** — `env GRANOLA_TOKEN`, not the token. `connectors.md` gets synced, shared, and handed to audits, and a secret in it is a secret published.

**0.17.0** — the release that came from a bill. A single intake run over two connectors cost **$40**, and none of the sixteen prior releases would have caught it, because nothing in the system could see cost at all.

**The most expensive sentence in the plugin was correct.** `corp-os-pull` said *"Content goes in essentially as retrieved. Do not summarize, condense, or rewrite"* — right for fidelity, and the only way a model can honour it is to re-emit every byte of every transcript as output, at several times the price of reading it. Paired with *"retrieve everything since its cutoff"* and no cap anywhere, one run reads the whole window and types it all back. Forty meetings at ~6k tokens is 240k in and 240k out before anything is proposed.

It is also this repo's own rule broken in the largest case it has: **moving bytes from a connector into a file is bookkeeping, not judgment.** Nine other always-required mechanical steps were moved into scripts. This one never was, because it does not look like a step — it looks like content.

**Capture is now a config block.** `capture.mode` is `triaged` (default) or `all`, and `capture.batch` caps items per pass in both pull and intake. Triaged retrieves the **list** first — titles, dates, participants, ids, tens of tokens per item instead of thousands — proposes keep or skip with a reason, and fetches bodies only for what a person confirms.

**One rule overrides the mode and it reads a field the connector registry already carried.** Triage is safe only where the source can be fetched back verbatim, because a skipped item is deferred rather than lost — which is exactly what `Verbatim fetch` records. For a source without one, pull captures everything regardless of mode. The registry was built for this in 0.9 and nobody finished the thought.

**Every skill now declares what kind of pass it is** — mechanical, mixed, or judgment — because twenty-three skills said nothing about it and the filing ones were running on the most expensive model available. Four are mechanical, five mixed, fourteen judgment; the validator fails a skill that declares none or more than one.

**And the usage log records cost.** `log_run.py` takes `--model`, `--items` and `--wrote`, and **measures** the bytes of the files it is given rather than accepting a claimed number — a model cannot observe its own token count, and writing one would be the fabrication this suite refuses everywhere else. Bytes written are the output half of the bill, which is the expensive half. A four-column log from an earlier release is widened in place rather than restarted, because `corp-os-improve` reads the whole file.

Deferred deliberately: getting the bytes out of the model entirely, by declaring a runnable `fetch` on the connector and dispatching it from a script. That is the one that takes capture cost to roughly zero, and it needs a credential contract and a per-source fetcher, which belongs in a pack rather than in a content-agnostic plugin.

**0.16.0** — a cost release. Nothing about what the model decides changed; what it has to read to decide it did.

**`data-model.md` was one 6,857-word file that seventeen of twenty-three skills loaded in full.** Most of them for one section: `corp-os-connect` needed the connector registry, 118 words, and paid for all 6,857. The claim record alone was 3,737 words, 55% of the file. It is now three — a spine (layer rules, directory shape, the scan contract), `claim-record.md`, and `records.md` for the job, decision, raw file, connector, usage log and `meta.json` shapes. Measured per skill: `connect` 6,857 → 1,279 reference words, `decide` and `recall` the same, `jobs` 7,915 → 2,337, `rebuild` and `redact` 6,857 → 1,962. Roughly **6,000 tokens off a typical run**, with no behavior change at all. The validator now names which file each schema field belongs in, rather than accepting it anywhere: a field that drifts into the spine is invisible to the skills that need it, which is the failure the split exists to fix.

**`find.py` is the eleventh shipped script, and it exists because the scan contract does not scale.** Read the index, then the layer index, then the detail file is the right order and it costs the whole file to answer a question about one entry — measured on a real shape, 156 tokens per claim, so a topic file holding forty costs all forty, while the index grows with the corpus and the answer does not. `find.py` narrows by id, job, topic, confidence or decay state and returns the matches; `--digest` renders one line each at about a fifth the size. The split is the one this suite keeps drawing: selecting is bookkeeping, and what the matches mean is not.

It refuses an unscoped search — that is what `INDEX.md` is for — and never returns from `proposals/`, because unreviewed material arriving in the same shape as reviewed material is precisely what the gate exists to stop.

**And building it found a bug in 0.15.0.** A corpus stores entries in two shapes, both legitimate: many per file as `### ID` blocks with bold-label fields, and one per file carrying its fields in YAML frontmatter. The evidence generator shipped last release read only the first, so against a fixture holding two open decisions it reported **"0 open decisions"** — not an error, not a warning, a confident zero. Both readers handle both encodings now, and the validator asserts a match from each, because a reader that silently halves the corpus is worse than one that crashes.

**0.15.0** — the first release driven by auditing a second, independently built skill set rather than by this one's own usage. `docs/improvement-packet-2026-09-09.md` is the packet; this is what came out of it, and it declined more than it accepted.

**An output built from claims inherits their decay, and nothing joined the two.** Decay is carried by the entry and swept by `corp-os-reality-check`. It is not carried by the things *built from* entries, so a dashboard registered in March off four claims, two of which went past their window in June, reads exactly like one refreshed yesterday. `build_index.py` now performs that join and renders **Resting on evidence that has gone stale** — per entry, as *n of m past its window*, with never-verified counted separately because an output resting on something nobody ever confirmed is a different weakness from one resting on something that aged. Same class as the finding that produced *open evidence across every job*: every field was already on disk and no view assembled them.

**`Rests on` is not the arguments layer's field.** It was introduced there in 0.14.0 because that is where it was first needed, and it belongs to any entry built from a bounded set of others — an argument, a registered dashboard, an authored brief in a layer someone declared. One field, one parser, and the two views that read it now apply wherever it appears. *Bounded* is the load-bearing word: an output built from a whole layer has nothing to list and keeps `Source files`, because listing a folder there renders as breadth nobody measured.

**Four of five pattern kinds had never been exercised.** `bind_pattern.py` has accepted `dashboard | export | deck | doc | brief` since 0.13.0 while the fixture carried one pattern and it was a dashboard — the binder validating against a list it had never had to honour, which is the same defect as a check that has never been seen to fail. `doc-initiative-evidence` is the second kind, with a working generator in the fixture, and the validator now fails if the fixtures exercise fewer than two kinds and if that generator stops emitting the `Rests on` line that is the whole point of it.

**The version bump is enforced rather than documented.** 0.14.1 established that a client caches by version string, so commits pushed without a bump reach nobody with no error and nothing inspectable from the inside. That was a rule with nothing behind it. `validate.py` now reads committed history, finds the last commit that changed the version, and fails if anything under `plugins/corp-os/` has been committed since. It reads committed history only, so it stays quiet during normal editing — a check that is red while someone works is one they learn to ignore.

**The write contract is stated outward.** `reference/data-model.md` now says what a skill set built by someone else on top of this one must obey: append to `raw/`, propose into `derived`, own your own `record` layers outright, and do not take the `corp-os-` prefix. The internal version is enforced by this repo's validator over this repo's skills; a companion has nothing checking it, and one companion now exists.

**And the conformance gap is printed on every run**: 17 of 23 skills have a case. The number was previously legible only by reading a run report, which answers a different question — which skills one run exercised, not which have a case at all. The two had already been confused once.

Declined, with the reasoning in the packet: a document-authoring skill in core (fails content-agnosticism; the field model that makes one useful is domain vocabulary pinned to whatever is downstream), an open-question layer as a model change (fails the config test — it is a declared layer with two extra fields), and a companion-plugin conformance kit (right shape, and **one** companion exists, so it waits for the second).

**0.14.1** — documentation, and it gets a version number for the reason the documentation is about. The client caches an installed plugin **by version string**: same version, different content, and every existing install keeps the old copy with no error and no way to tell from the inside. This README ships inside the plugin, so correcting it without a bump would have corrected it for nobody — which is the exact failure `docs/INSTALL.md` was written to name.

Two counts had gone stale in the way this project keeps catching: the repository README said nineteen skills three releases after there were twenty-three, and this one said twenty-one. Both are now checked by `validate.py` against the directories on disk rather than trusted, because a number typed by hand next to a number that changes is a defect with a delay on it. `corp-os-migrate` and `corp-os-pattern` were also missing from the skill tables here — shipped, documented in the version history, and absent from the list somebody actually reads.

`docs/INSTALL.md` is the new file, and its first sentence is the thing that keeps costing people a session: **there are two updates and they are not the same operation.** Updating the plugin replaces the skills; updating your OS brings the folder in line with them, and nothing about doing the first does the second. It covers the install paths that are actually supported (the marketplace; `--plugin-dir` for working on it) and says plainly that installing the packaged bundle directly is not one of them — `dist/corp-os.plugin` is a build artifact, not a distribution channel.

**0.14.0** — the schema work, and the first release where an existing OS has to change shape. Which is why the mechanism for it was built three releases ago: `corp-os-upgrade` has always named migrations and refused to perform them, and 0.14 is the first time it has any to name.

**`Source fidelity`** splits the medium out of confidence. One enum was carrying three independent questions — how faithful is the recording, how many sources exist, is the claim contested — and collapsing them made a specific thing invisible. Measured in a real corpus: **599 of 836 entries** were single-source summaries whose transcripts were still fetchable through the same connector that produced them, one API call from a higher confidence, and **zero had taken that route**, because a ceiling that is elective looked exactly like one that is permanent. `corp-os-connect` now records each source's `Medium` and `Verbatim fetch`; `corp-os-claims` reads them rather than judging; `build_index.py` renders **One call from promotion** as a count. Not a list of what is weak, a list of what is one call from being stronger.

**The arguments layer** ships optional, and it is one proposal rather than two: `rests_on` had to be introduced before anything could render it. A supporting-entry count reads as evidence breadth and does not measure it, because entries are minted at whatever granularity a pass chose — one argument in a real corpus rested on **nine entries that all traced to a single meeting**. So it renders as `N entries / M sources`, always both, and the index lists any argument whose distinct-source count is 1. No hand-set strength rating: the prior system had one, it was dropped as decorative, and its actual function was counting independent witnesses, which is derived for free and cannot go stale.

**`aliases` carry resolution provenance**, and read in both shapes. A bare string is an alias nobody confirmed, which is a legitimate state that should render as one. Requiring the object form would break every existing person record, and the goal is to make the distinction visible rather than to force a migration — in the corpus that reported it, an unconfirmed name resolution had already been promoted into the exact field deduplication reads.

**Reasons are sibling fields, never suffixes.** `needs_review` covers three situations a sweep cannot triage apart, so the reason is worth capturing — but writing it inside the value was proposed and declined, because everything downstream equality-tests that string. `Confidence reason` and `Sensitivity reason` carry it at no migration cost, and the validator now fails if a doc example puts a reason back inside a value.

**`migrate_schema.py`** is the tenth shipped script and draws the line this suite keeps drawing: a field whose value is derivable is bookkeeping, one whose value is judgment is not. It fills what the connector records already answer, **leaves the rest blank on purpose**, and reports both counts — because a blank field someone can see is honest, and a plausible wrong value is the failure this model exists to prevent.

One bug found by building it: `order_by` assumed `entry_schema` was a dict. A list of field names is equally legitimate and equally in the wild, and the first config to use both crashed the whole index.

**0.13.0** — patterns, which exist because of a problem that only appears with more than one person. One operator keeps their conventions in their head. Five operators produce five dashboards with five palettes and five ideas about what a panel owes the reader, and nothing in the model prevented it.

A pattern is a portable spec for producing one kind of output. The load-bearing rule is that it addresses layers **by role and field, never by name**: a pattern saying `claims/` binds in exactly one OS — the one it was written in — and fails everywhere else by rendering an empty panel, which reads as a state rather than a defect and so never gets investigated. `bind_pattern.py` resolves requirements against the receiving OS and produces three outcomes and no fourth: bound, bound with drops named out loud, or refused with the missing role and field stated. Demonstrated against the register fixture, which renamed `claim` to `entry` and disabled jobs: the claims requirement bound anyway, and the job-board requirement refused precisely.

`corp-os-pattern` is the twenty-third skill, and it authors in both directions — turning something already built into a spec, and adopting a pack from a teammate. `corp-os-dashboard` **got smaller**: it binds a pattern instead of carrying nine composition rules as prose, which is the test of whether patterns earned their place. `corp-os-upgrade` handles pack drift with the same mechanism it already uses for shipped scripts, because teammates carrying copies of files someone else maintains is that problem one layer up.

The screen-share shield is the substantial new material, and it comes from a real build. An OS dashboard gets opened on a shared screen, and `bearing` deliberately keeps sensitive load-bearing material in the scan path, so the moment the thing is genuinely useful is also the moment it is dangerous. The rule is that markup ships **redacted** and script *reveals* — the inverse is visible whenever the script fails, loads late or is disabled, which is exactly when it matters. `check_shield.py` performs that as a mechanical test: strip every script block and every parked attribute, reduce to visible text, grep for known probes. On the build that produced this rule, that test found **three leaks in a shield its author believed worked**.

Four more shield findings are in `reference/patterns.md`, and the last is the one nobody predicts. Sensitivity has to be *declared* and it is not only on claims: decisions inherit from what they rest on (6 of 18 in one OS, none catchable by reading the decision records), and a person record is sensitive only when their role or status is itself the protected fact (2 of 53). Redact the whole identifying row, not only the role. And **every derived summary is computed over the filtered set** — a search view stubbed its sensitive hits correctly and the "who said it" panel counted their speakers anyway, showing three speakers with the shield down and two with it up. The name is the disclosure.

A shield protects a screen; a redacted build protects a file that leaves. Ship both and let neither imply the other — and a redacted build filters once at the data-load boundary, because per-panel filtering is how a view added later arrives without the filter.

**0.12.0** — the first release driven by an audit of a real OS rather than by the eval suite, and the findings were different in kind: correctness and confidentiality rather than close-out discipline.

`corp-os-migrate` is the twenty-second skill. Bringing an existing body of work across had no owner — `corp-os-audit` ended by offering "setup alongside a plan for migrating," a plan with nobody to execute it, while setup asked one ceiling question and intake took one item at a time. So the most common first day fell between three skills, and four migration-shaped failures had nowhere to be prevented: no cohort ceiling, original dates replaced by today's, decay all firing on one day, and no record of what was deliberately left behind.

`stagger_decay.py` and `check_citations.py` are the fifth and sixth shipped scripts. The first exists because a migration verifies everything at once, so every window fires at once — 79 entries due on one day in a real corpus, 71 on another, **410 on a third** — and a backlog nobody can clear teaches people to skip the sweep permanently. It spreads the **windows** and never the `Verified` dates: the window is a policy choice, the verification date is a fact about the past, and falsifying it in a system built on provenance is not a trade worth making. The second clusters entries by citation and refuses an export whose members disagree about sensitivity — per-claim redaction was mechanically correct on all 836 claims of a real corpus and the boundary still leaked, withholding one copy of a quote and emitting the identical text in full twice.

`placement:` in raw frontmatter is the answer to the only irreversible failure in the audit: an operator instruction that overrides the schema, living in a derived file that regeneration never opens, so a rebuild honours the schema and destroys a commitment. `corp-os-intake` writes it, `corp-os-rebuild` reads it, and the validator fails if only one of those is true.

`build_index.py` gained five things. It generates a **per-layer index** for any layer over the threshold, because a layer holding 97% of an OS's content had no enumerated entry point and 33 of its entries were reachable only by grep. It renders **open evidence across every job** in one ranked list, oldest first, which is the single view a decision-heavy operator asks for most and the one that got lost when a flat register was correctly split into fifty places. It reports **undeclared root files**, not only directories — being named in `scan.excluded_from_scan` is not a declaration, and treating it as one is what made the quarantine file invisible. It says when `usage/log.md` has no rows while the derived layer is full, which is a condition it can already detect and the only reason an improvement packet had to be reconstructed from structural counts. And it stopped warning about a `note` key in the scan block, which fired on every run of every OS and is what taught one operator to ignore the warning that mattered.

Smaller: `bearing` is required only on sensitive entries now — it was filled 836 times to route zero claims. Job evidence items have a declared shape with a status and dates. Dashboards default to a local file rather than a published artifact, because `bearing` deliberately keeps load-bearing sensitive material in the scan path and a dashboard reads the scan path. `corp-os-claims` stamps proposals with their outcome. And `corp-os-improve` reads config `note` fields, because in the OS that reported an empty usage log, nearly every config block carried a note explaining why it deviated — the reflection had happened and had gone somewhere this skill was not looking.

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
