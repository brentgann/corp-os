#!/usr/bin/env python3
"""Move `note` fields out of config.json and into the OS's own README.

A note is written once, by a person, to explain why the config is shaped the
way it is. It is then re-read by a model on every run of every skill, forever.
In a real OS they totalled 1,627 tokens: 42% of config.json and 17% of the
pre-flight floor every skill pays before doing any work.

reference/configuration.md already says where they belong. Its precedence
list is: config.json is the authority, then "the OS's own README.md -- for
anything config does not cover, and for the human-readable explanation of why
the config is shaped the way it is." That is a note, in the wrong file.

Nothing is deleted. Each note moves to README.md under a generated heading,
labelled with the config path it came from, so the explanation stays next to
the OS rather than inside the file every skill reads first.

    python3 scripts/prune_config_notes.py --root .              # dry run
    python3 scripts/prune_config_notes.py --root . --apply
"""
import argparse
import json
import os
import sys
from datetime import date

HEADING = "## Why the config is shaped this way"


def walk(node, path=()):
    """(dotted path, note) for every `note` at any depth."""
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if k == "note" and isinstance(v, str):
                yield ".".join(path) or "(root)", v
            else:
                yield from walk(v, path + (str(k),))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, path + (str(i),))


def strip(node):
    if isinstance(node, dict):
        return {k: strip(v) for k, v in node.items()
                if not (k == "note" and isinstance(v, str))}
    if isinstance(node, list):
        return [strip(v) for v in node]
    return node


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cp = os.path.join(root, "config.json")
    if not os.path.exists(cp):
        sys.exit(f"no config.json in {root}")

    raw = open(cp, encoding="utf-8").read()
    cfg = json.loads(raw)
    notes = list(walk(cfg))
    if not notes:
        print("no `note` fields in config.json — nothing to move.")
        return 0

    tok = sum(round(len(v) / 4) for _, v in notes)
    print(f"{len(notes)} note field(s), about {tok} tokens, "
          f"{tok * 100 // max(1, round(len(raw) / 4))}% of config.json.\n")
    for p, v in notes:
        print(f"  {p}\n      {v[:96]}{'…' if len(v) > 96 else ''}")

    rp = os.path.join(root, "README.md")
    existing = open(rp, encoding="utf-8").read() if os.path.exists(rp) else \
        "# This OS\n"
    fresh = [(p, v) for p, v in notes if v.strip() not in existing]
    print(f"\n{len(notes) - len(fresh)} already present in README.md; "
          f"{len(fresh)} to add.")

    if not a.apply:
        print("\ndry run. Re-run with --apply to move them.")
        return 0

    block = [""] if existing.endswith("\n") else ["", ""]
    if HEADING not in existing:
        block += [HEADING, "",
                  "Moved out of `config.json` so the values stay machine-read "
                  "and the reasons stay human-read. `config.json` is still the "
                  "authority for what the settings ARE.", ""]
    block.append(f"<!-- moved from config.json, {date.today().isoformat()} -->")
    block.append("")
    for p, v in fresh:
        block += [f"**`{p}`** — {v}", ""]
    open(rp, "a" if os.path.exists(rp) else "w",
         encoding="utf-8").write("\n".join(block))

    # Written with the same indent the file already used, so the diff is the
    # removed lines and nothing else.
    indent = 2
    for line in raw.split("\n"):
        s = line.lstrip()
        if s.startswith('"') and len(line) - len(s) > 0:
            indent = len(line) - len(s)
            break
    json.dump(strip(cfg), open(cp, "w", encoding="utf-8"), indent=indent)
    open(cp, "a", encoding="utf-8").write("\n")
    new = round(len(open(cp, encoding="utf-8").read()) / 4)
    print(f"\nmoved {len(fresh)} to README.md. config.json is now ~{new} "
          f"tokens, down from ~{round(len(raw) / 4)}.")
    print("next: python3 scripts/build_index.py — the counts do not change, "
          "but the recount confirms nothing else did either.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
