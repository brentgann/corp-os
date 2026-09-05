---
name: corp-os-setup
description: Interrogates someone about their role, mandate, jobs to be done, valuable data, input paths, connected tools and protocols, company, design system, and sensitivity needs — then scaffolds a Corp-OS personal work knowledge base tailored to those answers and builds their first dashboard. Use when someone wants to "set up Corp-OS", "build a personal OS", "build a second brain for my work", "set up a knowledge base for my role", or asks to be onboarded into a work OS. Not for adding content to an existing OS (use corp-os-intake or corp-os-pull) and not for assessing a system someone already built by other means (use corp-os-audit).
---

# Corp-OS setup

Interrogate first, scaffold second. The interrogation is the deliverable as much as the folder is — a scaffold built without it produces a generic notebook that gets abandoned in a month.

Read `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md` and `${CLAUDE_PLUGIN_ROOT}/reference/interrogation.md` before starting. Read `${CLAUDE_PLUGIN_ROOT}/reference/jtbd-patterns.md` when working on jobs in area 3.

## Step 0 — check nothing already exists

Look for an existing Corp-OS root (`INDEX.md` + `meta.json` + `jobs/`) wherever the person means. If one exists, stop and say so — this skill does not re-scaffold over a live OS. Offer `corp-os-jobs` to add jobs, `improve-corp-os` to reshape structure, or `corp-os-rebuild` to re-derive.

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

## Step 3 — scaffold

Create the mandatory core: `raw/README.md`, `INDEX.md`, `meta.json`, `profile.md`, `jobs/INDEX.md`, `usage/log.md`, `usage/proposals.md`, and one job record per job from Step 1.

Create `proposals/` alongside them — the review gate writes there, so it is not optional.

Then create only the optional layers they asked for: `claims/`, `people/`, `topics/`, `glossary.md`, `company/`, `connectors.md`, `design.md`, `dashboards/registry.md`.

If area 9 turned up anything sensitive, create `sensitive.md` now and write into `INDEX.md` that it exists but is deliberately **not** linked from the scan path. A quarantine file added after the fact means retrofitting content out of files it has already been scanned and shared from.

Copy `${CLAUDE_PLUGIN_ROOT}/scripts/build_index.py` into the OS's `scripts/`, and tell the person what it is for: a thirty-second deterministic recount they can run after any manual edit. It reads nothing from `raw/` and retags nothing, which is what makes it safe.

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

Follow `${CLAUDE_PLUGIN_ROOT}/reference/dashboard-patterns.md` and hand off the actual build to `corp-os-dashboard` rather than reimplementing it here. Panels can be near-empty at this stage; that is fine and honest. An empty evidence-gaps panel that says "nothing captured yet — run corp-os-pull" is doing its job.

## Step 8 — verify, log, and hand off with one action

Verify programmatically: every file the spec calls for exists, every job in `jobs/` appears in `jobs/INDEX.md` with a one-liner, counts in `meta.json` and `INDEX.md` match an actual count.

Append the setup row to `usage/log.md`.

Then name **one** next action and offer to do it — pulling from their highest-value connector, or adding the meeting notes from this week. Do not leave someone with an empty, well-organized folder and a list of options.
