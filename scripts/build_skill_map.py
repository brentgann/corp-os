#!/usr/bin/env python3
"""Generate docs/skill-map.html from the plugin itself.

A skill map is a page that states how many skills there are, what each one
does, and what each one refuses. Committed as a static file, it is the fifth
instance of the defect this repo keeps finding: a fact maintained in a second
place, which nothing catches when it goes stale. The first four were
corp-os-setup saying "both shipped scripts" three releases after there were
four, scaffold.py hard-coding a version that was stale within one release,
corpos_version living in six files with six different values, and a dashboards
registry that counted 1 for five releases.

So the page is generated. Every fact on it -- the descriptions, the counts, the
command roster, what each script makes deterministic, the eval numbers -- is
read from the source of truth at build time. Add a skill and the page grows.

What CANNOT be derived is which phase a skill belongs to. That is judgment, so
it is declared once, below, and the generator refuses to run if the declaration
does not cover every skill on disk exactly once. Add skill 22 and this fails
until someone decides where it goes, which is the correct amount of friction:
placing it takes ten seconds and is the only part a person is needed for.

    python3 scripts/build_skill_map.py            # write docs/skill-map.html
    python3 scripts/build_skill_map.py --check    # fail if it is out of date
    python3 scripts/build_skill_map.py --fragment /tmp/x.html   # for publishing

`--check` is what validate.py runs, mirroring build_index.py's own drift check.
"""

import argparse
import ast
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "corp-os")
OUT = os.path.join(ROOT, "docs", "skill-map.html")

# --------------------------------------------------------------- the judgment
# Ordered. Each phase carries what it is for and what breaks without it -- the
# two things a list of skill names cannot tell you, and the reason this page is
# a map rather than a table of contents.
PHASES = [
    {
        "key": "capture",
        "rail": "Material lands in the append-only layer. Existing there means <em>said</em>, not true.", "name": "Capture", "tok": "p1",
        "for": "Getting things said into a layer that is never edited, never "
               "summarized in place, never deleted outside a declared "
               "obligation. One sanctioned exception: flipping "
               "<code>processed</code> to true.",
        "skip": "Nothing downstream can cite anything. A claim with no "
                "retrievable original is the one thing this model treats as "
                "corrosive, because nothing later can detect it.",
        "skills": ["corp-os-intake", "corp-os-pull", "corp-os-connect"],
    },
    {
        "key": "curate",
        "rail": "Raw becomes citable &mdash; a kind, a confidence, a verbatim quote, a decay window.", "name": "Curate", "tok": "p2",
        "for": "Turning a pile into knowledge, behind a review gate written to "
               "disk before it is presented. The declines are the valuable "
               "part &mdash; the only record of what someone chose not to know.",
        "skip": "You have a folder of transcripts. Search finds text; it does "
                "not find what you concluded, who said it, or whether it is "
                "still true.",
        "skills": ["corp-os-claims", "corp-os-jobs", "corp-os-decide",
                   "corp-os-glossary", "corp-os-company"],
    },
    {
        "key": "consult",
        "rail": "The only phase that pays you back. Questions answered with provenance attached.", "name": "Consult", "tok": "p3",
        "for": "Getting the knowledge back out with its provenance still "
               "attached. Three shapes, because a question, a standing digest, "
               "and a page you return to are genuinely different needs.",
        "skip": "You have built a write-only diary. This is the phase that "
                "repays the first two, and the one people quietly stop "
                "reaching for first.",
        "skills": ["corp-os-recall", "corp-os-brief", "corp-os-dashboard"],
    },
    {
        "key": "correct",
        "rail": "Confidence outlives its evidence unless something goes looking for it.", "name": "Correct", "tok": "p4",
        "for": "The fifth invariant made routine: something has to remove "
               "things. Claims past their decay window, claims never verified, "
               "contradictions, assumptions still worn as facts.",
        "skip": "The OS keeps answering with confidence it has not earned "
                "since March. That is worse than having no OS, because you now "
                "trust the answer.",
        "skills": ["corp-os-reality-check"],
    },
    {
        "key": "release",
        "rail": "The boundary. Where an OS stops helping and starts costing you something.", "name": "Release", "tok": "p5",
        "for": "One operator, but exports land in multi-person systems. "
               "Sensitivity is two axes: <code>sensitivity</code> says what "
               "must not leave, <code>bearing</code> says whether the OS can "
               "reason correctly without it.",
        "skip": "The wrong sentence goes out in a paste. Nothing is silently "
                "deleted &mdash; the cleaned copy and a private log of exactly "
                "what came out are written together, or neither is.",
        "skills": ["corp-os-redact"],
    },
]

# Not a sequence, so deliberately not numbered and deliberately not on the rail.
# corp-os-migrate fills raw/, which is Capture's job, and it is still not in
# the loop: it happens once, at an OS's founding, and it is setup's sibling
# rather than intake's. What decides it is repetition, not what the skill
# writes to.
BENCH = ["corp-os-guide", "corp-os-setup", "corp-os-migrate",
         "corp-os-configure", "corp-os-upgrade", "corp-os-rebuild",
         "corp-os-improve", "corp-os-audit", "corp-os-pattern",
         "corp-os-contribute"]

# How often a person actually reaches for it. Judgment, and the honest kind:
# nothing measures this yet -- see the open question about which commands get
# used. Stated so it can be argued with rather than left implicit.
RHYTHM = {
    "corp-os-intake": "As it happens",
    "corp-os-pull": "Daily or weekly",
    "corp-os-connect": "Once per source",
    "corp-os-claims": "Weekly &mdash; work the queue",
    "corp-os-jobs": "When the work changes",
    "corp-os-decide": "When a fork opens",
    "corp-os-glossary": "As terms surface",
    "corp-os-company": "Before a meeting",
    "corp-os-recall": "Constantly",
    "corp-os-brief": "Daily or weekly",
    "corp-os-dashboard": "Build once, refresh on cadence",
    "corp-os-reality-check": "Monthly",
    "corp-os-redact": "Every time something leaves",
    "corp-os-guide": "Whenever you are unsure",
    "corp-os-setup": "Once",
    "corp-os-migrate": "Once, at the start",
    "corp-os-configure": "When the shape stops fitting",
    "corp-os-upgrade": "After every plugin update",
    "corp-os-rebuild": "Rarely",
    "corp-os-improve": "After enough real use",
    "corp-os-audit": "On someone else's system",
    "corp-os-pattern": "Once per output worth repeating",
    "corp-os-contribute": "Maintainer path",
}


def die(msg):
    sys.exit(f"build_skill_map.py: {msg}")


# ------------------------------------------------------------------- reading

def frontmatter_description(path):
    t = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        return None
    d = re.search(r"^description:\s*(.+)$", m.group(1), re.M)
    return d.group(1).strip() if d else None


def split_description(desc):
    """A description carries three things. Pull them apart rather than
    restating them, because a restatement is a copy and copies go stale.

        <what it does>. Use when someone says "...". Not for X (use Y).
    """
    does, triggers, nots = desc, "", ""
    m = re.search(r"\bUse (?:when|this when)\b", desc)
    if m:
        does, rest = desc[:m.start()].strip(), desc[m.start():]
    else:
        rest = ""
    n = re.search(r"(?:(?<=\.\s)|(?<=\.\s\s)|^)Not(?:\s+for|\s+a|\s+the|\s)", rest)
    if n:
        triggers, nots = rest[:n.start()].strip(), rest[n.start():].strip()
    else:
        triggers = rest.strip()
    return does.rstrip(". ").strip(), triggers, nots


def quoted_phrases(text, limit=3):
    out = re.findall(r'"([^"]{3,42})"', text)
    return out[:limit]


def shipped_tuple():
    """The list of scripts an OS carries, from the one place it lives."""
    tree = ast.parse(open(os.path.join(PLUGIN, "scripts", "scaffold.py"),
                          encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "SHIPPED" for t in node.targets):
            return tuple(ast.literal_eval(node.value))
    die("could not read SHIPPED from scaffold.py")


def invariants():
    """Parsed from the README rather than retyped. There are five, and the
    page says five because it counted them."""
    t = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    m = re.search(r"not configurable.*?\n\n(.*?)\n\n", t, re.S)
    if not m:
        die("could not find the invariants list in README.md — the page "
            "states how many there are, so it has to count them")
    found = re.findall(r"^\d+\.\s+\*\*(.+?)\*\*", m.group(1), re.M)
    if not found:
        die("the invariants list in README.md no longer parses")
    return found


def eval_numbers():
    """Point-in-time numbers, read from the committed run reports. A page that
    hard-codes '100%' keeps saying it after the number moves."""
    out = {}
    p = os.path.join(ROOT, "evals", "runs", "conformance-v11.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        out["conf"] = (d.get("passed"), d.get("total"), len(d.get("runs", [])))
        out["conf_skills"] = len({r.get("skill") for r in d.get("runs", [])})
    p = os.path.join(ROOT, "evals", "runs", "routing-v4.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        out["routing"] = (d.get("overall"), d.get("repeats"))
    p = os.path.join(ROOT, "evals", "routing-set.json")
    if os.path.exists(p):
        out["queries"] = len(json.load(open(p, encoding="utf-8"))["queries"])
    return out


def install_ids():
    """The three strings an install command needs, read rather than typed.

    A page that hard-codes `/plugin install corp-os@brentgann` is a fourth
    copy of two names that already exist in two manifests, and the whole
    argument of this generator is that a fourth copy goes stale.
    """
    manifest = json.load(open(os.path.join(
        PLUGIN, ".claude-plugin", "plugin.json"), encoding="utf-8"))
    mkt = json.load(open(os.path.join(
        ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
    repo = (manifest.get("repository") or "").rstrip("/")
    slug = repo.split("github.com/")[-1]
    if slug.endswith(".git"):
        slug = slug[:-4]
    if not slug or "/" not in slug:
        die("plugin.json has no usable `repository` — the install command on "
            "the page is built from it rather than typed, so a missing one "
            "would ship an install line that does not work")
    return {"plugin": manifest["name"], "market": mkt["name"], "slug": slug}


def gather():
    d = {}
    d["version"] = json.load(open(os.path.join(
        PLUGIN, ".claude-plugin", "plugin.json"), encoding="utf-8"))["version"]

    skills = {}
    for path in sorted(glob.glob(os.path.join(PLUGIN, "skills", "*", "SKILL.md"))):
        name = os.path.basename(os.path.dirname(path))
        desc = frontmatter_description(path)
        if not desc:
            die(f"{name} has no description — it would render as a blank card")
        does, triggers, nots = split_description(desc)
        skills[name] = {"does": does, "triggers": quoted_phrases(triggers),
                        "not": nots}
    d["skills"] = skills

    # -- the completeness check that makes this file maintainable.
    placed = [s for ph in PHASES for s in ph["skills"]] + BENCH
    dupes = {s for s in placed if placed.count(s) > 1}
    if dupes:
        die(f"placed more than once: {sorted(dupes)}")
    missing = sorted(set(skills) - set(placed))
    if missing:
        die(f"{len(missing)} skill(s) on disk are not placed in any phase or on "
            f"the workbench: {missing}. Deciding where a skill belongs is the "
            "one thing this generator cannot do for you — add it to PHASES or "
            "BENCH and to RHYTHM.")
    ghosts = sorted(set(placed) - set(skills))
    if ghosts:
        die(f"placed but not on disk: {ghosts}")
    norhythm = sorted(set(skills) - set(RHYTHM))
    if norhythm:
        die(f"no rhythm declared for: {norhythm}")

    cmds = []
    for path in sorted(glob.glob(os.path.join(PLUGIN, "commands", "*.md"))):
        slug = os.path.basename(path)[:-3]
        t = open(path, encoding="utf-8").read()
        m = re.search(r"^description:\s*(.+)$", t, re.M)
        named = [n for n in re.findall(r"corp-os-[a-z-]+", t) if n in skills]
        if not named:
            die(f"command {slug} names no real skill")
        cmds.append({"slug": slug, "desc": m.group(1).strip() if m else "",
                     "skill": named[0]})
    d["commands"] = cmds
    d["cmd_for"] = {c["skill"]: c["slug"] for c in cmds}

    ship = shipped_tuple()
    scripts = []
    for path in sorted(glob.glob(os.path.join(PLUGIN, "scripts", "*.py"))):
        base = os.path.basename(path)
        doc = ast.get_docstring(ast.parse(open(path, encoding="utf-8").read())) or ""
        scripts.append({"name": base, "doc": doc.split("\n")[0],
                        "where": "In your OS" if base in ship else "In the plugin"})
    d["scripts"] = scripts
    d["refs"] = sorted(os.path.basename(p) for p in
                       glob.glob(os.path.join(PLUGIN, "reference", "*.md")))
    d["fixtures"] = sorted(os.path.basename(p) for p in
                           glob.glob(os.path.join(PLUGIN, "examples", "fixture-*")))
    d["invariants"] = invariants()
    d["evals"] = eval_numbers()
    d["install"] = install_ids()
    return d


# ------------------------------------------------------------------ rendering
def E(s):
    """Escape for element text. `quote=True` would turn an apostrophe in a
    quoted trigger phrase into &#x27;, and every one of these is text content
    rather than an attribute value."""
    return html.escape(str(s), quote=False)


def card(name, s, cmd_for, tone=""):
    chips = []
    if name in cmd_for:
        chips.append(f'<span class="chip cmd">/{E(cmd_for[name])}</span>')
    chips.append(f'<span class="chip">{RHYTHM[name]}</span>')
    trig = ""
    if s["triggers"]:
        items = "".join(f"<span>&ldquo;{E(t)}&rdquo;</span>" for t in s["triggers"])
        trig = f'<div class="trig">{items}</div>'
    nots = f'<p class="not">{E(s["not"])}</p>' if s["not"] else ""
    return f"""      <div class="card{tone}">
        <div class="name">{E(name)}</div>
        <p class="does">{E(s['does'])}.</p>
{trig}
{nots}
        <div class="meta">{''.join(chips)}</div>
      </div>"""


def render(d, fragment=False):
    S, C = d["skills"], d["cmd_for"]
    v = E(d["version"])
    ev = d["evals"]

    rail = "".join(f"""
    <div class="step" style="--sc:var(--{p['tok']}); --st:var(--{p['tok']}-text)">
      <div class="n">PHASE {i}</div><h4>{E(p['name'])}</h4>
      <p>{p['rail']}</p>
    </div>""" for i, p in enumerate(PHASES, 1))

    phases = ""
    for i, p in enumerate(PHASES, 1):
        cards = "\n".join(card(n, S[n], C) for n in p["skills"])
        n = len(p["skills"])
        phases += f"""
<section class="phase" id="{p['key']}" style="--sc:var(--{p['tok']}); --st:var(--{p['tok']}-text); --sb:var(--{p['tok']}-tint)">
  <div class="phase-head">
    <span class="n">PHASE {i}</span><h2>{E(p['name'])}</h2>
    <span class="count">{n} skill{'s' if n != 1 else ''}</span>
  </div>
  <div class="phase-why">
    <div><b>What it is for</b>{p['for']}</div>
    <div><b>Skip it and</b>{p['skip']}</div>
  </div>
  <div class="cards">
{cards}
  </div>
</section>
"""

    bench = "\n".join(card(n, S[n], C) for n in BENCH)
    bench_cmds = sum(1 for n in BENCH if n in C)
    bench_cmd_line = {
        0: "None of them has a slash command",
        1: "Only one has a slash command",
    }.get(bench_cmds, f"Only {bench_cmds} have slash commands")

    cmd_rows = "".join(
        f'<tr><td class="mono">/{E(c["slug"])}</td><td class="dim">{E(c["desc"])}</td>'
        f'<td class="mono">{E(c["skill"].replace("corp-os-", ""))}</td></tr>'
        for c in d["commands"])
    scr_rows = "".join(
        f'<tr><td class="mono">{E(s["name"])}</td><td class="dim">{E(s["doc"])}</td>'
        f'<td class="dim">{E(s["where"])}</td></tr>' for s in d["scripts"])

    ins = d["install"]
    ins_rows = "".join(
        f'<tr><td class="mono">{E(cmd)}</td><td class="dim">{why}</td></tr>'
        for cmd, why in (
            (f"/plugin marketplace add {ins['slug']}",
             "Point your client at this repository&rsquo;s marketplace manifest"),
            (f"/plugin install {ins['plugin']}@{ins['market']}",
             "Install the plugin. In the desktop app, use the plugin browser "
             "rather than the slash command"),
            (f"/plugin marketplace update {ins['market']}",
             "Refetch. This is the update that replaces <em>the skills</em>"),
            ("ask for corp-os-upgrade",
             "The other update: refresh the script copies inside your OS, "
             "stamp the version, and name the migrations it refuses to "
             "perform for you"),
        ))

    inv = " &middot; ".join(E(x) for x in d["invariants"])

    routing = ""
    if "routing" in ev and ev["routing"][0] is not None:
        pct = f"{round(ev['routing'][0] * 100)}%"
        routing = (f'<li><b>Routing: <span class="num">{pct}</span></b> over '
                   f'{ev.get("queries", "?")} queries &times; {ev["routing"][1]} '
                   f'repeats at {len(S)} skills, including near-miss pairs '
                   'written to pull each new skill toward its nearest '
                   'neighbours. The descriptions can be told apart from each '
                   'other. Whether a skill fires in a live session competing '
                   'with everything else installed is a different question, '
                   'and unmeasured.</li>')
    conf = ""
    if "conf" in ev:
        pa, to, ca = ev["conf"]
        conf = (f'<li><b>Conformance: <span class="num">{pa}/{to}</span></b> '
                f'across {ca} cases, {ev["conf_skills"]} skills and '
                f'{len(d["fixtures"])} fixtures &mdash; at one repeat, so a '
                f'baseline rather than rates. '
                f'{len(S) - ev["conf_skills"]} skills still have no case.</li>')

    body = f"""<div class="wrap">

<header>
  <div class="eyebrow">corp-os v{v} &nbsp;&middot;&nbsp; generated by <span class="mono">scripts/build_skill_map.py</span></div>
  <h1>Corp-OS Skill Map</h1>
  <p class="thesis">{len(S)} skills, and only {sum(len(p['skills']) for p in PHASES)} of them are things you do <em>with</em> a knowledge base. The other {len(BENCH)} are things you do <strong>to</strong> it &mdash; and knowing which is which is most of knowing when to reach for what.</p>
  <div class="facts">
    <div class="fact"><b>{len(S)}</b><span>Skills</span></div>
    <div class="fact"><b>{len(d['commands'])}</b><span>Slash commands</span></div>
    <div class="fact"><b>{len(d['scripts'])}</b><span>Shipped scripts</span></div>
    <div class="fact"><b>{len(d['refs'])}</b><span>Reference specs</span></div>
    <div class="fact"><b>{len(d['invariants'])}</b><span>Invariants</span></div>
  </div>
</header>

<section class="rail-block">
  <div class="eyebrow" style="margin-bottom:12px">The loop &mdash; what you do with the OS</div>
  <div class="rail">{rail}
  </div>
  <div class="loopnote">
    <svg width="46" height="18" viewBox="0 0 46 18" aria-hidden="true">
      <path d="M44 2 L44 9 Q44 13 40 13 L7 13" fill="none" stroke="currentColor" stroke-width="1.5"/>
      <path d="M11 9 L6.5 13 L11 17" fill="none" stroke="currentColor" stroke-width="1.5"/>
    </svg>
    <span>Release returns to Capture &mdash; what you sent out is itself material</span>
  </div>
</section>
{phases}
<section class="bench">
  <div class="bench-head">
    <span class="eyebrow">Off the loop</span>
    <h2>The workbench</h2>
    <span class="count">{len(BENCH)} skills</span>
  </div>
  <p>These act on the OS itself rather than on what it holds, so they are not a sequence and there is no order to them. {bench_cmd_line}, and that is deliberate: the commands cover the moments that recur, and these are rare and deliberate enough that you name them.</p>
  <div class="cards">
{bench}
  </div>
</section>

<section class="layer">
  <div class="eyebrow">Supporting layer</div>
  <h2>{len(d['commands'])} commands, named for the moment</h2>
  <p>Not one per skill. Someone reaching for the export boundary is thinking <em>share this</em>, not <em>redact</em>. Whether the one-line descriptions are actually distinguishable from each other was measured rather than assumed: picker cases give a person plain English and the roster and nothing else.</p>
  <div class="scroll">
    <table>
      <thead><tr><th>Command</th><th>The moment</th><th>Reaches</th></tr></thead>
      <tbody>{cmd_rows}</tbody>
    </table>
  </div>
</section>

<section class="layer">
  <div class="eyebrow">Supporting layer</div>
  <h2>{len(d['scripts'])} scripts, because instruction stopped working</h2>
  <p>Each of these was prose first. Each held at a stubborn rate &mdash; 33%, 67% &mdash; through two or more rewrites, and only moved when it became code. The rule they encode: <strong>a step that has to happen every time, that nothing else will catch if it is skipped, belongs in code rather than in an instruction.</strong> Your OS carries its own copies of the ones marked below, which is exactly why <span class="mono">upgrade_os.py</span> had to exist.</p>
  <div class="scroll">
    <table>
      <thead><tr><th>Script</th><th>What it makes deterministic</th><th>Lives</th></tr></thead>
      <tbody>{scr_rows}</tbody>
    </table>
  </div>
</section>

<section class="layer">
  <div class="eyebrow">Getting it</div>
  <h2>Two things are called &ldquo;update&rdquo; and they are not the same</h2>
  <p>Updating the plugin replaces the skills. Updating your OS brings the folder those skills operate on in line with them &mdash; its copies of the shipped scripts above, the version it records, and any shape change the release implies. <strong>Doing the first does nothing to the second</strong>, because an OS carries its own copies so that it still works when the plugin is not loaded. That is the whole reason <span class="mono">corp-os-upgrade</span> exists.</p>
  <div class="scroll">
    <table>
      <thead><tr><th>Do this</th><th>To</th></tr></thead>
      <tbody>{ins_rows}</tbody>
    </table>
  </div>
  <p>One thing that catches maintainers as often as users: a client caches an installed plugin <strong>by version string</strong>, so commits pushed without a bump in <span class="mono">plugin.json</span> reach nobody &mdash; no error, no warning, nothing to inspect from the inside. The full procedure is in <span class="mono">docs/INSTALL.md</span>.</p>
</section>

<section class="notes">
  <div class="eyebrow">Maintainer notes &mdash; skip if you are here to use it</div>
  <h2>What is measured, and what is not</h2>
  <p>The honest numbers behind the map above, read at build time from the committed run reports rather than typed in, and kept here rather than woven through, because an operator does not need them and a maintainer should not have to dig.</p>
  <ul>
    {routing}
    {conf}
    <li><b>Every conformance figure before v0.11.0 is void.</b> No shipped script had ever executed in a run: the harness ran with <span class="mono">acceptEdits</span>, which approves file edits and nothing else, so every <span class="mono">python3 scripts/&hellip;</span> was answered with <em>this command requires approval</em>. The file-level results were real; what produced them was never measured, because a model blocked from running a script writes the row by hand. It cost six runs and three instruction passes chasing a setup failure that was the instrument the whole time.</li>
    <li><b>One hand-off lands 2 times in 5.</b> When a dashboard needs a layer the OS has not declared, the skill should hand off to <span class="mono">corp-os-configure</span> rather than improvise one inline. Five runs, three behaviours. A wording pass making the requirement explicit measured 0/2 and was reverted &mdash; prose that does not move the number is churn. It is on the record at 2/5 rather than reworded a fourth time.</li>
    <li><b>The interrogation is untested by construction.</b> It needs a person who did not design it. The likeliest way setup fails is not a wrong answer but someone abandoning it halfway, and no check catches that &mdash; which is why the scaffolder runs first, so they still have a working OS when they do.</li>
    <li><b>This page is generated, and that is the point.</b> A static skill map is a fact maintained in a second place, which is the defect this repo has now found four times. Everything above is read from the plugin at build time; only the phase a skill belongs to is declared by hand, and <span class="mono">validate.py</span> fails if a skill on disk has not been placed.</li>
  </ul>
</section>

<footer>
  <span>corp-os v{v}</span>
  <span>{len(S)} skills &middot; {len(d['commands'])} commands &middot; {len(d['scripts'])} scripts &middot; {len(d['refs'])} reference specs &middot; {len(d['fixtures'])} fixtures</span>
  <span>{len(d['invariants'])} invariants: {inv}</span>
</footer>

</div>"""

    head = f"<title>Corp-OS Skill Map</title>\n{STYLE}"
    # Two consumers, one template. An Artifact supplies its own skeleton and
    # wants the content bare; a file in docs/ is opened straight off disk and
    # needs to be a whole document.
    if fragment:
        return f"{head}\n{body}\n"
    return ('<!doctype html>\n<html lang="en">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n')


STYLE = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap">
<style>
:root{
  --ink:#17132B; --ink-soft:#4A4459; --ink-faint:#8A8399;
  --paper:#FBF8F4; --paper-raised:#FFFFFF;
  --line:#9ED3DE; --line-soft:#C9E8ED; --line-pink:#EAB8D2;
  --p1:#4B3F95; --p1-tint:#EAE8F8;
  --p2:#2D6CAD; --p2-tint:#E4EEF7;
  --p3:#1F9C82; --p3-tint:#E1F3EE;
  --p4:#DC9E2E; --p4-tint:#FBF0DC;
  --p5:#E2604F; --p5-tint:#FCE7E3;
  --pink:#C7488E; --pink-tint:#FAE5F0;
  --cyan:#0FB8C9; --cyan-tint:#DFF6F8;
  --navy:#1B3A5C; --navy-tint:#E4EBF1;
  --navy-text:#1B3A5C;
  --p1-text:#4B3F95; --p2-text:#2D6CAD; --p3-text:#177561;
  --p4-text:#8a6512; --p5-text:#A9483B;
  --pink-text:#A93D78; --cyan-text:#087580;
  --radius-sm:8px; --radius-md:14px; --radius-lg:22px; --radius-pill:999px;
  --font-display:'Space Grotesk','Segoe UI',sans-serif;
  --font-body:'Inter','Segoe UI',system-ui,sans-serif;
  --font-mono:'IBM Plex Mono','SF Mono',ui-monospace,monospace;
  --shadow-sm:0 1px 2px rgba(23,19,43,0.06);
  --shadow-md:0 8px 24px rgba(23,19,43,0.08);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ink:#F2EEFA; --ink-soft:#C6BFDA; --ink-faint:#8A82A3;
    --paper:#130F24; --paper-raised:#1D1836;
    --line:#204656; --line-soft:#173039; --line-pink:#4A2A45;
    --p1-tint:#241E42; --p2-tint:#17293B; --p3-tint:#123028;
    --p4-tint:#3A2A0E; --p5-tint:#3B1D16;
    --pink-tint:#341728; --cyan-tint:#0E2C30;
    --navy-tint:rgba(111,182,222,0.16); --navy-text:#6FB6DE;
    --p1-text:#938BBF; --p2-text:#6C98C5; --p3-text:#47AD98;
    --p4-text:#DFA742; --p5-text:#E46F60;
    --pink-text:#D370A6; --cyan-text:#27BFCE;
    --shadow-sm:0 1px 2px rgba(0,0,0,0.4);
    --shadow-md:0 8px 24px rgba(0,0,0,0.45);
  }
}
:root[data-theme="dark"]{
  --ink:#F2EEFA; --ink-soft:#C6BFDA; --ink-faint:#8A82A3;
  --paper:#130F24; --paper-raised:#1D1836;
  --line:#204656; --line-soft:#173039; --line-pink:#4A2A45;
  --p1-tint:#241E42; --p2-tint:#17293B; --p3-tint:#123028;
  --p4-tint:#3A2A0E; --p5-tint:#3B1D16;
  --pink-tint:#341728; --cyan-tint:#0E2C30;
  --navy-tint:rgba(111,182,222,0.16); --navy-text:#6FB6DE;
  --p1-text:#938BBF; --p2-text:#6C98C5; --p3-text:#47AD98;
  --p4-text:#DFA742; --p5-text:#E46F60;
  --pink-text:#D370A6; --cyan-text:#27BFCE;
  --shadow-sm:0 1px 2px rgba(0,0,0,0.4);
  --shadow-md:0 8px 24px rgba(0,0,0,0.45);
}
*{box-sizing:border-box}
body{margin:0; background:var(--paper); color:var(--ink);
  font-family:var(--font-body); font-size:15px; line-height:1.6;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1120px; margin:0 auto; padding:44px 24px 80px}
h1,h2,h3,h4{font-family:var(--font-display); text-wrap:balance; margin:0}
p{margin:0}
code,.mono{font-family:var(--font-mono); font-size:.92em}
.eyebrow{font-family:var(--font-mono); font-size:11.5px; font-weight:600;
  letter-spacing:.1em; text-transform:uppercase; color:var(--ink-faint)}
header{display:flex; flex-direction:column; gap:16px}
h1{font-size:44px; font-weight:700; line-height:1.08; letter-spacing:-.02em}
.thesis{font-size:17px; color:var(--ink-soft); max-width:64ch}
.thesis strong{color:var(--ink); font-weight:600}
.facts{display:flex; flex-wrap:wrap; margin-top:8px;
  border:1px solid var(--line-soft); border-radius:var(--radius-md);
  background:var(--paper-raised); overflow:hidden}
.fact{flex:1 1 130px; padding:12px 16px; border-right:1px solid var(--line-soft)}
.fact:last-child{border-right:none}
.fact b{display:block; font-family:var(--font-display); font-size:22px;
  font-weight:700; line-height:1.2; font-variant-numeric:tabular-nums}
.fact span{font-family:var(--font-mono); font-size:11px; letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink-faint)}
.rail-block{margin:44px 0 8px}
.rail{display:grid; grid-template-columns:repeat(5,1fr); gap:10px}
.step{border:1px solid var(--line-soft); border-top:3px solid var(--sc);
  border-radius:var(--radius-md); background:var(--paper-raised);
  padding:14px 14px 16px; display:flex; flex-direction:column; gap:6px;
  box-shadow:var(--shadow-sm)}
.step .n{font-family:var(--font-mono); font-size:11px; font-weight:600;
  letter-spacing:.1em; color:var(--st)}
.step h4{font-size:17px; font-weight:600; letter-spacing:-.01em}
.step p{font-size:13px; color:var(--ink-soft); line-height:1.5}
.loopnote{display:flex; align-items:center; gap:10px; margin-top:14px;
  font-family:var(--font-mono); font-size:11.5px; letter-spacing:.04em;
  color:var(--ink-faint)}
.loopnote svg{flex:0 0 auto}
.phase{margin-top:40px; scroll-margin-top:20px}
.phase-head{display:flex; align-items:baseline; gap:14px; flex-wrap:wrap;
  padding-bottom:10px; border-bottom:2px solid var(--sc)}
.phase-head .n{font-family:var(--font-mono); font-size:12px; font-weight:600;
  letter-spacing:.12em; color:var(--st)}
.phase-head h2{font-size:29px; font-weight:700; letter-spacing:-.02em}
.count{margin-left:auto; font-family:var(--font-mono); font-size:11.5px;
  color:var(--ink-faint); letter-spacing:.06em}
.phase-why{display:grid; grid-template-columns:1fr 1fr; gap:14px; margin:14px 0 18px}
.phase-why div{padding:12px 14px; border-radius:var(--radius-sm);
  background:var(--sb); font-size:14px; color:var(--ink-soft); line-height:1.55}
.phase-why b{display:block; font-family:var(--font-mono); font-size:10.5px;
  letter-spacing:.1em; text-transform:uppercase; color:var(--st);
  margin-bottom:4px; font-weight:600}
.cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(310px,1fr)); gap:14px}
.card{border:1px solid var(--line-soft); border-radius:var(--radius-md);
  background:var(--paper-raised); padding:16px 18px 14px;
  display:flex; flex-direction:column; gap:9px}
.card .name{font-family:var(--font-mono); font-size:13.5px; font-weight:600;
  color:var(--ink); letter-spacing:-.01em; word-break:break-word}
.card .does{font-size:14px; line-height:1.55; color:var(--ink-soft)}
.trig{display:flex; flex-wrap:wrap; gap:5px}
.trig span{font-size:12px; color:var(--ink-faint); font-style:italic;
  background:var(--sb,transparent); padding:1px 7px; border-radius:var(--radius-pill);
  border:1px solid var(--line-soft)}
.card .not{font-size:12.5px; line-height:1.5; color:var(--ink-faint);
  padding-left:11px; border-left:2px solid var(--line)}
.meta{display:flex; flex-wrap:wrap; gap:6px; margin-top:auto; padding-top:4px}
.chip{font-family:var(--font-mono); font-size:10.5px; font-weight:600;
  letter-spacing:.05em; padding:3px 8px; border-radius:var(--radius-pill);
  border:1px solid var(--line); color:var(--ink-soft); white-space:nowrap}
.chip.cmd{background:var(--navy-tint); border-color:transparent; color:var(--navy-text)}
.bench{margin-top:52px; padding:26px; border:1px solid var(--line-pink);
  border-radius:var(--radius-lg); background:var(--pink-tint)}
.bench-head{display:flex; align-items:baseline; gap:14px; flex-wrap:wrap}
.bench-head h2{font-size:29px; font-weight:700; letter-spacing:-.02em}
.bench-head .eyebrow{color:var(--pink-text)}
.bench > p{margin:12px 0 20px; font-size:15px; color:var(--ink-soft); max-width:70ch}
.bench .card{border-color:var(--line-pink)}
.layer{margin-top:52px}
.layer h2{font-size:29px; font-weight:700; letter-spacing:-.02em}
.layer > p{margin:10px 0 18px; color:var(--ink-soft); max-width:72ch}
.scroll{overflow-x:auto; border:1px solid var(--line-soft);
  border-radius:var(--radius-md); background:var(--paper-raised)}
table{border-collapse:collapse; width:100%; min-width:600px}
th,td{text-align:left; padding:10px 16px; vertical-align:top;
  border-bottom:1px solid var(--line-soft); font-size:14px}
thead th{font-family:var(--font-mono); font-size:10.5px; font-weight:600;
  letter-spacing:.1em; text-transform:uppercase; color:var(--ink-faint);
  border-bottom:2px solid var(--line-pink)}
tbody tr:last-child td{border-bottom:none}
td.mono{font-size:13px; white-space:nowrap; color:var(--ink)}
td.dim{color:var(--ink-soft)}
.notes{margin-top:52px; border:1px dashed var(--line);
  border-radius:var(--radius-md); padding:24px 26px}
.notes h2{font-size:21px; font-weight:600; letter-spacing:-.01em}
.notes .eyebrow{margin-bottom:8px}
.notes > p{margin:10px 0 0; font-size:14px; color:var(--ink-soft); max-width:74ch}
.notes ul{margin:14px 0 0; padding-left:0; list-style:none;
  display:flex; flex-direction:column; gap:12px}
.notes li{font-size:14px; color:var(--ink-soft); line-height:1.55;
  padding-left:16px; border-left:2px solid var(--line-soft)}
.notes li b{color:var(--ink); font-weight:600}
.num{font-family:var(--font-mono); font-variant-numeric:tabular-nums;
  font-weight:600; color:var(--ink)}
footer{margin-top:40px; padding-top:18px; border-top:1px solid var(--line-soft);
  font-family:var(--font-mono); font-size:11.5px; letter-spacing:.05em;
  color:var(--ink-faint); display:flex; flex-wrap:wrap; gap:8px 20px}
@media (max-width:860px){
  .rail{grid-template-columns:repeat(2,1fr)}
  .phase-why{grid-template-columns:1fr}
  h1{font-size:34px}
  .phase-head h2,.bench-head h2,.layer h2{font-size:24px}
}
@media (max-width:520px){ .rail{grid-template-columns:1fr} }
@media (prefers-reduced-motion:no-preference){
  .card,.step{transition:box-shadow 200ms cubic-bezier(.4,0,.2,1)}
  .card:hover,.step:hover{box-shadow:var(--shadow-md)}
}
@media print{
  /* Print is a third theme, and it has to beat both stamps: someone printing
     from a dark-themed browser would otherwise get white text on white paper,
     because [data-theme] outranks a bare :root. */
  :root, :root[data-theme="dark"], :root:not([data-theme="light"]){
    --ink:#17132B; --ink-soft:#4A4459; --ink-faint:#6E6880;
    --paper:#FFFFFF; --paper-raised:#FFFFFF;
    --line:#9ED3DE; --line-soft:#C9E8ED; --line-pink:#EAB8D2;
    --p1-tint:#EAE8F8; --p2-tint:#E4EEF7; --p3-tint:#E1F3EE;
    --p4-tint:#FBF0DC; --p5-tint:#FCE7E3;
    --pink-tint:#FAE5F0; --cyan-tint:#DFF6F8; --navy-tint:#E4EBF1;
    --navy-text:#1B3A5C;
    --p1-text:#4B3F95; --p2-text:#2D6CAD; --p3-text:#177561;
    --p4-text:#7A5910; --p5-text:#A9483B;
    --pink-text:#A93D78; --cyan-text:#087580;
    --shadow-sm:none; --shadow-md:none;
  }
  @page{ margin:14mm 12mm; }
  html,body{background:#fff}
  *{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .wrap{max-width:none; padding:0}
  body{font-size:10.5pt; line-height:1.45}
  h1{font-size:26pt}
  .thesis{font-size:11.5pt}
  .phase-head h2,.bench-head h2,.layer h2{font-size:16pt}
  .step h4{font-size:12pt}
  .fact b{font-size:15pt}
  /* Nothing that reads as one object may be split across a page. */
  .card,.step,.phase-why div,.notes li,tr,.facts,.loopnote{break-inside:avoid}
  .phase-head,.bench-head,.layer h2,.notes h2{break-after:avoid}
  .phase,.bench,.layer,.notes{break-inside:auto}
  .bench,.layer,.notes{margin-top:24px}
  .phase{margin-top:22px}
  .rail-block{margin:22px 0 4px}
  /* The responsive breakpoints below fire in print, because the print
     viewport is about 590 CSS px wide. The rail collapsing to two columns
     destroys the one thing it exists to show — that these five are a
     sequence — so print restates the wide layout after them. */
  .rail{grid-template-columns:repeat(5,1fr)}
  .phase-why{grid-template-columns:1fr 1fr}
  /* Grid does not fragment across a page break: Chromium stops placing items
     at the boundary and leaves the rest of the section empty. The workbench
     lost half a page that way. Multi-column fragments correctly. */
  .cards{display:block; columns:2; column-gap:10px}
  .cards .card{display:block; margin:0 0 10px}
  .bench{padding:16px 18px}
  .card{padding:12px 14px 11px; gap:7px}
  /* A horizontally scrolling container is a screen affordance; on paper it
     just clips the right-hand column off the page. */
  .scroll{overflow:visible}
  table{min-width:0}
  th,td{padding:7px 10px}
  .step{padding:10px 11px 12px}
  .notes{border-style:solid}
  footer{margin-top:24px}
  a{text-decoration:none}
}
</style>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="fail if docs/skill-map.html is out of date")
    ap.add_argument("--fragment", metavar="PATH",
                    help="also write the head-less fragment an Artifact wants")
    a = ap.parse_args()

    d = gather()
    page = render(d)

    if a.check:
        if not os.path.exists(OUT):
            die("docs/skill-map.html does not exist — run without --check")
        if open(OUT, encoding="utf-8").read() != page:
            die("docs/skill-map.html is out of date. The plugin changed and "
                "the page did not. Run: python3 scripts/build_skill_map.py")
        print(f"skill map current — {len(d['skills'])} skills, "
              f"{len(d['commands'])} commands, {len(d['scripts'])} scripts.")
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(page)
    print(f"wrote docs/skill-map.html — {len(d['skills'])} skills across "
          f"{len(PHASES)} phases plus {len(BENCH)} on the workbench.")
    if a.fragment:
        open(a.fragment, "w", encoding="utf-8").write(render(d, fragment=True))
        print(f"wrote {a.fragment}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
