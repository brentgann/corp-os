---
name: corp-os-configure
description: Changes how a Corp-OS is shaped — renaming its vocabulary, adding or disabling layers, defining an entirely new custom layer with its own schema, adjusting decay windows, setting a retention or TTL policy on raw material, and tuning how strict the review gate is — handling any change that needs a migration as a migration. Use when someone says "add a layer for X", "call them findings instead of claims", "my raw folder is getting huge", "set a TTL on my sources", "change my decay windows", "loosen the review gate", or "this structure doesn't fit how I work". Not for setting up a new OS (use corp-os-setup) and not for content accuracy (use corp-os-reality-check).
---

# Corp-OS configure

The shipped model is a default profile, not a schema. This skill changes the profile.

Read `${CLAUDE_PLUGIN_ROOT}/reference/configuration.md` before touching anything.

## Pre-flight

Confirm the OS is accessible right now, not recalled. Read its `config.json`, `README.md`, `meta.json`, and enough of the affected layers to know what a change would actually hit. If there is no `config.json`, this OS is running on shipped defaults — write one reflecting its *current* actual state first, then make the requested change on top. Never write a config that describes a shape the OS is not already in.

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

### If it is `delete`, this is a claim-integrity event

Not file management. Run it in this order, and say so out loud:

1. **Find every claim citing the affected files.** All of them, across every layer. Report the count before proceeding.
2. **Re-cite each to `no source`** and **lower its confidence** — `confirmed` drops to `reconstructed` at best, because the thing that made it confirmable is being destroyed. Record the reason and date on each.
3. **Add a cohort ceiling** in `config.json` so no later pass promotes them back.
4. **Log it** in `meta.json`: what was deleted, under what obligation, how many claims were affected.
5. **Then** remove the files.

Skipping steps 1 and 2 leaves claims citing files that do not exist — worse than `no source`, because they still look sourced and nothing downstream can detect the difference.

Set `measure_from` to `frontmatter_date`, never filesystem mtime. A sync or a restore from backup changes mtime on everything at once, which would trip or reset every TTL in the corpus simultaneously.

Always offer to write the exceptions before applying a policy. Contracts, decisions of record, and anything legal-adjacent should be `keep` regardless of age.

## Step 5 — decay and gate

**Decay.** `by_kind` does the most work: decisions and constraints are usually `none`, metrics rot fastest. If everything is sitting at the default, say so — nobody set them thoughtfully and the sweep will surface noise. Turning decay off entirely is legitimate for a short-lived, single-project OS; say what it costs (nothing will ever flag a stale entry) and respect the answer.

**Gate.** If the complaint is that reviewing is tedious, `propose_batched` is the right answer, not a looser gate — volume is what turns a gate into a rubber stamp. If someone wants `trusted_sources`, name the cost plainly: every claim from that source enters the derived layer unreviewed. A filing, a query result, an audit export can qualify. Nothing conversational, summarized, or model-generated does.

## Step 6 — write, log, and verify

Write `config.json`, update the OS's `README.md` to match, add a dated `meta.json` history entry saying what changed **and why** — a config whose current state cannot be explained is a config nobody will dare edit later.

Then run `build_index.py` and report any drift the change introduced.

## Every run ends with

- A `usage/log.md` row.
- A plain statement of what changed, what it will do the next time each affected skill runs, and — for a migration — exactly how many entries were touched.
