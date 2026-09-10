#!/usr/bin/env python3
"""corp-os documents as PDFs, in the five-phase design system.

Markdown -> styled HTML -> PDF. Replaces the pandoc/LaTeX path, which had no
type system, no colour, and clipped its own tables.

Colour discipline, from the system's own rules:
  navy  interactive only — links, the cover rule, the TOC leader
  pink  secondary accent — pull quotes and the eyebrow marks
  cyan  tertiary, smallest touches — inline code tint
  p1-p5 structural, and used here for exactly one thing: the five invariants,
        which are a genuine ordered set of five. Nowhere else.
  p3/p4/p5 double as pass / warning / danger in the measured strip.
"""
import base64
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_DIR = os.path.join(HERE, "assets", "fonts")
DATA = os.path.join(ROOT, "dist", "corp-os-docs.json")
OUT = os.path.join(ROOT, "dist", "docs")

# Never a literal. The figures are whatever the committed run report holds,
# and when that report covers fewer cases than the suite defines it has no
# headline — both generators carried a hardcoded 203/208 for a day while the
# repo's report said 13/16 over two cases, which is how a published page goes
# on quoting a number nobody can reproduce.
if not os.path.exists(DATA):
    raise SystemExit("no dist/corp-os-docs.json — run "
                     "`python3 scripts/build_docs.py --data` first")
D = json.load(open(DATA, encoding="utf-8"))

C = D.get("conformance") or {}
PARTIAL = C.get("partial", True)
CONF = {"passed": C.get("passed"), "total": C.get("total"),
        "cases": C.get("cases", 0), "skills": C.get("skills_covered", 0),
        "skills_total": C.get("skills_total", 0),
        "defined": C.get("cases_defined", 0), "open": C.get("open_checks", 0),
        "model": C.get("model") or "—", "date": C.get("date") or "—"}
HEADLINE = ("—" if PARTIAL else f"{CONF['passed']}/{CONF['total']}")
COVER_NOTE = (
    f"No full-suite run is recorded. The last report covered {CONF['cases']} "
    f"of {CONF['defined']} cases; run `python3 evals/run_conformance.py "
    f"--workers 3 --timeout 900` to produce one."
    if PARTIAL else
    f"Measured {CONF['date']} on {CONF['model']}, one run per case")

FONTS = [("Inter", 400, "inter-latin-400-normal.woff2"),
         ("Inter", 500, "inter-latin-500-normal.woff2"),
         ("Inter", 600, "inter-latin-600-normal.woff2"),
         ("Inter", 700, "inter-latin-700-normal.woff2"),
         ("Space Grotesk", 600, "space-grotesk-latin-600-normal.woff2"),
         ("Space Grotesk", 700, "space-grotesk-latin-700-normal.woff2"),
         ("IBM Plex Mono", 500, "ibm-plex-mono-latin-500-normal.woff2"),
         ("IBM Plex Mono", 600, "ibm-plex-mono-latin-600-normal.woff2")]


def face_css():
    out = []
    for fam, wt, fn in FONTS:
        p = os.path.join(FONT_DIR, fn)
        b64 = base64.b64encode(open(p, "rb").read()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-style:normal;"
                   f"font-weight:{wt};font-display:block;"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "\n".join(out)


CSS = """
:root{
  --ink:#17132B; --ink-soft:#4A4459; --ink-faint:#8A8399;
  --paper:#FBF8F4; --paper-raised:#FFFFFF;
  --line:#9ED3DE; --line-soft:#C9E8ED;
  --line-pink:#EAB8D2; --line-pink-soft:#F1D6E7;
  --p1:#4B3F95; --p1-tint:#EAE8F8;
  --p2:#2D6CAD; --p2-tint:#E4EEF7;
  --p3:#1F9C82; --p3-tint:#E1F3EE; --p3-text:#177561;
  --p4:#DC9E2E; --p4-tint:#FBF0DC; --p4-text:#8a6512;
  --p5:#E2604F; --p5-tint:#FCE7E3; --p5-text:#A9483B;
  --pink:#C7488E; --pink-tint:#FAE5F0; --pink-text:#A93D78;
  --cyan:#0FB8C9; --cyan-tint:#DFF6F8; --cyan-text:#087580;
  --navy:#1B3A5C; --navy-tint:#E4EBF1;
  --radius-sm:8px; --radius-md:14px;
  --display:'Space Grotesk',sans-serif;
  --body:'Inter',sans-serif;
  --mono:'IBM Plex Mono',monospace;
}
@page{ size:Letter; margin:16mm 15mm 18mm; }
@page:first{ margin:0; }
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;background:var(--paper-raised);color:var(--ink);
  font-family:var(--body);font-size:10.2pt;line-height:1.58;
  font-feature-settings:"kern","liga"}
.eyebrow{font-family:var(--mono);font-weight:600;font-size:7.6pt;
  letter-spacing:.14em;text-transform:uppercase;color:var(--ink-faint);
  margin:0 0 8px}

/* ---------- cover ---------- */
.cover{page-break-after:always;height:247mm;padding:26mm 20mm 18mm;
  display:flex;flex-direction:column;background:var(--paper)}
.cover .mark{font-family:var(--mono);font-weight:600;font-size:8.4pt;
  letter-spacing:.16em;text-transform:uppercase;color:var(--navy)}
.cover .bar{height:4px;width:96px;background:var(--navy);margin:14px 0 30px;
  border-radius:2px}
.cover h1{font-family:var(--display);font-weight:700;font-size:39pt;
  line-height:1.03;letter-spacing:-.022em;margin:0;color:var(--ink)}
.cover .sub{font-size:13pt;color:var(--ink-soft);margin:16px 0 0;
  max-width:30em;line-height:1.45}
.cover .spacer{flex:1}
.strip{display:flex;gap:22px;border-top:1px solid var(--line);
  padding-top:16px;margin-top:26px;flex-wrap:wrap}
.stat{min-width:88px}
.stat b{font-family:var(--display);font-weight:700;font-size:19pt;display:block;
  line-height:1.1;letter-spacing:-.01em}
.stat span{font-family:var(--mono);font-weight:500;font-size:7.2pt;
  letter-spacing:.11em;text-transform:uppercase;color:var(--ink-faint)}
.stat.ok b{color:var(--p3-text)} .stat.warn b{color:var(--p4-text)}
.cover .meta{font-family:var(--mono);font-size:7.8pt;color:var(--ink-faint);
  margin-top:18px;letter-spacing:.03em}

/* ---------- contents ---------- */
.toc{page-break-after:always;padding-top:4mm}
.toc h2{font-family:var(--display);font-weight:600;font-size:15pt;margin:0 0 14px;
  color:var(--ink);border:0;padding:0}
.toc ol{list-style:none;margin:0;padding:0;counter-reset:t}
.toc li{display:flex;align-items:baseline;gap:10px;
  padding:6px 0;border-bottom:1px solid var(--line-soft);font-size:10pt}
.toc li::before{content:counter(t,decimal-leading-zero);font-family:var(--mono);
  font-weight:600;font-size:8pt;color:var(--navy);min-width:20px}
.toc li:not(.sub){counter-increment:t}
.toc li.sub{padding-left:30px;border-bottom:0;padding-top:2px;padding-bottom:2px;
  font-size:9.2pt;color:var(--ink-soft)}
.toc li.sub::before{content:"";min-width:0}

/* ---------- prose ---------- */
main{padding-top:2mm}
h1,h2,h3,h4{font-family:var(--display);letter-spacing:-.012em;
  break-after:avoid-page;page-break-after:avoid;text-wrap:balance}
main > h1{font-weight:700;font-size:20pt;margin:0 0 14px}
h2{font-weight:700;font-size:14.5pt;margin:26px 0 10px;padding-top:12px;
  border-top:2px solid var(--line);color:var(--ink)}
h3{font-weight:600;font-size:11.6pt;margin:18px 0 6px;color:var(--navy)}
h4{font-weight:600;font-size:10pt;margin:14px 0 4px;color:var(--ink-soft)}
p{margin:0 0 10px;orphans:2;widows:2}
ul,ol{margin:0 0 12px;padding-left:19px}
li{margin:3px 0}
li>ul,li>ol{margin:4px 0}
strong{font-weight:600}
a{color:var(--navy);text-decoration:none;border-bottom:1px solid var(--navy-tint)}
code{font-family:var(--mono);font-size:.86em;background:var(--cyan-tint);
  color:var(--ink);padding:.5px 3.5px;border-radius:3px}
pre{background:var(--paper);border:1px solid var(--line-soft);
  border-left:3px solid var(--navy);border-radius:var(--radius-sm);
  padding:10px 12px;margin:0 0 13px;overflow:hidden;
  break-inside:avoid-page;page-break-inside:avoid}
pre code{background:none;padding:0;font-size:8.3pt;line-height:1.5;
  white-space:pre-wrap;word-break:break-word}
blockquote{margin:0 0 13px;padding:8px 0 8px 14px;
  border-left:3px solid var(--pink);color:var(--pink-text);
  font-size:10.4pt;line-height:1.5}
blockquote p{margin:0}
blockquote strong{color:var(--pink-text)}
hr{border:0;border-top:1px solid var(--line-soft);margin:20px 0}
table{border-collapse:collapse;width:100%;margin:0 0 14px;font-size:8.6pt;
  table-layout:fixed;break-inside:avoid-page}
th{font-family:var(--mono);font-weight:600;font-size:7.2pt;letter-spacing:.08em;
  text-transform:uppercase;color:var(--ink-soft);text-align:left;
  border-bottom:2px solid var(--line-pink);padding:6px 9px 6px 0;
  vertical-align:bottom}
td{border-bottom:1px solid var(--line-soft);padding:6px 9px 6px 0;
  vertical-align:top;line-height:1.45;word-break:break-word}
td code,th code{font-size:.92em;background:none;padding:0;color:var(--navy)}
img{max-width:100%}

/* the five invariants — the one legitimate use of the phase colours */
ol.invariants{list-style:none;counter-reset:inv;padding:0;margin:0 0 14px}
ol.invariants li{counter-increment:inv;position:relative;padding:9px 0 9px 40px;
  border-bottom:1px solid var(--line-soft);margin:0;break-inside:avoid}
ol.invariants li::before{content:"0" counter(inv);position:absolute;left:0;top:9px;
  font-family:var(--mono);font-weight:600;font-size:8.4pt;
  padding:1px 6px;border-radius:4px}
ol.invariants li:nth-child(1)::before{color:var(--p1);background:var(--p1-tint)}
ol.invariants li:nth-child(2)::before{color:var(--p2);background:var(--p2-tint)}
ol.invariants li:nth-child(3)::before{color:var(--p3-text);background:var(--p3-tint)}
ol.invariants li:nth-child(4)::before{color:var(--p4-text);background:var(--p4-tint)}
ol.invariants li:nth-child(5)::before{color:var(--p5-text);background:var(--p5-tint)}
"""


def slug_ok(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "s"


def mark_invariants(html):
    """The 'What holds it together' list is five ordered items and nothing else
    in these documents is. Styling it with p1-p5 is the phase device used for
    what it is for, rather than as decoration."""
    def repl(m):
        block = m.group(0)
        if block.count("<li>") == 5 and "append-only source layer" in block:
            return block.replace("<ol>", '<ol class="invariants">', 1)
        return block
    return re.sub(r"<ol>.*?</ol>", repl, html, flags=re.S)


def build_toc(html, key):
    items, seen = [], {}
    def add(m):
        lvl, inner = m.group(1), m.group(2)
        text = re.sub(r"<[^>]+>", "", inner)
        base = f"{key}-{slug_ok(text)}"
        seen[base] = seen.get(base, 0) + 1
        sid = base if seen[base] == 1 else f"{base}-{seen[base]}"
        items.append((lvl, text, sid))
        return f'<h{lvl} id="{sid}">{inner}</h{lvl}>'
    html = re.sub(r"<h([23])(?:\s[^>]*)?>(.*?)</h\1>", add, html, flags=re.S)
    li = "".join(
        f'<li class="{"sub" if lvl == "3" else ""}">{t}</li>'
        for lvl, t, _ in items if lvl in ("2", "3"))
    return html, (f'<section class="toc"><h2>Contents</h2><ol>{li}</ol></section>'
                  if li else "")


def page(doc, ver):
    body = mark_invariants(doc["html"])
    body, toc = build_toc(body, doc["key"])
    strip = f"""
      <div class="strip">
        <div class="stat {'ok' if not PARTIAL else ''}"><b>{HEADLINE}</b>
          <span>conformance</span></div>
        <div class="stat"><b>{CONF['cases'] or '—'}</b><span>cases</span></div>
        <div class="stat"><b>{CONF['skills_total']}</b><span>skills</span></div>
        <div class="stat warn"><b>{CONF['open'] if not PARTIAL else '—'}</b>
          <span>checks open</span></div>
      </div>
      <p class="meta">{COVER_NOTE} &middot; generated from {doc['source']}</p>"""
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>corp-os — {doc['label']}</title>
<style>{face_css()}
{CSS}</style></head><body>
<section class="cover">
  <div class="mark">corp-os &middot; v{ver}</div>
  <div class="bar"></div>
  <h1>{doc['label']}</h1>
  <p class="sub">{doc['blurb']}</p>
  <div class="spacer"></div>
  {strip}
</section>
{toc}
<main>{body}</main>
</body></html>"""


def main():
    ver = D["version"]
    os.makedirs(OUT, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright is not installed here. This renderer needs a "
                 "browser; scripts/build_docs.py is the pandoc/LaTeX path "
                 "for machines without one.")
    made = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        for doc in D["docs"]:
            src = os.path.join(OUT, f".page-{doc['key']}.html")
            open(src, "w", encoding="utf-8").write(page(doc, ver))
            pg.goto("file://" + src)
            pg.wait_for_timeout(400)
            out = os.path.join(OUT, f"corp-os-{doc['key']}-v{ver}.pdf")
            pg.pdf(path=out, format="Letter", print_background=True,
                   display_header_footer=True,
                   header_template="<div></div>",
                   footer_template=(
                       '<div style="width:100%;font-family:\'IBM Plex Mono\','
                       'monospace;font-size:7pt;color:#8A8399;padding:0 15mm;'
                       'display:flex;justify-content:space-between;">'
                       f'<span>corp-os &middot; {doc["label"]} &middot; v{ver}</span>'
                       '<span class="pageNumber"></span></div>'),
                   margin={"top": "16mm", "bottom": "18mm",
                           "left": "15mm", "right": "15mm"})
            made.append(out)
            print(f"  {doc['key']:13} {os.path.getsize(out)//1024:>4}KB")
        b.close()
    for f in glob.glob(os.path.join(OUT, ".page-*.html")):
        os.remove(f)
    print(f"\n{len(made)} PDFs at v{ver} → {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
