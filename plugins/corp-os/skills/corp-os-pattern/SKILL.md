---
name: corp-os-pattern
description: Turns an output someone has already built — a dashboard, an export, a deck, a recurring document — into a portable pattern that other people's OSes can bind, and adopts patterns from a shared team pack. A pattern addresses layers by role and field rather than by name, so it survives an OS that renamed its vocabulary, and binding either resolves or names exactly what is missing. Use when someone says "make this repeatable", "share this dashboard with my team", "adopt our team's pack", "why does everyone's output look different", "turn this into a pattern", or when a pattern will not bind. Not for reshaping this OS's own layers (use corp-os-configure) and not for proposing changes to the corp-os plugin itself (use corp-os-contribute).
---

# Corp-OS pattern

One operator keeps their conventions in their head. Five operators produce five dashboards with five palettes and five ideas about what a panel owes the reader, and nothing about the model prevents it.

A pattern is the fix: a portable spec for producing one kind of output, carrying what it needs from an OS, what it must contain, what it refuses to do, and the generator that builds it.

Read `${CLAUDE_PLUGIN_ROOT}/reference/patterns.md` — it is the shape, the binding contract, the shield, and the composition rules every rendering pattern inherits.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — which direction

Two, and they need different conversations:

- **Authoring** — they built something and want it repeatable, or shareable with a team. Go to Step 1.
- **Adopting** — someone handed them a pack. Go to Step 4.

If they are asking why everyone's output looks different, the answer is that nobody has authored one yet. Start at Step 1 with whichever output they like best.

## Step 1 — interrogate the thing they built

This is the whole skill. Everything else is bookkeeping.

The output in front of you was built against one OS, and most of what it knows is accidentally specific to it. Separating what generalizes from what is only true here is the judgment nothing else can do, and getting it wrong produces a pattern that binds in exactly one place and fails silently everywhere else.

Four questions, and the first is the one that matters:

**Which layers did it actually read, and what did it read from them?** Not the folder names. The **role** each layer plays and the **fields** it used. *"It reads `claims/`"* is not portable. *"It reads the derived layer that carries a citation and a confidence"* is, and it binds in an OS that calls them findings.

**What would break it?** A missing layer, a field with no values, an empty corpus, a layer whose entry count runs to thousands. Anything that would break it is either a `requires:` entry or a `refuses:` line.

**What did you have to be careful about?** The things they got wrong first. Those become `## Refuses`, and they are the most valuable part — a rule stated without its reason gets simplified away by the next person, so keep the failure attached.

**Is any of it judgment that cannot be computed?** Authored commentary, a hand-set ordering. Keep it, keep it in one named place, and say in the pattern that it is the only authored part. Anything else authored is a smell, and authored prose is also the one thing a shield has nothing to inherit sensitivity from.

## Step 2 — write the pattern and move the generator

Write `patterns/<kind>-<slug>.md` in the shape `reference/patterns.md` specifies, then move the build script into the OS's `scripts/`.

**The script is the artifact; the output is its product.** A hand-written dashboard had wrong counts within a day — the same failure `build_index.py` exists to prevent, one directory over. Putting the generator in the OS also means the output is rebuildable when the plugin is not loaded, which is the same argument that puts `build_index.py` there.

Set `target:` and `shield:` deliberately rather than by default. An output that reads the scan path renders sensitive material, because `bearing` keeps load-bearing sensitive entries there on purpose. A job board can publish; a stakeholder map should not.

## Step 3 — bind it against this OS, then against a different one

```bash
python3 scripts/bind_pattern.py --root <the OS> --pattern patterns/<file>.md
```

Binding against the OS it was written in proves almost nothing — it was written there. **Bind it against a second OS if one is reachable**, or at minimum read the requirements back and ask whether each would resolve in an OS that renamed its vocabulary, disabled a layer, or never declared one.

Three outcomes and no fourth: bound, bound with drops, or refused. A refusal that names the missing role is the pattern working. A pattern that binds everywhere without ever dropping anything usually has requirements too loose to mean anything.

## Step 4 — adopting a pack

A pack is a folder: `pack.json`, `patterns/`, `assets/`, `scripts/`. Copying it is the entire distribution mechanism.

Copy it in, then bind everything at once:

```bash
python3 scripts/bind_pattern.py --root <the OS> --all
```

Walk the results with them. For each refusal there are exactly two answers, and both are legitimate:

- **Declare the missing layer** — hand off to `corp-os-configure`, whose Step 3 interrogation is what stops a layer being shaped wrong in passing.
- **Take the pack without that pattern** — say which view they are giving up.

What is not an answer is rendering it anyway. An empty panel reads as a state rather than a defect, and nobody investigates it.

Record which pack and version the OS is on, so drift is detectable later. `corp-os-upgrade` compares adopted patterns against the pack by content and reports what has fallen behind.

## Step 5 — verify before calling it done

Run the pattern's own `## Verification` section. For anything declaring `shield: required`:

```bash
python3 scripts/check_shield.py <the built file> --probes usage/probes.txt
```

The probe list is the part a person maintains, and it is out of the scan path. On a real build this test found three leaks in a shield its author believed worked.

Two checks it cannot do, both by hand: round-trip the toggle outside a browser, and diff every derived aggregation shield-up against shield-down. The second catches the leak nobody predicts — results correctly stubbed while the *"who said it"* panel counted their speakers anyway, because the name is the disclosure.

## What this skill does not do

- **Reshape this OS's layers.** Declaring a layer is `corp-os-configure`, and a failed binding hands off to it.
- **Change the corp-os plugin.** Proposing a change upstream is `corp-os-contribute`. The distinction is the target: a pattern goes in a pack, a plugin change goes in the repo.
- **Build the output.** `corp-os-dashboard` binds a pattern and runs its generator. This skill produces the pattern.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-pattern --scope "<authored or adopted what>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<pattern name; bound / refused with what missing>"
```
