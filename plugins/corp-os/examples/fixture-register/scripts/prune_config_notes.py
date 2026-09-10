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
            # `profile_note` and friends are notes that escaped the check by
            # not being called one. Same content, same cost, same file.
            if (k == "note" or k.endswith("_note")) and isinstance(v, str):
                yield ".".join(path + ((k,) if k != "note" else ())) or "(root)", v
            else:
                yield from walk(v, path + (str(k),))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, path + (str(i),))


def strip(node, keep, path=()):
    """Remove notes except at the paths named in `keep`."""
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if (k == "note" or k.endswith("_note")) and isinstance(v, str):
                where = ".".join(path + ((k,) if k != "note" else ())) or "(root)"
                if where in keep:
                    out[k] = v
                continue
            out[k] = strip(v, keep, path + (str(k),))
        return out
    if isinstance(node, list):
        return [strip(v, keep, path + (str(i),)) for i, v in enumerate(node)]
    return node


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", default="",
                    help="comma-separated config paths to move; everything "
                         "else stays")
    ap.add_argument("--except", dest="keep", default="",
                    help="comma-separated config paths to leave in place")
    a = ap.parse_args()

    # A note is not automatically documentation. Some of them change how a
    # skill behaves -- "a readable view over claims, not an independent source
    # of truth" is a rule, not a reason -- and moving those out of the file
    # every skill reads is a behaviour change wearing a cost fix's clothes.
    #
    # The test, per note: would a skill do anything differently if it never
    # read this sentence? No, and it is a reason -- move it. Yes, and it is
    # not a note at all; it is a field or a layer description that belongs in
    # the schema, stated in a line rather than a paragraph.
    #
    # No script can make that call, so it is a flag rather than a default.
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

    only = {x.strip() for x in a.only.split(",") if x.strip()}
    keep = {x.strip() for x in a.keep.split(",") if x.strip()}
    if only:
        keep |= {p for p, _ in notes if p not in only}
    notes = [(p, v) for p, v in notes if p not in keep]
    if not notes:
        print("every note was excluded — nothing to move.")
        return 0
    tok = sum(round(len(v) / 4) for _, v in notes)
    print(f"{len(notes)} note field(s), about {tok} tokens, "
          f"{tok * 100 // max(1, round(len(raw) / 4))}% of config.json.\n")
    # A note on a LIST entry sits beside peers of the same shape, so it may be
    # the only thing telling them apart. Two confidence ceilings in one real
    # OS were "the original source text no longer exists" (permanent) and "a
    # deliberate downgrade" (elective) -- identical as data, and the run that
    # has to decide which entries can ever be promoted reads the ceiling, not
    # the README. Flagged, not blocked: once the distinction is a field the
    # note is genuinely redundant.
    for p, v in notes:
        peer = p.rsplit(".", 1)[-1].isdigit()
        print(f"  {p}{'   [peer entry — see below]' if peer else ''}"
              f"\n      {v[:96]}{'…' if len(v) > 96 else ''}")
    if any(p.rsplit(".", 1)[-1].isdigit() for p, _ in notes):
        print("\n  One or more of these sits in a LIST, beside entries of the "
              "same shape.\n  Check whether the note is the only thing "
              "distinguishing it from its\n  peers. If it is, it is carrying "
              "a value the schema should carry, and\n  moving it makes the "
              "distinction invisible to every skill that reads\n  that list.")

    rp = os.path.join(root, "README.md")
    existing = open(rp, encoding="utf-8").read() if os.path.exists(rp) else \
        "# This OS\n"
    fresh = [(p, v) for p, v in notes if v.strip() not in existing]
    print(f"\n{len(notes) - len(fresh)} already present in README.md; "
          f"{len(fresh)} to add.")

    if not a.apply:
        print("\ndry run. Re-run with --apply to move them, or narrow with "
              "--only / --except.\n\nBefore applying, ask of each: would a "
              "skill do anything differently if it\nnever read this sentence?"
              "\n\n  No  — it is a reason. Move it; the README is where "
              "reasons live.\n  Yes — it is a RULE in a field called `note`, "
              "and a rule every skill\n        must obey has to live where "
              "every skill reads. That cost is the\n        rule working. "
              "Keep it, and shorten it to the instruction —\n        drop the "
              "history, the example and the justification, keep\n        the "
              "sentence that changes what a run does.")
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
    json.dump(strip(cfg, keep), open(cp, "w", encoding="utf-8"), indent=indent)
    open(cp, "a", encoding="utf-8").write("\n")
    new = round(len(open(cp, encoding="utf-8").read()) / 4)
    print(f"\nmoved {len(fresh)} to README.md. config.json is now ~{new} "
          f"tokens, down from ~{round(len(raw) / 4)}.")
    print("next: python3 scripts/build_index.py — the counts do not change, "
          "but the recount confirms nothing else did either.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
