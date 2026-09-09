---
name: corp-os-upgrade
description: Brings an existing Corp-OS up to date with a newer version of the plugin — refreshing the shipped scripts the OS carries its own copies of, recording which version it is now on, and naming the structural migrations the version gap implies. Use when someone updated or reinstalled the plugin, says their OS is on an old version, sees a warning from build_index.py that a newer plugin would explain, gets counts that look wrong after an update, or asks "does my OS need anything now". Not for reshaping an OS to fit the person (use corp-os-configure) and not for creating one (use corp-os-setup).
---

# Corp-OS upgrade

Updating the plugin does not update anyone's OS.

Every Corp-OS carries its own copies of the shipped scripts, because an OS should keep working when the plugin is not loaded, and because sixteen skills call them at the OS path rather than the plugin path. The cost of that is this skill. When `build_index.py` was fixed in 0.10.1 to count a single-file layer correctly, every OS created before it kept the copy that counts wrong, and nothing would ever have said so.

Read `${CLAUDE_PLUGIN_ROOT}/reference/configuration.md` — the migration section is what separates the two halves of this job.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — report before touching anything

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/upgrade_os.py --root <the OS>
```

Dry run by default. It reports three things, and they are not the same kind of thing:

- **Missing scripts.** The OS does not have one it should. Skills that call it fail against this OS today.
- **Stale scripts.** The OS's copy differs from the installed plugin's, compared by content rather than by date, because a file restored from a backup has a new date and old behavior.
- **Migrations.** The OS's *shape* is from an older model. Moving someone's files is not something a script decides.

If everything is current, say so in one line and stop. An upgrade skill that finds nothing and performs a ceremony anyway teaches people to stop running it.

## Step 1 — refresh the scripts

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/upgrade_os.py --root <the OS> --apply
```

This copies the missing and stale scripts, records the new version in `config.json`, and appends a `meta.json` history entry saying what happened.

**Step 0's report is the confirmation.** It already named every file that is about to be overwritten, which is the whole reason this script is dry-run by default — the same shape as `delete_source.py`, where the count is what makes the decision decidable. Show the report, then apply. Do not stop after the report and wait: someone who asked to bring their OS in line has already said yes to copying four files, and an upgrade run that ends in a summary of what it could have done has upgraded nothing.

There is exactly one reason to ask again first: the person says they edited one of the shipped scripts on purpose, or the OS's own `README.md` says so. Overwriting is otherwise correct, because these are shipped bookkeeping and deliberately not content.

**Then re-run the counter**, from inside the OS:

```bash
cd <the OS> && python3 scripts/build_index.py
```

A refreshed counter can report different numbers than the old one did. That difference is the entire reason for the upgrade, so say it out loud: *"your dashboards now count 3 rather than 1, which is what was actually there."* A number that silently changes reads as the tool being unreliable. A number that changes with a reason attached reads as the tool being fixed.

## Step 1.5 — the same check for an adopted pack

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/bind_pattern.py --root <the OS> --all
```

A pattern pack is this skill's own problem one layer up. Teammates carry copies of files someone else maintains, copies drift, and updating the pack updates nobody's OS — which is exactly why this skill exists for the shipped scripts. Same discipline, no second mechanism: compare by content rather than by date, say which patterns are behind, and refuse to perform anything structural.

Two findings come out of it. A pattern whose **content** differs from the pack's is behind, or was deliberately edited locally — report it either way rather than overwriting, because someone who diverged on purpose should be told they did, not corrected. And a pattern that no longer **binds** means this OS changed underneath it: a layer was disabled or renamed, and the output has been silently missing a panel since. That is a migration, not a refresh, so it goes to `corp-os-configure` with the rest.

## Step 2 — hand the migrations over

Do not perform them here. Each one moves or restructures the person's own files, which is exactly what `corp-os-configure` Step 1 exists to sort into safe changes and migrations — and a migration gets enumeration, a plan, and a confirmation before anything is written.

For each one the report named, say what it is, what it costs to leave alone, and offer `corp-os-configure`. Leaving one alone is a legitimate answer: an OS with a registry in the old place still works, it just under-counts, and someone with three dashboards and a deadline may reasonably not care this week. What is not legitimate is doing it silently while they thought you were copying files.

If they want it now, hand off to `corp-os-configure` with the migration named. Come back afterwards and re-run Step 0 to confirm it cleared.

## Step 3 — say what changed and what did not

Three lines, not a report:

- Which scripts were refreshed, and what the recount now says differently.
- Which migrations are outstanding, and what each one costs while it waits.
- The version the OS is now on.

If nothing was outstanding, that is one line: current, on this version, nothing to do.

## What this skill does not do

- **Reshape an OS to fit the person.** Adding a layer, renaming vocabulary, changing decay windows — `corp-os-configure`.
- **Create one.** `corp-os-setup`.
- **Update the plugin itself.** That is `/plugin marketplace update` in the person's client, and it happens before this skill is any use. If their plugin is old, this skill will faithfully bring their OS in line with the old one.
- **Fix content.** Stale claims are `corp-os-reality-check`; a drifted derived layer is `corp-os-rebuild`.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-upgrade --scope "<from version to version>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<scripts refreshed, migrations outstanding>"
```

Run it from inside the OS, after Step 1, so the row is written by the refreshed copy.
