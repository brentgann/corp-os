---
name: corp-os-setup
description: Interrogates someone about their role, mandate, jobs to be done, valuable data, input paths, connected tools and protocols, company, design system, and sensitivity needs — then scaffolds a Corp-OS personal work knowledge base tailored to those answers and builds their first dashboard. Use when someone wants to "set up Corp-OS", "build a personal OS", "build a second brain for my work", "set up a knowledge base for my role", or asks to be onboarded into a work OS. Not for adding content to an existing OS (use corp-os-intake or corp-os-pull) and not for assessing a system someone already built by other means (use corp-os-audit).
---

# Corp-OS setup

> **Judgment pass** — the reasoning is the product here. Run it on your best model, and do not economise by skipping the questions it asks.

Interrogate first, scaffold second. The interrogation is the deliverable as much as the folder is — a scaffold built without it produces a generic notebook that gets abandoned in a month.

Read `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md` and `${CLAUDE_PLUGIN_ROOT}/reference/interrogation.md` before starting. Read `${CLAUDE_PLUGIN_ROOT}/reference/jtbd-patterns.md` when working on jobs in area 3.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — scaffold first, then interrogate

**Before the first question, run the scaffolder.** Check nothing already exists (below), then:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py --root <where the OS lives> --profile minimal
```

Say what you did in one line — "there's a working OS at that path now; the interrogation is about making it yours" — and move on. It takes a second and it is the difference between a session that ends with an OS and one that ends with a folder.

**Why this order, when the interrogation is supposed to shape the scaffold.** Run against an empty directory and asked to set up an OS for a contracts manager, this skill produced a *contracts filing system* — `agreements/`, `renewals.md`, `vendors/`, a template, a clause checklist. Sensible, useful to that person, and not a Corp-OS: no `INDEX.md`, no `meta.json`, no `config.json`, no `raw/`. Nothing else in the suite could operate on it.

That observation stands. The measurement that used to be cited here does not, and the correction matters more than the paragraph. Six runs were read as *"scaffolding first did not fix it, so the domain must be overpowering the instruction"* — and the scaffolder had in fact never executed, because the eval harness could not run a script at all (ARCHITECTURE §4.27). With that fixed, this skill produces a valid OS in every run. **Scaffolding first works.** Nothing here needed the three instruction passes that were made when the failure looked real.

Two pressures cause it and both are legitimate. A person describes their work in their own vocabulary and this skill is *right* to adapt to it. And a person who says "I'd rather see something than answer twenty questions" is asking for exactly what they should get. Neither is a reason to hand back something the rest of the suite cannot read. Scaffolding first satisfies both: the invariants are on disk before the domain can push them off it, and the person sees something immediately.

It also fixes the more common failure. The likeliest way this skill fails is not a wrong answer, it is someone abandoning the interrogation halfway — and scaffolding first means they still have a working OS when they do.

The scaffold is minimal and empty on purpose. Everything after this makes it theirs: the layers they actually need, their vocabulary, their decay windows, their README in their words.

## Step 0.5 — check nothing already exists

**If they already have a body of work** — a wiki, a notes app, a previous second brain, a folder of documents — scaffold and interrogate here as normal, then hand off to `corp-os-migrate` rather than filing any of it yourself. Bringing material across has its own failure modes (a cohort ceiling nobody set, dates replaced by today's, decay that all fires on one day, and no record of what was deliberately left behind), and none of them is visible until months later. Say so in one line and finish this skill first: the interrogation decides the shape the material lands in, so doing it afterwards means reshaping around whatever the migration happened to produce.

Look for an existing Corp-OS root — `INDEX.md` + `meta.json`, with `config.json` beside them as confirmation — wherever the person means. If one exists, stop and say so: this skill does not re-scaffold over a live OS. Offer `corp-os-jobs` to add jobs, `corp-os-configure` to reshape structure, or `corp-os-rebuild` to re-derive.

**Never make the presence of `jobs/`, `claims/`, or any other layer part of that test.** Those layers are optional by design, and a `jobs`-disabled OS that reads as "no OS" is one confirmation away from being overwritten — the only path in this suite that destroys a working system.

If a knowledge system exists but is not corp-os-shaped, offer `corp-os-audit` instead of converting it unasked.

## Step 1 — run the interrogation

Work the nine areas in `interrogation.md`: role and mandate, intent for the OS, jobs to be done, what data earns its keep, input paths, tools and protocols, company and market, output and design, sensitivity.

How to run it:

- Ask in batches of two to four. Reflect back what was heard before moving on.
- **Enumerate, don't ask them to guess.** In area 6, check what connectors and design skills are actually available in this environment and confirm against that list. Asking "what tools do you have connected?" wastes the one thing this environment knows better than the person does.
- Push once on an abstract answer, then accept it and mark it low readiness. Do not interrogate someone into a crisper answer than they have.
- Supply shapes, never domain content. This suite ships no role templates on purpose.

Leave the interrogation with three to five jobs, not fifteen.

## Step 2 — confirm the shape before writing

Summarize back, in plain language: the jobs, which sources feed which jobs, which optional layers they asked for, whether sensitivity tracking is on, and where the OS will live. Get a yes.

Name what is deliberately being left out and why — a declined source is a decision worth recording, and saying it out loud now prevents it being re-litigated monthly.

## Step 3 — shape the scaffold to the answers

The skeleton is already on disk from Step 0. This step makes it theirs.

Re-run the scaffolder with what the interrogation actually established — it is safe to point at the same root with `--force` since nothing has been written into it yet:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py --root <path> --force \
    --profile <profile> --layers <what they asked for> --vocab claim=<their word>
```

Anything the shipped model has no name for is a **custom layer**, and the scaffolder deliberately refuses to guess at one. Declare it in `config.json` by hand with its own `entry_schema` and `index_line`, per `${CLAUDE_PLUGIN_ROOT}/reference/configuration.md`. A layer with no `index_line` is invisible to the scan contract.

Create `proposals/` alongside them — the review gate writes there, so it is not optional.

Then create only the optional layers they asked for: `claims/`, `glossary.md`, `company/`, `connectors.md`, `design.md`, `dashboards.md`.

**Do not scaffold a layer you cannot write a schema for.** A person layer, a topic layer, anything the interrogation turned up that the shipped model has no name for — each is a declared layer with its own `entry_schema` and `index_line`, or it is not created. A folder that exists, appears in `INDEX.md`, and has no stated record shape fills with whatever the first session to touch it invented. If area 4 called for one, write the declaration now per `${CLAUDE_PLUGIN_ROOT}/reference/configuration.md`; the `relationship` profile carries a worked `people` declaration to copy.

Sensitivity is two fields, not one — `sensitivity` for what must not leave, `bearing` for whether the OS can reason correctly without it. Say that plainly in area 9 if anything sensitive comes up, because the person's instinct will be that sensitive means hidden, and hiding load-bearing material from its own owner is what makes an OS quietly wrong.

If area 9 turned up anything sensitive, create `sensitive.md` now and write into `INDEX.md` that it exists but is deliberately **not** linked from the scan path. A quarantine file added after the fact means retrofitting content out of files it has already been scanned and shared from.

**The scripts are already in `scripts/` — the scaffolder copied them in Step 3.** Do not copy them again by hand, and do not maintain a list of them here: this instruction listed two of them for three releases after there were four, which is the same defect it is written to prevent. `scaffold.py` is the one place that list lives.

They all exist for the same reason: a step that has to happen every time, that nothing else will catch if it is skipped, belongs in code rather than in an instruction. Point the person at them once, in their own README, so they know the counts are regenerated rather than hand-kept.

They also mean this OS keeps working when the plugin is not loaded — and that the OS will not receive plugin fixes on its own. `corp-os-upgrade` is what closes that gap later; there is nothing to do about it now.

Use the shapes in `data-model.md` exactly for frontmatter and field names — every other skill in this suite depends on finding them where the spec says. Adapt prose and section wording to the person's own vocabulary.

**Write `config.json`.** This is what makes the OS the person's shape rather than the shipped one, and it is the file every other skill reads first. Per `${CLAUDE_PLUGIN_ROOT}/reference/configuration.md`:

- Start from the structural profile the interrogation pointed at — `minimal` is the honest default for most people and grows easily.
- Set `layers` to exactly what they asked for, each with its `role`. Anything they described that the shipped model has no name for becomes a custom layer with its own `entry_schema` and `index_line`; a layer without an `index_line` is invisible to the scan contract.
- Rename anything in `vocabulary` they have a better word for. "Claim" is wrong in several fields, and being stuck with it is a real reason people abandon a system.
- Set `decay.by_kind` deliberately rather than leaving it at the default. Ask what rots fastest in their work — that answer beats any shipped guess.
- Set `retention.raw` to `keep` unless they named a real obligation. Do not offer `delete` unprompted.
- Leave `gate.mode` at `propose`. It gets loosened later, once they know what the gate costs them.

`claims/` is effectively mandatory in practice: without it there is nowhere for reviewed knowledge to live and the OS is just a tagged archive. Recommend it plainly rather than presenting it as one option among many, but respect a no.

## Step 4 — write the OS's own README

This is the step most likely to get skipped and the one that determines whether the OS survives. Write a `README.md` in the OS root covering:

- What this OS is for, in the person's own words from area 2.
- The two-layer split and why the review gate exists.
- The entry schema — source, confidence, sensitivity, decay — with the labels they chose.
- The scan-from-INDEX rule, and that `sensitive.md` sits outside it.
- The pre-flight rule, and that these files outrank an agent's memory of past sessions.
- Any cohort confidence ceiling, if material is being migrated in from a previous system.
- A "how this gets operated" section naming each job and which skill handles it.

The OS has to be legible to someone who opens the folder without this plugin loaded. Conventions that live only in the plugin are conventions that break.

## Step 5 — bind the design system

If `design.md` was requested, write which design system or design skill governs rendered output, and how to invoke it. If a design skill is available in this environment, name it explicitly. If none, note that outputs will use a restrained default and that binding one later is a one-line change.

## Step 6 — register connectors, do not pull

Write `connectors.md` from area 6: category, protocol, auth shape, what it feeds, jobs served, cadence, status, and blind spots. Include `not-connected` entries with the reason.

**Do not pull any data during setup.** Setup builds the container. First intake is a separate, deliberate run so the person sees what it does.

## Step 7 — build the first dashboard

Build one, not four. Default to the job board unless the interrogation pointed clearly elsewhere — area 4 answers about what they keep re-looking-up usually name the right first panel.

Hand off the actual build to `corp-os-dashboard`, which reads the pattern library itself — reimplementing it here duplicates the skill that owns it. If the interrogation named a panel shape the job board does not cover, read `${CLAUDE_PLUGIN_ROOT}/reference/dashboard-patterns.md` first so the hand-off names a specific pattern rather than a wish. Panels can be near-empty at this stage; that is fine and honest. An empty evidence-gaps panel that says "nothing captured yet — run corp-os-pull" is doing its job.

## Step 8 — verify, log, and hand off with one action

Verify programmatically: every file the spec calls for exists, every job in `jobs/` appears in `jobs/INDEX.md` with a one-liner, counts in `meta.json` and `INDEX.md` match an actual count.

Close the run with the script the scaffolder copied in:

```bash
python3 scripts/log_run.py --skill corp-os-setup --scope "<the shape they chose>" \
    --friction "<where the interrogation stalled, or 'none'>" \
    --event "scaffolded from the <profile> profile"
```

It writes the `usage/log.md` row and the dated `meta.json` history entry together. Use it here rather than writing either by hand — this is the one run where the person is watching, so it is also where they learn the tool exists.

The friction field matters more on this run than on any other. "Could not state a definition of done for two of three jobs", "had no idea what their connectors were called" — that is what `corp-os-improve` reads later, and setup is the only run that sees the person before they have adapted to the system.

Then name **one** next action and offer to do it — pulling from their highest-value connector, or adding the meeting notes from this week. Do not leave someone with an empty, well-organized folder and a list of options.
