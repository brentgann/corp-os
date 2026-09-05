---
name: corp-os-dashboard
description: Builds and refreshes dashboards from what a Corp-OS knowledge base actually holds — a job board, evidence gaps, claim health, source coverage, stakeholder map, company brief, or decision log — published as artifacts and recorded in the dashboard registry, following whatever design system the OS binds. Use when someone says "build me a dashboard", "show me my jobs", "visualize my OS", "what's my claim health", "refresh my dashboard", or wants a view of the data they have collected. Not for a written brief in chat (use corp-os-brief) and not for answering a specific question (use corp-os-recall).
---

# Corp-OS dashboard

Renders what the OS holds. The governing rule: **never render what the OS does not have.** A panel that would need missing data shows the gap instead of an estimate, because the gap is the information the person needed.

Read `${CLAUDE_PLUGIN_ROOT}/reference/dashboard-patterns.md` before building.

## Step 0 — scan, and check the registry first

Read `config.json` first — its `layers` block says what exists to render, `design` says what governs the look, and `dashboards.default_target` says whether output persists as an artifact or as a local file. Then `INDEX.md`, `jobs/INDEX.md`, `claims/INDEX.md`, `connectors.md`, and `dashboards/registry.md`.

A custom layer is dashboard material like any other: if its `index_line` renders, it can be a panel.

Check the registry before building anything. If the requested dashboard already exists, this is a **refresh to the same URL**, not a new build. A person with three generations of the same dashboard has no dashboard.

## Step 1 — pick from the person's jobs, not from the catalogue

The patterns reference lists seven views. Do not offer all seven. Read their active jobs and propose the one or two that serve them:

- Jobs blocked on missing information → **evidence gaps**.
- Jobs running on old claims → **claim health**.
- Relationship-heavy jobs → **stakeholder map**.
- Many jobs, unclear priorities → **job board**.
- Recurring "why did we decide that" → **decision log**.
- A counterparty-facing job → **company brief**.
- Uncertainty about what is even feeding the OS → **source coverage**.

Build one well. Two half-built dashboards is worse than one, because neither gets trusted.

## Step 2 — build each panel from named files

Every panel declares the files it was built from. If a panel cannot name its sources, it does not ship — that rule is what keeps a dashboard from quietly drifting into decoration.

Composition rules that matter more than they sound:

- **Scannable in fifteen seconds.** If it needs a legend, it is two dashboards.
- **Counts before charts.** A labelled number beats a donut of four categories. Reach for a chart only when change over time is the actual point.
- **Freshness on every panel.** A real date, not "recently." Invisible data age is how a dashboard gets trusted long after it should not be.
- **Empty states say what to do.** "No claims past decay — next sweep due Oct 4" is a working panel. A blank box is a bug.
- **No decorative data.** No sparklines encoding nothing, no progress rings on things that do not progress, no nested cards inside cards.

## Step 3 — surface the uncomfortable numbers

The temptation is to build a dashboard that looks healthy. Resist it. The panels that change behavior are the ones showing what is wrong:

- Claims past decay, as a count and a share of the total.
- Evidence items open longest, with which job each blocks.
- Jobs untouched for a full horizon period.
- Connectors stale or broken.
- Assumptions load-bearing on active jobs.

A dashboard where every number is green after four months of real use is measuring the wrong things.

Pair each problem panel with the specific instruction that fixes it — "run corp-os-reality-check on the 14 overdue claims." A health panel with no path out of what it found is decoration.

## Step 4 — bind the design system

Read `design.md`. If it names a design system or design skill, load that skill and use its tokens and components rather than inventing colors and type. If it names nothing, use a restrained neutral palette, one accent, one type family at two weights, and generous whitespace — then mention once that binding a design system would make all outputs consistent.

Never invent a second palette for a second dashboard in the same OS. Cross-output consistency is the entire reason `design.md` exists.

Build it theme-aware and responsive: define the light palette as tokens, redefine only those tokens for dark, and let wide tables scroll inside their own container rather than the page.

## Step 5 — publish and register

Publish as an artifact, since a dashboard exists to be returned to and shared. Then record it in `dashboards/registry.md`: name, URL, owning job, source files, cadence, last built.

On refresh, republish to the same URL and update `last built`. Never create a second artifact for the same dashboard.

If the person framed this as a one-off look — "just show me what it'd look like" — write a self-contained HTML file into the OS folder instead and skip the registry. Persisting something nobody returns to is clutter.

## Step 6 — offer the cadence

A dashboard nobody refreshes is a snapshot. Offer to schedule the refresh at the cadence in the registry, and offer `corp-os-brief` for the narrative version — the two work together, and the brief is what actually gets read on a Monday morning.

## Every run ends with

- Registry updated.
- A `usage/log.md` row.
- One or two sentences on what the dashboard shows, and specifically the worst number on it. Do not narrate the panels; the person can look. Tell them the thing they would have missed.
