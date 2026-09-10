# corp-os

A portable, configurable personal work OS — as an installable Claude plugin.

Your knowledge base is a folder of markdown files. This plugin is the twenty-three skills that operate on it: an interrogation that shapes it to your actual work, ingestion from meetings and documents, citable claims you can refine against reality, recall with provenance, dashboards, and an audit that will tell you when the model is wrong for you.

## Install

```
/plugin marketplace add brentgann/corp-os
/plugin install corp-os@brentgann
```

In the desktop app, use the plugin browser rather than the slash command. To work on it instead of using it, clone and run `claude --plugin-dir ./corp-os/plugins/corp-os`.

## Update

```
/plugin marketplace update brentgann
```

Then bring your OS in line with the plugin you just updated, which is a **separate** operation and the one people miss:

```
ask for corp-os-upgrade
```

Updating the plugin replaces the skills. It does nothing to the folder they operate on, because every OS carries its own copies of the shipped scripts so it keeps working when the plugin is not loaded. `corp-os-upgrade` refreshes those copies, records the version, and names the structural migrations it will not perform.

One thing worth knowing before you publish anything here: the client caches an installed plugin **by version string**, so new commits without a bump in `plugin.json` reach nobody, silently. `validate.py` fails if the two version fields disagree, and the full procedure is in **[`docs/INSTALL.md`](docs/INSTALL.md)**.

## Start

Ask for corp-os setup. The interrogation covers your role and mandate, why you want this, what you are actually trying to accomplish, which data earns its keep, how information reaches you, what you can connect and how, your company and market, your design and output needs, and your sensitivity boundaries.

It takes fifteen to twenty minutes and it is the deliverable as much as the folder is. A scaffold built without it produces a generic notebook that gets abandoned in a month.

## What holds it together

Five properties are not configurable, because everything else rests on them:

1. **An append-only source layer** — existence in it means *said*, not *true*.
2. **Provenance** on derived entries — source, date, verbatim citation, confidence.
3. **A review gate** in front of anything treated as knowledge.
4. **An index that can be scanned** rather than a corpus that must be loaded.
5. **Something that removes things.**

That last one is what most systems lack and what decides whether yours survives two years.

## Measured, not asserted

Every skill has a conformance case, and each case runs the real skill against a throwaway copy of a fixture and scores what it did to the filesystem — not what it said about it.

**203 of 208 checks, 28 cases, 23 of 23 skills** (Opus 5, one run each). Reports are committed under `evals/runs/`, so the figures here are the ones in the repo rather than the ones remembered.

Three failures are open and named:

- `corp-os-guide` opens a decision itself instead of handing off, and does not route the fork to `corp-os-decide`. Both passed at 0.18.6 and regressed since; undiagnosed.
- `corp-os-recall` dropped a load-bearing sensitive fact in this run. It has scored 1-in-4, then 7/7, then this — a rate rather than a state, and the highest-stakes check in the suite.

What the harness measures has been wrong three times, and each time is recorded next to what it cost: a conditional check divided by the run count, a plugin guard that reported this repo's own commit, and a case that asserted against the OS's own capture rule. `docs/BACKLOG.md` carries all of them.

Costs were measured too, on a real 852-claim OS rather than the fixture: the per-run pre-flight floor went **9,508 → 5,501 tokens**, and one generated index went **14,943 → 244**. `docs/COST.md` has the journey and the things that did *not* save money.

## Everything else is yours

Layer names, label vocabulary, decay windows, how long source material is kept, and how strict the review gate is are declared in a `config.json` that every skill reads first. A layer the model never imagined — `experiments/`, `matters/`, `readouts/` — gets its own field schema and index template, and every skill then treats it like a shipped one.

Including the organizing idea itself: the jobs layer is a default, not a requirement, and `corp-os-audit` runs an empirical test before recommending it rather than assuming it fits. Nothing in the suite treats the presence of an optional layer as evidence that an OS exists, and no layer may be enabled without declaring what one entry contains and what one line of it looks like in the index.

`examples/config-worked-example.json` is a verified config expressing a real four-month-old system that shares none of this model's layer names.

## Repository

```
plugins/corp-os/     the plugin — skills, reference specs, shipped scripts,
                     synthetic fixtures, and the README that ships inside it
.claude-plugin/      the marketplace manifest this repo is installed through
scripts/validate.py  structure, frontmatter, cross-references, the cross-cutting
                     rules every skill must carry, and leakage checks
scripts/build_skill_map.py  regenerates docs/skill-map.html from the plugin
.validate-denylist   gitignored; private terms the leakage check greps for
build.sh             validate + package
evals/               three harnesses: commands, routing, conformance — plus the
                     committed run reports the skill map reads its figures from
docs/INSTALL.md      installing, updating the plugin, updating an OS, releasing
docs/ARCHITECTURE.md the design, every decision and why, and what is still open
docs/skill-map.html  every skill, mapped to the phase it belongs to — generated
```

**[`docs/skill-map.html`](docs/skill-map.html)** is the one-page tour: what each skill does, what it refuses, which phase it belongs to, and the commands and scripts underneath. Open it in a browser. It is **generated** — every count, description and eval number on it is read from the plugin at build time, and `validate.py` fails if it has drifted. The only thing declared by hand is which phase a skill belongs to, and the generator refuses to run until a new skill has been placed.

For a PDF, open it and print to PDF: the page carries print styles, so it paginates properly rather than reproducing the screen layout. The PDF itself is deliberately **not** committed &mdash; it is a render of a file that regenerates itself, and a binary in the tree is the one artifact here nothing could check for staleness.

`validate.py` is not only a linter. It enforces the rules that live in twenty-three skill files at once — the pre-flight and config-first blocks, the usage-log row, and the rule that no optional layer may be used to detect whether an OS exists. Those had all drifted by 0.5.0, which is why they are checked rather than merely documented.

Start at [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) to work on this. Start at [`plugins/corp-os/README.md`](plugins/corp-os/README.md) to use it.

## License

MIT.
