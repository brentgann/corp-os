#!/usr/bin/env python3
"""
Deterministic INDEX.md regenerator and drift checker for a corp-os.

Recounts what is actually on disk, rewrites INDEX.md's listings and counts to
match, and reports any drift it corrected.

Config-driven: reads config.json for which layers exist, what they are called,
each layer's index_line template, and what is excluded from the scan path. A
custom layer with an index_line renders exactly like a shipped one. Falls back
to the shipped defaults when there is no config.

It does NOT read raw/ content, does NOT retag anything, and does NOT touch the
derived layer's substance. Bookkeeping, not judgment. Safe to run after any
manual edit; a full re-derivation is corp-os-rebuild's job, not this script's.

Usage:
    python3 scripts/build_index.py [os_root] [--check]

    --check   report drift and exit non-zero if any; write nothing.
"""

import glob
import json
import os
import re
import sys
from datetime import date

FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def frontmatter(path):
    """Parse flat scalar keys out of a file's YAML frontmatter. Lists -> []."""
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return {}
    m = FM.match(text)
    if not m:
        return {}
    out, key = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^\s*-\s+", line) and key:
            out.setdefault(key + "__list", []).append(
                line.strip().lstrip("-").strip().strip("\"'")
            )
            continue
        m2 = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m2:
            key, val = m2.group(1), m2.group(2).strip().strip("\"'")
            if val:
                out[key] = val
    return out


# Only layers with a declared index_line are enabled here. A layer that is
# enabled without one degrades the scan contract silently, so people/ and
# topics/ are no longer shipped defaults -- an OS that wants either declares it
# in config.json with its own entry_schema and index_line. See
# reference/configuration.md, "No layer is enabled without a schema".
DEFAULT_LAYERS = {
    "raw":       {"enabled": True, "role": "source"},
    "jobs":      {"enabled": True, "role": "derived",
                  "index_line": "{id} — {statement}"},
    "claims":    {"enabled": True, "role": "derived"},
    "company":   {"enabled": False, "role": "derived",
                  "index_line": "{company} — {relationship}"},
    "proposals": {"enabled": True, "role": "record"},
}


def load_config(root):
    """config.json is the authority; shipped defaults fill the gaps."""
    path = os.path.join(root, "config.json")
    cfg = {}
    if os.path.exists(path):
        try:
            cfg = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"WARNING: config.json unreadable ({e}) — using defaults.")
            cfg = {}
    layers = dict(DEFAULT_LAYERS)
    for name, spec in (cfg.get("layers") or {}).items():
        merged = dict(layers.get(name, {}))
        merged.update(spec or {})
        layers[name] = merged
    cfg["layers"] = layers
    return cfg


def _lbl(name, layers):
    """A layer's display name: its configured label, else its key."""
    spec = layers.get(name) or {}
    return spec.get("label") or name.replace("_", " ").title()


def render_line(template, fm, fallback):
    """Fill an index_line template from frontmatter. Missing keys degrade to
    the literal placeholder being dropped, never to a crash."""
    if not template:
        return fallback
    out = template
    for key, val in fm.items():
        out = out.replace("{" + key + "}", str(val))
    out = re.sub(r"\s*[-—·|]?\s*\{[a-zA-Z_][\w-]*\}", "", out)
    return out.strip(" -—·|") or fallback


def md_files(root, sub):
    d = os.path.join(root, sub)
    if not os.path.isdir(d):
        return []
    return sorted(
        f for f in glob.glob(os.path.join(d, "*.md"))
        if os.path.basename(f) not in ("README.md", "INDEX.md")
    )


def count_headers(path, marker="### "):
    """Count entries in a file. `marker` is per-layer configurable because
    layers legitimately differ: heading-per-entry ("### "), list-per-entry
    ("- **"), or bold-term-per-entry ("**"). Assuming one shape silently
    reports zero for the others."""
    if not os.path.exists(path):
        return 0
    return sum(
        1 for line in open(path, encoding="utf-8", errors="replace")
        if line.startswith(marker)
    )


def survey(root, cfg):
    """Everything on disk, for every enabled layer including custom ones."""
    s = {}
    s["_single"] = {}
    for name, spec in cfg["layers"].items():
        if not spec.get("enabled", False):
            continue
        path = (spec.get("path") or name).rstrip("/")
        if path.endswith(".md"):
            # A whole layer living in one file (gaps.md, themes.md). Count its
            # entry headers, and its group headers if it declares a grouping.
            full = os.path.join(root, path)
            marker = spec.get("entry_marker", "### ")
            groups = {}
            if os.path.exists(full):
                for line in open(full, encoding="utf-8", errors="replace"):
                    m = re.match(r"^## (.+?)(?:\s*\((\d+)\))?\s*$", line)
                    if m:
                        groups[m.group(1).strip()] = 0
                        cur = m.group(1).strip()
                    elif line.startswith(marker) and groups:
                        groups[cur] = groups.get(cur, 0) + 1
            s["_single"][name] = {
                "path": path,
                "entries": count_headers(full, marker),
                "groups": groups,
                "in_scan": spec.get("in_scan_path", True),
            }
            continue
        s[name] = md_files(root, path)
    s.setdefault("raw", md_files(root, "raw"))
    s.setdefault("claims", [])
    s["claim_entries"] = sum(count_headers(f) for f in s.get("claims", []))
    gspec = cfg["layers"].get("glossary") or {}
    s["glossary_terms"] = count_headers(
        os.path.join(root, gspec.get("path", "glossary.md")),
        gspec.get("entry_marker", "### "))
    s["unprocessed"] = [
        f for f in s["raw"]
        if str(frontmatter(f).get("processed", "false")).lower() != "true"
    ]
    s["unlisted"] = sorted(
        d for d in os.listdir(root)
        if os.path.isdir(os.path.join(root, d))
        and not d.startswith((".", "_"))
        and d not in ("scripts", "usage")
        and d not in {(sp.get("path") or n).rstrip("/")
                      for n, sp in cfg["layers"].items()}
        and d not in {"archive", "_archive"}
    )
    return s


def render_index(root, s, cfg):
    """Build INDEX.md. Every entry gets a one-line descriptor -- that is what
    makes the scan contract work; a bare link forces a second read."""
    layers = cfg["layers"]
    scan = cfg.get("scan") or {}
    # A misspelled key here fails silently and renders a plausible but wrong
    # "not in the scan path" section, so say so rather than falling back mutely.
    for k in scan:
        if k not in ("excluded_from_scan", "stop_early", "order"):
            print(f"WARNING: config scan.{k} is not a key this script knows — "
                  "check reference/configuration.md; it is being ignored.")
    excluded = scan.get("excluded_from_scan", ["sensitive.md", "raw/_archive/"])
    L = [
        "# corp-os — Index",
        "",
        "Scan this first. Most questions should be answerable from this file "
        "alone; open a detail file only when the one-liners here are not enough.",
        "",
        f"_Regenerated {date.today().isoformat()} by scripts/build_index.py "
        "(counts and listings only — no retagging)._",
        "",
        "## Counts",
        "",
        f"- **Raw files**: {len(s['raw'])} ({len(s['unprocessed'])} unprocessed)",
    ]
    if s.get("jobs"):
        L.insert(-1, f"- **{_lbl('jobs', layers)}**: {len(s['jobs'])}")
    if s.get("claim_entries"):
        L.append(f"- **{_lbl('claims', layers)}**: {s['claim_entries']}")
    for name in sorted(k for k in s if isinstance(s.get(k), list)
                       and k not in ("raw", "jobs", "claims", "unprocessed",
                                     "unlisted")):
        if s[name]:
            L.append(f"- **{_lbl(name, layers)}**: {len(s[name])}")
    for name, meta in sorted(s.get("_single", {}).items()):
        if not meta["in_scan"]:
            continue
        detail = ""
        if meta["groups"]:
            detail = " (" + ", ".join(f"{k.lower()} {v}"
                                      for k, v in meta["groups"].items()) + ")"
        L.append(f"- **{_lbl(name, layers)}**: {meta['entries']}{detail}")
    if s["glossary_terms"] and "glossary" not in (s.get("_single") or {}):
        L.append(f"- **Glossary terms**: {s['glossary_terms']}")
    L.append("")

    # One section per enabled file-per-entry layer, shipped or custom, each
    # rendered through its own index_line template.
    missing_template = []
    for name in ["jobs"] + sorted(k for k in s if isinstance(s.get(k), list)
                                  and k not in ("raw", "jobs", "claims",
                                                "unprocessed", "unlisted")):
        files = s.get(name) or []
        if not files:
            continue
        spec = layers.get(name, {})
        if spec.get("role") == "record":
            continue
        template = spec.get("index_line")
        if not template:
            missing_template.append(name)
        L += [f"## {name.replace('_', ' ').title()}", ""]
        for f in files:
            fm = frontmatter(f)
            fallback = os.path.basename(f)[:-3].replace("-", " ")
            label = (fm.get(spec.get("label_field", "")) or fm.get("id")
                     or fm.get("title") or fm.get("name") or fm.get("company")
                     or fallback)
            line = render_line(template, fm, "")
            if line.startswith(label):
                line = line[len(label):].lstrip(" -—·|")
            rel = os.path.relpath(f, root)
            L.append(f"- **[{label}]({rel})**" +
                     (f" — {line}" if line else ""))
        L.append("")

    if missing_template:
        L += ["> **Incomplete index.** These layers have no `index_line` in "
              "`config.json`, so their entries are listed as bare links and "
              "cannot be scanned without opening each file: "
              + ", ".join(f"`{m}`" for m in missing_template)
              + ". Run corp-os-configure to give each one a template.", ""]

    for name, meta in sorted(s.get("_single", {}).items()):
        if not meta["in_scan"] or not meta["groups"]:
            continue
        L += [f"## {_lbl(name, layers)}", "",
              f"{meta['entries']} entries in [`{meta['path']}`]({meta['path']}), "
              "grouped as:", ""]
        for g, n in meta["groups"].items():
            L.append(f"- **{g}** — {n}")
        L.append("")

    if s["unprocessed"]:
        L += ["## Unprocessed queue", "",
              "Raw material not yet folded into the derived layer.", ""]
        for f in s["unprocessed"]:
            fm = frontmatter(f)
            rel = os.path.relpath(f, root)
            gist = fm.get("gist") or fm.get("type", "")
            L.append(f"- [{os.path.basename(f)[:-3]}]({rel})" +
                     (f" — {gist}" if gist else ""))
        L.append("")

    L += ["## Not in the scan path", ""]
    for x in excluded:
        L.append(f"- `{x}` — excluded by config. Open only when the task "
                 "specifically requires it.")
    L += ["- `raw/` — source of truth, but never loaded wholesale. "
          "corp-os-rebuild is the sole exception.", ""]

    if s.get("unlisted"):
        L += ["", "> **Directories on disk but not in `config.json`**: "
              + ", ".join(f"`{d}/`" for d in s["unlisted"])
              + ". Every skill treats config as the authority, so these are "
              "invisible to all of them. Declare or remove them.", ""]
    return "\n".join(L)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_only = "--check" in sys.argv
    root = os.path.abspath(args[0]) if args else os.getcwd()

    if not os.path.isdir(os.path.join(root, "raw")):
        sys.exit(f"No raw/ found in {root} — is this a corp-os root?")

    cfg = load_config(root)
    s = survey(root, cfg)
    counted = {
        "claims": s["claim_entries"],
        "raw": len(s["raw"]),
        "unprocessed": len(s["unprocessed"]),
        "glossary_terms": s["glossary_terms"],
    }
    for name in s:
        if isinstance(s.get(name), list) and name not in (
                "raw", "claims", "unprocessed", "unlisted"):
            counted[name] = len(s[name])
    for name, meta in (s.get("_single") or {}).items():
        counted[name] = meta["entries"]

    meta_path = os.path.join(root, "meta.json")
    drift = []
    meta = {}
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path, encoding="utf-8"))
        stored = meta.get("counts", {})
        for k, actual in counted.items():
            if k in stored and stored[k] != actual:
                drift.append((k, stored[k], actual))

    if drift:
        print("Drift found (meta.json vs. disk):")
        for k, was, now in drift:
            print(f"  {k:16s} meta={was:<6} actual={now:<6} ({now - was:+d})")
    else:
        print("No count drift.")

    if check_only:
        sys.exit(1 if drift else 0)

    open(os.path.join(root, "INDEX.md"), "w", encoding="utf-8").write(
        render_index(root, s, cfg)
    )

    if meta:
        meta.setdefault("counts", {}).update(counted)
        meta["generated_at"] = date.today().isoformat()
        json.dump(meta, open(meta_path, "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)

    parts = [f"{counted['raw']} raw ({counted['unprocessed']} unprocessed)"]
    for k in sorted(k for k in counted
                    if k not in ("raw", "unprocessed", "glossary_terms")):
        if counted[k]:
            parts.append(f"{counted[k]} {k}")
    print("INDEX.md regenerated: " + ", ".join(parts) + ".")
    if s.get("unlisted"):
        print("Undeclared directories (invisible to every skill): "
              + ", ".join(s["unlisted"]))
    if s["unprocessed"]:
        print("Unprocessed material is waiting — run corp-os-claims to work the queue.")


if __name__ == "__main__":
    main()
