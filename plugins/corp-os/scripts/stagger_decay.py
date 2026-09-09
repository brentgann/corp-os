#!/usr/bin/env python3
"""Spread a migrated corpus's decay windows so the first sweep is clearable.

A migration verifies everything on the day it runs. Every window is then
measured from the same date, so they all fire together. Measured in a real
corpus: 79 entries coming due on one day, 71 on another, and **410 on a
third**. The rubric already says a backlog nobody can clear teaches people to
skip the sweep entirely, so a migrated OS is born with the sweep pre-broken --
and every teammate migrating into their own OS is born with the same phase, so
a team hits its cliffs together and concludes collectively that the decay
machinery was decorative.

**What this does not do, and why.** The obvious fix is to spread the
`Verified` dates. That is falsifying a record in a system whose entire premise
is provenance: it would assert that a review happened on a day no review
happened, and every count, sweep and audit downstream would inherit the lie.
The verification date is a fact about the past.

The decay window is not a fact. It is a policy choice about how long a kind of
knowledge stays trustworthy, and 90 days was never precise -- it is a
reasonable round number standing in for "about a quarter". So the window is
what gets varied. The record stays true and the queue stops arriving in one
lump, which is the whole objective.

Jitter is deterministic, hashed on the entry id, so a rebuild reproduces the
same spread rather than reshuffling the queue every time anyone regenerates.

    python3 scripts/stagger_decay.py                  # report the distribution
    python3 scripts/stagger_decay.py --apply          # rewrite the windows
    python3 scripts/stagger_decay.py --spread 0.3     # wider than the default

Dry-run by default, like every other script here that changes the person's
files, because the distribution is what makes the decision decidable.
"""

import argparse
import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import date, timedelta

DECAY_RE = re.compile(r"^(?P<pre>[-*]?\s*\*\*Decay\*\*\s*:\s*)(?P<val>\d+)d\s*$",
                      re.I)
VERIFIED_RE = re.compile(r"^[-*]?\s*\*\*Verified\*\*\s*:\s*(\d{4}-\d{2}-\d{2})",
                         re.I)


def jitter(entry_id, days, spread):
    """A stable offset in [-spread, +spread] of `days`, keyed on the id.

    hashlib rather than hash(): Python randomises str hashing per process, so
    the built-in would give a different spread on every run and the queue would
    reshuffle itself each time the OS was rebuilt.
    """
    h = int(hashlib.sha256(entry_id.encode("utf-8")).hexdigest()[:8], 16)
    frac = (h % 10000) / 10000.0 * 2 - 1          # -1.0 .. +1.0
    out = int(round(days * (1 + frac * spread)))
    return max(7, out)                             # never below a week


def derived_files(root, cfg):
    for name, spec in (cfg.get("layers") or {}).items():
        if not spec.get("enabled") or spec.get("role") != "derived":
            continue
        path = (spec.get("path") or name).rstrip("/")
        full = os.path.join(root, path)
        if path.endswith(".md"):
            if os.path.exists(full):
                yield name, spec, full
        else:
            for f in sorted(glob.glob(os.path.join(full, "*.md"))):
                if os.path.basename(f) not in ("README.md", "INDEX.md"):
                    yield name, spec, f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--spread", type=float, default=0.25,
                    help="fraction of the window to vary by (default 0.25)")
    ap.add_argument("--min-cohort", type=int, default=20,
                    help="only report/act on due-dates carrying at least this "
                         "many entries (default 20)")
    a = ap.parse_args()

    root = os.path.expanduser(a.root)
    if not os.path.exists(os.path.join(root, "meta.json")):
        sys.exit(f"{root} does not look like a Corp-OS (no meta.json).")
    try:
        cfg = json.load(open(os.path.join(root, "config.json"), encoding="utf-8"))
    except (OSError, ValueError):
        cfg = {"layers": {}}

    marker_default = "### "
    before, after, edits = Counter(), Counter(), []

    for name, spec, path in derived_files(root, cfg):
        marker = spec.get("entry_marker", marker_default)
        lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
        # Two passes per entry, not one, because field order is not fixed and
        # the shipped shape puts Decay *before* Verified. A single forward pass
        # sees the window before it knows the date to measure it from, and
        # silently finds nothing -- which is exactly how this first shipped.
        blocks, cur = [], []
        for ln in lines:
            if ln.startswith(marker) and cur:
                blocks.append(cur)
                cur = []
            cur.append(ln)
        blocks.append(cur)

        out, changed = [], False
        for blk in blocks:
            head = blk[0] if blk else ""
            eid = (head[len(marker):].split("—")[0].strip()
                   if head.startswith(marker) else None)
            verified = None
            for ln in blk:
                m = VERIFIED_RE.match(ln)
                if m:
                    verified = m.group(1)
            if eid and verified:
                for i, ln in enumerate(blk):
                    d = DECAY_RE.match(ln)
                    if not d:
                        continue
                    days = int(d.group("val"))
                    new = jitter(eid, days, a.spread)
                    y, mo, dd = (int(x) for x in verified.split("-"))
                    before[(date(y, mo, dd) + timedelta(days=days)).isoformat()] += 1
                    after[(date(y, mo, dd) + timedelta(days=new)).isoformat()] += 1
                    if new != days:
                        blk[i] = f"{d.group('pre')}{new}d"
                        changed = True
                        edits.append((eid, days, new))
            out.extend(blk)
        if changed and a.apply:
            open(path, "w", encoding="utf-8").write("\n".join(out))

    if not before:
        print("No dated decay windows found. Nothing to spread.")
        return 0

    peaks = sorted((n, d) for d, n in before.items() if n >= a.min_cohort)
    print(f"{sum(before.values())} entries carry a dated decay window.")
    if not peaks:
        print(f"No single day carries {a.min_cohort} or more. The queue is "
              "already spread; nothing to do.")
        return 0

    print(f"\nBefore — {len(peaks)} day(s) carrying {a.min_cohort}+ entries:")
    for n, d in sorted(peaks, reverse=True)[:6]:
        print(f"  {d}   {n:>4} entries")
    worst_after = sorted(((n, d) for d, n in after.items()), reverse=True)[:6]
    print(f"\nAfter  — spread ±{int(a.spread * 100)}% of each window, "
          f"deterministic on entry id:")
    for n, d in worst_after:
        print(f"  {d}   {n:>4} entries")
    print(f"\n  worst single day: {max(before.values())} → {max(after.values())}")

    if not a.apply:
        print(f"\nDry run. {len(edits)} window(s) would change. Re-run with "
              "--apply.\nVerified dates are never touched: the window is a "
              "policy choice, the\nverification date is a fact about the past.")
        return 0

    meta_path = os.path.join(root, "meta.json")
    try:
        meta = json.load(open(meta_path, encoding="utf-8"))
        meta.setdefault("history", []).append({
            "date": date.today().isoformat(),
            "event": f"decay windows spread ±{int(a.spread * 100)}% across "
                     f"{len(edits)} entries (deterministic on entry id); "
                     f"worst day {max(before.values())} → {max(after.values())}",
        })
        json.dump(meta, open(meta_path, "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)
    except (OSError, ValueError):
        pass

    print(f"\nSpread {len(edits)} window(s). Run scripts/build_index.py next.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
