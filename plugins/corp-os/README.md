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

**0.26.2** — provenance is the second invariant and nothing enforced it; a derived entry now says where it came from or the run does not close.

**0.26.1** — the plugin guard reported the repo's own commit; "the directory changed" is not "this run changed it".

**0.26.0** — every skill has a conformance case, and the harness watches its own plugin.

**0.25.4** — a source layer's index is the shape of the archive, not a listing of it: 14,943 tokens to 244.

**0.25.3** — a conditional check divided by the wrong denominator, and a release chased the number it produced.

**0.25.2** — three checks that were prose become three exit codes: layer shape, queue reachability, and a view the OS has no pattern for.

**0.25.1** — a layer that is one file was invisible to the gate, which is the shape `glossary` has.

**0.25.0** — the gate is checked by `log_run.py`, the one step measurement says never gets skipped.

**0.24.0** — the gate becomes a numbered step, because a rule beside a list loses to the list.

Third attempt at one defect, and the first two were both true and both irrelevant. `--repeats 3` measured it: `corp-os-jobs` **0/3**, `corp-os-decide` **0/3**, after 0.18.7 moved the gate above everything that writes and 0.20.0 turned it into a script call.

`corp-os-jobs`' "Adding a job" is a numbered procedure whose step 5 is *"write the record."* The gate sat in a section above the list. `corp-os-claims`, which passes this check 6/6, puts the proposal at **Step 5 of its own sequence.** A run executes the enumerated steps and reads the prose around them.

`corp-os-glossary` confirms it from the other side: it *had* a numbered proposal step — at Step 4, after *"Step 3 — write the entry."* A skill contradicting its own order scored 1/3.

The proposal is now item *n* in the list that writes, in `jobs`, `glossary`, `decide` and `company`, with the write renumbered after it. The validator checks for the numbered form rather than a mention, and caught `corp-os-company` immediately — fixed the same wrong way an hour before. §4.52.

**0.23.0** — registering an unfamiliar system, checked rather than remembered.

Asked how the OS walks someone through a connection it has never seen, the answer exposed drift I created in a day. `corp-os-connect` Step 1 still said *"all seven fields"* while listing ten, six more had been added since morning, and the question that decides which fields even apply — is this a source you pull from, or one you ask? — was asked at Step 1.3, **after** the field list. A rule read after the step it governs is a rule the run has already passed, which 0.18.7 recorded and this repeated within the week.

Restructured: shape first, then the fields that shape implies, then a clean sequence through Step 10.

Two new steps do the work that memory was doing:

**Probe it once, bounded, before trusting any of it.** One list call with the selector, capped at ten — or one statement with a `LIMIT`. Show what came back and ask whether it is the slice they meant. **A wrong selector is obvious in ten rows and invisible in a registry entry.** Fetch nothing, write nothing; the probe checks the contract, not the material.

**`scripts/check_connector.py`** checks each record against the shape it declares. Three shapes: a queried source needs a query interface and must not carry a cutoff or selector; a listed one needs its call pair, limits and a ceiling; a manual one has no system to call and is exempt from both — holding a hallway conversation to the listed checklist produces six findings about a correctly configured source. It also refuses a credential value in a file that gets synced, shared and handed to audits.

The shipped fixture registry was rewritten to satisfy it, which it did not.

**0.22.0** — a warehouse is a third source shape, and it is never pulled.

Two shapes were assumed everywhere: a source you *list and fetch from*, and a source you *export from*. Redshift, session analytics, a metrics store are neither — the data is generated faster than anyone could capture it, there is no list worth walking, and no cutoff means anything. Registered as a listed source it reads like any other connector and produces a run that asks a warehouse for everything since Tuesday.

`Access: query` says so. No selector (it is scoped per question, not per slice), `Cadence: on demand`, a read-only role, and `corp-os-pull` skips it outright and reports that it did.

**What lands in `raw/` is a measurement, not the data.** One file per question asked: the question, the statement verbatim, the result, the run date. So **the query is the citation** — and it is a better one than a quote, because a sentence can only be re-read while a statement can be re-run and either reproduces the number or does not.

That is what makes the last part possible, and it is the real payoff. **The failure this shape has is not over-capture; it is an OS where numbers go to get stale.** A metric captured once and never re-run looks exactly like a sourced claim and is quietly wrong a quarter later.

So a decayed metric from a queried source is **re-run, not chased**. Same number and `Verified` moves — the cheapest confidence in the model and the only kind that costs no judgment. Different number and it is **not a stale claim to retire, it is a finding**: the thing changed, and two run dates now bracket when. Query no longer runs, and that is a more urgent finding still — every claim resting on it just became unverifiable.

**0.21.1** — what a source produced, against how much of it became anything.

A `Selector` narrows a shared system to a slice. Inside the slice, most of what a wiki or a tracker holds still will not earn a claim, and nothing measured which sources those were.

**Triage decides per item on metadata, which is the weakest evidence available.** The strongest — what the last two hundred items from that source actually turned into — was already on disk and uncounted. A raw file carries `source:`; a claim carries `Source: raw/…`. That is a join, and `scripts/source_yield.py` performs it: per source, raw files captured, how many any derived entry cites, how many of those serve a job.

`corp-os-connect` runs it before adjusting a registered source. `corp-os-improve` runs it alongside the usage log, because **the friction column says what was hard and yield says what was pointless, and the two rarely name the same thing.** A source at 200 files and 4 claims generates no friction at all — nobody complains, and it costs a pull a day to stay that way.

Three answers when a slice yields almost nothing: narrow the `Selector`, lengthen the `Cadence`, or decline the source. There is never a reason to delete what was captured. `raw/` is append-only and the fix is to stop capturing, not to remove.

Read it as a ratio, not a score. Three claims per hundred files may be a narrow and precious source. It is asking whether the selector still describes what you wanted.

**0.21.0** — a shared system is not a source; a slice of it is.

The suite scoped by **time** (the cutoff) and by **triage** (per item, after listing) and had no notion of scoping by **subject**. For Granola or a mail account that is enough, because the source is already only one person's. In Confluence, *"everything since Tuesday"* is every page anyone in the company touched since Tuesday — the cutoff narrowed nothing, and the list call alone walked the instance before triage got a chance to decline anything.

`Selector` is now a connector-record field: the query naming the slice in the system's own terms — a CQL query, a JQL filter, a board, a label, a segment. It is `n/a` only where the source is already personal.

So register `Confluence — Product Decisions space`, not `Confluence`. Three spaces are three sources, each with its own cutoff, cadence, blind spots and jobs, which is the right shape: they answer different questions, go stale at different rates, and one being useless is no reason to stop reading the others.

This sharpens a test the registry already had. **A source serving no job is worth declining** — and a whole shared system serves every job and therefore none, which is the tell that nobody has chosen a slice yet.

`corp-os-pull` passes the selector to every list call and refuses to list outside it. And for a shared system the first pull defaults to **no backfill at all**: start from today and let the slice fill forward. What is already in a wiki has been findable there the whole time; the value of capturing it starts when someone cites it.

**0.20.1** — a throttled source is not a broken one, and a knowledge base is not a crawler.

Nothing in twenty-three skills and fourteen reference files mentioned a rate limit, a 429, backoff, concurrency or a credential scope. Meanwhile `corp-os-pull` Step 3 said to mark anything *"missing, unauthorized, or erroring"* as `broken` — so a rate-limited Jira was recorded dead, the next run skipped it, and the person believed they were covered on a source returning nothing. Wrong twice, and it becomes likely the moment anyone points this at a shared system.

Four things, and they matter most for a team:

- **`Scope: read-only`** on the connector record, and `corp-os-connect` asks for it. This suite never writes to a source. A write-scoped token carries risk the OS has no use for, and in a shared workspace it is the difference between a tool that stays installed and one an administrator removes.
- **`Limits` and `Ceiling` are two numbers.** The limit is the source's; the ceiling is yours and should be well under it. A system permitting 100 calls a minute is not asking for 100 from one person's notes.
- **`throttled` is its own status.** Back off, leave the cutoff where it is, carry on with the other sources, try next run.
- **Fetch sequentially** unless the record says otherwise. Concurrency is how a personal knowledge base becomes noticeable traffic on someone else's system, and nothing here is urgent.

**0.20.0** — the gate stops being a rule and becomes a command.

Four skills wrote to derived layers with no proposal on disk in one conformance run, and two of them had already had a prose fix applied — 0.18.7 moved `corp-os-jobs`' write gate above every section that writes, and it still did not fire.

Counting the roster settled it in a minute. **Every skill that passes that check names `proposals/`. Every skill that fails says "propose" and never says it is a file.** `corp-os-claims` has an entire step called *"write the proposal to disk, then present it"* with the literal path, and passes 6/6. The other four say "propose" between two and seven times each. A model satisfies *"propose and wait for confirmation"* by proposing in the conversation, which is a fair reading of the words and leaves nothing behind.

So it stops being a rule to remember. `scripts/propose.py` writes the proposal file and, in a second call, records the outcome per item — and says so when a batch has no declines, because a gate that confirms everything is a formality. `corp-os-jobs`, `corp-os-glossary`, `corp-os-decide` and `corp-os-company` now run it, in a section placed above everything that writes.

`corp-os-improve` failed differently and gets a different fix: it wrote a claim while reading the usage log, and proposed from a single friction row. Both are things a *helpful* run does, so they are now named as the shape of the temptation rather than forbidden in a line.

The validator checks an explicit set rather than pattern-matching the prose. The first version guessed at "write … `<layer>/`" and missed `corp-os-glossary`, whose layer is a file — a regex standing in for reading, which §4.51 already records four times.

**0.19.12** — a gated read cost `corp-os-dashboard` a rule it had for five releases.

The first full conformance run since 0.18.5 came back **152/163**, and one of the eleven failures was caused by this repo's own cost work. `dashboard-hub-and-registry` had passed at 7/7 for months; it now rebuilds `dashboards/` as a directory — the shape whose removal was the point of the layout fix, because a registry-as-directory made the index report `1` however many dashboards were in it.

The rule lived in `reference/dashboard-patterns.md`. 0.18.4 gated that read behind *"if this OS has adopted no pattern that fits"*, which is correct for a catalogue and wrong for a rule. A run with an adopted pattern never read it again.

§4.48 exactly: a refactor removes a capability without touching the skill that had it. The rule is now in the skill, ungated, with the reason attached, and the validator fails its absence.

**0.19.11** — the unknown-role warning only looks at enabled layers.

`fixture-register` turns `jobs` off and gives it no role, which is fine and which 0.19.9 warned about on every run. A disabled layer's role changes nothing, and a warning that fires when nothing is wrong is what teaches people to skip the one that matters — the reason the `scan.*` warning was scoped the same way two releases earlier.

**0.19.10** — most of what is left in a `note` field is not a note.

`prune_config_notes.py` now also catches keys like `profile_note`, which escaped the check by not being called one, and its guidance separates the two things that live in these fields:

- **A reason.** A skill does nothing differently for having read it. Move it.
- **A rule in a field called `note`.** A rule every skill must obey has to live where every skill reads, and that cost is the rule working. Keep it, and shorten it to the instruction — drop the history, the example and the justification.

Read against a real OS, most of the 844 tokens remaining after the first pass were the second kind: when to mark a person record sensitive and which script reads that field; that a topic file asserting something uncited is invisible to `corp-os-reality-check`; that any skill writing person records must check `placement_instructions` first. Moving those to a README would have been a behaviour change reported as a saving.

**0.19.9** — two things `config.json` could be wrong about while looking right.

**A duplicate key.** JSON keeps the last of two identical keys and reports nothing. A real OS declared `dashboards` twice — an existing layer for the rendered directory, and a new one added to declare the registry file — and the second silently replaced the first. The file the edit was made to declare stayed undeclared, the edit looked correct, and nothing anywhere would have said so.

**A role nothing reads.** Every rule in this suite branches on `source`, `derived` or `record`. A layer declaring anything else falls through the review gate, through the write-freely exemption and through the rebuild protection, all three. The same OS carried four — `view`, `quarantine`, `output`, `reference` — each reading as a considered decision and none of them doing anything. `gated: true` is in the same category: it appears in the shipped defaults and the documentation and no code reads it.

Both warn on every `build_index.py` run, alongside the existing warning for an unknown `scan.*` key.

**0.19.8** — the schema rule states its exemption.

*"A layer may only be enabled if it declares an `entry_schema` and an `index_line`. This applies to shipped layers and custom ones alike."* The shipped fixture declares `connectors` and `dashboards` with neither, and `build_index.py` skips `record` layers when rendering entries, so an `index_line` there is never read.

The rule is right and its scope was wrong. A `record` layer whose shape is fixed in `reference/records.md` declares `role` and `path` and nothing else. A **custom** `record` layer gets no exemption, because nothing in the plugin says what one of its entries contains — which is the case the rule exists for.

In a real OS three files sat roleless for months, `connectors.md` among them, holding the only copy of the source registry. The undeclared-files report names them on every run; the rule as written made declaring them look like it required a schema nobody had, for files that plainly did not need one.

**0.19.7** — an entry whose path is the slug of its name no longer spells the path out.

Measured on a real OS: across 82 entry lines, the label cost 720 tokens and **the path cost 1,004** — 24% of `INDEX.md`, for a string that restates the name in a form that tokenizes worse than the name. `<layer>/<name-lowercased-and-hyphenated>.md` is a lookup, and a document that restates a lookup is a cache.

The convention is now stated once in the header and the per-entry path is dropped **only where the filename is exactly the slug of the label**. Anything named differently keeps its link, so nothing becomes unreachable.

This was found by splitting a per-entry cost into label, path and rendered content. The previous three attempts at that number all blamed the `index_line` template, and one of the layers costing 43 tokens an entry has a two-field template with nothing in it to remove.

**0.19.6** — a note on a list entry may be the only thing telling it from its peers.

In a real OS two `confidence_ceilings` entries were *"the original source text no longer exists"* and *"a deliberate downgrade from how the source system treated it."* One is permanent and one is elective. As data they are identical, and the note is the whole distinction — while the run deciding which claims can ever be promoted reads the ceiling, not the README.

`prune_config_notes.py` now marks any note whose path ends in a list index and says what to check. Flagged rather than blocked: once that distinction is a field, the note is genuinely redundant.

**0.19.5** — `prune_config_notes.py` takes `--only` and `--except`, because a note is not automatically documentation.

Run against a real OS, the fifteen notes were not fifteen explanations. Some were: *"Tuned to what actually rots in this work rather than left at the shipped default."* Others were rules wearing a reason's clothes — *"A readable view over claims, not an independent source of truth"* changes how a skill treats that layer, and *"Mirrored here from `sensitive.md` because `sensitive.md` sits outside the scan path"* is provenance on a load-bearing instruction.

Moving those out of the file every skill reads is a behaviour change dressed as a cost fix. So the move is now per-path, and the dry run prints the test: **would a skill do anything differently if it never read this sentence?** No, and it is a reason — move it. Yes, and it is not a note at all; it is a field or a layer description that belongs in the schema, stated in a line rather than a paragraph.

No script can make that call, which is why it is a flag and not a default.

**0.19.4** — `note` fields move out of the file every skill reads first.

A note is written once by a person to explain why the config is shaped the way it is, and then re-read by a model on every run of every skill forever. In a real OS they totalled **1,627 tokens: 42% of `config.json` and 17% of the whole pre-flight floor.**

`reference/configuration.md` already says where they go. Its precedence list is `config.json`, then *"the OS's own README.md — for anything config does not cover, and for the human-readable explanation of why the config is shaped the way it is."* That is a note, in the wrong file.

`scripts/prune_config_notes.py` moves each one to the OS README labelled with the config path it came from, losing nothing. Dry run by default. `build_index.py` warns above 400 tokens of notes rather than enforcing anything — it is the person's config.

**0.19.3** — a layer with its own index is no longer listed twice.

`raw` and `claims` were exempted from the root index's per-entry listing **by name**, which reads as a size rule and is not one. Every other layer was rendered in full however large it grew. Measured against a real 852-claim OS: a `people` layer of 54 was listed in the root *and* in the `people/INDEX.md` that 0.19.0 started generating for it — 1,424 tokens duplicated into the file every skill reads on every run.

The root now uses the same threshold `write_layer_index` uses, so the two cannot disagree: over it, a count and a pointer; under it, the entries.

`corpus_load.py --sections` also reports entries and tokens-per-entry per section. A scannable line is roughly 15-20 tokens; well above that is an `index_line` template doing more than one line of work, paid once per entry. In the same real OS, sections were running 43-57 tokens an entry, which is a config question the tooling could not previously show anyone.

**0.19.2** — `corp-os-upgrade` declares `model: sonnet`.

The one skill of twenty-three that survived 0.18.2's reclassification as genuinely mechanical: comparing files and copying the ones that differ, with migrations explicitly excluded. Roughly 60% cheaper per token.

Whether a surface other than Claude Code honours skill frontmatter is unverified, and an ignored field is a change that reaches nobody. It is the first open item in `docs/BACKLOG.md`.

**0.19.1** — filing moves into a script.

`scripts/file_raw.py` takes a whole batch of fetched items and does the deterministic half in one call: dedupe on `external_id` against what is already filed, build the `YYYY-MM-DD--<source>--<slug>.md` name, suffix rather than overwrite a collision, write the frontmatter from the spec, optionally advance the source cutoff. It reports what it filed, what was already there, and what it rejected for missing fields.

Done in the model this was one turn per item, and every turn re-sends the whole session prefix. That is how a filing run became the most expensive thing in the suite. What stays with the model is the judgment: which items to keep, and what the derived layer should hold.

The cutoff is passed in rather than computed. A batch remainder must not fall behind it, and only the run knows what it did not reach.

**0.19.0** — the index carries what the OS holds; a new `usage/health.md` carries what is wrong with it.

Measured against a generated 800-claim OS, which is the first fixture large enough to show any of this. `INDEX.md` was **1,440 tokens, 1,029 of them findings** — *resting on stale evidence*, *arguments on one source*, *one call from promotion*, *open evidence*. Every skill read all of it on every run and almost none of them act on it.

Capping the lists was the obvious fix and the wrong one: these sections exist to make problems visible, and finding #31 is the one nobody goes looking for. They move out whole and **uncapped** into `usage/health.md`, which `corp-os-reality-check` owns. `INDEX.md` keeps a line saying they exist.

**INDEX.md 1,440 → 468. Pre-flight floor, paid by every skill on every run, 2,513 → 1,541.**

`write_layer_index` counted files while the problem it exists for is about entries, so 800 claims grouped into 25 topic files fell under the 40 threshold and the largest layer in the OS was the one with no enumerated entry point — the "reachable only by grep" case its own docstring names. Either count crossing is now enough, and `claims/INDEX.md` generates at 965 tokens.

All three fixtures carried a 414-line `build_index.py` against a shipped 888, and `fixture-stale` — deliberately two releases behind — was newer than the two that are not. Sixteen skills run the OS's copy, so every conformance result about script behaviour was measured against something else. Synced, and drift now fails the build.

New: `scripts/corpus_load.py` reports what each skill reads on pre-flight against a real OS, and `scripts/make_fixture.py` generates a corpus of any size. Both cost nothing to run — no model, no tokens.

**0.18.7** — two skills whose rules were in the wrong place.

`corp-os-jobs` wrote two job files with no proposal behind either. Its write gate was correct and sat forty lines below *Adding a job*, so a run reached the action first and the constraint after. The gate now precedes all four sections that write, and the validator checks the ordering rather than the presence.

`corp-os-improve`, asked to study the usage log, wrote `claims/pricing.md`. Nothing in the skill said where it may write. It now says it writes only under `usage/` and hands anything worth capturing to the skills that carry the citation and gate rules.

**0.18.6** — the front door was doing the work.

A conformance case gave `corp-os-guide` an undecided fork phrased as an instruction — *"we still haven't landed on whether to keep the legacy importer, can you get that into my OS?"* — and it wrote `decisions/legacy-importer.md`, edited a job, skipped the gate, and never said `corp-os-decide`.

The skill said "never does the work itself" in one line and then told itself, in Step 4, to *"offer to do it"*. The same self-contradiction 0.18.4 found in `corp-os-dashboard`. The rule is now positive and concrete — every run ends by naming a skill, and the only files it writes are `usage/log.md` and its `meta.json` row — and the validator fails both a missing rule and the return of "offer to do it".

**0.18.5** — the arguments layer gets its own file, and two skills that discussed it could not reach it.

`corp-os-recall` cited `records.md` for the arguments record. `records.md` does not document it — the spec was in `claim-record.md` the whole time. `corp-os-configure` has a section headed *Offering the arguments layer* and reached neither file. Both now point at `reference/arguments.md`.

An optional layer's spec and its 548-token worked example were being read on every run by the three skills that read `claim-record.md` unconditionally and mostly write ordinary claims. Suite unconditional load 84,823 to 82,894.

**This finishes the gating work.** What remains is `configuration.md` for `corp-os-setup`, `claim-record.md` for `claims`, `rebuild` and `reality-check`, and `data-model.md` for six skills. Each of those is a reader that needs most of the file, so the next honest move is a conformance run against what has changed, not another split.

**0.18.4** — `corp-os-dashboard` reads nothing unconditionally, and the capture spec now lives where its readers are.

Dashboard went from 12,786 unconditional reference tokens to zero. Three gates: the pattern catalogue is read only when no adopted pattern fits (Step 1 already said to pick from `patterns/`, "not from a catalogue in this file" — the skill was contradicting itself), the pattern *format* only when a file will not parse, and the scheduling spec only if the person accepts the cadence Step 6 offers.

The `capture` block lived in `configuration.md`, which `corp-os-pull` and `corp-os-intake` do not read — so the block governing what a run fetches was unreachable by the only two skills it governs, and charged to six that do not use it. It now has its own file. Moving it to `records.md` first made the suite total *worse*, because records has more unconditional readers; that is recorded rather than quietly corrected.

Suite unconditional reference load is 84,823 against 89,458 conditional. Six skills read nothing unconditionally.

**0.18.3** — the check §4.48 asked for, and two lessons from building it.

Every skill must now name the reference file defining any spec field it uses. Eight gaps in six skills on the first run, including `corp-os-configure` enforcing `entry_schema` and `index_line` while never naming the file that defines them.

Then: the first pointers were written as statements, which satisfied the check and pulled the whole file every run — `corp-os-configure` went 5,696 to 14,574 unconditional tokens before they were rewritten to name their branch. And the measurement that picked the work order scored `corp-os-guide` worst in the suite when it was already correct, because its condition trails the clause instead of opening it. §4.51.

`docs/BACKLOG.md` now carries the running list of measured, unfixed things, with the command that produced each number.

**0.18.2** — two skills described themselves as mechanical and were not, found while pricing whether the pass declarations could drive `model:` in frontmatter.

`corp-os-pull` said "little here is a judgment call" — accurate when written, and false by the end of the same release that wrote it, because 0.17 added triage to that skill. Proposing keep-or-skip is the one decision downstream cannot undo: nothing re-derives material that was never retrieved. `corp-os-guide` said it too, while routing on an open fork against a recorded decision against a job, distinctions its own text calls consequential.

Both are now mixed passes. The validator fails a mechanical declaration that sits alongside `infer` or `keep or skip`, the two markers these cases and 0.18.1's `corp-os-intake` had in common. It does not catch `corp-os-guide`'s kind, and §4.50 records that rather than pretending a keyword would.

One skill of twenty-three is now safe to run on a cheaper model, and it is the rarest one. The saving was never in routing judgment somewhere cheap; it is in having less judgment to route.

Installing in Cowork is documented, which it was not: Cowork serves plugins from a separate account catalogue and does not read Claude Code's marketplaces at all.

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
