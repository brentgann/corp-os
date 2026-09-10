#!/usr/bin/env python3
"""Write the gate's proposal file, and later record what was decided.

The gate is the third invariant and it is a FILE, not a conversation. Four
skills failed that check in one conformance run and two of them had already
had a prose fix applied. The reason was visible once counted: every skill that
passes names `proposals/` and writes there; every skill that fails says
"propose" and never says it is a file. A model satisfies "propose and wait for
confirmation" by proposing in the conversation, which is a reasonable reading
of the words and leaves nothing on disk.

So the instruction stops being a rule to remember and becomes a command to
run. Same move as file_raw.py: a step that happens every time, that nothing
catches if it is skipped, belongs in code.

    python3 scripts/propose.py --root . --layer jobs --slug renewal-early-warning \
        --headline "One job, repaired from an artifact request" \
        --item "create · renewal-early-warning · When a renewal approaches..." \
        --item "decline · dashboard · an artifact, not an outcome" \
        --not-proposing "the support-load split — no second occurrence yet"

    # after the person answers
    python3 scripts/propose.py --root . --record proposals/PROPOSAL-2026-09-10-renewal.md \
        --outcome "renewal-early-warning: confirmed" --outcome "dashboard: declined"
"""
import argparse
import os
import re
import sys
from datetime import date


def slugify(s, n=48):
    return (re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower()))
            .strip("-")[:n].rstrip("-")) or "batch"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--layer", help="the derived layer this batch enters")
    ap.add_argument("--slug", help="short name for the batch")
    ap.add_argument("--headline", default="",
                    help="the one thing in this batch that matters")
    ap.add_argument("--item", action="append", default=[],
                    help="one per proposed entry: '<recommendation> · <id> · <what>'")
    ap.add_argument("--not-proposing", action="append", default=[],
                    help="what is deliberately NOT being proposed, and why")
    ap.add_argument("--record", help="an existing proposal file to append outcomes to")
    ap.add_argument("--outcome", action="append", default=[],
                    help="'<item>: confirmed|declined|deferred|modified'")
    a = ap.parse_args()

    root = os.path.abspath(a.root)
    pdir = os.path.join(root, "proposals")
    if not os.path.isdir(root):
        sys.exit(f"no such OS root: {root}")

    if a.record:
        path = a.record if os.path.isabs(a.record) else os.path.join(root, a.record)
        if not os.path.exists(path):
            sys.exit(f"no proposal at {a.record} — write it before recording outcomes")
        if not a.outcome:
            sys.exit("--record needs at least one --outcome")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(f"\n## Decided {date.today().isoformat()}\n\n")
            for o in a.outcome:
                fh.write(f"- {o}\n")
        declines = [o for o in a.outcome if "declin" in o.lower()]
        print(f"recorded {len(a.outcome)} outcome(s) in {os.path.relpath(path, root)}"
              + (f", {len(declines)} declined" if declines else ""))
        if not declines:
            print("  (no declines in this batch — worth a second look. The "
                  "declines are the only record of what someone chose not to "
                  "know, and a gate that confirms everything is a formality.)")
        return 0

    if not a.layer or not a.item:
        sys.exit("need --layer and at least one --item (or --record to close one out)")

    os.makedirs(pdir, exist_ok=True)
    name = f"PROPOSAL-{date.today().isoformat()}-{slugify(a.slug or a.layer)}.md"
    path = os.path.join(pdir, name)
    k = 2
    while os.path.exists(path):
        path = os.path.join(pdir, name[:-3] + f"-{k}.md")
        k += 1

    L = [f"# Proposal — {a.layer}", "",
         f"_{date.today().isoformat()} · {len(a.item)} item"
         f"{'' if len(a.item) == 1 else 's'} for `{a.layer}/`_", ""]
    if a.headline:
        L += ["## Headline", "", a.headline, ""]
    L += ["## Proposed", ""]
    L += [f"- {i}" for i in a.item]
    L += ["", "## Deliberately not proposed", ""]
    L += ([f"- {n}" for n in a.not_proposing] if a.not_proposing
          else ["- _nothing held back in this batch_"])
    L += ["", "## Decided", "", "_awaiting the person; append outcomes with "
          "`propose.py --record`_", ""]
    open(path, "w", encoding="utf-8").write("\n".join(L))

    rel = os.path.relpath(path, root)
    print(f"wrote {rel}")
    print("Now present it in conversation and wait. Nothing enters "
          f"`{a.layer}/` until this file records the outcome:")
    print(f"  python3 scripts/propose.py --root {a.root} --record {rel} "
          "--outcome '<item>: confirmed' --outcome '<item>: declined'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
