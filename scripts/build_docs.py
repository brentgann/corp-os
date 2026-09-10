#!/usr/bin/env python3
"""Regenerate the shareable documents from the markdown that is the source.

Three PDFs sat in docs/ for a week with no generator anywhere in the repo:
handbook, architecture-diagram and skill-map, referenced by nothing, a week
stale, and impossible for anyone to rebuild correctly. A generated artefact
with no generator is worse than no artefact -- a reader takes it as current
and there is no way to check.

So the generator is the thing that ships, and the outputs carry the version
they were built from in their filename. Everything comes from the markdown
already in the repo; nothing here has content of its own.

    python3 scripts/build_docs.py                 # PDFs, into dist/docs
    python3 scripts/build_docs.py --only cost     # one
    python3 scripts/build_docs.py --data          # also dist/corp-os-docs.json

`--data` writes every document as rendered HTML plus a section list, the skill
roster read from the plugin's own frontmatter, and the version — which is what
the single-page tabbed build consumes. It is one file so that page cannot
quote a figure the repo does not hold.

Needs pandoc and a LaTeX engine for the PDFs. Without one it still writes the
HTML and says which step it skipped, rather than failing the whole run.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# label -> (source, title, subtitle, toc)
DOCS = {
    "overview":     ("README.md", "corp-os",
                     "What it is, what holds it together, and what is measured", False),
    "handbook":     ("plugins/corp-os/README.md", "corp-os — Handbook",
                     "The plugin's own README: every skill, and the release history", True),
    "architecture": ("docs/ARCHITECTURE.md", "corp-os — Architecture",
                     "The design, every decision and why, and what is still open", True),
    "cost":         ("docs/COST.md", "corp-os — Cost",
                     "What a run costs, measured on a real corpus", True),
    "backlog":      ("docs/BACKLOG.md", "corp-os — Backlog",
                     "Measured and unfixed, with the numbers behind each", True),
    "install":      ("docs/INSTALL.md", "corp-os — Installing and releasing",
                     "Installing, updating an OS, and cutting a release", True),
}

# Chosen by trying them. Charter reads better and xelatex cannot resolve it
# here — it falls through to METAFONT and dies looking for a .tfm — so the
# font list is the one this machine actually has rather than the one that
# would look best. Box-drawing characters appear in every directory listing
# in these docs and the default mono font has none of them, which is a
# warning per line and a dropped glyph in the output.
FONTS = ["-V", "mainfont=DejaVu Serif",
         "-V", "sansfont=DejaVu Sans",
         "-V", "monofont=DejaVu Sans Mono",
         "-V", "geometry:margin=1.1in",
         "-V", "fontsize=10pt",
         "-V", "colorlinks=true",
         "-V", "linkcolor=RoyalBlue",
         "-V", "urlcolor=RoyalBlue",
         "-V", "toccolor=black"]



# Tables in these docs carry code in both columns, and LaTeX sizes a longtable
# from its source widths rather than the page — the three-`scripts/` table in
# COST.md ran off the right margin and clipped `prune_config_notes.py` in half.
# Shrinking the table body fixes every one of them without touching the prose,
# and `\sloppy` stops long unbreakable paths overflowing a line.
HEADER_TEX = r"""
\usepackage{etoolbox}
\AtBeginEnvironment{longtable}{\footnotesize}
\AtBeginEnvironment{tabular}{\footnotesize}
\setlength{\emergencystretch}{3em}
\sloppy
"""


def header_file(dist):
    os.makedirs(dist, exist_ok=True)
    path = os.path.join(dist, ".header.tex")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(HEADER_TEX)
    return path


def version():
    with open(os.path.join(ROOT, "plugins", "corp-os",
                           ".claude-plugin", "plugin.json"), encoding="utf-8") as fh:
        return json.load(fh)["version"]


def engine():
    for e in ("xelatex", "lualatex", "pdflatex"):
        if shutil.which(e):
            return e
    return None


def build(label, out_dir, ver, eng, html_only, header=None):
    src, title, subtitle, toc = DOCS[label]
    src_path = os.path.join(ROOT, src)
    if not os.path.exists(src_path):
        print(f"  {label}: no {src} — skipped")
        return None
    stem = f"corp-os-{label}-v{ver}"
    meta = ["-V", f"title={title}", "-V", f"subtitle={subtitle}",
            "-V", f"date=v{ver}", "-V", "author="]
    if html_only or not eng:
        return None
    out = os.path.join(out_dir, stem + ".pdf")
    cmd = (["pandoc", src_path, "-o", out, "--pdf-engine=" + eng,
            "--from", "gfm+smart", "--standalone"]
           + (["-H", header] if header else []) + FONTS + meta
           + (["--toc", "--toc-depth=2"] if toc else []))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  {label}: FAILED\n{(r.stderr or r.stdout)[-600:]}")
        return None
    print(f"  {label}: {os.path.basename(out)}  "
          f"{os.path.getsize(out) // 1024}KB")
    return out



def emit_data(ver, dist):
    """Everything the single-page build reads, from the repo and nowhere else.

    The skill roster comes from each SKILL.md's own frontmatter rather than a
    transcribed list, so the page cannot claim a skill the plugin does not
    have. Section ids are namespaced by document because all six render into
    one page and `#the-shape-of-a-bill` would otherwise collide.
    """
    import glob
    import re
    try:
        import markdown
    except ImportError:
        print("  data: python-markdown is not installed — skipped")
        return None

    def slug(t, seen):
        s = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "s"
        n, out = 1, s
        while out in seen:
            n += 1
            out = f"{s}-{n}"
        seen.add(out)
        return out

    data = {"version": ver, "docs": []}
    for key, (src, label, blurb, _) in DOCS.items():
        path = os.path.join(ROOT, src)
        if not os.path.exists(path):
            continue
        raw = open(path, encoding="utf-8").read()
        body = markdown.Markdown(
            extensions=["tables", "fenced_code", "sane_lists"]).convert(raw)
        seen, toc = set(), []

        def add_id(m):
            lvl, inner = m.group(1), m.group(2)
            text = re.sub(r"<[^>]+>", "", inner)
            sid = f"{key}-" + slug(text, seen)
            if lvl == "2":
                toc.append({"id": sid, "text": text})
            return f'<h{lvl} id="{sid}">{inner}</h{lvl}>'

        body = re.sub(r"<h([23])>(.*?)</h\1>", add_id, body, flags=re.S)
        data["docs"].append({"key": key, "label": label.split("— ")[-1],
                             "blurb": blurb, "source": src, "html": body,
                             "toc": toc, "words": len(raw.split())})

    data["skills"] = []
    for sp in sorted(glob.glob(os.path.join(
            ROOT, "plugins", "corp-os", "skills", "*", "SKILL.md"))):
        b = open(sp, encoding="utf-8").read()
        pas = re.search(r"> \*\*(Mechanical|Mixed|Judgment) pass", b)
        data["skills"].append({
            "name": re.search(r"^name:\s*(.+)$", b, re.M).group(1).strip(),
            "pass": pas.group(1) if pas else "—",
            "one_line": re.search(r"^description:\s*(.+)$", b, re.M)
                          .group(1).split(".")[0].strip() + "."})

    os.makedirs(dist, exist_ok=True)
    out = os.path.join(dist, "corp-os-docs.json")
    json.dump(data, open(out, "w", encoding="utf-8"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="one label from the set")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "docs"))
    ap.add_argument("--html-only", action="store_true")
    ap.add_argument("--data", action="store_true",
                    help="also emit dist/corp-os-docs.json for the tabbed page")
    a = ap.parse_args()

    ver = version()
    eng = engine()
    os.makedirs(a.out, exist_ok=True)
    if not shutil.which("pandoc"):
        sys.exit("pandoc is not installed; it is what converts the markdown")
    if not eng and not a.html_only:
        print("NOTE: no LaTeX engine (xelatex/lualatex/pdflatex), so no PDFs "
              "this run.\n")

    labels = [a.only] if a.only else list(DOCS)
    bad = [l for l in labels if l not in DOCS]
    if bad:
        sys.exit(f"unknown: {bad}. Known: {', '.join(DOCS)}")

    print(f"corp-os v{ver} → {os.path.relpath(a.out, ROOT)}"
          + (f" ({eng})" if eng else "") + "\n")
    hdr = header_file(a.out) if eng and not a.html_only else None
    made = [p for l in labels
            if (p := build(l, a.out, ver, eng, a.html_only, hdr))]
    if hdr and os.path.exists(hdr):
        os.remove(hdr)
    print(f"\n{len(made)} document(s).")
    if a.data:
        out = emit_data(ver, os.path.dirname(a.out.rstrip("/")) or a.out)
        print(f"data: {os.path.relpath(out, ROOT)} "
              f"{os.path.getsize(out) // 1024}KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
