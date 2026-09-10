#!/usr/bin/env python3
"""What each source produced, against how much of it ever became anything.

A selector narrows a shared system to a slice. Inside the slice, most of what
a wiki or a tracker holds still will not earn a claim, and nothing was
measuring which sources those were. Triage decides per item on metadata, which
is the weakest evidence available; the strongest evidence is what the last two
hundred items from that source actually turned into, and it is already on disk.

Costs nothing to run. No model.

    python3 scripts/source_yield.py --root .
    python3 scripts/source_yield.py --root . --source confluence-product

Read it as a ratio, not a score. A source at 3 claims per 100 files is not
failing -- it may be narrow and precious. It is asking whether its selector
still describes what you wanted, and whether it should be pulled monthly
rather than daily.
"""
import argparse
import os
import re
import sys
from collections import defaultdict

FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
SRC = re.compile(r"^[-*]?\s*\*\*Source\*\*\s*:\s*(.+?)\s*$", re.I | re.M)
JOBS = re.compile(r"^[-*]?\s*\*\*Jobs\*\*\s*:\s*(.+?)\s*$", re.I | re.M)
ENTRY = re.compile(r"^###\s+(\S+)", re.M)


def fm_field(text, name):
    m = FM.match(text)
    if not m:
        return None
    f = re.search(rf"^{name}:\s*(.+?)\s*$", m.group(1), re.M)
    return f.group(1).strip().strip("\"'") if f else None


def read(p):
    try:
        return open(p, encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--source", help="one source only")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    raw = os.path.join(root, "raw")
    if not os.path.isdir(raw):
        sys.exit(f"no raw/ in {root} — is this a corp-os root?")

    # raw file -> its source, and whether anyone marked it processed
    by_file, files_for = {}, defaultdict(list)
    processed = set()
    for f in sorted(os.listdir(raw)):
        if not f.endswith(".md") or f in ("INDEX.md", "README.md"):
            continue
        t = read(os.path.join(raw, f))
        s = fm_field(t, "source") or "(unlabelled)"
        by_file[f] = s
        files_for[s].append(f)
        if (fm_field(t, "processed") or "").lower() == "true":
            processed.add(f)

    # every derived entry that cites a raw file, and whether it serves a job
    cited, cited_with_job = defaultdict(set), defaultdict(set)
    for dirpath, _dirs, names in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        if rel.startswith(("raw", "proposals", "usage", ".git")):
            continue
        for n in names:
            if not n.endswith(".md") or n in ("INDEX.md", "README.md"):
                continue
            body = read(os.path.join(dirpath, n))
            for block in re.split(r"(?m)^(?=###\s)", body):
                m = SRC.search(block)
                if not m:
                    continue
                base = os.path.basename(m.group(1).strip().strip("`"))
                if base not in by_file:
                    continue
                s = by_file[base]
                cited[s].add(base)
                j = JOBS.search(block)
                if j and j.group(1).strip() not in ("", "none", "-"):
                    cited_with_job[s].add(base)

    rows = []
    for s, fs in sorted(files_for.items()):
        if a.source and a.source not in s:
            continue
        n = len(fs)
        c = len(cited[s])
        rows.append((s, n, c, len(cited_with_job[s]),
                     len([f for f in fs if f in processed and f not in cited[s]])))
    if not rows:
        print("no sources matched.")
        return 0

    print(f"{'source':26}{'raw':>6}{'cited':>7}{'serving a job':>15}"
          f"{'processed, nothing':>20}")
    for s, n, c, j, dead in sorted(rows, key=lambda r: -r[1]):
        print(f"{s[:25]:26}{n:>6}{c:>7}{j:>15}{dead:>20}"
              f"   {c * 100 // max(1, n):>3}%")

    print()
    tot = sum(r[1] for r in rows)
    tc = sum(r[2] for r in rows)
    print(f"{tot} raw files, {tc} cited by something ({tc * 100 // max(1, tot)}%).")
    thin = [r for r in rows if r[1] >= 20 and r[2] * 100 // max(1, r[1]) < 10]
    if thin:
        print("\nUnder 10% cited, on 20+ files — the selector is worth "
              "revisiting:")
        for s, n, c, _j, _d in thin:
            print(f"  {s} — {n} files, {c} cited")
        print("  Narrow the Selector, lengthen the Cadence, or decline the "
              "source. Nothing here needs deleting:\n  raw/ is append-only, and "
              "the fix is to stop capturing, not to remove what was captured.")
    dead_tot = sum(r[4] for r in rows)
    if dead_tot:
        print(f"\n{dead_tot} file(s) marked processed that nothing cites. "
              "That is a normal and useful state —\nsomeone read them and "
              "concluded nothing. It is only a signal when one source "
              "supplies most of them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
