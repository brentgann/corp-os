#!/usr/bin/env python3
"""Destroy raw material under a retention obligation, in the right order.

Deleting a source file is not file management. The claims that cite it have to
be re-cited first, or they end up pointing at files that do not exist -- worse
than `no source`, because they still look sourced and nothing downstream can
tell the difference.

corp-os-configure describes that sequence in five steps and has been measured
running it correctly two times in three. The third run edits the original file
into a tombstone instead of writing a tombstone beside it and unlinking, which
is an edit to a raw file: the one operation raw/ never permits, and the one
whose failure destroys source material. Two instruction passes did not fix it.

So the sequence lives here instead, in the order that cannot be got wrong:

    1. find every entry citing the file
    2. re-cite each to `no source` and lower its confidence
    3. record a cohort ceiling so no later pass promotes them back
    4. log what is about to be destroyed, and under what obligation
    5. write the tombstone, then unlink the original

    python3 scripts/delete_source.py --dry-run raw/2026-08-14--email--x.md \
        --reason "deletion clause, Meridian MSA section 9"
    python3 scripts/delete_source.py --apply raw/2026-08-14--email--x.md \
        --reason "deletion clause, Meridian MSA section 9"

Nothing is destroyed without --apply, and --apply refuses without --reason.
"Housekeeping" is not an obligation; if there is no clause, no schedule and no
deletion right, the answer is `archive`, which costs nothing and is reversible.
"""

import argparse
import json
import os
import re
import sys
from datetime import date

CONFIDENCE_FLOOR = "reconstructed"


def find_citing(root, target):
    """Every derived file that names this raw file, and how many times."""
    base = os.path.basename(target)
    stem = os.path.splitext(base)[0]
    hits = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "raw")]
        for f in fn:
            if not f.endswith(".md"):
                continue
            p = os.path.join(dp, f)
            try:
                txt = open(p, encoding="utf-8").read()
            except OSError:
                continue
            n = txt.count(stem)
            if n:
                hits[os.path.relpath(p, root)] = n
    return hits


def recite(root, rel, stem, today, reason):
    """Point citations at `no source` and cap confidence, per entry.

    Entry-scoped on purpose. A file-wide substitution would demote every
    `confirmed` claim in any file that merely happens to contain one citing
    entry -- destroying confidence that was never in question, silently, in a
    script whose whole job is not destroying things silently.
    """
    p = os.path.join(root, rel)
    txt = open(p, encoding="utf-8").read()

    # Split on entry headings, keeping the headings with their blocks.
    parts = re.split(r"(?m)^(?=### )", txt)
    changed = False
    out = []
    for block in parts:
        if stem not in block:
            out.append(block)
            continue
        b = re.sub(rf"^(\s*-\s*\*\*Source\*\*:).*$",
                   rf"\1 no source  <!-- destroyed {today}: {reason} -->",
                   block, flags=re.M)
        b = re.sub(r"^(\s*-\s*\*\*Citation\*\*:).*$",
                   r"\1 no source", b, flags=re.M)
        # Confidence cannot outlive the thing that confirmed it.
        b = re.sub(r"^(\s*-\s*\*\*Confidence\*\*:\s*)confirmed\s*$",
                   rf"\1{CONFIDENCE_FLOOR}", b, flags=re.M)
        if b != block:
            changed = True
        out.append(b)

    if changed:
        open(p, "w", encoding="utf-8").write("".join(out))
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="+", help="raw files to destroy, relative to --os-root")
    ap.add_argument("--os-root", default=".")
    ap.add_argument("--reason", default=None,
                    help="the obligation. A clause, a retention schedule, a "
                         "deletion right. Not 'housekeeping'")
    ap.add_argument("--cohort", default=None,
                    help="cohort key for the confidence ceiling "
                         "(default: deleted-<date>)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true",
                   help="report what would happen and change nothing")
    g.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    root = a.os_root
    today = date.today().isoformat()
    cohort = a.cohort or f"deleted-{today}"

    if a.apply and not a.reason:
        print("ERROR: --apply requires --reason naming the obligation. If there "
              "is no clause, schedule or deletion right behind this, the answer "
              "is `archive` — out of the scan path, still on disk, reversible, "
              "and it costs nothing.", file=sys.stderr)
        return 1

    missing = [t for t in a.targets if not os.path.exists(os.path.join(root, t))]
    if missing:
        print(f"ERROR: not found: {missing}", file=sys.stderr)
        return 1

    plan = {t: find_citing(root, t) for t in a.targets}
    total = sum(sum(v.values()) for v in plan.values())
    print(f"{len(a.targets)} file(s) to destroy, {total} citation(s) across "
          f"{len(set().union(*[set(v) for v in plan.values()]) if plan else [])} entr(ies).\n")
    for t, hits in plan.items():
        print(f"  {t}")
        for rel, n in sorted(hits.items()):
            print(f"      cited {n}x in {rel}")
        if not hits:
            print("      no citations found — nothing to re-cite")
    print()

    if a.dry_run:
        print("dry run — nothing changed. Re-run with --apply and --reason to "
              "carry it out.")
        return 0

    touched = set()
    for t, hits in plan.items():
        stem = os.path.splitext(os.path.basename(t))[0]
        for rel in hits:
            if recite(root, rel, stem, today, a.reason):
                touched.add(rel)

    # -- cohort ceiling, so nothing promotes these back later
    cfg_path = os.path.join(root, "config.json")
    if os.path.exists(cfg_path):
        cfg = json.load(open(cfg_path, encoding="utf-8"))
        cfg.setdefault("confidence_ceilings", {})[cohort] = {
            "ceiling": CONFIDENCE_FLOOR,
            "reason": f"source destroyed {today} under: {a.reason}",
        }
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
            f.write("\n")

    # -- log before destroying, so the record survives a failure at the last step
    meta_path = os.path.join(root, "meta.json")
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path, encoding="utf-8"))
        meta.setdefault("history", []).append({
            "date": today,
            "event": (f"destroyed {len(a.targets)} raw file(s) under: {a.reason}. "
                      f"{len(touched)} entr(ies) re-cited to `no source`; "
                      f"cohort ceiling `{cohort}` recorded."),
        })
        meta.setdefault("deletions", []).append({
            "date": today, "reason": a.reason, "cohort": cohort,
            "files": list(a.targets), "entries_recited": sorted(touched),
        })
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
            f.write("\n")

    # -- tombstone beside it, THEN unlink. Never an edit of the original.
    for t in a.targets:
        src = os.path.join(root, t)
        fm = ""
        try:
            head = open(src, encoding="utf-8").read()
            m = re.match(r"^---\n(.*?)\n---\n", head, re.S)
            fm = m.group(1) if m else ""
        except OSError:
            pass
        tomb = os.path.join(root, os.path.splitext(t)[0] + ".deleted.md")
        with open(tomb, "w", encoding="utf-8") as f:
            f.write("---\n" + fm + "\ndeleted: " + today +
                    "\ndeleted_under: " + json.dumps(a.reason) +
                    "\ncohort: " + cohort + "\n---\n\n"
                    "The source file that stood here was destroyed under a "
                    "retention obligation. Its content is gone by design and is "
                    "not reproduced here.\n\n"
                    "This tombstone exists so a rebuild reading `raw/` can tell "
                    "*destroyed under obligation* from *never captured* — two "
                    "situations that call for opposite responses — and so the "
                    "`no source` entries left behind trace to a reason rather "
                    "than looking like sloppiness.\n\n"
                    f"- **Entries re-cited**: {len(touched)}\n"
                    f"- **Confidence ceiling**: `{cohort}` at `{CONFIDENCE_FLOOR}`\n")
        os.remove(src)
        print(f"destroyed {t}\n  tombstone {os.path.relpath(tomb, root)}")

    print(f"\n{len(touched)} entr(ies) re-cited, ceiling `{cohort}` recorded, "
          "logged in meta.json. Run scripts/build_index.py to recount.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
