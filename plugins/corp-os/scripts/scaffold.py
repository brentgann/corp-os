#!/usr/bin/env python3
"""Create the mandatory core of a Corp-OS. Not the content — the skeleton.

Measured: `corp-os-setup`, run against an empty directory by someone who
described their work as contract management, produced a contracts filing
system. Sensible folders, a template, a couple of playbooks — and no
`INDEX.md`, no `meta.json`, no `config.json`, no `raw/`, no `proposals/`. Not
a Corp-OS at all, and so nothing else in the suite could operate on it.

It is the same failure as every other one this repo has found: a step that has
to happen every time, skipped under pressure, at the point where the
interesting work is done. Here the pressure is a person's own vocabulary, and
adapting to it is something `corp-os-setup` is right to do — but the five
invariants are not vocabulary, and a scaffold that drops them has produced a
folder rather than an OS.

So the skeleton is written by code. What goes in it stays with the skill.

    python3 scripts/scaffold.py --root ~/work-os --profile minimal \\
        --layers claims,glossary --vocab claim=finding

Refuses to touch a directory that already holds an OS.
"""

import argparse
import json
import os
import shutil
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(HERE)
SHIPPED = ("build_index.py", "write_export.py", "log_run.py", "delete_source.py")


def plugin_version():
    """Read the version rather than carry a second copy of it.

    It was hard-coded here and went stale within one release, which is the
    same class of bug as everything else this repo has found: a fact that has
    to be updated every time, that nothing catches when it is not. The version
    an OS records is what `upgrade_os.py` compares against, so a wrong one is
    worse than none.
    """
    p = os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json")
    try:
        return json.load(open(p, encoding="utf-8")).get("version")
    except (OSError, ValueError):
        return None

# Not configurable. These are the five invariants made concrete: an append-only
# source layer, a place for the review gate's record, and the index and counts
# the scan contract reads. Everything else is the person's choice.
MANDATORY = ("raw", "proposals", "usage", "scripts")

OPTIONAL = ("claims", "jobs", "glossary", "company", "decisions", "people",
            "topics")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--profile", default="minimal")
    ap.add_argument("--layers", default="claims",
                    help="comma-separated optional layers to enable")
    ap.add_argument("--vocab", default="",
                    help="comma-separated term=replacement, e.g. claim=finding")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    root = os.path.expanduser(a.root)
    if os.path.exists(os.path.join(root, "meta.json")) and not a.force:
        sys.exit(f"{root} already holds an OS (meta.json exists). This does not "
                 "re-scaffold over a live one; use corp-os-configure to reshape "
                 "it, or --force if you are certain.")

    layers = [x.strip() for x in a.layers.split(",") if x.strip()]
    unknown = [x for x in layers if x not in OPTIONAL]
    if unknown:
        sys.exit(f"unknown layer(s) {unknown}. Known: {', '.join(OPTIONAL)}. "
                 "A layer the model has no name for is a custom layer — declare "
                 "it in config.json with its own entry_schema and index_line "
                 "(see reference/configuration.md), which this script "
                 "deliberately will not guess at.")

    vocab = {}
    for pair in a.vocab.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            vocab[k.strip()] = v.strip()

    today = date.today().isoformat()
    os.makedirs(root, exist_ok=True)
    for d in MANDATORY + tuple(l for l in layers if l not in ("glossary",)):
        os.makedirs(os.path.join(root, d), exist_ok=True)

    # -- config.json: the file every skill reads first
    cfg = {
        "corpos_version": plugin_version(),
        "profile": a.profile,
        "vocabulary": {
            **({"claim": vocab["claim"]} if "claim" in vocab else {}),
            "confidence": ["confirmed", "needs_review", "reconstructed",
                           "disputed", "retired"],
            "sensitivity": ["internal", "sensitive"],
            "bearing": ["incidental", "load_bearing"],
            "tags": [],
        },
        "layers": {
            "raw": {"enabled": True, "role": "source", "path": "raw/"},
            "proposals": {"enabled": True, "role": "record", "path": "proposals/"},
            **{l: {"enabled": True, "role": "derived", "gated": True,
                   "path": f"{l}/" if l != "glossary" else "glossary.md"}
               for l in layers},
            **{l: {"enabled": False} for l in OPTIONAL if l not in layers},
        },
        "decay": {"enabled": True, "default": "90d", "applies_to": "sourced",
                  "by_kind": {"decision": "none", "constraint": "none"}},
        "retention": {"raw": {"policy": "keep",
                              "measure_from": "frontmatter_date"}},
        "gate": {"mode": "propose"},
        "confidence_ceilings": {},
        "scan": {"excluded_from_scan": ["usage/", "sensitive.md"]},
    }
    write(os.path.join(root, "config.json"),
          json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")

    write(os.path.join(root, "meta.json"), json.dumps({
        "created": today,
        "next_claim_id": 1,
        "cutoff": {},
        "confidence_ceilings": {},
        "history": [{"date": today,
                     "event": f"scaffolded from the {a.profile} profile "
                              f"by corp-os {plugin_version() or '(unknown)'}"}],
    }, indent=2) + "\n")

    write(os.path.join(root, "INDEX.md"),
          "# Index\n\nScan this first. Regenerated by "
          "`scripts/build_index.py` — do not hand-edit the counts.\n\n"
          "_Nothing captured yet. Run corp-os-intake with something you already "
          "have, or corp-os-connect to register a source._\n")

    write(os.path.join(root, "raw", "README.md"),
          "# Raw\n\n**Append-only.** Never edited, never summarized in place, "
          "never deleted. Existing here means *said*, not *true*.\n\n"
          "One sanctioned exception: the `processed` flag in a file's "
          "frontmatter gets flipped to `true` once the derived layer has drawn "
          "from it. That is bookkeeping about the file, not part of what was "
          "said.\n\nFile shape: `YYYY-MM-DD--<source>--<slug>.md`, with "
          "frontmatter carrying `source`, `person`, `date`, `type`, `tags`, "
          "`external_id`, `processed`.\n")

    write(os.path.join(root, "usage", "log.md"),
          "# Usage log\n\nOne row per run, written by `scripts/log_run.py`. "
          "The friction column is the whole input to corp-os-improve.\n\n"
          "| date | skill | scope | friction |\n|---|---|---|---|\n")
    write(os.path.join(root, "usage", "proposals.md"),
          "# Improvement backlog\n\nWhat corp-os-improve proposed, and what was "
          "rejected and why — the record that stops the same idea being "
          "re-proposed every quarter.\n")
    write(os.path.join(root, "proposals", "README.md"),
          "# Proposals\n\nThe review gate, persisted. Every proposal is written "
          "here **before** it is presented, and the outcome per item is "
          "appended after review.\n\nThe declines are the valuable part: they "
          "are the only record of what was deliberately chosen not to know.\n")

    for l in layers:
        if l == "glossary":
            write(os.path.join(root, "glossary.md"), "# Glossary\n")
        else:
            write(os.path.join(root, l, "INDEX.md"),
                  f"# {l.replace('-', ' ').title()}\n")

    for s in SHIPPED:
        src = os.path.join(HERE, s)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(root, "scripts", s))

    print(f"scaffolded {root}")
    print(f"  layers:  raw, proposals" + (", " + ", ".join(layers) if layers else ""))
    print(f"  scripts: {', '.join(SHIPPED)}")
    print("\nThe skeleton is here and it is empty on purpose. What goes in it — "
          "the README in their words, the jobs or open items, the connectors "
          "and their blind spots — is corp-os-setup's job, not this script's.")
    return 0


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    sys.exit(main())
