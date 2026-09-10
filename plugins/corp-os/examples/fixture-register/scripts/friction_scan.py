#!/usr/bin/env python3
"""Count what the usage log actually supports, before anything is proposed.

corp-os-improve states the bar in prose -- "a cluster of one is not a finding",
"one friction row is one occurrence, and the bar is more than one" -- in two
places, and across three runs it wrote a packet from a single row twice and
proposals from a single row twice. The bar reads as advice because the skill is
invoked by a person who has just asked for changes, and a run under that
pressure finds some.

So the count stops being a judgment and becomes a command, the way filing did
in 0.19.1 and the gate did in 0.25.0. Two things happen here, and only the
first needs any cleverness at all:

  1. The arithmetic floor. A log with fewer than `--bar` rows carrying real
     friction cannot support a finding at that bar, whatever the rows say.
     No clustering is involved and no reading is required. This exits 3.

  2. The citation. Above the floor, grouping friction rows into a theme IS
     judgment and stays with the model -- but a candidate has to name the
     dated rows behind it, and this checks that those rows exist and carry
     real friction. The same rule claims live under: a count you cannot cite
     is a count you invented.

    python3 scripts/friction_scan.py --root .
    python3 scripts/friction_scan.py --root . \
        --candidate "index scan too long" --row 2026-08-20 --row 2026-09-02

`--row` attaches to the `--candidate` before it, so several candidates can be
checked in one call.
"""
import argparse
import os
import re
import sys

EMPTY = {"", "-", "none", "n/a", "na", "nothing", "no friction"}


def rows(root):
    """(date, skill, friction) for every data row in usage/log.md."""
    path = os.path.join(root, "usage", "log.md")
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return None
    out = []
    for ln in text.split("\n"):
        if not re.match(r"^\|\s*\d{4}-\d{2}-\d{2}\s*\|", ln):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 3:
            continue
        # Four-column (pre-0.17) and six-column rows both end in friction.
        out.append((c[0], c[1], c[-1]))
    return out


def real(friction):
    f = friction.strip().lower()
    # A gate note is this script's own bookkeeping, not the person's friction.
    f = re.sub(r"·\s*gate:.*$", "", f).strip()
    return f not in EMPTY and bool(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--bar", type=int, default=2,
                    help="occurrences a finding needs. The shipped bar is 2: "
                         "one occurrence is an anecdote and this skill's "
                         "failure mode is manufacturing findings from it")
    ap.add_argument("--candidate", action="append", default=[],
                    help="a theme you want to propose. Each needs --row dates "
                         "behind it")
    ap.add_argument("--row", action="append", default=[],
                    help="a dated log row supporting the --candidate before it")
    a = ap.parse_args()

    # Rebuild the candidate -> rows association from argv order, since argparse
    # flattens both lists.
    pairs = []
    i, argv = 0, sys.argv[1:]
    while i < len(argv):
        if argv[i] == "--candidate" and i + 1 < len(argv):
            pairs.append([argv[i + 1], []])
            i += 2
        elif argv[i] == "--row" and i + 1 < len(argv):
            if pairs:
                pairs[-1][1].append(argv[i + 1])
            i += 2
        else:
            i += 1

    R = rows(a.root)
    if R is None:
        print(f"no usage/log.md under {a.root} — an OS with no log has no "
              "usage to study. The correct output is to say so.", file=sys.stderr)
        return 3

    fr = [r for r in R if real(r[2])]
    print(f"{len(R)} logged run{'' if len(R) == 1 else 's'}, "
          f"{len(fr)} carrying real friction (bar is {a.bar})")
    if fr:
        print()
        by_skill = {}
        for d, s, f in fr:
            by_skill.setdefault(s, []).append(d)
            print(f"  {d}  {s:<22} {f}")
        print()
        for s, ds in sorted(by_skill.items(), key=lambda kv: -len(kv[1])):
            if len(ds) >= a.bar:
                print(f"  {s}: {len(ds)} friction rows — clears the bar by "
                      "skill, though the theme still has to")

    if len(fr) < a.bar:
        print(f"\nNothing here can clear a bar of {a.bar}: there "
              f"{'is' if len(fr) == 1 else 'are'} {len(fr)} friction row"
              f"{'' if len(fr) == 1 else 's'} in the whole log. Write nothing "
              "to usage/proposals.md and\nno improvement packet. Say what a "
              "second occurrence would look like so the\nnext run recognises "
              "it — an empty pass is the correct output of a thin log.",
              file=sys.stderr)
        return 3

    if not pairs:
        print("\nGrouping these into themes is yours. Come back with each "
              "candidate and the\ndated rows behind it, and this will check "
              "them:\n\n  python3 scripts/friction_scan.py --root "
              f"{a.root} --candidate \"<theme>\" --row <date> --row <date>")
        return 0

    dates = {d for d, _, _ in fr}
    bad = 0
    print()
    for theme, ds in pairs:
        missing = [d for d in ds if d not in dates]
        n = len([d for d in ds if d in dates])
        if missing:
            print(f"  REJECTED  {theme}\n            no friction row on "
                  f"{', '.join(missing)}", file=sys.stderr)
            bad += 1
        elif n < a.bar:
            print(f"  REJECTED  {theme}\n            {n} occurrence"
                  f"{'' if n == 1 else 's'}, bar is {a.bar}", file=sys.stderr)
            bad += 1
        else:
            print(f"  OK        {theme} — {n} occurrences "
                  f"({', '.join(ds)})")
    if bad:
        print(f"\n{bad} candidate{'' if bad == 1 else 's'} did not clear the "
              "bar. Those go in usage/proposals.md as\nconsidered-and-rejected "
              "with the count, not as proposals — that record is what\nstops "
              "the same idea coming back every quarter.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
