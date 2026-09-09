#!/usr/bin/env python3
"""File fetched items into raw/ in one call. Dedupe, name, write, cutoff.

Every step here is deterministic given the item, and every one of them was
being done by a model, one item at a time. That is the expensive shape: each
turn re-sends the whole session prefix, so filing forty items paid the prefix
forty times to do arithmetic and string formatting. The repo's own rule is
that a step which has to happen every time, and which nothing else catches if
it is skipped, belongs in code. Filing never presented as a step because it
presents as content.

What stays with the model is what needs judgment: deciding which items to
capture at all, and proposing what the derived layer should hold. Neither is
in here, and the cutoff is passed in rather than computed -- a batch remainder
must not fall behind it, and only the run knows what it did not reach.

    python3 scripts/file_raw.py --root . --items items.json
    python3 scripts/file_raw.py --root . --items - --cutoff 2026-09-08

items.json is a list of objects:
    external_id  required, the dedupe key
    date         required, YYYY-MM-DD
    source       required, the connector's `Feeds` source value
    type         required, e.g. meeting / thread / note
    body         required, verbatim; this script never rewrites it
    slug         optional, derived from title when absent
    title        optional
    person       optional
    also_present optional list
    jobs         optional list
    tags         optional list
"""
import argparse
import json
import os
import re
import sys

FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def slugify(s, n=48):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return (s[:n].rstrip("-")) or "untitled"


def existing_ids(raw):
    """external_id -> path, for everything already filed."""
    out = {}
    for f in sorted(os.listdir(raw)) if os.path.isdir(raw) else []:
        if not f.endswith(".md") or f in ("INDEX.md", "README.md"):
            continue
        p = os.path.join(raw, f)
        m = FM.match(open(p, encoding="utf-8", errors="ignore").read())
        if not m:
            continue
        e = re.search(r"^external_id:\s*(.+?)\s*$", m.group(1), re.M)
        if e:
            out[e.group(1).strip().strip('"\'')] = f
    return out


def yaml_list(v):
    return "[" + ", ".join(str(x) for x in v) + "]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--items", required=True, help="JSON file, or - for stdin")
    ap.add_argument("--cutoff", help="advance this source's cutoff in "
                                     "connectors.md. Omit when the batch left "
                                     "anything unreached")
    ap.add_argument("--source", help="connector name for the cutoff line")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    root = os.path.abspath(a.root)
    raw = os.path.join(root, "raw")
    if not os.path.isdir(raw):
        sys.exit(f"no raw/ in {root} — is this a corp-os root?")

    items = json.load(sys.stdin if a.items == "-" else
                      open(a.items, encoding="utf-8"))
    if isinstance(items, dict):
        items = [items]

    seen = existing_ids(raw)
    wrote, dupes, bad = [], [], []

    for it in items:
        missing = [k for k in ("external_id", "date", "source", "type", "body")
                   if not it.get(k)]
        if missing:
            bad.append((it.get("external_id") or "?", f"missing {', '.join(missing)}"))
            continue
        eid = str(it["external_id"])
        if eid in seen:
            dupes.append((eid, seen[eid]))
            continue

        name = f"{it['date']}--{slugify(it['source'], 24)}--" \
               f"{slugify(it.get('slug') or it.get('title'))}.md"
        # Two items can legitimately land on the same day with the same title.
        # Suffixing keeps both; overwriting would silently destroy source
        # material, which is the one thing nothing can rebuild.
        path, k = os.path.join(raw, name), 2
        while os.path.exists(path):
            path = os.path.join(raw, name[:-3] + f"-{k}.md")
            k += 1

        fm = [f"source: {it['source']}"]
        if it.get("person"):
            fm.append(f"person: {it['person']}")
        if it.get("also_present"):
            fm.append(f"also_present: {yaml_list(it['also_present'])}")
        fm += [f"date: {it['date']}", f"type: {it['type']}",
               f"jobs: {yaml_list(it.get('jobs') or [])}",
               f"tags: {yaml_list(it.get('tags') or [])}",
               f"external_id: {eid}", "processed: false"]
        doc = "---\n" + "\n".join(fm) + "\n---\n\n" + it["body"].rstrip() + "\n"
        if not a.dry_run:
            open(path, "w", encoding="utf-8").write(doc)
        seen[eid] = os.path.basename(path)
        wrote.append((eid, os.path.basename(path), len(doc)))

    if a.cutoff and a.source and not a.dry_run:
        cp = os.path.join(root, "connectors.md")
        if os.path.exists(cp):
            t = open(cp, encoding="utf-8").read()
            pat = re.compile(r"(^-\s*\*\*Cutoff\*\*\s*:\s*)(.+?)\s*$", re.M)
            blocks = re.split(r"(?m)^(?=##\s)", t)
            for i, b in enumerate(blocks):
                if a.source.lower() in b.split("\n")[0].lower() and pat.search(b):
                    blocks[i] = pat.sub(lambda m: m.group(1) + a.cutoff, b, count=1)
                    open(cp, "w", encoding="utf-8").write("".join(blocks))
                    print(f"cutoff for {a.source} -> {a.cutoff}")
                    break
            else:
                print(f"WARNING: no Cutoff line found for {a.source} in "
                      "connectors.md; left unchanged")

    for eid, name, n in wrote:
        print(f"  wrote  {name}  ({n} bytes)")
    for eid, name in dupes:
        print(f"  dupe   {eid} already filed as {name}")
    for eid, why in bad:
        print(f"  SKIP   {eid}: {why}")
    print(f"\n{len(wrote)} filed, {len(dupes)} already present, {len(bad)} rejected."
          + ("  (dry run)" if a.dry_run else ""))
    if wrote and not a.dry_run:
        print("next: python3 scripts/build_index.py — counts and INDEX.md")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
