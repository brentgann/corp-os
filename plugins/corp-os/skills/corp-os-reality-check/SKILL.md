---
name: corp-os-reality-check
description: Sweeps a Corp-OS knowledge base for knowledge that has drifted from reality — claims past their decay window, claims never verified, contradictions between claims, assumptions still treated as facts, and jobs whose evidence no longer holds — then interrogates the person to resolve each one. Use when someone says "is my OS still accurate", "what's stale", "check my claims", "this doesn't match reality anymore", "audit what I know", or "I think some of this is wrong". Not for creating new claims from source material (use corp-os-claims) and not for regenerating the whole derived layer (use corp-os-rebuild).
---

# Corp-OS reality check

Every personal knowledge system degrades the same way: not by being wrong at the moment of capture, but by staying unchanged while the world moves. This skill is the correction loop, and it works by interrogation — the person is the only available source of ground truth for most of what needs checking.

Read the claim record section of `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md`.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

`decay.by_kind` and `decay.by_tag` determine what is overdue — not a shipped 90 days. If `decay.enabled` is false, this OS deliberately opted out: say the decay bucket has nothing to work from, offer the buckets that do not depend on it (contradictions, unverified, orphans, identities, cohort escapes), and mention that enabling decay is one `corp-os-configure` run away.

## Step 0 — scan and triage

Read `INDEX.md`, `jobs/INDEX.md`, `claims/INDEX.md`, and enough of `claims/` to evaluate the fields. Do not load `raw/` except to re-read a specific citation under dispute.

Build the worklist in eight buckets:

1. **Past decay** — `Verified` date plus `Decay` window is in the past. Honor `decay.applies_to`: under the default `sourced`, only entries with a retrievable citation belong in this bucket.
2. **Unsourced, awaiting disposition** — entries whose citation is `no source`. These are **not** decay candidates and must not be mixed into bucket 1: nothing can ever re-confirm them, so carrying them as overdue produces a permanently unresolvable backlog, and a sweep that always ends in failure is a sweep people stop running. Handle them as a **one-time disposition pass** instead — keep as an `assumption` with the person as its source, retire, or backfill a real source — and then stop carrying them. Report the size of this bucket separately, since on a migrated corpus it is often a third of everything.
3. **Never verified** — has a source but no `Verified` field, or still `needs_review` after a long time.
4. **Contradictions** — two claims whose statements cannot both be true. Look for these actively rather than only reporting the ones already marked `disputed`; an unmarked contradiction is the more common and more damaging case.
5. **Assumptions aging into facts** — claims of kind `assumption` that other claims or job records now treat as settled, and long-standing assumptions nothing has ever tested.
6. **Orphans** — claims serving only retired jobs, and claims serving no job at all.
7. **Unresolved identities** — claims of kind `identity` still open, and any place the same person, initiative, or metric appears under two names. These decay differently from facts: they do not become wrong, they stay ambiguous, and ambiguity in a people-heavy corpus quietly corrupts everything attributed to the wrong party.
8. **Cohort ceilings** — claims from a cohort with a recorded ceiling in `meta.json` that have somehow been promoted above it. A `confirmed` claim inside a `reconstructed` cohort means a pass promoted material it should not have.

## Step 1 — order the worklist by consequence, not by age

The temptation is to work oldest-first. Do not. Order by what a wrong answer would cost:

- Claims an **active job** depends on come first.
- Claims of kind `decision` and `constraint` outrank `fact` — a stale decision misroutes work, while a stale fact usually just embarrasses.
- Anything already surfaced in a **published dashboard** outranks internal-only claims, because other people are reading it.
- `disputed` pairs come before merely old claims.

Then say how long the sweep will take and offer to do it in batches. A worklist of 60 items presented at once gets abandoned; ten resolved is a real improvement.

## Step 1.5 — write the proposal before resolving anything

A sweep rewrites the derived layer, often across a dozen files in one pass, and until now this skill had no gate step at all. That is a real gap and it was found by measurement rather than review: the cross-cutting check that every derived-layer write has a proposal behind it **failed on three of four runs of this skill**, with one run rewriting fourteen files and filing nothing.

The gate is not paperwork. A sweep is the operation most likely to *remove* things — retire a claim, downgrade a confidence, drop an assumption — and the declines are the valuable part of the record: they are the only trace of what someone deliberately chose not to keep. A retirement that happened in conversation and nowhere else is indistinguishable, six months later, from something that was never there.

So write `proposals/PROPOSAL-<date>-sweep.md` **before** presenting anything: each item, what is being proposed for it, and what the evidence is. Then stamp it with the outcome afterwards, the same way `corp-os-claims` does. One proposal per sweep, not one per item — a sweep is a batch, and a batch behind one reviewable record is the point.

## Step 2 — interrogate, one item at a time

For each item, show the claim with its citation and date, then ask the question that actually resolves it. Match the question to the bucket:

**Past decay** — "Is this still true?" Then, whatever the answer: "how do you know?" A person saying "yes, still true" from memory produces `reconstructed`, not `confirmed`. Only a fresh source moves it back to `confirmed`. This distinction is the whole point of the field and it is the easiest one to let slide.

**Never verified** — "Where did this come from, and is there anything that would confirm it?" If nothing can, ask whether it should be re-filed as an `assumption`. An honest assumption beats a permanent `needs_review` fact, which is a claim in limbo that nobody trusts and nobody fixes.

**Unsourced** — batch these; do not walk them one at a time. Ask once, for the whole set: "none of these has a retrievable source. Keep them as assumptions attributed to you, retire them, or work through them individually?" Then apply the answer and mark them so no later sweep re-raises them. The goal is to empty this bucket permanently, not to revisit it monthly.

**Contradiction** — show both claims and both citations side by side. Then ask which is right, or whether both were true at different times. The third answer is common and important: two claims that conflict because reality changed should become a `retired` claim and a current one linked by `Relations`, not a `disputed` pair. Only genuinely unresolved conflicts stay `disputed`.

**Assumption treated as fact** — "This is currently recorded as an assumption, but job-004 is being run as though it's settled. Has anything actually tested it?" This is often the most valuable question in the whole sweep, because an untested assumption load-bearing on an active job is the highest-cost error the OS can hold.

**Orphan** — "This served a job that's retired. Keep it as durable knowledge, or retire it?" Default to retiring. Growth without pruning is what killed the person's last system.

## Step 3 — write the resolutions

Per resolved item:

- Re-verified with a real source → update `Verified` with today's date and what confirmed it, keep `confirmed`, reset the decay clock.
- Re-verified from memory only → `Verified` updated, confidence set to `reconstructed`, and say plainly that this is now weaker evidence than before.
- No longer true → `retired`, with `Relations` pointing at whatever superseded it. Never delete.
- Reality changed → old claim `retired`, new claim created via the `corp-os-claims` shape, linked both ways.
- Still genuinely contested → `disputed`, both citations retained.
- Re-typed → kind changed, with a note of the change and why.
- Reclassified on `bearing` → **logged as a decision, and act on it.** Promoting `incidental` to `load_bearing` means moving the entry back out of `sensitive.md` into its normal layer; demoting does the reverse. The flag and the placement have to agree, or the next scan gets a different answer than the schema says it should. Watch for the specific case worth catching: an entry in `sensitive.md` that other claims or an active job clearly depend on. That is a fact the OS has been reasoning without, and it is the sensitivity equivalent of an assumption load-bearing on an active job.
- Reclassified on sensitivity → **logged as a decision, not an edit.** A `sensitive` flag downgraded because the content turned out to be business signal rather than personnel signal is a judgment about how the schema applies, and the next reader needs to see it was reviewed rather than assume it was never flagged. Same in reverse.
- Identity resolved → record the resolution *and* every place it propagated, including any sensitivity change that follows. "Both names refer to one person; corrected in two topic files and one person file; also downgraded from sensitive to internal, because the departure turned out to be from a role rather than the organization."

Also check the OS's own documentation against the corpus while sweeping. A README stating that the `confirmed` tier is empty, in an OS that now holds two hundred confirmed claims, is stale documentation misleading every future reader and every future rebuild. Propose the correction in the same pass — it costs one line and nothing else will catch it.

All of these are derived-layer writes: propose, confirm, write. Batch the confirmations so the person is not clicking through sixty individual approvals.

## Step 4 — feed the jobs

Resolution changes what jobs need. Update the affected `What I still need to know` lists: an item confirmed comes off, and a claim that turned out to be unverifiable goes **on** as a new evidence need. That second direction is what turns this sweep into intake priority rather than just housekeeping.

If a job's supporting claims mostly failed the check, say so directly. A job running on stale evidence is worth flagging as `readiness: low` rather than leaving it looking healthy.

## Step 5 — report the truth about the OS

End with a plain assessment: how many claims were checked, how many held, how many were retired, how many contradictions were found, and which active jobs are now running on weaker evidence than they appeared to be.

Then set the next sweep. Recurring is better than heroic — offer to schedule a small regular pass over the past-decay bucket, per `${CLAUDE_PLUGIN_ROOT}/reference/scheduling.md`. A sweep that happens monthly and resolves ten items keeps an OS honest; one that happens once a year and resolves two hundred is an event nobody repeats.

## The promotion backlog, and the arguments resting on one source

Two things `build_index.py` now surfaces that belong in this sweep:

**One call from promotion.** Entries whose fidelity is `summary` and whose source still exposes a verbatim fetch. This is not a list of what is weak — it is a list of what is **one call from being stronger**, which is actionable in a way a weakness list is not. Work the ones gating the nearest decisions first; promoting the whole backlog is not the goal, and auto-promoting any of it without the actual fetch would raise a number while lowering the corpus's honesty.

**Arguments resting on one source.** An entry whose `Rests on` list traces back to a single raw file. Not wrong — an argument built on one conversation is a legitimate thing — but it is a different object from one built on nine, and the supporting count reads as breadth while measuring granularity. Ask whether it should be held more loosely, not whether it should be deleted.

## Also sweep the citation clusters

```bash
 python3 scripts/check_citations.py <the OS>
```

Reporting, not strict — a split cluster is something to resolve, not something to be stopped by, until the moment it is about to leave. Two findings come out of it:

- **Split** — entries sharing a quote and disagreeing about its sensitivity. A confidentiality failure waiting for an export, and invisible to every per-entry check.
- **Unlinked** — entries sharing a quote, agreeing on sensitivity, and not referencing each other. Usually two passes minting near-duplicates from one source. In one audited corpus, thirteen of fifteen shared-citation groups were unlinked and one of them contradicted itself on substance, with one member asserting a resolution as settled and another, from the same quote, stating it was never confirmed.

Treat a self-contradicting cluster as a contradiction finding, because that is what it is.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-reality-check --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

- Recounted `meta.json` and a dated `history` entry describing the sweep's outcome.
- A `usage/log.md` row. If a whole category kept coming up — "every pricing claim was past decay" — that friction points at a decay window set wrong at capture time, which is a model problem worth handing to `corp-os-improve`.
