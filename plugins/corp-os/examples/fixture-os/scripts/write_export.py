#!/usr/bin/env python3
"""Write a redaction's two outputs, together, with fixed names.

corp-os-redact produces two things: a cleaned copy safe to send, and a private
log of every removal with its reason. The log is what makes redaction
reviewable rather than a black box -- and measured across five conformance
runs it was the one that went missing, or got written under four different
names. The instruction to write it is present, concrete, explained, and was
strengthened twice. It still varied.

So this takes it out of the model's hands, the same way build_index.py took
the index out. The design point is the refusal: **there is no way to get the
cleaned copy without the log.** One call writes both or neither, which is the
guarantee an instruction could not make.

    python3 scripts/write_export.py spec.json          # writes both, prints paths
    python3 scripts/write_export.py --print-schema

The spec:

    {
      "slug":     "northwind-renewal",     # short, kebab-case
      "audience": "external",              # team | company | external | published
      "cleaned":  "# ...\\n\\nthe redacted markdown ...",
      "removals": [
        {"category":  "personnel",
         "location":  "What moved, second bullet",
         "action":    "generalized",       # generalized | removed
         "original":  "the actual text that was there",
         "replacement": "a discussion about internal promotion readiness",
         "reason":    "names an individual in a promotion context; audience is company-wide"}
      ]
    }

`removals` may be an empty list -- a sweep that found nothing is a real
outcome and the log records that it ran. It may not be absent: that is the
difference between "nothing needed removing" and "nobody looked", and only one
of those is safe to send.
"""

import argparse
import json
import os
import sys
from datetime import date

REQUIRED_REMOVAL = ("category", "location", "action", "reason")
AUDIENCES = ("team", "company", "external", "published")


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def validate(spec):
    for key in ("slug", "audience", "cleaned", "removals"):
        if key not in spec:
            die(f"spec is missing {key!r}. `removals` in particular is required "
                "even when empty -- an absent log and an empty one mean "
                "different things, and only one of them is safe to send.")
    if not isinstance(spec["removals"], list):
        die("`removals` must be a list")
    if spec["audience"] not in AUDIENCES:
        die(f"audience must be one of {AUDIENCES}, got {spec['audience']!r}")
    if not str(spec["cleaned"]).strip():
        die("`cleaned` is empty — nothing to send")
    for i, r in enumerate(spec["removals"], 1):
        missing = [k for k in REQUIRED_REMOVAL if not r.get(k)]
        if missing:
            die(f"removal {i} is missing {missing}. A log entry without a "
                "reason is not a log entry; it is a note that something "
                "vanished.")
        if r["action"] == "generalized" and not r.get("replacement"):
            die(f"removal {i} is marked generalized but has no replacement")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?", help="path to the spec JSON, or - for stdin")
    ap.add_argument("--os-root", default=".", help="the OS root (default: cwd)")
    ap.add_argument("--print-schema", action="store_true")
    a = ap.parse_args()

    if a.print_schema:
        print(__doc__)
        return 0
    if not a.spec:
        die("no spec given; see --print-schema")

    raw = sys.stdin.read() if a.spec == "-" else open(a.spec, encoding="utf-8").read()
    try:
        spec = json.loads(raw)
    except ValueError as e:
        die(f"spec is not valid JSON: {e}")
    validate(spec)

    today = date.today().isoformat()
    outdir = os.path.join(a.os_root, "usage", "exports")
    os.makedirs(outdir, exist_ok=True)
    stem = f"{today}--{spec['slug']}"
    clean_path = os.path.join(outdir, f"{stem}--{spec['audience']}.md")
    log_path = os.path.join(outdir, f"{stem}--redaction-log.md")

    for p in (clean_path, log_path):
        if os.path.exists(p):
            die(f"{p} already exists — pick a different slug rather than "
                "overwriting an export someone may already have sent")

    n = len(spec["removals"])
    header = (
        f"> Redacted copy for a **{spec['audience']}** audience, {today}. "
        f"{n} removal{'s' if n != 1 else ''}. "
        "The full record of what was taken out and why stays in the OS at "
        f"`usage/exports/{os.path.basename(log_path)}` and is not included here.\n\n"
    )

    log = [f"# Redaction log — {spec['slug']}", "",
           f"- **Date**: {today}",
           f"- **Audience**: {spec['audience']}",
           f"- **Cleaned copy**: `{os.path.basename(clean_path)}`",
           f"- **Removals**: {n}", "",
           "This file holds the removed material by design. It stays local, "
           "never travels with the cleaned copy, and is never published.", ""]
    if not n:
        log += ["## No removals", "",
                "The sweep ran and found nothing that had to come out at this "
                "threshold. Recorded because a log that says so and a log that "
                "does not exist mean different things.", ""]
    for i, r in enumerate(spec["removals"], 1):
        log += [f"## Removal {i}", "",
                f"- **Category**: {r['category']}",
                f"- **Location**: {r['location']}",
                f"- **Action**: {r['action']}",
                f"- **Original**: {r.get('original', '(not recorded)')}"]
        if r.get("replacement"):
            log.append(f"- **Replacement**: {r['replacement']}")
        log += [f"- **Reason**: {r['reason']}", ""]

    # Write the log first. If anything is going to fail, fail before the
    # sendable copy exists -- a cleaned copy with no log is the failure this
    # script is here to make impossible.
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    with open(clean_path, "w", encoding="utf-8") as f:
        f.write(header + str(spec["cleaned"]).strip() + "\n")

    print(f"wrote {clean_path}")
    print(f"wrote {log_path}")
    print(f"{n} removal{'s' if n != 1 else ''} logged. The log stays local.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
