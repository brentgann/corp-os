# Installing, and the two things called "update"

There are two updates in this project and they are not the same operation.

**Updating the plugin** replaces the skills. **Updating your OS** brings the folder those skills operate on in line with them — its copies of the shipped scripts, the version it records, and the shape changes a new model implies. Doing the first does nothing to the second, by design and permanently: every Corp-OS carries its own copies of the shipped scripts so that it keeps working when the plugin is not loaded, and sixteen skills call them at the OS path rather than the plugin path.

That gap is invisible when it bites. In 0.10.1 `build_index.py` was fixed to count a single-file layer correctly; every OS created before it kept the copy that counts wrong, and nothing anywhere would have said so. `corp-os-upgrade` exists because of that day.

---

## Install

### From the marketplace — the supported path

```
/plugin marketplace add brentgann/corp-os
/plugin install corp-os@brentgann
```

The first command reads `.claude-plugin/marketplace.json` from the repo root; the second installs the one plugin it catalogues. `corp-os` is the plugin, `brentgann` is the marketplace, and the `plugin@marketplace` form is how the client tells two same-named plugins apart. A full git URL works in place of the shorthand:

```
/plugin marketplace add https://github.com/brentgann/corp-os.git
```

The `/plugin` slash command is Claude Code's. In the **desktop app**, use the plugin browser UI instead — same marketplaces, same installs, different surface. In a **cloud or web session** where neither is available, declare it in `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "brentgann": ["corp-os"]
  }
}
```

### From a clone — for working on it

```bash
git clone https://github.com/brentgann/corp-os.git
claude --plugin-dir ./corp-os/plugins/corp-os
```

This loads the working tree for the current session, which is what you want while changing skills: edit a file, restart, run it. Nothing is cached and nothing is versioned, so there is no update step and no way to be stale.

### The packaged bundle

```bash
./build.sh          # validates, then writes dist/corp-os.plugin
```

`dist/corp-os.plugin` is a zip of `plugins/corp-os/`, and it is a build artifact rather than a distribution channel: installing a bundle file directly is not a documented path in any client, so do not tell people to. What it is good for is proving the package is well-formed, attaching a byte-exact copy of a version to a GitHub release, and loading that version later without a checkout — unzip it and point `--plugin-dir` at the directory.

### Then start

Ask for Corp-OS setup, or run `/corp-os`, which finds an existing OS or offers to build one. The setup interrogation is fifteen to twenty minutes and it is the deliverable as much as the folder is.

---

## Updating the plugin

```
/plugin marketplace update brentgann
```

That refetches the marketplace and the plugin content behind it. Then reinstall or confirm from the `/plugin` panel, whose **Installed** tab shows the version you are actually on. Auto-update is on by default only for official Anthropic marketplaces; for a third-party one like this, updating is something you do.

### The version pin, which is the part that surprises people

The client caches an installed plugin **by version string**, at `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. A cache hit loads from disk and touches the network not at all. So:

> **New commits without a version bump reach nobody.** Same version, different content, and every existing install keeps the old copy — with no error, no warning, and no way for the person running it to tell.

Which makes the release rule short: **the version in `plugin.json` is bumped on every release, or the release did not happen.** `scripts/validate.py` fails the build if `plugin.json` and `.claude-plugin/marketplace.json` disagree about which version that is, because two numbers that must match and are typed twice will eventually not match.

This is also why a documentation-only change to the plugin gets a version. `plugins/corp-os/README.md` ships *inside* the plugin, so a correction to it that skips the bump is a correction nobody receives.

### Confirming what you have

| Where | What it tells you |
|---|---|
| `/plugin` → Installed | the version of the plugin this client is running |
| `claude plugin details corp-os@brentgann` | the same, without the panel |
| `config.json` → `corpos_version` in an OS | the version that OS was last brought in line with |
| `meta.json` → `history` in an OS | what was done to it, and on what date |

The first two answer *what am I running*. The last two answer *what has this folder been through*, and they move only when `corp-os-upgrade` moves them.

---

## Updating your OS

Do this **after** the plugin update, not before. `corp-os-upgrade` faithfully brings an OS in line with whatever plugin is currently loaded, so running it against a stale plugin achieves an orderly nothing.

Ask for `corp-os-upgrade`, or run the same script it runs:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/upgrade_os.py --root <the OS>
```

`${CLAUDE_PLUGIN_ROOT}` is set for you when a skill runs. From your own terminal it is not, so substitute the path to `plugins/corp-os/` in the checkout or cache you installed from. `upgrade_os.py` is deliberately one of the two scripts an OS does **not** carry a copy of — a stale upgrader cannot report itself stale.

Dry run by default. It reports three things, and they are three different kinds of thing:

- **Missing scripts** — the OS does not have one it should, so skills that call it fail against this OS today.
- **Stale scripts** — the OS's copy differs from the plugin's, compared **by content and never by date**, because a file restored from a backup has a new date and old behavior.
- **Migrations** — the OS's *shape* is from an older model.

The first two are bookkeeping and the script performs them:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/upgrade_os.py --root <the OS> --apply
cd <the OS> && python3 scripts/build_index.py
```

Re-run the counter afterwards and read the difference out loud. A refreshed counter can report different numbers than the old one did, and that difference is the entire reason for the upgrade — a number that silently changes reads as the tool being unreliable, and a number that changes with a reason attached reads as the tool being fixed.

The third is not bookkeeping and the script refuses it. A migration moves or restructures your files, so `upgrade_os.py` names each one and hands it to `corp-os-configure`, which enumerates what it will touch and asks before writing anything. Migrations are detected from **the shape on disk**, never from the version an OS claims to be on, because the recorded version is the one field guaranteed to be wrong on an OS somebody edited by hand.

Leaving a migration alone is a legitimate answer. An OS with a registry in the old place still works, it just under-counts. What is not legitimate is performing one while somebody thought you were copying files.

Some schema changes ship a filler for the derivable half:

```bash
cd <the OS>
python3 scripts/migrate_schema.py --root . --list
python3 scripts/migrate_schema.py --root . --migration source_fidelity
```

It fills what is already written down somewhere else, **leaves the rest blank on purpose**, and reports both counts, because a blank field someone can see is honest and a plausible wrong value is the failure this whole model exists to prevent.

---

## Updating an adopted pattern pack

A pack is the same problem one layer up: teammates carry copies of files somebody else maintains, the copies drift, and updating the pack updates nobody's OS.

```bash
cd <the OS> && python3 scripts/bind_pattern.py --root . --all
```

Two findings come out of it and they need different answers. A pattern whose **content** differs from the pack's is behind, or was edited locally on purpose — report it either way rather than overwriting, because somebody who diverged deliberately should be told they did, not corrected. A pattern that no longer **binds** means the OS changed underneath it: a layer was renamed or disabled, and the output has been quietly missing a panel ever since. That one is a migration, and it goes to `corp-os-configure` with the rest.

---

## When something looks wrong after an update

| What you see | What it usually is |
|---|---|
| A count changed and you did not change anything | The refreshed counter is right and the old one was wrong. That is the upgrade working; `build_index.py` reads only what is on disk. |
| A skill the release notes mention is not there | The plugin did not actually update. Check the version in `/plugin` against `plugin.json` — if they match and the notes do not, the release skipped its version bump. |
| `python3 scripts/...` fails inside the OS | A script copy is missing. `upgrade_os.py --root <the OS>` names it. |
| A dashboard panel is empty | A pattern stopped binding. `bind_pattern.py --all` says which requirement, and an empty panel is never the right output — it reads as a state rather than a defect. |
| The OS reports a version older than the plugin | Expected. That field moves when `corp-os-upgrade` moves it, not when the plugin changes. |

---

## Releasing — for whoever maintains this

1. Make the change, and write the reasoning into `docs/ARCHITECTURE.md` §4 while you still remember it.
2. Bump `version` in **both** `plugins/corp-os/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`.
3. Add a version-history entry to `plugins/corp-os/README.md`. The validator requires one for the shipped version, on the theory that a change nobody can explain later gets reverted by accident.
4. Regenerate the skill map, because `build.sh` will not do it for you — it only checks:

   ```bash
   python3 scripts/build_skill_map.py          # rewrite docs/skill-map.html
   python3 scripts/build_skill_map.py --check  # what validate.py runs
   ```

   The generator refuses to run until every skill on disk has been placed in a phase, which is the one judgment nothing can derive.
5. Run `./build.sh`. It runs `scripts/validate.py` and packages only if that passes.
6. Push. Then say the words **run `/plugin marketplace update brentgann`**, because nothing in any client will say them for you.
