---
name: corp-os-migrate
description: Brings an existing body of work into a Corp-OS — a previous knowledge system, a wiki or notes-app export, a folder of documents, a hand-grown second brain — filing it into the append-only raw layer, setting a cohort confidence ceiling for material whose originals cannot be re-fetched, spreading decay windows so the first sweep is clearable, and recording what did not come across and why. Use when someone says "I have six months of notes to bring in", "migrate my old system", "import my wiki", "move my second brain into this", or has just set up an OS and has existing material waiting. Not for one pasted item (use corp-os-intake), not for a source that is already registered (use corp-os-pull), and not for creating the OS itself (use corp-os-setup).
---

# Corp-OS migrate

> **Judgment pass** — the reasoning is the product here. Run it on your best model, and do not economise by skipping the questions it asks.

Setup builds an empty OS. This fills one from work that already exists, which is a different act with different failure modes — and it is what almost every real first day looks like, because someone who wants a knowledge system usually has six months of notes and a wiki they are tired of.

Read `${CLAUDE_PLUGIN_ROOT}/reference/claim-record.md` and `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md` before starting, and the OS's own `README.md` if it has one.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

**There must already be an OS.** If `INDEX.md` and `meta.json` are not there, this has nothing to migrate into: run `corp-os-setup` first, then come back. Do not scaffold one silently — the interrogation is what decides the shape the incoming material lands in, and doing it afterwards means reshaping around whatever the migration happened to produce.

## Step 0 — count it before touching it

Get the size and the shape, and say both out loud. A migration is the one operation where the person's estimate is routinely wrong by an order of magnitude, and where the right plan depends on which.

- **How many items, and of what kinds?** Notes, meeting summaries, documents, a database export, a wiki tree.
- **How much of it has a retrievable original?** This is the question that decides everything downstream. A meeting summary whose transcript is still fetchable is a different object from one whose source was a tool the person no longer pays for.
- **What is already structured?** Existing tags, dates, authors, statuses. Structure that survives is structure nobody has to re-derive.

Report it as counts, not adjectives. *"412 files: 280 meeting summaries, 90 documents, 42 loose notes. About 300 have a source you can still get to; 112 do not."*

## Step 1 — decide what does not come across, first

Before anything is written. This is the step that gets skipped, and skipping it is why nobody can later tell the difference between material that was deliberately left behind and material that was lost.

Three honest outcomes, and all three are common:

- **Comes across as source.** It records something someone said or wrote. Into `raw/`.
- **Does not come across.** Errands, calendar logs, meeting attendance records, drafts superseded twice over, anything whose only content is that a conversation happened. A knowledge base is not an archive — and in one audited migration, roughly a fifth of the prior system's "resolved" tier turned out to be meeting logs filed as closed questions, which had been inflating its headline count for months.
- **Comes across, but changed.** A structure that mixed forms — findings, errands and open questions in one list — gets split, and the split is a decision worth recording as one.

Propose the disposition and get it confirmed before writing anything. If the person wants everything, say plainly what that costs: every item that comes across is an item the sweep will carry forever.

## Step 2 — write raw, append-only, with the original dates

Each item becomes a file in `raw/` under the shipped naming shape, with frontmatter carrying `source`, `person`, `date`, `type`, `tags`, `external_id`, `processed: false`. If any of those fields is ambiguous for this source, read the raw-file spec in `${CLAUDE_PLUGIN_ROOT}/reference/records.md` — `external_id` is what every later dedupe reads.

**Use the original date, never today's.** The date is what makes elapsed time recoverable, and elapsed time is the primary ranking signal for everything about what has not been settled. One audited migration stamped every item with its migration date and lost six months of age in a single pass, with nothing recording that it had happened.

Where an item carries an instruction that overrides where its derived content should live — *"this stays out of her person record"* — write `placement:` into that raw file's frontmatter now, per `${CLAUDE_PLUGIN_ROOT}/reference/claim-record.md`. An instruction that lives only in a derived file is an instruction a rebuild will not read.

## Step 3 — set the cohort ceiling before minting a single claim

A migrated corpus is structurally weaker than one built from live capture, and it is weaker in a way per-claim judgment cannot catch — because every claim in the batch looks equally plausible on its own.

Record a ceiling in `meta.json` under `confidence_ceilings`, with its reason and its escape route, per `${CLAUDE_PLUGIN_ROOT}/reference/configuration.md`. Two ceilings usually apply and they are not the same:

- **Material with a retrievable original** — a summary whose transcript can still be fetched. Ceiling with an escape route: *one call promotes it.* Say so in the ceiling's own note, because a ceiling that reads as permanent gets treated as permanent, and in one audited corpus 599 claims sat one API call from promotion with zero having taken it.
- **Material whose original is gone** — reconstructed from a tool that no longer exists, or from memory. Nothing can ever re-confirm these. They need a one-time disposition pass rather than a decay window, and `corp-os-reality-check` handles them as their own bucket.

Do not merge these two into one ceiling. The whole point is that the record can tell "cheap route available" from "unrecoverable".

## Step 4 — mint claims through the gate, in batches

`corp-os-claims` does the work; this skill decides the batching. Go job by job or topic by topic, not file by file, and write a proposal per batch so the gate leaves a trail proportional to what is entering.

Do not attempt the whole corpus in one pass. A migration that mints four hundred claims behind one proposal has a gate in name only.

## Step 5 — spread the decay before anyone sees the first sweep

```bash
python3 scripts/stagger_decay.py --root <the OS>
```

Everything just verified on the same day comes due on the same day. Measured in a real migrated corpus: 79 entries due on one date, 71 on another, **410 on a third**. The first sweep is then unclearable, and the rubric's own finding is that a backlog nobody can clear teaches people to skip the sweep permanently. A migrated OS is otherwise born with its most important discipline pre-broken.

The script spreads the **windows**, deterministically, and never the `Verified` dates — the window is a policy choice, the verification date is a fact about the past. Show the person the before-and-after distribution; it is dry-run by default for exactly that reason.

## Step 6 — write the disposition record

```
usage/MIGRATION-<date>.md
```

The artifact that makes a migration auditable rather than something to be trusted. In one real case it was the only reason an audit could verify a migration at all, and nothing in the model had asked for it — the operator happened to write one.

Four sections, and the second is the one that matters:

1. **What came across** — counts by kind, and where each kind landed.
2. **What did not, and why** — a row per item or per class. This is the section nobody can reconstruct later, and it is the reason the file exists.
3. **What changed shape** — a structure that was split or merged, with the reasoning. *"146 items in one urgency-tiered list became 18 decisions and 42 evidence items; the tiering was dropped because a decide-by date expires and a tier does not."*
4. **What is still unresolved** — anything with no home yet, named rather than quietly dropped.

Record any losses honestly, including the ones nobody chose. *"All amendment dates were dropped; the prior system had them and the shipped model has nowhere to put them"* is exactly the sentence an audit six months later needs, and exactly the one that never gets written unless a step demands it.

## Step 7 — recount, and say what the OS now holds

```bash
cd <the OS> && python3 scripts/build_index.py
```

Then check the boundary before anything derived from this leaves:

```bash
python3 scripts/check_citations.py <the OS>
```

A bulk migration mints many claims from the same sources in several passes, which is exactly the condition that produces two claims from one quote classified differently. Better found now than at an export.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-migrate --scope "<what came across>" \
    --friction "<where it hurt, or 'none'>" \
    --event "migrated <n> items; <n> not carried; ceilings set"
```

A migration is the single most informative run an OS ever has, and it is the one where the friction field is most likely to be left blank because everyone is tired. Write it anyway — the next person migrating is reading it.
