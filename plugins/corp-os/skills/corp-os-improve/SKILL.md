---
name: corp-os-improve
description: Analyzes how a Corp-OS knowledge base is actually being used — from its usage log, structure, and drift — and proposes specific changes to the OS's own shape, plus an anonymized improvement packet that can be sent back to whoever maintains the Corp-OS model. Use when someone says "improve my OS", "this is getting annoying to use", "what should I change about how this is set up", "is this working", "what am I not using", or after enough real use to have evidence. Not for fixing content accuracy (use corp-os-reality-check) and not for regenerating the derived layer (use corp-os-rebuild).
---

# Corp-OS improve

> **Judgment pass** — the reasoning is the product here. Run it on your best model, and do not economise by skipping the questions it asks.

The OS watches how it gets used and reshapes itself from evidence. This is what stops a personal knowledge system from being frozen at whatever its owner guessed on day one.

The discipline that makes this skill worth running: **every proposal carries a count.** A hunch about what would be nicer is worth less than one line of the usage log, because a hunch is how the previous system got over-built.

**This skill writes only under `usage/`, and a cluster of one is not a finding.**

Two things go wrong here and a conformance run caught both in the same pass. Read them as the shape of the temptation, because both are things a helpful run does:

- **Reading the log surfaces material worth capturing.** It is not this skill's to capture. Name it and hand off to `corp-os-intake` or `corp-os-claims`, which carry the citation and gate rules. A claim written from here arrives with no proposal behind it and no source anyone can check — and it is the kind of thing that looks like initiative until someone tries to cite it.
- **A person who asks for changes wants changes.** One friction row is one occurrence, and the bar is more than one. When the evidence is thin, say so, write nothing to `usage/proposals.md`, and name what a second occurrence would look like so the next run can recognise it. An empty pass is the correct output of a thin log, and it is the output this skill is least likely to produce unprompted. It studies how the OS is used and proposes changes to the OS; it does not add to what the OS knows. Material worth capturing that surfaces while reading the log goes to `corp-os-intake` or `corp-os-claims`, which carry the citation and gate rules for it. A claim written from here arrives with no proposal behind it and no source anyone can check.

Read `${CLAUDE_PLUGIN_ROOT}/reference/improvement-packet.md` and `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md`.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — check there is enough evidence

Read `usage/log.md`, `usage/proposals.md`, `meta.json` history, and the OS structure.

Then run `python3 scripts/source_yield.py --root <the OS>`. The friction column says what was hard; yield says what was pointless, and the two rarely name the same thing. A source at 200 files and 4 claims is not friction — nobody complained, and it costs a pull every day to stay that way. Propose narrowing its `Selector` or lengthening its `Cadence`, with the ratio as the count.

Under roughly twenty logged runs, say so. Report what is visible, note that the sample is thin, and suggest running again after more real use. Restructuring an OS on five data points is how it gets worse. The exception is a single loud friction — a person who says "this is annoying" has real evidence even at run three; take that seriously and scope the proposal narrowly.

## Step 1 — mine the friction field

The friction column in `usage/log.md` is the primary source. Cluster it, then count each cluster. Patterns worth naming:

- **A skill repeatedly ran and produced nothing.** Either it is being reached for wrongly, or its input is missing.
- **The same manual step keeps appearing.** Something the person does by hand every run should be structure.
- **Recall kept opening detail files.** The index one-liners are too thin — a scan-contract failure.
- **Claims kept turning up past decay at recall time.** Decay windows are set wrong at capture, or reality-check is not running often enough.
- **Material could not be assigned to a job.** Either a job is unnamed, or the job set does not match the actual work.
- **Confidence kept being ambiguous.** The kind/confidence distinction is not landing; likely needs sharper guidance at capture time.

## Step 2 — find what is unused

The section people skip, and unused structure is a cost rather than a neutral — it dilutes every scan and makes the OS feel like a chore.

Count writes per category since creation:

- A category created at setup and written to twice in four months should probably go. Say it plainly and offer to retire it (move its content into wherever it actually belongs, do not delete).
- A connector that has returned nothing in a month is either broken or pointing at a source that does not matter.
- Jobs `active` with no touch for a full horizon are candidates for retirement — hand to `corp-os-jobs`.
- A dashboard in the registry with a stale `last built` and no refreshes is a dashboard nobody opens.

## Step 3 — check the shape of any open-items layer

Whatever layer holds gaps, questions, or open items is where these systems rot first, and three checks catch it:

- **Sort its entries by grammatical form.** Findings (a fact with an implied concern), errands (imperatives), decisions (a live fork), questions (genuinely open and re-asked). A layer that has drifted mostly to findings has become a **status register** rather than a question queue, and the fix is splitting by form — findings back to the subject files that already cover them, errands to a task tracker — not adding structure above it.
- **Audit the resolved tier for misfiled entries.** If a large share of what sits in "resolved" was never an item of that kind, every count is inflated and the tier is not measuring what it appears to.
- **Look for a recurring attribute nothing groups.** Many entries whose real substance is the same property — nobody owns this, this is blocked on one person, this waits on a decision above me — scattered across an urgency-tiered layer where nothing surfaces the pattern. This is usually a one-page view rather than a restructure, and it is often the highest-value finding in the run.

## Step 4 — find what is missing

Read the shape of what the person keeps doing by hand, or keeps asking for:

- Repeatedly asking a question the OS cannot answer from its structure → a missing category or field.
- Repeatedly adding the same kind of note to a job's free text → that free text wants to be a field. This is the single most common real finding.
- Repeatedly needing something before meetings → a missing recurring brief or dashboard.
- Repeatedly hitting the same blind spot → a missing connector, or an honest constraint worth writing down so it stops being rediscovered.

## Step 5 — check the model's own load-bearing parts are holding

Four specific checks, because these are the parts that fail quietly:

- **Is the review gate being honored, or has it become a rubber stamp?** If every proposal is confirmed unread, the gate is theater. The fix is `gate.mode: propose_batched` or fewer, better proposals — never turning the gate off.
- **Are decay windows real?** If nearly everything sits at `decay.default`, nobody set `by_kind` thoughtfully and the sweep will surface noise instead of signal.
- **Does config match reality?** Layers enabled in `config.json` with no files; folders on disk absent from config; vocabulary values nothing uses. Config drift is quieter than count drift and does more damage, because every skill treats config as the authority.
- **Is any layer's `role` wrong?** A hand-maintained folder marked `derived` is one rebuild away from destruction. Highest-consequence check in the run.
- **Is `decay.applies_to` right for this corpus?** If it is `all` and a large share of entries have no retrievable source, every sweep is surfacing a backlog nobody can clear. Propose `sourced` plus a one-time disposition pass.
- **Is the jobs layer earning its place?** If jobs exist but nothing references them — intake not using their evidence lists, recall not scoping by them — they are overhead. Run the subject-shape test in `${CLAUDE_PLUGIN_ROOT}/reference/jtbd-patterns.md` and be willing to propose turning them off. A model finding that its own default primitive does not fit this person is a legitimate result, not a failure.
- **Do the indexes match reality?** Count and compare. Drifted counts mean something is skipping its recount step, which is a bug to name specifically.
- **Is `raw/` still append-only?** Check for edited raw files. If the discipline has broken, that is the most important finding in the run.

## Step 6 — clear the bar before writing anything

1. **Count what the log supports.** Not a judgment made while reading it — a call, because a run invoked by someone who has just asked for changes finds changes:

   ```bash
   python3 scripts/friction_scan.py --root <the OS>
   ```

   It exits non-zero when the whole log carries fewer friction rows than the bar. That is not a failure to work around: it means nothing in this OS can support a finding yet, and the correct output of the run is to say so, write nothing to `usage/proposals.md`, write no packet, and name what a second occurrence would look like so the next run recognises it.

2. **Cite each candidate.** Grouping rows into a theme is yours; the count behind it is checked:

   ```bash
   python3 scripts/friction_scan.py --root <the OS> \
     --candidate "<theme>" --row <date> --row <date>
   ```

   A candidate it rejects goes into `usage/proposals.md` as considered-and-rejected with its count — that record is what stops the same idea coming back every quarter — and never into the packet.

3. **Then write the proposals.** Only what cleared.

Write proposals into `usage/proposals.md`, each with: what to change, the count supporting it, the diagnosis, and the cost of the change.

Rank by evidence strength, not by how appealing the change sounds. Then recommend **one to three** to act on now. Proposing fifteen changes produces zero changes.

Distinguish three kinds explicitly, because they have different owners:

- **Config changes** — the largest category now that the model is configurable, and the cheapest to act on: retire an unused layer, add a field people keep writing into free text, fix a decay window that is wrong for a whole kind, tighten or loosen the gate, set a retention policy on a raw folder that has grown unwieldy. Hand these to `corp-os-configure` rather than editing files directly — it knows which changes are migrations and enumerates the blast radius first.
- **Content and hygiene fixes** — a stale README, drifted counts, a retrofit that never happened. This skill can carry these out on confirmation.
- **Model changes** — things wrong with Corp-OS itself that no config can express. These go into the packet.

That last boundary has a clean test: **if a proposal could have been a config setting, it is not a model change.** Wanting a field the model lacks is a config finding. Needing a *concept* the model lacks — something no field, layer, or vocabulary could express — is a model finding. Conflating the two sends noise to whoever maintains the plugin while leaving fixable friction sitting in the person's own OS.

## Step 7 — write the improvement packet

Only for candidates `friction_scan.py` cleared in Step 6. A packet is the most expensive thing anyone can act on — it sends someone to edit the plugin — and it is the output this skill is most likely to produce from an n of 1.

For anything in the model-change bucket, plus any structure the person invented that the shipped model lacks, write `usage/improvement-packet-<date>.md` per the reference format — unless the person maintains the corp-os plugin themselves, or is handing this straight to someone who does. In that case, don't write prose here at all: hand off to `corp-os-contribute`, which reads the plugin's actual source and produces apply-ready diffs instead of an anonymized note. Ask, if it isn't already clear from context, rather than assuming either way.

Two rules, both absolute:

**Anonymize by construction.** Build the packet from counts, structure, and friction fields. Never open a claim body, person file, or company record to write it. If a friction entry cannot be described without quoting private content, describe it abstractly or leave it out.

**Never edit the plugin from a packet.** A packet is a proposal for whoever maintains the model. Applying it is their deliberate act.

The invented-structures section is the most valuable part. A person who has run this for months has solved things the model has not — a field they added to job records, a convention for handling a recurring case, a ritual that made the review gate stick. Describe the shape, why it emerged, how often it is used, and whether it generalizes beyond their role.

## Step 8 — act on what was confirmed

Carry out confirmed local fixes: retire the unused category (relocating its content), add the field to the record shape and backfill where possible, adjust the decay defaults, update the OS's own `README.md` so the conventions stay legible.

Update the OS `README.md` on any structural change. A structure that changed while its documentation did not is worse than either the old or new structure alone.

## Read the config notes, not only the usage log

Every block in `config.json` may carry a free `note`, and in practice that is where an operator's reasoning about their own OS actually accumulates — decay windows tuned to what rots in this work, a taxonomy kept from a prior system because it carries more signal, a field marked load-bearing rather than a nicety, a ceiling declared with its escape route.

This matters because of what it means when the usage log is empty. In an audited OS the log had zero rows after a full-day migration, and the conclusion looked like *this operator does not reflect on their system*. The opposite was true: nearly every config block carried a note explaining why it deviated from the shipped default. The reflection had happened and had gone somewhere this skill was not looking.

So read the notes as a first-class input. They answer *why is it shaped this way*, which the log cannot; the log answers *where does it hurt*, which the notes cannot. A proposal that contradicts a stated reason without addressing it will be rejected, and rightly.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-improve --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

It also refuses to close a run that put something in a derived layer with no proposal file behind it, and names the files and the `propose.py` call that repairs the record. The gate is checked here because this is the step that never gets skipped — three attempts at stating it nearer the write got it to one run in three.

- `usage/proposals.md` updated with everything considered, including what was rejected and why — that record stops the same idea being re-proposed every quarter.
- A dated `history` entry in `meta.json`.
- A `usage/log.md` row.
- A plain statement of the top three findings and which one was acted on. If the honest finding is "this is working, change nothing," say that — an improvement skill that always finds work to do is not measuring anything.
