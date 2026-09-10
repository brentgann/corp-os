---
name: corp-os-dashboard
description: Builds and refreshes dashboards from what a Corp-OS knowledge base actually holds — a job board, evidence gaps, claim health, source coverage, stakeholder map, company brief, or decision log — published as artifacts and recorded in the dashboard registry, following whatever design system the OS binds. Use when someone says "build me a dashboard", "show me my jobs", "visualize my OS", "what's my claim health", "refresh my dashboard", or wants a view of the data they have collected. Not for a written brief in chat (use corp-os-brief) and not for answering a specific question (use corp-os-recall).
---

# Corp-OS dashboard

> **Mixed pass** — binding the pattern and running the generator is bookkeeping; choosing which view this OS needs is not. Worth the better model, and worth keeping the mechanical half in scripts so the model is paying for the judgment rather than the typing.

Renders what the OS holds. The governing rule: **never render what the OS does not have.** A panel that would need missing data shows the gap instead of an estimate, because the gap is the information the person needed.

If this OS has adopted no pattern that fits what they want, read the catalogue in `${CLAUDE_PLUGIN_ROOT}/reference/dashboard-patterns.md`. When one fits, Step 1 picks from `patterns/` and the catalogue adds nothing.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — scan, and check the registry first

Read `config.json` first — its `layers` block says what exists to render, `design` says what governs the look, and `dashboards.default_target` says whether output persists as an artifact or as a local file. Then `INDEX.md`, `jobs/INDEX.md`, `claims/INDEX.md`, `connectors.md`, and `dashboards.md`.

A custom layer is dashboard material like any other: if its `index_line` renders, it can be a panel. When a custom layer has no `index_line`, read what one must contain in `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md` before deciding it cannot be rendered.

Check the registry before building anything. If the requested dashboard already exists, this is a **refresh to the same URL**, not a new build. A person with three generations of the same dashboard has no dashboard.

## Step 1 — pick from the person's jobs, not from the catalogue

Read `patterns/` and offer from what this OS has adopted, matched to their active jobs — not from a catalogue in this file. Jobs blocked on missing information want an evidence-gaps view; jobs running on old entries want claim health; many jobs and unclear priorities want a job board. The OS's own `patterns/` says what is actually available here. If one of those files will not parse or carries a section this skill does not recognise, its format is specified in `${CLAUDE_PLUGIN_ROOT}/reference/patterns.md`.

Build one well. Two half-built dashboards is worse than one, because neither gets trusted.

**Once a second dashboard already exists**, offer a home/index view linking to all of them, plus the single most consequential thing across the OS right now. That does not compete with "build one well" — it is a thin hub, not another analytical view.

**If a pattern needs a layer this OS has not declared** — a stakeholder map with no person layer, a decision log with no decisions layer — do not invent one inline to get the dashboard built. Hand off to `corp-os-configure` first; the `relationship` profile in `${CLAUDE_PLUGIN_ROOT}/reference/configuration.md` carries a worked `people` declaration. A layer improvised to serve a rendering is a layer declared without the interrogation that catches shape mistakes, and those are expensive to unpick once entries are in it.

## Step 2 — bind the pattern before building anything

```bash
python3 scripts/bind_pattern.py --root <the OS> --pattern patterns/<file>.md
```

The pattern carries the composition rules, what it refuses to do, and its generator. This skill does not carry them: nine rules held as prose are nine things to remember on every build, and they were held as prose right up until a real build broke on four of them.

Three outcomes and no fourth:

- **Bound** — run the generator.
- **Bound with drops** — an optional requirement did not resolve. Say which panel is being dropped. Do not render it empty; a blank panel reads as a state rather than a defect and nobody investigates it.
- **Refused** — hand off to `corp-os-configure` to declare the missing layer, or build without that pattern. Both are answers.

If the OS has no pattern for what they want, that is `corp-os-pattern`'s job, not this one's. Build the thing once by hand if you must, then have it authored into a pattern so the second person does not start from nothing.

## Step 3 — run the generator, never write the HTML

The generator lives in the OS's `scripts/`, so the output is rebuildable when the plugin is not loaded — the same argument that puts `build_index.py` there. Every count, row, ranking and distribution is computed at build time.

A hand-written job board had wrong counts within a day. That is the failure `build_index.py` exists to prevent, reproduced one directory over, and it is why the script is the artifact and the HTML is its product.

## Step 4 — bind the design system

Read `design.md`. If it names a design system or design skill, load that skill and use its tokens and components rather than inventing colors and type. If it names nothing, use a restrained neutral palette, one accent, one type family at two weights, and generous whitespace — then mention once that binding a design system would make all outputs consistent.

Never invent a second palette for a second dashboard in the same OS. Cross-output consistency is the entire reason `design.md` exists.

Build it theme-aware and responsive: define the light palette as tokens, redefine only those tokens for dark, and let wide tables scroll inside their own container rather than the page.

## Step 5 — publish and register

Publish as an artifact, since a dashboard exists to be returned to and shared. Then record it in `dashboards.md`: name, URL, owning job, source files, cadence, last built.

**`dashboards` is a registry file, not a folder. Never create a `dashboards/` directory to hold a built page.** It was a directory holding one file for five releases, and that shape made the index report `1` however many dashboards were registered — recreating it reintroduces the bug the layout fix removed. When a build has to land as a local file rather than an artifact, write it under `usage/` and put its path in the registry row. Check the layer's declared `path` in `config.json` before writing anywhere: a layer whose path ends in `.md` is a file, and a directory of that name is a second, competing copy of it.

On refresh, republish to the same URL and update `last built`. Never create a second artifact for the same dashboard.

**If the dashboard stands on a bounded, nameable set of entries, record them as `Rests on`** — the same field the arguments layer uses — if you are unsure what belongs in it, read its spec in `${CLAUDE_PLUGIN_ROOT}/reference/claim-record.md` — and the reason is the join it enables. A dashboard built from a whole layer has nothing to list and keeps `Source files` alone; listing a folder there is worse than listing nothing, because it renders as breadth nobody measured.

**Then say what the recount says about the grounding.** `build_index.py` renders **Resting on evidence that has gone stale** into `usage/health.md`: anything whose cited entries have gone past their decay window since it was built. If this dashboard is on that list, say so in the same breath as the refresh, with the number — *"republished; it rests on four claims and two of them went past their window in June."* A view that silently keeps rendering stale evidence is the exact failure decay exists to prevent, one layer up, and the person looking at the page has no way to see it from the page.

If the person framed this as a one-off look — "just show me what it'd look like" — write a self-contained HTML file into the OS folder instead and skip the registry. Persisting something nobody returns to is clutter.

## Step 6 — offer the cadence

A dashboard nobody refreshes is a snapshot. Offer to schedule the refresh at the cadence in the registry, and offer `corp-os-brief` for the narrative version — the two work together, and the brief is what actually gets read on a Monday morning.

If they accept, schedule it per `${CLAUDE_PLUGIN_ROOT}/reference/scheduling.md`; a refresh that silently stopped running is worse than no refresh, because the dashboard still looks current.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-dashboard --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

- Registry updated.
- A `usage/log.md` row.
- One or two sentences on what the dashboard shows, and specifically the worst number on it. Do not narrate the panels; the person can look. Tell them the thing they would have missed.
