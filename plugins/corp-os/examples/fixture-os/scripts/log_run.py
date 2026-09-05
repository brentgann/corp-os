#!/usr/bin/env python3
"""Close out a skill run: the usage-log row and the meta.json history entry.

Every skill in this suite ends the same two ways -- a row in usage/log.md
carrying the honest friction, and, for anything that changed the OS, a dated
entry in meta.json's history. Both are bookkeeping nothing else will catch if
they are skipped, and both are at the end of a run, which measurement says is
exactly where they get dropped: corp-os-brief wrote its history entry in one
run out of three.

So they leave the model's hands, the same way build_index.py took the index
and write_export.py took redaction's log. One call writes both. It exercises
no judgment -- the caller supplies the words, including the friction, which is
the one field a script could never invent.

    python3 scripts/log_run.py --skill corp-os-brief \\
        --scope "since 2026-08-20" \\
        --friction "no prior brief recorded; had to ask for a window" \\
        --event "weekly brief covering 2026-08-20 to 2026-09-05"

Omit --event for a run that changed nothing (a recall, a brief that found
nothing) and only the log row is written. Omit --friction and it refuses:
"none" is a real answer and an empty one is not, and that field is the entire
input to corp-os-improve.
"""

import argparse
import json
import os
import sys
from datetime import date

HEADER = ("| date | skill | scope | friction |\n"
          "|---|---|---|---|\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True)
    ap.add_argument("--scope", required=True,
                    help="what the run covered, in a few words")
    ap.add_argument("--friction", required=True,
                    help="where it hurt. 'none' is a real answer; blank is not. "
                         "This field is the whole input to corp-os-improve, "
                         "which refuses to propose anything without a count "
                         "behind it")
    ap.add_argument("--event", default=None,
                    help="dated meta.json history entry. Omit only when the "
                         "run changed nothing on disk")
    ap.add_argument("--os-root", default=".")
    a = ap.parse_args()

    if not a.friction.strip():
        print("ERROR: --friction is empty. Write 'none' if there genuinely was "
              "none — a blank field and an honest 'none' are different data.",
              file=sys.stderr)
        return 1

    today = date.today().isoformat()
    root = a.os_root

    # -- usage/log.md
    log = os.path.join(root, "usage", "log.md")
    os.makedirs(os.path.dirname(log), exist_ok=True)
    existing = ""
    if os.path.exists(log):
        existing = open(log, encoding="utf-8").read()
    if "| date |" not in existing:
        existing = (existing.rstrip() + "\n\n" if existing.strip() else
                    "# Usage log\n\n") + HEADER
    row = (f"| {today} | {a.skill} | {a.scope.replace('|', '/')} "
           f"| {a.friction.replace('|', '/')} |\n")
    with open(log, "w", encoding="utf-8") as f:
        f.write(existing.rstrip("\n") + "\n" + row)

    # -- meta.json history
    wrote_event = False
    meta_path = os.path.join(root, "meta.json")
    if a.event:
        if not os.path.exists(meta_path):
            print(f"ERROR: --event given but {meta_path} does not exist. The "
                  "log row was still written; fix the path and re-run with "
                  "--event alone.", file=sys.stderr)
            return 1
        try:
            meta = json.load(open(meta_path, encoding="utf-8"))
        except ValueError as e:
            print(f"ERROR: {meta_path} is not valid JSON ({e}). The log row was "
                  "written; meta.json was left alone rather than overwritten.",
                  file=sys.stderr)
            return 1
        meta.setdefault("history", []).append({"date": today, "event": a.event})
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
            f.write("\n")
        wrote_event = True

    print(f"logged {a.skill} in usage/log.md"
          + (" and meta.json history" if wrote_event else
             " (no history entry — nothing changed on disk)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
