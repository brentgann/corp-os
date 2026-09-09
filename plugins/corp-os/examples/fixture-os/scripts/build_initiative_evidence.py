#!/usr/bin/env python3
"""Render the evidence brief for one initiative, from what is on disk.

The generator behind `patterns/doc-initiative-evidence.md`. It reads the derived
layers, groups by confidence, separates what is contested from what is settled,
and emits the `Rests on` line the author pastes into whatever they write -- so
the document they produce joins the stale-grounding view rather than standing
outside it.

    python3 scripts/build_initiative_evidence.py --topic pricing
    python3 scripts/build_initiative_evidence.py --job job-001 --out brief.md

It recounts; it does not judge. Every figure here is derivable from the files,
which is the whole reason this is a script and the document it feeds is not.
"""

import argparse
import glob
import json
import os
import re
import sys

F = "^[-*]?\\s*\\*\\*{f}\\*\\*\\s*:\\s*(.+?)\\s*$"


# Two entry encodings, both legitimate: `### ID` blocks with bold-label fields,
# and one-entry-per-file with YAML frontmatter. This generator shipped reading
# only the first, so every decisions layer answered a confident zero.
FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def field(body, name):
    m = re.search(F.format(f=name), body, re.I | re.M)
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
    text = open(path, encoding="utf-8", errors="replace").read()
    if FM.match(text):
        return [(field(text, "id") or os.path.basename(path)[:-3], text)]
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


def layer_files(root, spec):
    path = (spec.get("path") or "").rstrip("/")
    full = os.path.join(root, path)
    if path.endswith(".md"):
        return [full] if os.path.exists(full) else []
    return [f for f in sorted(glob.glob(os.path.join(full, "*.md")))
            if os.path.basename(f) not in ("README.md", "INDEX.md")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--topic", help="match against the entry body")
    ap.add_argument("--job", help="match against the entry's Jobs field")
    ap.add_argument("--out", help="write here instead of stdout")
    a = ap.parse_args()
    if not a.topic and not a.job:
        sys.exit("pass --topic or --job. An unscoped brief is the whole corpus, "
                 "which is what the index is for.")

    root = os.path.expanduser(a.root)
    cfg = json.load(open(os.path.join(root, "config.json"), encoding="utf-8"))
    layers = cfg.get("layers") or {}
    word = (cfg.get("vocabulary") or {}).get("claim", "claim")

    hits, decisions = [], []
    for name, spec in layers.items():
        # proposals/ is a record of what was proposed, not what was confirmed.
        # Reading it here is the one thing this generator must never do.
        if not spec.get("enabled") or spec.get("role") != "derived":
            continue
        for f in layer_files(root, spec):
            for eid, body in blocks(f, spec.get("entry_marker", "### ")):
                hay = body.lower()
                if a.topic and a.topic.lower() not in hay:
                    continue
                if a.job and a.job.lower() not in field(body, "Jobs").lower():
                    continue
                if "decide_by" in body.lower() or field(body, "Decide by"):
                    decisions.append((eid, body))
                else:
                    hits.append((eid, body, os.path.relpath(f, root)))

    scope = a.job or a.topic
    L = [f"# Evidence brief — {scope}", "",
         f"Generated from what is on disk. {len(hits)} {word}(s), "
         f"{len(decisions)} open decision(s).", ""]

    by_conf = {}
    for eid, body, rel in hits:
        by_conf.setdefault(field(body, "Confidence") or "unstated", []).append(
            (eid, body, rel))

    disputed = by_conf.pop("disputed", [])
    if by_conf:
        L += ["## What is known", ""]
        for conf in sorted(by_conf):
            L += [f"**{conf}** — {len(by_conf[conf])}", ""]
            for eid, body, rel in by_conf[conf]:
                cite = field(body, "Citation")
                L.append(f"- **{eid}** — {field(body, 'Statement')}")
                if cite:
                    L.append(f"  - {cite}  ·  `{rel}`")
            L.append("")

    if disputed:
        L += ["## What is contested", "",
              "Both readings, neither resolved here. A brief that quietly "
              "picks a winner has destroyed the disagreement it exists to "
              "surface.", ""]
        for eid, body, rel in disputed:
            L.append(f"- **{eid}** — {field(body, 'Statement')}  ·  `{rel}`")
        L.append("")

    if decisions:
        L += ["## What is still open", ""]
        for eid, body in sorted(
                decisions, key=lambda x: field(x[1], "Decide by") or "9999"):
            L.append(f"- **{eid}** — {field(body, 'Statement')} · "
                     f"owner {field(body, 'Owner') or 'UNASSIGNED'} · "
                     f"by {field(body, 'Decide by') or 'no date'}")
        L.append("")

    cheap = [e for e, b, _ in hits
             if field(b, "Source fidelity").lower() == "summary"]
    if cheap:
        L += ["## Cheap to strengthen", "",
              f"{len(cheap)} entr{'y is a summary' if len(cheap) == 1 else 'ies are summaries'}. "
              "If the source still exposes a verbatim fetch, that is one call "
              "for a stronger citation than this brief currently carries.", "",
              "- " + ", ".join(cheap), ""]

    ids = [e for e, _b, _r in hits] + [e for e, _b in decisions]
    if ids:
        L += ["## Rests on", "",
              "Paste this into whatever you write from this brief, so the "
              "document joins the stale-grounding view instead of standing "
              "outside it.", "",
              "```markdown", "- **Rests on**: " + ", ".join(ids), "```", ""]
    else:
        L += ["## Nothing on disk matches", "",
              "That is the finding. Capture before specifying.", ""]

    text = "\n".join(L)
    if a.out:
        open(os.path.join(root, a.out), "w", encoding="utf-8").write(text)
        print(f"wrote {a.out} — {len(hits)} entries, {len(decisions)} decisions")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
