#!/usr/bin/env python3
"""Find entries that share a citation and disagree about it.

The model mints claims per topic, so one source routinely yields several
claims across several files, written by several passes. Sensitivity is then
set per claim, while the thing being protected is the source text. Nothing
reconciles the two.

Measured, in a real corpus: fifteen citation strings were each carried by two
or three claims. One group was classified `sensitive` on one member and the
default on the other two. Per-claim redaction was mechanically correct on all
836 claims and the export boundary still leaked -- it withheld the sensitive
member as a stub and emitted the byte-identical citation in full, twice.

That is not a hygiene problem that grows slowly. It is a confidentiality
failure whose likelihood rises with every pass, and it is invisible to every
per-claim check, because each claim on its own is correct.

The same clustering answers a second question for free. Thirteen of those
fifteen groups had no cross-reference between their members, and one group
disagreed with itself on substance -- one claim asserting a resolution as
settled, another from the same quote saying it was never confirmed.

    python3 scripts/check_citations.py              # report, exit 0
    python3 scripts/check_citations.py --strict     # exit 1 on a split cluster

`--strict` is what an export path calls. Reporting is what a sweep calls: a
split cluster is a thing to resolve, not a thing to be stopped by, until the
moment it is about to leave.
"""

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict

# `no source` is a sanctioned value meaning the claim traces to a summary with
# no retrievable original. Every such claim shares that literal string, so
# clustering on it would group hundreds of unrelated claims and report a
# permanent, meaningless conflict -- the kind of finding that teaches people
# to stop reading the output.
NOT_A_CITATION = {"no source", "no raw file", "none", "n/a", ""}

FIELD = r"^[-*]?\s*\*\*{f}\*\*\s*:\s*(.+?)\s*$"


def load_config(root):
    p = os.path.join(root, "config.json")
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return {"layers": {}}


def entries(root, cfg):
    """Every derived entry carrying a citation, wherever it lives.

    Addressed by role rather than by the name `claims`, because an operator
    renames vocabulary and this check has to keep working when they do.
    """
    out = []
    for name, spec in (cfg.get("layers") or {}).items():
        if not spec.get("enabled") or spec.get("role") not in ("derived", "record"):
            continue
        path = (spec.get("path") or name).rstrip("/")
        full = os.path.join(root, path)
        files = ([full] if path.endswith(".md") and os.path.exists(full)
                 else sorted(glob.glob(os.path.join(full, "*.md"))))
        marker = spec.get("entry_marker", "### ")
        for f in files:
            if os.path.basename(f) in ("README.md", "INDEX.md"):
                continue
            cur = None
            for line in open(f, encoding="utf-8", errors="replace"):
                if line.startswith(marker):
                    cur = {"id": line[len(marker):].split("—")[0].strip(),
                           "file": os.path.relpath(f, root), "layer": name,
                           "citation": None, "sensitivity": None,
                           "statement": None, "relations": None}
                    out.append(cur)
                elif cur:
                    for key, label in (("citation", "Citation"),
                                       ("sensitivity", "Sensitivity"),
                                       ("statement", "Statement"),
                                       ("relations", "Relations")):
                        m = re.match(FIELD.format(f=label), line, re.I)
                        if m:
                            cur[key] = m.group(1).strip()
    return out


def clusters(rows):
    by = defaultdict(list)
    for r in rows:
        c = (r["citation"] or "").strip().strip('"').lower()
        if c in NOT_A_CITATION or not c:
            continue
        by[c].append(r)
    return {k: v for k, v in by.items() if len(v) > 1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".", help="the OS root")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any cluster disagrees on sensitivity")
    a = ap.parse_args()

    root = os.path.expanduser(a.root)
    cfg = load_config(root)
    rows = entries(root, cfg)
    cl = clusters(rows)

    split, unlinked = [], []
    for cite, members in sorted(cl.items()):
        vals = {(m["sensitivity"] or "internal").lower() for m in members}
        if len(vals) > 1:
            split.append((cite, members, sorted(vals)))
        elif not any(m["relations"] for m in members):
            unlinked.append((cite, members))

    if not cl:
        print("No shared citations. Nothing to reconcile.")
        return 0

    print(f"{len(rows)} entries · {len(cl)} citation(s) carried by more than "
          f"one entry.")

    if split:
        print(f"\nSPLIT — {len(split)} citation(s) whose entries disagree "
              "about sensitivity:")
        for cite, members, vals in split:
            print(f'\n  "{cite[:90]}"')
            print(f"    classified: {', '.join(vals)}")
            for m in members:
                print(f"    {m['id']:<12} {(m['sensitivity'] or 'internal'):<10} "
                      f"{m['file']}")
        print("\n  Sensitivity is a property of the source text, so these "
              "cannot both be right.\n  Resolve to one class before anything "
              "derived from them leaves: the export\n  boundary withholds the "
              "sensitive member and emits the identical quote in\n  full as "
              "the others.")

    if unlinked:
        print(f"\nUNLINKED — {len(unlinked)} citation(s) whose entries agree "
              "on sensitivity but\ndo not reference each other. Not a leak; "
              "the usual cause is two passes\nminting near-duplicate claims "
              "from one quote, and it is worth reading them\ntogether once:")
        for cite, members in unlinked[:10]:
            ids = ", ".join(m["id"] for m in members)
            print(f'  {ids}  —  "{cite[:70]}"')
        if len(unlinked) > 10:
            print(f"  …and {len(unlinked) - 10} more.")

    if not split and not unlinked:
        print("Every shared citation agrees on sensitivity and is "
              "cross-referenced.")

    if a.strict and split:
        print(f"\nREFUSING: {len(split)} split cluster(s). An export that "
              "proceeds here leaks\nthe quote it is withholding.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
