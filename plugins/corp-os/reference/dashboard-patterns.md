# Dashboard patterns

Reference for `corp-os-dashboard`. Which views are worth building, what each one is made of, and what makes them go stale.

## The rule that governs all of them

A dashboard in Corp-OS renders **what the OS actually holds**, never a projection of what it wishes it held. If a panel would need data the OS does not have, the panel shows the gap instead of an estimate. A dashboard that quietly interpolates is worse than no dashboard, because it removes the one signal the person needed: that they are flying blind on something.

Every panel therefore declares its source files. If a panel cannot name the files it was built from, it does not ship.

## Which dashboard to build first

Pick from the person's jobs, not from this list. The setup interrogation's area 3 and area 4 answers determine which of these is worth the first build; the rest wait until asked.

### Job board
The default first dashboard. One card per active job: statement, status, readiness, count of supporting claims, count of open evidence items, top blocker, days since last touched.

Built from `jobs/INDEX.md` plus each job record. Goes stale when jobs change status without being touched — which is exactly the thing worth seeing.

### Evidence gaps
One row per open evidence item across all jobs, sorted by which job it blocks and how long it has been open. This is the intake worklist, and it is the panel most likely to change someone's behavior, because it converts "I should capture more" into a specific list.

Built from the `What I still need to know` sections.

### Claim health
The reality-check surface. Claims bucketed by confidence, with a count past decay, a count never verified, and any `disputed` pairs shown side by side rather than resolved.

Built from `claims/INDEX.md`. Pair it with a one-click-equivalent instruction telling the person to run `corp-os-reality-check` on the overdue set — a health panel with no path to fixing what it found is decoration.

### Source coverage
One row per connector: category, status, last pull, cadence, jobs served, and the blind-spots note verbatim. The blind-spots column is the reason this view exists; without it the panel just says "everything is connected," which is never true.

Built from `connectors.md`.

### Stakeholder map
Only for relationship-heavy jobs. One card per person: role, which jobs they touch, last contact, what they last said that mattered (with its claim ID), and open asks.

Built from a declared person layer plus claim cross-references. Needs that layer to exist — without one, propose the company brief or the job board instead rather than rendering a panel from nothing.

### Company brief
A single-page rendering of `company/<slug>.md` — what they sell, users versus buyers, pricing shape, monetization, funding and status, competitors. Useful precisely because it is the thing people re-explain most often.

### Decision log
Claims of kind `decision`, in reverse chronological order, each with its rationale citation and what it superseded. The panel that saves the most time six months out, and the one almost nobody builds until they have been burned.

## Composition

- **One page, scannable in fifteen seconds.** If it needs a legend, it is two dashboards.
- **Counts before charts.** A number with a label beats a donut chart of four categories. Reach for a chart only when the shape over time is the point.
- **Every panel carries its freshness.** A date, not "recently." A dashboard whose data age is invisible gets trusted long after it should not be.
- **Empty states say what to do.** "No claims past decay" is good. A blank panel is a bug.
- **No decorative data.** No sparklines that encode nothing, no progress rings on things that do not progress.

## Design binding

Read `design.md` in the OS root. If it names a design system or a design skill, load that skill and use its tokens and components rather than inventing colors and type. If it names nothing, use a restrained neutral palette, one accent, one type family with two weights, and generous whitespace — and mention that binding a design system would make outputs consistent.

Never invent a second palette for a second dashboard in the same OS. Consistency across the person's outputs is the reason `design.md` exists.

## Publishing and refresh

Dashboards persist as published artifacts by default, because a dashboard exists to be returned to. Record every one in `dashboards/registry.md`:

```markdown
### Job board
- **URL**: <artifact url>
- **Owning job**: all active
- **Built from**: jobs/INDEX.md, jobs/*.md
- **Cadence**: refresh weekly, or on any job status change
- **Last built**: 2026-09-04
```

On refresh, republish to the same URL rather than creating a second one — a person with three generations of the same dashboard has no dashboard. Read the registry before building anything, to find out whether the thing being asked for already exists.

If the person asked for a one-off look rather than something they will return to, write a self-contained HTML file into the OS folder instead and skip the registry.
