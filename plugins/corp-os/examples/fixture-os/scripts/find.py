#!/usr/bin/env python3
"""Return the entries that match, instead of reading the files that contain them.

The scan contract says read INDEX.md, then the layer index, then the detail
file. That is correct and it does not scale: the index grows with the corpus and
is read on every run, and a topic file hands back every entry in it to answer a
question about one. Measured on a real entry shape: 156 tokens to read one claim,
and a topic file holding forty costs all forty.

This does the narrowing part deterministically, which is the same split as
everywhere else in this suite -- selecting by id, job, topic, confidence or decay
state is bookkeeping; deciding what the matches mean is not.

    python3 scripts/find.py --topic pricing
    python3 scripts/find.py --job job-004 --stale
    python3 scripts/find.py --id CL-0042 --id CL-0044
    python3 scripts/find.py --topic renewal --digest
    python3 scripts/find.py --layer decisions --overdue

`--digest` is one line per entry -- id, kind, confidence, decay state, jobs and
the statement. About a fifth the size of the entries themselves, and usually
enough to decide which of them you actually need in full.
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import date, timedelta

F = "^[-*]?\\s*\\*\\*{f}\\*\\*\\s*:\\s*(.+?)\\s*$"


# A corpus stores entries in two shapes and both are legitimate: many entries per
# file as `### ID — statement` blocks with bold-label fields (claims, arguments),
# and one entry per file carrying its fields in YAML frontmatter (jobs, decisions).
# Anything that reads entries has to handle both, and a reader that handles one
# returns a confident, quiet zero for every layer using the other.
FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def field(body, name):
    """Look for the field in both encodings, bold-label first."""
    m = re.search(F.format(f=re.escape(name)), body, re.I | re.M)
    if m:
        return m.group(1).strip()
    fm = FM.match(body)
    if fm:
        key = name.strip().lower().replace(" ", "_")
        for ln in fm.group(1).split("\n"):
            if ":" not in ln or ln.startswith((" ", "\t", "#")):
                continue
            k, v = ln.split(":", 1)
            if k.strip().lower() == key:
                return v.strip().strip('"').strip("'").strip("[]")
    return ""


def blocks(path, marker="### "):
    """(id, body) per entry, in whichever shape the file uses."""
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return []
    if FM.match(text):
        eid = field(text, "id") or os.path.basename(path)[:-3]
        return [(eid, text)]
    out, cur, buf = [], None, []
    for ln in text.split("\n"):
        if ln.startswith(marker):
            if cur:
                out.append((cur, "\n".join(buf)))
            cur, buf = ln[len(marker):].split("—")[0].strip(), [ln]
        elif cur:
            buf.append(ln)
    if cur:
        out.append((cur, "\n".join(buf)))
    return out


def decay_state(body, today):
    """'stale' | 'never' | 'fresh' | 'durable' | '' — the same rule build_index
    applies, so a person never sees the two disagree."""
    win = field(body, "Decay").rstrip(".,").lower()
    if not win:
        return ""
    if win in ("none", "never", "-", "n/a"):
        return "durable"
    d = re.fullmatch(r"(\d+)\s*d", win)
    if not d:
        return ""
    v = field(body, "Verified")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", v)
    if not m:
        return "never"
    try:
        due = date(*map(int, m.groups())) + timedelta(days=int(d.group(1)))
    except ValueError:
        return ""
    return "stale" if due < today else "fresh"


def layers(root, cfg, want=None):
    for name, spec in (cfg.get("layers") or {}).items():
        # proposals/ is what was proposed, not what was confirmed. A search that
        # returns from it hands back unreviewed material wearing the same shape
        # as reviewed material, which is the one thing the gate exists to stop.
        if not spec.get("enabled") or spec.get("role") == "source":
            continue
        if name == "proposals" or spec.get("role") == "record" and want != name:
            if want != name:
                continue
        if want and name != want:
            continue
        path = (spec.get("path") or name).rstrip("/")
        full = os.path.join(root, path)
        files = ([full] if path.endswith(".md") and os.path.exists(full)
                 else [f for f in sorted(glob.glob(os.path.join(full, "*.md")))
                       if os.path.basename(f) not in ("README.md", "INDEX.md")])
        for f in files:
            yield name, spec, f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--id", action="append", default=[], help="entry id, repeatable")
    ap.add_argument("--job", help="entries serving this job")
    ap.add_argument("--topic", help="free text, matched against the whole entry")
    ap.add_argument("--layer", help="restrict to one declared layer")
    ap.add_argument("--confidence", help="exact confidence value")
    ap.add_argument("--stale", action="store_true", help="past its decay window")
    ap.add_argument("--never-verified", action="store_true")
    ap.add_argument("--overdue", action="store_true", help="decide_by in the past")
    ap.add_argument("--digest", action="store_true", help="one line per entry")
    ap.add_argument("--limit", type=int, default=40)
    a = ap.parse_args()

    if not any((a.id, a.job, a.topic, a.layer, a.confidence, a.stale,
                a.never_verified, a.overdue)):
        sys.exit("find.py: give it something to narrow by. An unscoped search is "
                 "the whole corpus, which is what INDEX.md is for.")

    root = os.path.expanduser(a.root)
    try:
        cfg = json.load(open(os.path.join(root, "config.json"), encoding="utf-8"))
    except (OSError, ValueError):
        sys.exit(f"find.py: no readable config.json at {root}")
    today = date.today()
    ids = {i.strip().lower() for i in a.id}

    hits, scanned = [], 0
    for name, spec, f in layers(root, cfg, a.layer):
        for eid, body in blocks(f, spec.get("entry_marker", "### ")):
            scanned += 1
            st = decay_state(body, today)
            if ids and eid.lower() not in ids:
                continue
            if a.job and a.job.lower() not in field(body, "Jobs").lower():
                continue
            if a.topic and a.topic.lower() not in body.lower():
                continue
            if a.confidence and field(body, "Confidence").lower() != a.confidence.lower():
                continue
            if a.stale and st != "stale":
                continue
            if a.never_verified and st != "never":
                continue
            if a.overdue:
                d = field(body, "Decide by")
                if not (re.match(r"\d{4}-\d{2}-\d{2}", d) and d < today.isoformat()):
                    continue
            hits.append((name, eid, body, st, os.path.relpath(f, root)))

    if not hits:
        print(f"No match. {scanned} entries scanned.\n"
              "That is a finding, not an error — say the corpus does not cover "
              "it rather than answering from anywhere else.")
        return 0

    shown = hits[:a.limit]
    if a.digest:
        for name, eid, body, st, rel in shown:
            print("\t".join([eid, name, field(body, "Kind") or "-",
                             field(body, "Confidence") or "-", st or "-",
                             field(body, "Jobs") or "-",
                             (field(body, "Statement") or
                              field(body, "So what") or "")[:120]]))
    else:
        for name, eid, body, st, rel in shown:
            print(body.rstrip())
            print(f"    ↳ {rel}" + (f"  ·  decay: {st}" if st else ""))
            print()

    print(f"— {len(hits)} match of {scanned} scanned"
          + (f", {len(hits) - len(shown)} not shown (--limit {a.limit})"
             if len(hits) > len(shown) else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
