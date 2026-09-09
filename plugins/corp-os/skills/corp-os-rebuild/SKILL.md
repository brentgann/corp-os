---
name: corp-os-rebuild
description: Regenerates the entire derived layer of a Corp-OS knowledge base — claims, jobs, people, topics, glossary, indexes — from scratch out of the full raw archive, splitting overloaded groupings, merging duplicates, retiring what raw no longer supports, and reporting exactly what changed structurally. Use when someone says "rebuild my OS", "regenerate my claims", "this has drifted, redo it from source", "my taxonomy doesn't fit anymore", or when the derived layer no longer reflects the corpus. Never touches the raw archive. Not for a targeted staleness sweep (use corp-os-reality-check) and not for adding new material (use corp-os-intake or corp-os-pull).
---

# Corp-OS rebuild

The one operation permitted to restructure the derived layer, because none of it is destructive: `raw/` is untouched and the derived layer was always meant to be regenerable.

Read `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md` and the OS's own `README.md` (its conventions win over the shipped spec).

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

`config.json`'s layer roles decide what this skill may touch at all — see Step 1. Reading it is not optional here.

## Step 0 — check this is the right operation

Rebuilds are expensive and often unnecessary. Diagnose before proceeding:

- **One file has grown unwieldy** → offer to split that file. Not a rebuild.
- **Some claims are stale** → `corp-os-reality-check`. Not a rebuild.
- **Recurring friction with the structure itself** → `corp-os-improve` first, so the rebuild targets a better model rather than faithfully reproducing a bad one.
- **The taxonomy genuinely no longer fits what is in raw/** → rebuild. Categories that worked at 20 entries rarely work at 400.
- **Nobody is confident the derived layer still reflects the corpus** → rebuild.

Say plainly that the current derived layer will be replaced by a fresh derivation. Nothing is actually at risk — `raw/` is the backup — but the person should hear it before it happens.

## Step 0.5 — read the placement overrides before deriving anything

Scan `raw/` frontmatter for `placement:` and honour every one of them. These are instructions the person gave about where derived content may and may not live, and they **override the schema** — which is the whole reason they exist, and the reason they are written where regeneration reads rather than in the file they govern.

A rebuild is schema-driven, and that is exactly what makes it safe in every other respect. It is also what makes this the one operation that can destroy a commitment: told nothing, it will re-derive personal content into a person record that someone explicitly said must not carry it, faithfully and irreversibly, with the original still sitting in `raw/` as justification.

If a `placement:` value names a layer this OS has not declared, stop and say so rather than guessing. An override that cannot be resolved is not an override that can be ignored.

## Step 1 — read config and refuse to touch what is not derived

Read `config.json`. **A rebuild only ever regenerates layers whose `role` is `derived`.** Layers marked `source` or `record` are off limits — `raw/` obviously, but also `proposals/` and any custom layer the person declared as its own truth.

This is the one configuration error in Corp-OS that destroys data: a `source` layer mislabeled `derived` gets overwritten by a rebuild with nothing to restore it from. So verify rather than assume. If a layer's role looks wrong for what it plainly contains — a folder of hand-written material marked `derived` — **stop and ask**. Do not rebuild it and do not silently skip it.

Check retention too. If archived raw material exists under `retention.raw.archive_to`, a full rebuild should read it: it is still source, just outside the scan path. If material was **deleted** under a retention policy, the corpus is now genuinely smaller than the claims derived from it — respect the cohort ceilings in `config.json` and never re-promote a claim whose source is gone.

## Step 2 — confirm scope

Everything, or specific categories? A claims-only rebuild is common and much cheaper than a full one.

Ask whether the **job set** is in scope. Rebuilding jobs from `raw/` is a different and stronger claim than rebuilding claims: jobs come from the person's intent, not from the corpus. Default to keeping jobs as they are and re-deriving everything else against them, unless the person specifically wants the job set reconsidered.

## Step 3 — read the whole corpus

Every file in `raw/`, not a sample. This is the one operation in the suite that is supposed to load everything — partial coverage defeats the entire purpose. Note each file's `source`, `type`, `date`, `person`, `jobs`, `tags`, and `processed` state as you go.

For a large corpus, work in date-ordered batches and keep a running derivation rather than trying to hold everything at once. Say up front roughly how long this will take.

## Step 4 — re-derive each category from source

Build each category back up from what `raw/` actually contains, not from what the old version said. The four moves:

**Split** what has become overloaded — a topic covering two genuinely distinct subjects that only looked related when there were six entries in it.

**Merge** duplicates and near-duplicates that only become visible with the whole corpus in view. This is the main payoff of a rebuild: incremental intake cannot see that CL-0031 and CL-0198 are the same claim, and a rebuild can.

**Re-confidence.** With the full corpus visible, a claim that was `needs_review` on a single mention may now have three independent sources. Raise it. Equally, a claim that looked corroborated may turn out to rest on two captures of one conversation — lower it. Watch for that case specifically; it is the most common way confidence was inflated during incremental intake.

**Retire** what `raw/` no longer supports, and claims that served only retired jobs. Move them to retired status with a reason. Never delete.

Every entry keeps full provenance. A rebuild is license to reorganize, never to drop sources, citations, sensitivity flags, or decay windows. Where the old entry had a `Verified` date, carry it forward — re-deriving a claim from the same source does not re-verify it.

## Step 5 — reassign claim IDs never, renumber never

Keep existing claim IDs. A rebuild that renumbers breaks every external reference — dashboards, exported briefs, documents the person already sent. New claims discovered during the rebuild take fresh IDs from `next_claim_id`.

## Step 6 — verify counts programmatically

Count files, count section headers, count entries by actually counting. Cross-check every number written into `INDEX.md` and `meta.json` against that count. Hand-totaling across a full rebuild is precisely where drift enters, and a wrong count in `INDEX.md` poisons the scan contract for every later run.

Also verify the index contract: every job in `jobs/` appears in `jobs/INDEX.md` with a one-liner; every claim appears in `claims/INDEX.md`. A rebuild that leaves an entry unindexed has failed.

## Step 7 — report structurally, not "done"

The report is the deliverable. Specifically:

- What was **split**, and why.
- What was **merged**, with the IDs.
- What was **re-confidenced**, in both directions, with the reason.
- What was **retired**, and what supported the decision.
- What **stayed the same** — meaningful, because it says the old layer was largely sound.
- What raw material still supports **no** claim, and whether that looks like an unmined seam or genuinely thin material.

"Rebuild complete" with no detail defeats the purpose of doing one deliberately rather than letting the OS keep drifting.

## What this never does

Never edits, deletes, or rewrites anything in `raw/`. Never touches a layer whose role is not `derived`. Never drops provenance or sensitivity flags. Never renumbers existing IDs. Never finishes without the structural report.

## Write the disposition record

A rebuild that splits, merges or retires anything writes `usage/MIGRATION-<date>.md` the same way `corp-os-migrate` does: what changed shape, what was retired and why, and anything that came out of a grouping and did not go back into one.

The reason is the same in both cases. A structural pass is the moment where things quietly stop existing, and six months later nobody can tell a deliberate retirement from a loss. The record costs a paragraph and it is the only thing that can answer the question later.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-rebuild --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

- A dated `history` entry in `meta.json` summarizing the rebuild.
- A `usage/log.md` row — and if the rebuild found a systemic pattern, such as every claim from one source needing re-confidencing, that belongs in the friction field for `corp-os-improve`.
