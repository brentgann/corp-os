#!/usr/bin/env python3
"""Add a schema field across a layer, filling only what can be derived.

0.14 is the first release where an existing OS has to change shape, and the
line it draws is the one this whole suite keeps drawing: **a field whose value
is derivable is bookkeeping; a field whose value is a judgment is not.**

`upgrade_os.py` names structural migrations and refuses to perform them,
because moving someone's files is judgment. This performs the other half:
adding a field and filling it where the answer is already written down
somewhere else. It never guesses, and what it cannot derive it leaves blank
and counts, because a blank field a person can see is honest and a plausible
wrong value is the thing this model exists to prevent.

    python3 migrate_schema.py --root ~/os --migration source_fidelity
    python3 migrate_schema.py --root ~/os --migration source_fidelity --apply
    python3 migrate_schema.py --list

Dry-run by default. The report is the point: it says how many entries it can
answer for and how many it cannot, and those two numbers are what make the
migration decidable.
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import date

FIELD = "^[-*]?\\s*\\*\\*{f}\\*\\*\\s*:\\s*(.+?)\\s*$"


def read_cfg(root):
    try:
        return json.load(open(os.path.join(root, "config.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return {"layers": {}}


def layer_files(root, cfg, role="derived"):
    for name, spec in (cfg.get("layers") or {}).items():
        if not spec.get("enabled") or spec.get("role") != role:
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


def blocks(text, marker="### "):
    out, cur, buf = [], None, []
    for ln in text.split("\n"):
        if ln.startswith(marker):
            if cur is not None:
                out.append((cur, buf))
            cur, buf = ln, [ln]
        elif cur is not None:
            buf.append(ln)
        else:
            out.append((None, [ln]))
    if cur is not None:
        out.append((cur, buf))
    return out


def field(body, name):
    m = re.search(FIELD.format(f=name), "\n".join(body), re.I | re.M)
    return m.group(1).strip() if m else None


def insert_after(buf, after, line):
    """Put the new field beside the one it relates to, not at the end.

    A schema field appended to the bottom of every entry reads as an
    afterthought and gets skimmed past. Next to the field it qualifies, it is
    read as part of the same thought.
    """
    for i, ln in enumerate(buf):
        if re.match(FIELD.format(f=after), ln, re.I):
            buf.insert(i + 1, line)
            return True
    buf.append(line)
    return False


# ------------------------------------------------------------- migrations

def m_source_fidelity(root, cfg):
    """Derive from the source's connector record; blank where it cannot.

    The connector says what medium it produces. That is a property of the
    source, not a judgment about the entry, which is exactly why it can be
    filled mechanically -- and exactly why a per-entry guess would be wrong.
    """
    conn, cur = {}, None
    cpath = os.path.join(root, "connectors.md")
    if os.path.exists(cpath):
        for ln in open(cpath, encoding="utf-8", errors="replace"):
            if ln.startswith("### "):
                cur = ln[4:].strip()
            m = re.match(r"^[-*]?\s*\*\*Medium\*\*\s*:\s*(\w+)", ln, re.I)
            if m and cur:
                conn[cur.lower()] = m.group(1).lower()

    filled, blank, already, edits = 0, 0, 0, []
    for name, spec, path in layer_files(root, cfg):
        text = open(path, encoding="utf-8", errors="replace").read()
        bs = blocks(text, spec.get("entry_marker", "### "))
        changed = False
        for head, buf in bs:
            if head is None:
                continue
            if field(buf, "Source fidelity"):
                already += 1
                continue
            src = (field(buf, "Source") or "").lower()
            cit = (field(buf, "Citation") or "").lower()
            val = None
            if src.startswith("no source") or "no raw file" in src or not src:
                val = "absent"
            elif cit.startswith("no source"):
                val = "absent"
            else:
                for cname, medium in conn.items():
                    if cname in src:
                        val = {"summary": "summary", "verbatim": "verbatim",
                               "reconstructed": "reconstructed"}.get(medium)
                        break
            if val:
                insert_after(buf, "Confidence", f"- **Source fidelity**: {val}")
                filled += 1
                changed = True
            else:
                blank += 1
        if changed:
            edits.append((path, "\n".join("\n".join(b) for _h, b in bs)))
    return {"filled": filled, "blank": blank, "already": already,
            "edits": edits,
            "cannot": "no connector record names the source, so the medium is "
                      "not written down anywhere and only a person knows it"}


MIGRATIONS = {
    "source_fidelity": {
        "since": "0.14.0",
        "what": "adds `Source fidelity` beside `Confidence` on every derived entry",
        "why": "one enum was carrying three questions, and the cheapest "
               "promotion route was invisible: 599 entries in a real corpus "
               "sat one connector call from a higher confidence with zero "
               "having taken it",
        "fn": m_source_fidelity,
    },
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--migration")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    if a.list or not a.migration:
        print("Available migrations:\n")
        for k, m in MIGRATIONS.items():
            print(f"  {k}  [{m['since']}]\n    {m['what']}\n    {m['why']}\n")
        return 0

    if a.migration not in MIGRATIONS:
        sys.exit(f"migrate_schema.py: no migration named {a.migration!r}. "
                 f"Known: {', '.join(MIGRATIONS)}")

    root = os.path.expanduser(a.root)
    if not os.path.exists(os.path.join(root, "meta.json")):
        sys.exit(f"{root} does not look like a Corp-OS (no meta.json).")

    m = MIGRATIONS[a.migration]
    r = m["fn"](root, read_cfg(root))
    total = r["filled"] + r["blank"] + r["already"]

    print(f"{a.migration}  [{m['since']}]\n  {m['what']}\n")
    print(f"  {total} entr{'y' if total == 1 else 'ies'} examined")
    print(f"  {r['already']:>5} already carry it")
    print(f"  {r['filled']:>5} can be filled from what is already written down")
    print(f"  {r['blank']:>5} cannot — left blank on purpose")
    if r["blank"]:
        print(f"\n  Why not: {r['cannot']}.\n  A blank field someone can see is "
              "honest. A plausible wrong value is what\n  this model exists to "
              "prevent, so these are yours to fill.")

    if not a.apply:
        print(f"\nDry run. Re-run with --apply to write "
              f"{r['filled']} field(s).")
        return 0

    for path, content in r["edits"]:
        open(path, "w", encoding="utf-8").write(content)

    meta_path = os.path.join(root, "meta.json")
    try:
        meta = json.load(open(meta_path, encoding="utf-8"))
        meta.setdefault("history", []).append({
            "date": date.today().isoformat(),
            "event": f"schema migration {a.migration} [{m['since']}]: "
                     f"{r['filled']} filled, {r['blank']} left blank",
        })
        json.dump(meta, open(meta_path, "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)
    except (OSError, ValueError):
        pass

    print(f"\nWrote {r['filled']} field(s) across {len(r['edits'])} file(s). "
          "Run scripts/build_index.py next.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
