# Patterns

A **pattern** is a portable specification for producing one kind of output: a dashboard, an export, a deck, a recurring document. It says what the output needs from an OS, what it must contain, what it must refuse to do, and which script builds it.

Patterns exist because of a problem that only appears with more than one person. One operator can keep their conventions in their head. Five operators produce five dashboards with five palettes and five ideas about what a panel owes the reader, and nothing about the model prevents it. `design.md` already binds one thing — the palette. A pattern binds the rest.

---

## The shape

```
patterns/dashboard-job-board.md
---
name: dashboard-job-board
kind: dashboard              # dashboard | export | deck | doc | brief
pack: acme-product@2.1.0     # where it came from, or `local`
requires:
  - role: derived
    fields: [citation, confidence]
  - role: source
produces: one self-contained HTML file
target: local                # local | artifact | redacted-artifact
shield: required             # required | n/a
generator: scripts/build_dashboard_job_board.py
---

## What it answers
## Composition
## Refuses
## Verification
```

Everything above the `---` is machine-read: `bind_pattern.py` resolves `requires:` against an OS's `config.json` and either binds or names exactly what is missing. Everything below it is for whoever builds the thing.

---

## `requires:` addresses roles and fields, never layer names

**This is the whole reason a pattern is portable, and it is the rule most likely to be broken by someone writing their first one.**

An operator renames their vocabulary. One OS calls them claims, another calls them findings, another calls them entries. A pattern that says `claims/` binds in exactly one OS — the one it was written in — and fails silently everywhere else by rendering an empty panel.

So a requirement names the **role** the layer plays and the **fields** the pattern reads:

```yaml
requires:
  - role: derived
    fields: [citation, confidence]      # from the layer's entry_schema
  - role: source                         # any raw layer will do
  - role: derived
    label: person                        # a semantic hint when role is ambiguous
    fields: [aliases]
    optional: true                       # the panel is dropped, the bind still succeeds
```

`optional: true` is how a pattern degrades honestly. A stakeholder panel that needs a person layer either binds or is dropped **and said out loud**; what it must never do is render empty. A blank panel is a bug, not a state.

## Binding either resolves or names what is missing

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/bind_pattern.py --root <os> --pattern patterns/x.md
```

Three outcomes and no fourth:

- **Bound.** Every required role resolved. The generator can run.
- **Bound with drops.** An optional requirement did not resolve; the pattern names the panels it is dropping.
- **Refused.** A required role or field is absent. The output names it: *"needs a layer with role `derived` carrying a `person` field; this OS declares none."*

A refusal is a decision to make once, not a defect to discover in the output. Hand it to `corp-os-configure` to declare the layer, or take the pattern without that view.

**A layer with no `entry_schema` cannot be field-checked.** That is a warning rather than a refusal — most layers in the wild have none — but it means the bind is weaker than it looks, and the pattern should say so rather than pretending.

---

## A pattern declares requirements, never counts or content

The failure this repo keeps finding is a fact maintained in a second place. A pattern that says *"renders the 14 open decisions"* is that defect with a new name.

Requirements, composition rules and refusals are stable. Numbers, entry ids and names are not. If a pattern would be wrong the day after someone adds a claim, it is holding content it should be reading.

---

## Packs: how a team ends up looking alike

A **pack** is a folder of patterns plus the shared assets they use, published by one person and adopted by the others:

```
acme-product-pack/
  pack.json                 # name, version, what it assumes
  patterns/*.md
  assets/design-system.css
  scripts/*.py
```

Copying it is the entire distribution mechanism. There is no server, no registry, nothing to run.

**Adopting a pack is the same problem `upgrade_os.py` already solves.** Teammates carry copies of files someone else maintains, copies drift, and updating the pack updates nobody's OS. That is exactly the shipped-script problem one layer up, so it reuses the same discipline rather than inventing a second one: compare by **content** rather than by date, record the version the OS is on, report what drifted, and refuse to perform a structural migration. `corp-os-upgrade` does pack drift alongside script drift.

A local edit to an adopted pattern shows up as drift rather than being silently overwritten. Someone who deliberately diverged should be told they have, not corrected.

---

## `target:` and `shield:` are properties of the output, not global rules

`target` decides where the output lands:

- **`local`** — a self-contained file in the OS. The default for anything reading the scan path.
- **`artifact`** — published. Only for output that carries nothing sensitive.
- **`redacted-artifact`** — published from a build that filtered sensitive material out at load time.

`shield` decides whether the output needs a screen-share shield (below). A job board can publish; a stakeholder map never should. As a global rule that trade-off has to be resolved once for everything; as a pattern field each output gets the answer that fits it.

---

## The screen-share shield

An OS dashboard gets opened on a shared screen. `bearing` deliberately keeps `sensitive` + `load_bearing` material in the scan path, because quarantining it produces confidently wrong answers rather than visible gaps. A dashboard reads the scan path. **So the moment this thing is genuinely useful is also the moment it is dangerous.**

Any pattern whose output renders derived content and can be opened in front of other people declares `shield: required`.

### Redact in the markup; let script *reveal*

Ship sensitive content as a placeholder, with the real markup parked in a `data-real` attribute, and reveal by assigning from it.

The inverse — render it visible and hide with JS — is visible whenever the script fails, loads late, or is disabled, which is exactly the moment it matters. The test is mechanical: strip every `<script>` block and every `data-real` attribute, reduce what is left to visible text, and grep for known secrets. On a real implementation that test found **three leaks in the first pass**.

### Default to hidden on every load, and never persist the state

Do not remember that it was last left revealed. Forgetting to re-hide before sharing a screen is a disclosure; one extra click is an inconvenience. Those costs are not symmetric, so fail toward the recoverable one — the same reasoning that makes `load_bearing` the default for `bearing`.

Grep the built file for `localStorage`. If the shield persists, a previous session can leave it off.

### Placeholder, not blur

A CSS blur leaves the text in the DOM: selectable, copyable, present in a saved page, and plainly visible if the stylesheet fails. Replace the content.

Keep a visible marker — `sensitive · hidden` — so the page still says something is being withheld rather than silently omitting it. Same reason the export boundary sends stubs instead of dropping claims: a gap that announces itself is safe, a gap that does not is a wrong answer.

### Make the revealed state impossible to miss

A persistent high-contrast banner while anything sensitive is visible, a state-labelled toggle, a keyboard flip that is ignored while typing so it cannot fire mid-query, an escape key that hides everything, and re-hide on `visibilitychange` so switching to the meeting window re-hides.

### Sensitivity has to be declared, and it is not only on claims

Claims carry a `Sensitivity` field, so tagging them is the easy part. The leaks are everywhere else, and each needs its own declarative source:

- **Decisions inherit.** A decision record has no sensitivity field of its own, but *"does the incoming CEO approve retiring this revenue stream"* discloses precisely what the claim protects. A decision is sensitive if any entry it rests on is. Measured: **6 of 18** in one OS, none of which reading the decision records would have caught.
- **People need a declaration, and the criterion is narrow.** A person record is sensitive when their **role or status is itself the protected fact** — an unannounced hire, a departure not yet public. Being the *subject* of a sensitive claim does not qualify: a trust judgment about a consultant is sensitive, the consultant's existence is not. Over-applying this hides most of the directory for nothing. Measured: **2 of 53** qualify. Add `sensitivity` to the person `entry_schema` so it is a declared field rather than something a renderer infers.
- **Redact the whole identifying row, not only the role.** A name under a "C-suite" heading with the role hidden still discloses that there is a new C-suite person. Name, aliases, role and status all go; counts and dates stay, so the row and its tier count remain honest that someone is there.
- **Authored prose has nothing to inherit from.** Hand-written commentary needs a flag set by hand, which is a real cost of authoring it and an argument for deriving such notes from records instead.
- **Glossary terms can be the secret** — an unannounced product name, a deal codename. Support a per-entry sensitivity field there even where nothing currently uses it.

### The aggregation leak, which is the one nobody predicts

A search view stubs its sensitive hits correctly, and then the *"who said it"* panel counts their speakers anyway. **The name is the disclosure.** Measured: a query showed **3 speakers with the shield down and 2 with it up** — one name leaking out of results that were themselves correctly hidden. Topic aggregation has the same problem, because a topic slug can name the protected thing.

**Every derived summary — counts by person, counts by topic, a top-contributors list — is computed over the filtered set, never the raw one.** This is the single easiest thing to get wrong, because each individual result looks correctly redacted.

### A shield is not a boundary, and the output should say so

The sensitive content is still in the file. The shield governs what renders; anyone holding the file can read it.

- **The shield** protects *a screen*. Runtime, reversible, on by default.
- **A redacted build** protects *a file that leaves*. It omits the material entirely.

Ship both and do not let either imply the other. And a redacted build **filters once at the data-load boundary, not per panel** — one implementation filtered only its search index while three other views rendered the same material in place. It disclosed that honestly in three places, and disclosure is not a fix: per-panel filtering is how a view added later arrives without the filter.

---

## Composition rules every rendering pattern inherits

These came from a real build, and each is stated with the failure that produced it, because a rule without its reason gets simplified away by the next person.

**One file, in-page routing.** Not linked pages. A local HTML file opened through a preview pane, a file card, an attachment or a chat client renders in a sandbox where relative navigation between sibling files is blocked: the page looks correct and clicking does nothing. The first real build was six linked pages, a link-resolution check reported zero broken paths, and every link was dead in the operator's hands. **Verifying that link targets exist is not verifying that navigation works.** Links *out* to `raw/` are different and should stay — they are the point of a citation, and they resolve when the file is opened from its folder. Board navigation must never depend on them.

**Never `fetch()` at runtime.** From a `file://` page it is a cross-origin request, blocked in Chrome and Safari. The page loads, the panel stays empty, and the console error is invisible to anyone who did not open devtools. Embed the data in a `<script type="application/json">` block and parse it from `textContent` — escaping `</` as `<\/`, or a `</script>` inside a quoted claim terminates the block early. Write the JSON alongside for other consumers; just do not let the page depend on it.

**Generate it; never hand-write it.** Every count, row, ranking and distribution is computed from the files at build time. A hand-written job board had wrong counts within a day — the same failure `build_index.py` exists to prevent, reproduced one directory over. The one sanctioned exception is judgment that cannot be computed, and it is kept in a single named structure with a comment saying so; anything else authored is a smell.

**No panel recomputes a headline figure.** Cite it from `meta.json`, which `build_index.py` already generates. A panel that recalculates is a second source of truth for the same number, and the two disagree at the worst possible moment.

**Rank recurrence by distinct sources, never by volume.** The obvious metric — how many entries support a theme — is wrong, and wrong invisibly, because the number looks like breadth. Measured: one argument rested on nine entries that all traced to a single meeting. Nine entries from one conversation is one data point, and ranking by count promotes the best-documented conversation rather than the most recurrent pattern. Rank by distinct raw sources across the theme and everything it rests on, and **display both** — `11 sources · 9 entries` — so the ratio is visible.

**Resolve people through the alias layer before counting.** Naively aggregating an attribution string is wrong twice over: the same person appears under a short form and a full name as two speakers, and a jointly attributed entry becomes a third, composite one. Measured: **63 attribution strings resolving to 44 real people**, with the largest single voice split in two. Map an unambiguous first name to its canonical person only when exactly one person in the directory carries it, and credit both people on a joint attribution rather than inventing one.

**Surface the uncomfortable numbers.** The temptation is to build something that looks healthy, and the panels that change behaviour are the ones showing what is wrong: entries past decay as a count *and* a share, evidence items open longest with what each blocks, jobs untouched for a full horizon, connectors stale or broken, assumptions load-bearing on active work. **A dashboard where every number is green after four months of real use is measuring the wrong things.** And pair each problem panel with the instruction that fixes it — *"run corp-os-reality-check on the 14 overdue entries"* — because a health panel with no path out of what it found is decoration.

**Scannable in fifteen seconds.** If it needs a legend, it is two outputs. Counts before charts: a labelled number beats a donut of four categories, and a chart earns its place only when change over time is the actual point. No decorative data — no sparklines encoding nothing, no progress rings on things that do not progress, no cards nested inside cards.

**Freshness on every panel.** A real date, not "recently". Invisible data age is how an output gets trusted long after it should not be.

**Every panel names its source files.** The cheapest possible defence against a panel quietly drifting from the data, and what makes "renders what the OS holds" checkable rather than aspirational.

**State what a panel is bad for, on the panel.** A people view says outright that entry counts measure attendance and proximity, not reliability. A panel presenting a misleading number without its caveat is worse than no panel.

**Empty states say what to run.** "No entries past decay" is a state. A blank panel is a bug.

**Theme-aware without owning the page.** Define the full light palette on bare `:root`, then repeat dark values under both `@media (prefers-color-scheme: dark){:root:not([data-theme="light"])}` and `:root[data-theme="dark"]`. Honouring only one of those renders one theme's text on the other theme's background wherever the host stamps its own attribute.

**Intrinsic layout only.** `repeat(auto-fit, minmax(…, 1fr))`, never a fixed column count behind a media query. These get rendered in panes narrower than the window, where viewport media queries never fire.

---

## Verification

A pattern's `## Verification` section is not decoration. Every item below came from a check that was skipped once.

1. **Open it the way the operator will** — the preview or the file card, not a browser tab you navigated to deliberately. Click every nav item.
2. **Syntax-check the generated JS** (`node --check`). Template brace escaping is the likeliest failure and it fails silently in a browser.
3. **Exercise the data logic outside the browser.** Load the embedded JSON, run the filters against real queries, assert non-zero hits and correct aggregation. This is what caught the split-speaker bug.
4. **Assert zero cross-file navigation links.**
5. **Re-run `build_index.py --check`.** Producing an output should never change the OS's own counts.

For anything declaring `shield: required`, also:

```bash
python3 scripts/check_shield.py <built file> --probes probes.txt
```

which performs the JS-off leak test, confirms the default state is hidden, and greps for `localStorage`. Keep the probe list in the OS and add to it whenever new sensitive material lands.

Two more that the script cannot do:

- **Round-trip the toggle** outside a browser: hidden by default, reveal restores the real markup, re-hide restores the placeholder. Assert on elements, not appearance.
- **Diff every derived aggregation shield-up against shield-down.** Any count that differs in a way the stub count does not explain is a leak. This is how the speaker-aggregation bug surfaced.
