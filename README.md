# corp-os

A portable, configurable personal work OS — as an installable Claude plugin.

Your knowledge base is a folder of markdown files. This plugin is the eighteen skills that operate on it: an interrogation that shapes it to your actual work, ingestion from meetings and documents, citable claims you can refine against reality, recall with provenance, dashboards, and an audit that will tell you when the model is wrong for you.

## Install

Download `dist/corp-os.plugin` from a release, or build it:

```bash
./build.sh          # validates, then writes dist/corp-os.plugin
```

Then install the `.plugin` file in Claude, or add this repo as a marketplace.

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

## Everything else is yours

Layer names, label vocabulary, decay windows, how long source material is kept, and how strict the review gate is are declared in a `config.json` that every skill reads first. A layer the model never imagined — `experiments/`, `matters/`, `readouts/` — gets its own field schema and index template, and every skill then treats it like a shipped one.

Including the organizing idea itself: the jobs layer is a default, not a requirement, and `corp-os-audit` runs an empirical test before recommending it rather than assuming it fits.

`examples/config-worked-example.json` is a verified config expressing a real four-month-old system that shares none of this model's layer names.

## Repository

```
plugins/corp-os/     the plugin — skills, reference specs, shipped scripts
scripts/validate.py  structure, frontmatter, cross-reference and leakage checks
build.sh             validate + package
docs/ARCHITECTURE.md the design, every decision and why, and what is still open
```

Start at [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) to work on this. Start at [`plugins/corp-os/README.md`](plugins/corp-os/README.md) to use it.

## License

MIT.
