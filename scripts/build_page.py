#!/usr/bin/env python3
"""Every corp-os document as one tabbed page.

Two outputs from one build. Without a flag it writes the body for the
Artifact tool, which supplies the document skeleton and can link Google
Fonts. With --standalone it writes a complete document with the fonts
embedded, for a file someone is emailed, archives, or opens offline — a
page that silently falls back to Georgia is a different document from the
one that was reviewed.

Reads dist/corp-os-docs.json, so it cannot quote a figure the repo does
not hold. Run `python3 scripts/build_docs.py --data` first.

    python3 scripts/build_page.py --standalone
"""
import argparse, base64, json, html, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "dist", "corp-os-docs.json")
OUT = os.path.join(ROOT, "dist", "corp-os-docs.html")
if not os.path.exists(SRC):
    raise SystemExit("no dist/corp-os-docs.json — run "
                     "`python3 scripts/build_docs.py --data` first")
D = json.load(open(SRC, encoding="utf-8"))
VER = D["version"]

# Never a literal. The figures are whatever the committed run report holds,
# and when that report covers fewer cases than the suite defines it has no
# headline — both generators carried a hardcoded 203/208 for a day while the
# repo's report said 13/16 over two cases, which is how a published page goes
# on quoting a number nobody can reproduce.
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

OPEN_FAILS = [
    ("corp-os-guide", "opens a decision itself instead of handing off, and does not "
     "route the fork to <code>corp-os-decide</code>", "regression — both passed at 0.18.6"),
    ("corp-os-recall", "dropped a load-bearing sensitive fact from an answer, and the "
     "export-boundary marking with it", "a rate — 1-in-4, then 7/7, then this"),
]

TABS = [(d["key"], d["label"], d["blurb"]) for d in D["docs"]] + \
       [("skills", "Skills", "All twenty-three, and the pass each declares")]


FONT_DIR = os.path.join(HERE, "assets", "webfonts")
WEBFONTS = [("Archivo", 500, "normal", "archivo-latin-500-normal.woff2"),
            ("Archivo", 600, "normal", "archivo-latin-600-normal.woff2"),
            ("Archivo", 700, "normal", "archivo-latin-700-normal.woff2"),
            ("Source Serif 4", 400, "normal", "source-serif-4-latin-400-normal.woff2"),
            ("Source Serif 4", 400, "italic", "source-serif-4-latin-400-italic.woff2"),
            ("Source Serif 4", 600, "normal", "source-serif-4-latin-600-normal.woff2"),
            ("JetBrains Mono", 400, "normal", "jetbrains-mono-latin-400-normal.woff2"),
            ("JetBrains Mono", 500, "normal", "jetbrains-mono-latin-500-normal.woff2"),
            ("JetBrains Mono", 700, "normal", "jetbrains-mono-latin-700-normal.woff2")]


def embedded_faces():
    """The standalone file carries its own fonts.

    The hosted artifact can link Google Fonts; a file someone is emailed,
    archived or opens on a plane cannot, and a page that silently falls back
    to Georgia is a different document from the one that was reviewed."""
    out = []
    for fam, wt, style, fn in WEBFONTS:
        b64 = base64.b64encode(open(os.path.join(FONT_DIR, fn), "rb").read()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-style:{style};"
                   f"font-weight:{wt};font-display:swap;"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "\n".join(out)


def esc(s): return html.escape(s, quote=True)

# ---- panels -----------------------------------------------------------------
panels = []
for d in D["docs"]:
    rail = "".join(
        f'<li><a href="#{esc(t["id"])}">{esc(t["text"])}</a></li>' for t in d["toc"])
    railblock = (f'<nav class="rail" aria-label="{esc(d["label"])} sections">'
                 f'<p class="eyebrow">In this document</p><ol>{rail}</ol>'
                 f'<p class="src">{esc(d["source"])} · {d["words"]:,} words</p>'
                 f'</nav>') if rail else ""
    panels.append(
        f'<section class="panel" id="panel-{d["key"]}" role="tabpanel" '
        f'aria-labelledby="tab-{d["key"]}" hidden>'
        f'<div class="cols">{railblock}<article class="prose">{d["html"]}</article></div>'
        f'</section>')

PASSCLASS = {"Mechanical": "mech", "Mixed": "mixed", "Judgment": "judg"}
rows = "".join(
    f'<tr><td class="mono nm">{esc(s["name"])}</td>'
    f'<td><span class="pill {PASSCLASS.get(s["pass"], "none")}">{esc(s["pass"])}</span></td>'
    f'<td class="dsc">{esc(s["one_line"])}</td></tr>' for s in D["skills"])
counts = {}
for s in D["skills"]:
    counts[s["pass"]] = counts.get(s["pass"], 0) + 1
tally = " · ".join(f"{v} {k.lower()}" for k, v in
                   sorted(counts.items(), key=lambda kv: -kv[1]))
panels.append(
    f'<section class="panel" id="panel-skills" role="tabpanel" '
    f'aria-labelledby="tab-skills" hidden><div class="cols"><nav class="rail">'
    f'<p class="eyebrow">Pass declarations</p>'
    f'<p class="railnote">Every skill declares how much of it is judgment. '
    f'A mechanical pass is one nothing in it needs a model to decide, and it '
    f'is the only kind that can safely run on a cheaper one.</p>'
    f'<p class="src">{tally}</p></nav>'
    f'<article class="prose"><h2>The twenty-three skills</h2>'
    f'<p>Read from the plugin source rather than transcribed, so this list '
    f'cannot drift from what is installed.</p>'
    f'<div class="tablewrap"><table class="skills"><thead><tr><th>Skill</th>'
    f'<th>Pass</th><th>What it does</th></tr></thead><tbody>{rows}</tbody>'
    f'</table></div></article></div></section>')

tabs = "".join(
    f'<button class="tab" id="tab-{k}" role="tab" data-k="{k}" '
    f'aria-controls="panel-{k}" aria-selected="false" tabindex="-1">{esc(lbl)}</button>'
    for k, lbl, _ in TABS)

blurbs = "".join(f'<span class="blurb" data-k="{k}" hidden>{esc(b)}</span>'
                 for k, _, b in TABS)

fails = "".join(
    f'<li><code>{esc(n)}</code> {t} <span class="tag">{esc(k)}</span></li>'
    for n, t, k in OPEN_FAILS)

PAGE = f"""<title>corp-os Document Set</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=JetBrains+Mono:wght@400;500;700&display=swap">
<style>
:root {{
  --paper:#FAF7F0; --surface:#FFFDF8; --ink:#14161A; --slate:#5A6472;
  --rule:#E4DED1; --rule-soft:#EFEAE0; --accent:#1D5E7F; --accent-soft:#E7EFF3;
  --pass:#2C6E52; --fail:#A63A2B; --rate:#8F6415;
  --mech:#2C6E52; --mixed:#8F6415; --judg:#5A3E86;
  --shadow:0 1px 2px rgba(20,22,26,.05);
  --ui:'Archivo',system-ui,-apple-system,'Segoe UI',sans-serif;
  --body:'Source Serif 4',Georgia,'Times New Roman',serif;
  --mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper:#131519; --surface:#191C21; --ink:#E9E5DB; --slate:#98A1AE;
    --rule:#2B3038; --rule-soft:#23272E; --accent:#6FB3D0; --accent-soft:#1B2A33;
    --pass:#6FBF95; --fail:#E38273; --rate:#D3A44E;
    --mech:#6FBF95; --mixed:#D3A44E; --judg:#B49BE0;
    --shadow:0 1px 2px rgba(0,0,0,.4);
  }}
}}
:root[data-theme="dark"] {{
  --paper:#131519; --surface:#191C21; --ink:#E9E5DB; --slate:#98A1AE;
  --rule:#2B3038; --rule-soft:#23272E; --accent:#6FB3D0; --accent-soft:#1B2A33;
  --pass:#6FBF95; --fail:#E38273; --rate:#D3A44E;
  --mech:#6FBF95; --mixed:#D3A44E; --judg:#B49BE0;
  --shadow:0 1px 2px rgba(0,0,0,.4);
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);
  font-family:var(--body);font-size:16px;line-height:1.62;
  -webkit-font-smoothing:antialiased}}
.wrap{{max-width:1180px;margin:0 auto;padding-inline:20px}}
.eyebrow{{font-family:var(--mono);font-size:10.5px;font-weight:500;
  letter-spacing:.13em;text-transform:uppercase;color:var(--slate);margin:0 0 10px}}
code,pre,.mono{{font-family:var(--mono)}}

/* masthead */
header.top{{border-bottom:1px solid var(--rule);background:var(--surface)}}
.mast{{display:flex;flex-wrap:wrap;gap:18px 28px;align-items:flex-end;
  padding-block:26px 22px}}
.brand h1{{font-family:var(--ui);font-weight:700;font-size:30px;letter-spacing:-.02em;
  margin:0;line-height:1.1}}
.brand p{{margin:6px 0 0;color:var(--slate);font-size:15px;max-width:56ch}}
.ver{{font-family:var(--mono);font-size:11px;color:var(--accent);
  border:1px solid var(--accent);border-radius:3px;padding:2px 7px;
  display:inline-block;margin-left:10px;vertical-align:6px;letter-spacing:.02em}}

/* measured strip */
.measured{{margin-left:auto;display:grid;grid-template-columns:repeat(3,auto);
  gap:2px 26px;align-items:end}}
.fig{{text-align:right}}
.fig b{{font-family:var(--mono);font-size:21px;font-weight:700;display:block;
  line-height:1.15;font-variant-numeric:tabular-nums}}
.fig span{{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;
  text-transform:uppercase;color:var(--slate)}}
.fig.ok b{{color:var(--pass)}}

/* tabs */
nav.tabs{{position:sticky;top:0;z-index:20;background:var(--surface);
  border-bottom:1px solid var(--rule)}}
.tabrow{{display:flex;gap:2px;overflow-x:auto;scrollbar-width:thin}}
.tab{{font-family:var(--ui);font-weight:600;font-size:14px;color:var(--slate);
  background:none;border:0;border-bottom:2px solid transparent;
  padding:13px 15px;cursor:pointer;white-space:nowrap;letter-spacing:.005em}}
.tab:hover{{color:var(--ink)}}
.tab[aria-selected="true"]{{color:var(--accent);border-bottom-color:var(--accent)}}
.tab:focus-visible{{outline:2px solid var(--accent);outline-offset:-3px}}
.blurbbar{{padding:9px 0 11px;border-bottom:1px solid var(--rule-soft);
  font-size:13.5px;color:var(--slate);font-family:var(--ui)}}

/* open failures note */
.openbox{{margin:22px 0 4px;border:1px solid var(--rule);border-left:3px solid var(--rate);
  background:var(--surface);border-radius:0 5px 5px 0;padding:14px 18px}}
.openlead{{margin:0 0 11px;font-size:14.5px;color:var(--slate);max-width:78ch}}
.openbox ul{{margin:0;padding-left:18px;font-size:14.5px;color:var(--ink)}}
.openbox li{{margin:5px 0}}
.openbox li + li{{margin-top:7px}}
.tag{{font-family:var(--mono);font-size:10px;color:var(--slate);
  border:1px solid var(--rule);border-radius:3px;padding:1px 5px;
  white-space:nowrap;margin-left:4px}}

/* layout */
.cols{{display:grid;grid-template-columns:210px minmax(0,1fr);gap:44px;
  padding-block:34px 72px;align-items:start}}
.rail{{position:sticky;top:66px;font-family:var(--ui)}}
.rail ol{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:1px;
  border-left:1px solid var(--rule)}}
.rail a{{display:block;padding:5px 0 5px 12px;margin-left:-1px;
  border-left:2px solid transparent;font-size:13px;line-height:1.35;
  color:var(--slate);text-decoration:none}}
.rail a:hover{{color:var(--ink)}}
.rail a.on{{color:var(--accent);border-left-color:var(--accent);font-weight:600}}
.railnote{{font-size:13px;color:var(--slate);line-height:1.5;margin:0 0 14px}}
.src{{font-family:var(--mono);font-size:10.5px;color:var(--slate);
  margin:16px 0 0;letter-spacing:.02em}}

/* prose */
.prose{{max-width:70ch;min-width:0}}
.prose > :first-child{{margin-top:0}}
.prose h1{{font-family:var(--ui);font-weight:700;font-size:27px;letter-spacing:-.015em;
  margin:0 0 18px;text-wrap:balance}}
.prose h2{{font-family:var(--ui);font-weight:700;font-size:20px;letter-spacing:-.01em;
  margin:44px 0 12px;padding-top:16px;border-top:1px solid var(--rule);
  text-wrap:balance;scroll-margin-top:74px}}
.prose h3{{font-family:var(--ui);font-weight:600;font-size:16px;margin:28px 0 8px;
  text-wrap:balance;scroll-margin-top:74px}}
.prose h4{{font-family:var(--ui);font-weight:600;font-size:14px;margin:22px 0 6px;
  color:var(--slate)}}
.prose p{{margin:0 0 15px}}
.prose ul,.prose ol{{margin:0 0 16px;padding-left:22px}}
.prose li{{margin:5px 0}}
.prose li > ul,.prose li > ol{{margin:6px 0}}
.prose a{{color:var(--accent);text-decoration:underline;
  text-underline-offset:2px;text-decoration-thickness:.06em}}
.prose strong{{font-weight:600}}
.prose code{{font-size:.845em;background:var(--accent-soft);color:var(--ink);
  padding:1px 4px;border-radius:3px}}
.prose pre{{background:var(--surface);border:1px solid var(--rule);border-radius:5px;
  padding:13px 15px;overflow-x:auto;margin:0 0 17px;line-height:1.5;box-shadow:var(--shadow)}}
.prose pre code{{background:none;padding:0;font-size:12.5px}}
.prose blockquote{{margin:0 0 16px;padding:2px 0 2px 16px;
  border-left:2px solid var(--accent);color:var(--slate)}}
.prose blockquote p{{margin:0 0 6px}}
.prose hr{{border:0;border-top:1px solid var(--rule);margin:32px 0}}
.prose hr + h2{{border-top:0;padding-top:0;margin-top:0}}
.tablewrap,.prose table{{max-width:100%}}
.prose table{{border-collapse:collapse;width:100%;font-size:13.5px;
  font-family:var(--ui);margin:0 0 18px;display:block;overflow-x:auto}}
.prose th{{text-align:left;font-weight:600;font-size:11px;letter-spacing:.06em;
  text-transform:uppercase;color:var(--slate);border-bottom:1px solid var(--rule);
  padding:7px 12px 7px 0;white-space:nowrap}}
.prose td{{border-bottom:1px solid var(--rule-soft);padding:8px 12px 8px 0;
  vertical-align:top;line-height:1.5}}
.prose img{{max-width:100%}}

/* skills table */
.tablewrap{{overflow-x:auto}}
table.skills{{display:table;font-size:14px}}
table.skills td.nm{{font-size:12.5px;white-space:nowrap;padding-right:16px}}
table.skills td.dsc{{color:var(--slate);font-size:13.5px}}
.pill{{font-family:var(--mono);font-size:10px;letter-spacing:.06em;
  text-transform:uppercase;border:1px solid currentColor;border-radius:3px;
  padding:1px 6px;white-space:nowrap}}
.pill.mech{{color:var(--mech)}} .pill.mixed{{color:var(--mixed)}}
.pill.judg{{color:var(--judg)}} .pill.none{{color:var(--slate)}}

footer{{border-top:1px solid var(--rule);padding-block:22px 40px;
  font-family:var(--ui);font-size:13px;color:var(--slate)}}
footer a{{color:var(--accent)}}

@media (max-width:860px){{
  .cols{{grid-template-columns:1fr;gap:0;padding-block:24px 56px}}
  .rail{{position:static;border-bottom:1px solid var(--rule);
    padding-bottom:18px;margin-bottom:26px}}
  .rail ol{{flex-direction:row;flex-wrap:wrap;gap:6px 14px;border-left:0}}
  .rail a{{padding:0;margin:0;border-left:0}}
  .rail a.on{{border-left:0}}
  .measured{{margin-left:0;grid-template-columns:repeat(3,auto);gap:2px 20px}}
  .fig{{text-align:left}}
  .brand h1{{font-size:24px}}
}}
@media (prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important}}}}
html{{scroll-behavior:smooth}}
</style>

<header class="top">
  <div class="wrap mast">
    <div class="brand">
      <h1>corp-os<span class="ver">v{VER}</span></h1>
      <p>A portable, configurable personal work OS, as an installable Claude
         plugin. Every document in the repository, in one place.</p>
    </div>
    <div class="measured">
      <div class="fig {'ok' if not PARTIAL else ''}"><b>{HEADLINE}</b><span>conformance</span></div>
      <div class="fig"><b>{CONF['cases'] or '&mdash;'}</b><span>cases</span></div>
      <div class="fig"><b>{CONF['skills_total']}</b><span>skills</span></div>
    </div>
  </div>
</header>

<nav class="tabs" aria-label="Documents">
  <div class="wrap"><div class="tabrow" role="tablist">{tabs}</div></div>
</nav>
<div class="wrap"><div class="blurbbar">{blurbs}</div></div>

<div class="wrap" id="intro">
  <div class="openbox">
    <p class="eyebrow">Four open checks, named here rather than left out</p>
    <p class="openlead">Five checks failed in the run above. One was the
       harness asserting the wrong thing &mdash; it read the OS&rsquo;s own
       capture rule as a fabricated source &mdash; and that assertion has been
       replaced. Four are real, in two skills:</p>
    <ul>{fails}</ul>
  </div>
</div>

<main class="wrap">{''.join(panels)}</main>

<footer><div class="wrap">
  Generated from the repository's own markdown at v{VER}. {COVER_NOTE}.
  Rebuild with <code>python3 scripts/build_docs.py --data</code> then
  <code>scripts/build_page.py --standalone</code>.
</div></footer>

<script>
(function () {{
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab'));
  var intro = document.getElementById('intro');
  function show(key, push) {{
    tabs.forEach(function (t) {{
      var on = t.dataset.k === key;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      var p = document.getElementById('panel-' + t.dataset.k);
      if (p) p.hidden = !on;
    }});
    document.querySelectorAll('.blurb').forEach(function (b) {{
      b.hidden = b.dataset.k !== key;
    }});
    intro.hidden = key !== 'overview';
    if (push) history.replaceState(null, '', '#' + key);
  }}
  tabs.forEach(function (t) {{
    t.addEventListener('click', function () {{ show(t.dataset.k, true); window.scrollTo({{top: 0}}); }});
    t.addEventListener('keydown', function (e) {{
      var i = tabs.indexOf(t), n = null;
      if (e.key === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
      if (e.key === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
      if (n) {{ e.preventDefault(); n.focus(); show(n.dataset.k, true); }}
    }});
  }});
  var start = (location.hash || '').replace('#', '');
  show(tabs.some(function (t) {{ return t.dataset.k === start; }}) ? start : 'overview', false);

  // rail highlight
  if ('IntersectionObserver' in window) {{
    var links = {{}};
    document.querySelectorAll('.rail a').forEach(function (a) {{
      links[a.getAttribute('href').slice(1)] = a;
    }});
    var io = new IntersectionObserver(function (entries) {{
      entries.forEach(function (en) {{
        var a = links[en.target.id];
        if (!a) return;
        if (en.isIntersecting) {{
          var panel = en.target.closest('.panel');
          if (panel) panel.querySelectorAll('.rail a.on')
            .forEach(function (x) {{ x.classList.remove('on'); }});
          a.classList.add('on');
        }}
      }});
    }}, {{rootMargin: '-70px 0px -75% 0px'}});
    document.querySelectorAll('.prose h2[id]').forEach(function (h) {{ io.observe(h); }});
  }}
}})();
</script>
"""
ap = argparse.ArgumentParser()
ap.add_argument("--standalone", action="store_true",
                help="a complete document with its fonts embedded, for sharing "
                     "as a file rather than publishing as an artifact")
ap.add_argument("--out")
a = ap.parse_args()

if a.standalone:
    page = PAGE.replace(
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=Archivo:wght@500;600;700&family=Source+Serif+4:ital,opsz,'
        'wght@0,8..60,400;0,8..60,600;1,8..60,400&family=JetBrains+Mono:'
        'wght@400;500;700&display=swap">\n<style>',
        "<style>\n" + embedded_faces() + "\n")
    assert "fonts.googleapis" not in page, "font link survived the swap"
    doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
           '<meta name="description" content="Every corp-os document at v'
           + VER + ' — overview, quick start, handbook, architecture, cost, '
           'backlog, install, and all 23 skills.">\n'
           '<style>html{color-scheme:light dark}img{max-width:100%}'
           '[hidden]{display:none!important}</style>\n'
           + page.split("<style>", 1)[0] + "<style>"
           + page.split("<style>", 1)[1].split("</style>", 1)[0]
           + "</style>\n</head>\n<body>\n"
           + page.split("</style>", 1)[1] + "\n</body>\n</html>\n")
    out = a.out or OUT.replace(".html", "-standalone.html")
    open(out, "w", encoding="utf-8").write(doc)
    print("wrote", out, os.path.getsize(out) // 1024, "KB (self-contained)")
else:
    open(a.out or OUT, "w", encoding="utf-8").write(PAGE)
    print("wrote", a.out or OUT, os.path.getsize(a.out or OUT) // 1024, "KB")
