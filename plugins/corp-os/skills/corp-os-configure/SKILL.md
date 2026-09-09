---
name: corp-os-configure
description: Changes how a Corp-OS is shaped — renaming its vocabulary, adding or disabling layers, defining an entirely new custom layer with its own schema, adjusting decay windows, setting a retention or TTL policy on raw material, and tuning how strict the review gate is — handling any change that needs a migration as a migration. Use when someone says "add a layer for X", "call them findings instead of claims", "my raw folder is getting huge", "set a TTL on my sources", "change my decay windows", "loosen the review gate", or "this structure doesn't fit how I work". Not for setting up a new OS (use corp-os-setup) and not for content accuracy (use corp-os-reality-check).
---

# Corp-OS configure

The shipped model is a default profile, not a schema. This skill changes the profile.

Read `${CLAUDE_PLUGIN_ROOT}/reference/configuration.md` before touching anything.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

Read the OS's `README.md`, `meta.json`, and enough of the affected layers to know what a change would actually hit. If there is no `config.json`, this OS is running on shipped defaults — write one reflecting its *current* actual state first, then make the requested change on top. Never write a config that describes a shape the OS is not already in.

## Step 1 — separate the safe changes from the migrations

Say which kind this is before doing anything, because the person's expectations differ completely.

**Safe** — renaming vocabulary, adding a layer, adding a field, loosening decay, changing dashboard target or brief cadence. Apply, log, done.

**Migration** — needs enumeration, a plan, and a confirmation:

- Disabling a layer. Its content has to go somewhere; never orphan a folder.
- Removing a vocabulary value. Every entry using it needs remapping.
- Tightening decay. Will immediately mark a share of the corpus overdue.
- Any retention change toward `delete`.
- Changing a layer's `role` from `derived` to `source`, or the reverse.

**Always lead with the count.** "Tightening pricing decay to 30 days will mark 47 claims overdue as of today" is a decision someone can make. "This will mark some claims overdue" is not, and the next sweep will look like a catastrophe instead of a backlog.

## Step 2 — renaming vocabulary

Renaming changes what the person reads, never what skills mean. A `claim` renamed `finding` still needs a source, a confidence, and a decay window.

Update `config.json`, then update the OS's `README.md` so the folder stays legible to someone who opens it without this plugin loaded. Existing files keep their paths — rename the label, not the directory, unless the person specifically wants the churn.

Push back once, gently, if someone wants to **remove** a semantic rather than rename it. Dropping `assumption` from `kinds` does not simplify the model; it removes the ability to distinguish what was observed from what is believed, which is the distinction that keeps the OS honest with its owner. Say what it costs, then respect the answer.

## Step 3 — adding a custom layer

The interesting case, and the one where the model earns or loses its portability.

Interrogate the shape before writing it:

1. **What is one entry?** Get a concrete example, not a category name.
2. **What is its `role`?** `source` (its own truth, never regenerated), `derived` (regenerable from raw), or `record` (an audit trail). This is the field that destroys data when wrong — a `source` layer mislabeled `derived` gets overwritten by the next rebuild with nothing to restore from. **Default to `source` when there is any doubt**; that is the direction that fails safely.
3. **What fields does an entry carry, and which are required?**
4. **What does one line of it look like in `INDEX.md`?** Write the `index_line` template. This is not cosmetic: without it the layer becomes a folder that must be opened to be understood, and the scan contract degrades one layer at a time.
5. **Is it a category or a tier?** A tier — insights, decisions of record, confirmed findings — needs a `promotion_bar` written as prose, or it fills with everything adjacent and stops being read.
6. **Does it carry provenance?** It should. A layer that opts out of source and confidence is a notes folder with extra steps, and `corp-os-reality-check` cannot see it.
7. **Is it gated?** Almost always yes for anything `derived`.

Then write the layer block, scaffold the directory with a README stating what belongs there, add it to the OS's own README, and run `build_index.py` so it appears in the index immediately. A layer that exists on disk but not in `INDEX.md` is invisible to every other skill.

## Step 4 — retention and raw TTL

When someone asks to expire raw material, find out what is actually wrong first. The complaint is almost always "raw/ has grown unwieldy," and the fix for that is **`archive`** — moved out of the scan path, still on disk, fully rebuildable, completely reversible. Offer that before anything destructive.

Reach for `delete` only when there is a real obligation: a retention schedule, an NDA clause, a customer's deletion right, a regulatory requirement. `reason` is required and should name the obligation. "Housekeeping" is not a reason to destroy source material.

### If it is `delete`, run the script

Not file management, and not something to carry out by hand. `scripts/delete_source.py` in the OS does the whole sequence in the order that cannot be got wrong:

```bash
python3 scripts/delete_source.py --dry-run <paths> --os-root .
python3 scripts/delete_source.py --apply <paths> --reason "<the obligation>" --os-root .
```

It finds every entry citing the file and reports the count; re-cites each to `no source` and drops `confirmed` to `reconstructed`, scoped to the citing entry rather than the whole file; records a cohort ceiling in `config.json` so no later pass promotes them back; logs what is being destroyed and under what obligation in `meta.json`; then writes a tombstone beside the original and unlinks it.

**Always run `--dry-run` first and show the person the count**, because that is the decision: "this destroys the source behind 14 entries, all of which drop to `no source`" is something someone can weigh. "This will delete some files" is not.

`--apply` refuses without `--reason`, and the reason should name the obligation — a clause, a retention schedule, a customer's deletion right. Measured, the hand-run sequence wrote the tombstone by editing the original file two times in three: an edit to a raw file, which is the one operation `raw/` never permits and the one whose failure destroys source material. That is why it is a script.

Afterwards, run `scripts/build_index.py` to recount.

Set `measure_from` to `frontmatter_date`, never filesystem mtime. A sync or a restore from backup changes mtime on everything at once, which would trip or reset every TTL in the corpus simultaneously.

Always offer to write the exceptions before applying a policy. Contracts, decisions of record, and anything legal-adjacent should be `keep` regardless of age.

## Step 5 — decay and gate

**Decay.** `by_kind` does the most work: decisions and constraints are usually `none`, metrics rot fastest. If everything is sitting at the default, say so — nobody set them thoughtfully and the sweep will surface noise. Turning decay off entirely is legitimate for a short-lived, single-project OS; say what it costs (nothing will ever flag a stale entry) and respect the answer.

**Gate.** If the complaint is that reviewing is tedious, `propose_batched` is the right answer, not a looser gate — volume is what turns a gate into a rubber stamp. If someone wants `trusted_sources`, name the cost plainly: every claim from that source enters the derived layer unreviewed. A filing, a query result, an audit export can qualify. Nothing conversational, summarized, or model-generated does.

## Step 6 — write, log, and verify

Write `config.json`, update the OS's `README.md` to match, add a dated `meta.json` history entry saying what changed **and why** — a config whose current state cannot be explained is a config nobody will dare edit later.

Then run `build_index.py` and report any drift the change introduced.

## Offering the arguments layer

Optional, and offered rather than scaffolded. It holds a conclusion built across entries, with a `timing` field and a `Rests on` list — the thing no shipped layer can express.

Offer it to a decision-heavy or orientation-shaped role. Do not offer it to a build-heavy or operate-heavy one: they would write two a year and the layer would read as overhead, which is how an unused layer becomes a cost rather than a neutral.

Two things to get right at declaration time, because both are expensive later. Ship **one** dependency field, not two — the OS this came from declared both `connections` and `rests_on`, populated both on all 23 entries, and stated the difference nowhere. And do **not** add a hand-set strength rating: the prior system had one, it was dropped as decorative, and its real function was counting independent witnesses, which `rests_on` derives for free and which cannot go stale.

## When a pattern refuses to bind

`bind_pattern.py` refuses when a pattern needs a role or field this OS does not declare, and it names exactly which. That refusal is the reason to be here, and the interrogation in Step 3 is what it is for.

Declare the layer properly or decline it — both are answers. What is not an answer is loosening the pattern until it binds: a requirement weakened to make a refusal go away produces an output that renders an empty panel, which reads as a state rather than a defect and so never gets investigated.

If a layer already exists and the pattern still refuses, the usual cause is a missing `entry_schema`. Declaring one is cheap and it is what makes every future binding checkable rather than hopeful.

## Every non-regenerable file is a declared layer

If a file holds content that a rebuild could not reproduce from `raw/`, it is a layer and it needs a `role` — even when it is one file rather than a directory, and even when it is deliberately outside the scan path.

Listing it in `scan.excluded_from_scan` is **not** a declaration. That keeps it out of the scan path and leaves it roleless, which is the state that caused the only irreversible failure in the audit record: a quarantine file named nowhere but the exclusion list, holding the sole copy of an operator instruction, invisible to every skill including the one that would have overwritten it.

`build_index.py` reports undeclared root files on every run for this reason. Declare them here with a role and `in_scan_path: false` where that applies.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-configure --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

- A `usage/log.md` row.
- A plain statement of what changed, what it will do the next time each affected skill runs, and — for a migration — exactly how many entries were touched.
