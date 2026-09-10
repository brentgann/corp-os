#!/usr/bin/env python3
"""What a skill reads on pre-flight against a REAL OS, in tokens. No model.

Every cost number in this repo until now came from the plugin's own files:
skill bodies and reference/. That is the half that does not grow. The other
half is the OS itself -- INDEX.md, config.json, the layer indexes -- and it
grows with the corpus, so it is invisible in a four-entry fixture and is the
only part that scales with a real deployment.

This costs nothing to run. Point it at a copy of a real OS and it says what
one invocation of each skill pays before it does any work.

    python3 scripts/corpus_load.py /path/to/an-os
    python3 scripts/corpus_load.py /path/to/an-os --sections   # INDEX.md breakdown
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def find_plugin(explicit=None):
    """Where the skills and reference/ live.

    This is repo tooling, not an OS script: it is not in scaffold.py's SHIPPED
    list and no OS carries a copy. It still has to run against an OS that
    lives anywhere, and against an installed plugin rather than a clone, so
    the location is a flag with two fallbacks and never an assumption.
    """
    for c in (explicit, os.environ.get("CLAUDE_PLUGIN_ROOT"),
              os.path.join(ROOT, "plugins", "corp-os")):
        if c and os.path.isdir(os.path.join(c, "skills")):
            return c
    return None


def tok(s):
    return round(len(s) / 4)


def read(p):
    try:
        return open(p, encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def index_sections(text):
    """Token cost per '## ' section of an index, largest first."""
    parts, cur, name = [], [], "(header)"
    for line in text.split("\n"):
        if line.startswith("## "):
            parts.append((name, "\n".join(cur)))
            name, cur = line[3:].strip(), [line]
        else:
            cur.append(line)
    parts.append((name, "\n".join(cur)))
    return sorted(((n, tok(b), sum(1 for x in b.split("\n")
                                   if x.startswith("- ")))
                   for n, b in parts), key=lambda x: -x[1])


def _notes(o):
    """Every `note` value at any depth. They are for people and cost tokens."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "note" and isinstance(v, str):
                yield v
            else:
                yield from _notes(v)
    elif isinstance(o, list):
        for v in o:
            yield from _notes(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("os_root")
    ap.add_argument("--sections", action="store_true")
    ap.add_argument("--plugin", help="path to plugins/corp-os, or an installed "
                                     "copy. Defaults to $CLAUDE_PLUGIN_ROOT, "
                                     "then this repo's own")
    a = ap.parse_args()
    PLUGIN = find_plugin(a.plugin)
    r = a.os_root

    if not os.path.isdir(os.path.join(r, "raw")):
        sys.exit(f"no raw/ in {r} — is this a corp-os root?")

    root_index = read(os.path.join(r, "INDEX.md"))
    cfgtxt = read(os.path.join(r, "config.json"))
    layer_idx = {p: tok(read(p)) for p in
                 sorted(glob.glob(os.path.join(r, "*", "INDEX.md")))}

    # Everything every skill reads in pre-flight, before its own body.
    floor = tok(root_index) + tok(cfgtxt)
    print(f"OS: {r}\n")
    print(f"  config.json          {tok(cfgtxt):>7}")
    print(f"  INDEX.md             {tok(root_index):>7}")
    print(f"  ---------------------{'':->7}")
    print(f"  pre-flight floor     {floor:>7}  paid by every skill, every run\n")

    if layer_idx:
        print("  layer indexes (read when that layer is touched):")
        for p, n in sorted(layer_idx.items(), key=lambda x: -x[1]):
            print(f"    {os.path.relpath(p, r):<28} {n:>7}")
        print()

    if a.sections:
        # config.json is the authority and every skill reads it first, so its
        # size is paid on every run of every skill and has never once been
        # counted. In one real OS it was 3,846 tokens, 40% of the pre-flight
        # floor, against 1,073 in a synthetic one -- the difference being
        # layer count and prose `note` fields, which are documentation the
        # model re-reads forever.
        try:
            cfg = json.loads(cfgtxt)
            print("  config.json by key:")
            rows = [(k, tok(json.dumps(v))) for k, v in cfg.items()]
            for k, n in sorted(rows, key=lambda x: -x[1]):
                print(f"    {k[:44]:<46} {n:>7}")
            if isinstance(cfg.get("layers"), dict):
                print("    layers, by layer:")
                for k, v in sorted(cfg["layers"].items(),
                                   key=lambda x: -tok(json.dumps(x[1]))):
                    print(f"      {k[:42]:<44} {tok(json.dumps(v)):>7}")
            notes = sum(tok(str(v)) for v in _notes(cfg))
            if notes:
                print(f"\n    prose `note` fields, total          {notes:>9}"
                      "  documentation, re-read every run")
            print()
        except ValueError:
            print("  (config.json did not parse)\n")

        print("  INDEX.md by section:")
        for n, c, e in index_sections(root_index):
            if c:
                per = f"{c // e:>4}/entry" if e else ""
                print(f"    {n[:36]:<38} {c:>7} {e:>5} entries {per}")
        print("\n    A scannable line is roughly 15-20 tokens. Well above that "
              "is an\n    `index_line` template doing more than one line of "
              "work, paid once\n    per entry in the file every skill reads "
              "first.\n")
        # Where an entry line's tokens actually go. A template of two fields
        # still cost 43 tokens an entry in one real OS, which means the
        # template was not the lever and reading the number without the
        # mechanism would have sent someone to edit the wrong thing. Every
        # line is `- **[label](path)** — rest`, and label and path are a
        # fixed cost paid before any content: a long entry name is charged
        # twice, once as the label and once inside its own slugified path.
        rows = []
        for line in root_index.split("\n"):
            m = re.match(r"^- \*\*\[(.+?)\]\((.+?)\)\*\*\s*(?:—\s*(.*))?$", line)
            if m:
                rows.append((tok(m.group(1)), tok(m.group(2)),
                             tok(m.group(3) or "")))
        if rows:
            n = len(rows)
            lab = sum(r[0] for r in rows)
            pth = sum(r[1] for r in rows)
            rest = sum(r[2] for r in rows)
            print(f"  where {n} entry lines go:")
            print(f"    label (the entry's name)        {lab:>7} {lab // n:>5}/entry")
            print(f"    path (a link to the file)       {pth:>7} {pth // n:>5}/entry")
            print(f"    everything the template renders {rest:>7} {rest // n:>5}/entry")
            over = lab + pth
            print(f"\n    {over * 100 // max(1, lab + pth + rest)}% of an entry "
                  f"line is its name and its path.\n    Shortening a template "
                  "cannot touch that; shortening entry NAMES can,\n    because "
                  "the name is charged twice — once as the label, once inside\n"
                  "    the slug of its own path.\n")

        # The template is the fix, so print it next to what it costs. Nobody
        # can shorten a line they have to go and look up, and this is the last
        # large item that is a config question rather than a plugin one.
        try:
            layers = (json.loads(cfgtxt).get("layers") or {})
            tmpl = [(k, v.get("index_line")) for k, v in layers.items()
                    if isinstance(v, dict) and v.get("index_line")]
            if tmpl:
                print("  index_line templates:")
                for k, v in sorted(tmpl, key=lambda x: -len(x[1] or "")):
                    print(f"    {k:<14} {v}")
                print("\n    Each field costs on every entry. A template "
                      "carrying four fields and\n    three separators is four "
                      "lookups the scan did not ask for; the one\n    that "
                      "earns its place answers \"is this the entry I want\" "
                      "and stops.\n")
        except ValueError:
            pass

    if not PLUGIN:
        print("  The OS numbers above are the ones that scale with a corpus "
              "and they are complete.\n  For the per-skill table, pass "
              "--plugin <path to plugins/corp-os>.")
        return 0
    try:
        from ref_load import scan, tok as _t          # noqa: F401
        sizes = {os.path.basename(f): tok(read(f))
                 for f in glob.glob(os.path.join(PLUGIN, "reference", "*.md"))}
        rows = []
        for d in sorted(glob.glob(os.path.join(PLUGIN, "skills", "*"))):
            u, c, _ = scan(d, sizes)
            body = re.sub(r"^---\s*\n.*?\n---\s*\n", "",
                          read(os.path.join(d, "SKILL.md")), count=1, flags=re.S)
            rows.append((os.path.basename(d), tok(body),
                         sum(sizes.get(x, 0) for x in u)))
        rows.sort(key=lambda x: -(x[1] + x[2] + floor))
        print(f"  {'skill':26}{'body':>7}{'refs':>7}{'OS':>7}{'total':>8}")
        for n, b, rf in rows:
            print(f"  {n:26}{b:>7}{rf:>7}{floor:>7}{b + rf + floor:>8}")
        print(f"\n  The OS column is identical for every skill and grows with "
              f"the corpus.\n  At this size it is "
              f"{floor * 100 // max(1, (rows[0][1] + rows[0][2] + floor))}% of the "
              f"most expensive skill's pre-flight.")
    except ImportError:
        print("  (ref_load.py not importable; skipping the per-skill table)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
