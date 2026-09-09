#!/usr/bin/env python3
"""Validate the corp-os plugin before packaging.

Checks structure, frontmatter, cross-references, step numbering, and that no
private content has leaked in. Exits non-zero on any error.
"""
import ast
import filecmp
import glob
import json
import shutil
import subprocess
import tempfile
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "corp-os")

# corp-os-audit assesses someone else's system, so it has nothing to log a
# run against. Every other exemption from a cross-cutting rule is a bug.
LOG_ROW_EXEMPT = {"corp-os-audit"}

errors, warnings = [], []
COVERAGE = None


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def main():
    os.chdir(PLUGIN)

    # --- manifest
    try:
        manifest = json.load(open(".claude-plugin/plugin.json"))
    except Exception as e:                                    # noqa: BLE001
        err(f"plugin.json unreadable: {e}")
        return report()
    if not re.fullmatch(r"[a-z0-9-]+", manifest.get("name", "")):
        err(f"plugin name not kebab-case: {manifest.get('name')!r}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
        err(f"version not semver: {manifest.get('version')!r}")

    # --- skills
    names = set(os.listdir("skills"))
    for d in sorted(names):
        path = f"skills/{d}/SKILL.md"
        if not os.path.exists(path):
            err(f"{d}: no SKILL.md")
            continue
        text = open(path, encoding="utf-8").read()
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not fm:
            err(f"{d}: no frontmatter")
            continue
        block = fm.group(1)
        name = re.search(r"^name:\s*(\S+)", block, re.M)
        desc = re.search(r"^description:\s*(.+)$", block, re.M)
        if not name or name.group(1) != d:
            err(f"{d}: frontmatter name does not match directory")
        if not desc:
            err(f"{d}: no description")
        elif len(desc.group(1)) < 80:
            warn(f"{d}: description is thin ({len(desc.group(1))} chars) — "
                 "descriptions are the trigger, so they need real phrases")

        words = len(text.split())
        if words > 3000:
            warn(f"{d}: SKILL.md is {words} words — over the 3000 guidance, "
                 "consider moving detail to reference/")

        for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`)]+)", text):
            if not os.path.exists(ref):
                err(f"{d}: broken plugin-root reference -> {ref}")

        steps = [int(x) for x in re.findall(r"^## Step (\d+)", text, re.M)]
        if steps != sorted(steps):
            err(f"{d}: step headings out of order: {steps}")

    # --- cross-references resolve to real skills
    # Everything that can name a skill, not just skills/ and the plugin README —
    # a broken skill name in reference/ or docs/ used to pass silently.
    strict = [f"skills/{d}/SKILL.md" for d in sorted(names)]
    strict += ["README.md", "CONNECTORS.md"] + sorted(glob.glob("reference/*.md"))
    # docs/ is a design record: it discusses skills that do not exist yet on
    # purpose, so an unknown name there is a note, not a broken reference.
    advisory = sorted(glob.glob(os.path.join(ROOT, "docs", "*.md")))
    advisory += [os.path.join(ROOT, "README.md")]

    def refs(paths):
        blob = "".join(open(s, encoding="utf-8").read()
                       for s in paths if os.path.exists(s))
        return sorted(set(re.findall(r"`(corp-os-[a-z-]+)`", blob)))

    for ref in refs(strict):
        if ref not in names:
            err(f"reference to unknown skill: {ref}")
    for ref in refs(advisory):
        if ref not in names:
            warn(f"docs mention a skill that does not exist: {ref} "
                 "(fine if it is a proposal)")

    # --- shipped assets parse
    for script in ("scripts/build_index.py", "scripts/write_export.py",
                   "scripts/log_run.py", "scripts/delete_source.py",
                   "scripts/scaffold.py", "scripts/upgrade_os.py"):
        try:
            ast.parse(open(script, encoding="utf-8").read())
        except SyntaxError as e:
            err(f"{script} syntax error: {e}")
        except OSError as e:
            err(f"{script} missing: {e}")

    # --- the list of scripts an OS carries lives in exactly two places, and
    # they have to agree. scaffold.py puts them there; upgrade_os.py refreshes
    # them. A name in one and not the other means either a new OS gets a script
    # that never updates, or an upgrade tries to refresh one that was never
    # installed. corp-os-setup used to carry a third copy of this list in prose
    # and it went stale within one release, which is why the prose copy is gone
    # rather than synced.
    def shipped_tuple(path):
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except (OSError, SyntaxError):
            return None
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if any(isinstance(t_, ast.Name) and t_.id == "SHIPPED"
                   for t_ in node.targets):
                try:
                    return tuple(ast.literal_eval(node.value))
                except ValueError:
                    return None
        return None

    a_ = shipped_tuple("scripts/scaffold.py")
    b_ = shipped_tuple("scripts/upgrade_os.py")
    if a_ is None or b_ is None:
        err("could not read SHIPPED from scaffold.py and upgrade_os.py — the "
            "two lists of what an OS carries can no longer be compared")
    elif set(a_) != set(b_):
        err(f"scaffold.py SHIPPED {sorted(a_)} != upgrade_os.py SHIPPED "
            f"{sorted(b_)} — an OS would be scaffolded with scripts the "
            "upgrade path never refreshes, or asked to refresh scripts it "
            "was never given")
    else:
        for s in a_:
            if not os.path.exists(os.path.join("scripts", s)):
                err(f"SHIPPED names scripts/{s}, which does not exist — every "
                    "OS scaffolded from here would silently lack it")

    for p in ("examples/config-worked-example.json",):
        try:
            json.load(open(p, encoding="utf-8"))
        except Exception as e:                                # noqa: BLE001
            err(f"{p}: {e}")

    # --- cross-cutting rules that ARCHITECTURE claims every skill obeys.
    # These live in many files by design, which is exactly why they drift; the
    # checks are here so a skill cannot ship without them again.
    for d in sorted(names):
        path = f"skills/{d}/SKILL.md"
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        if not re.search(r"^## Pre-flight$", text, re.M):
            err(f"{d}: no '## Pre-flight' section — the accessible-now and "
                "files-beat-memory rules are cross-cutting")
        if "config.json" not in text:
            err(f"{d}: never reads config.json — it is the authority every "
                "skill reads first")
        if d not in LOG_ROW_EXEMPT and "usage/log.md" not in text:
            err(f"{d}: never appends a usage/log.md row — that field is the "
                "whole improvement flywheel")
        # An optional layer must never be a test for whether an OS exists.
        # Lines that forbid the practice are the point, so skip negated ones.
        for line in text.splitlines():
            if re.search(r"\b(never|do not|don't|no longer|not thereby)\b", line, re.I):
                continue
            for layer in ("jobs/", "claims/", "people/", "topics/"):
                if re.search(r"(?:\bOS root\b|\blook for\b|\bfolder containing\b)"
                             r"[^\n]{0,90}`" + re.escape(layer) + "`", line, re.I):
                    err(f"{d}: appears to test for `{layer}` when detecting an "
                        "OS — every layer but the source archive is optional")

    # --- stated counts match the headings that follow them
    WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
               "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
               "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
               "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
    for path, pattern, counter in (
        ("skills/corp-os-reality-check/SKILL.md",
         r"worklist in (\w+) buckets", lambda tx: len(re.findall(r"^\d+\. \*\*", tx, re.M))),
        ("reference/os-audit-rubric.md",
         r"(\w+) dimensions", lambda tx: len(re.findall(r"^## Dimension ", tx, re.M))),
    ):
        if not os.path.exists(path):
            continue
        tx = open(path, encoding="utf-8").read()
        m2 = re.search(pattern, tx)
        if m2 and m2.group(1).lower() in WORDNUM:
            stated, actual = WORDNUM[m2.group(1).lower()], counter(tx)
            if stated != actual:
                err(f"{path}: says {m2.group(1)} but there are {actual}")

    # --- the roster count, wherever a README states it in words
    #
    # Both READMEs said a number of skills and both were wrong: nineteen three
    # releases after there were twenty-three, and twenty-one two after. It is
    # the same defect as the hard-coded version, the prose list of shipped
    # scripts, and the hand-kept skill map -- a fact that is already true on
    # disk, retyped somewhere that nothing recounts.
    #
    # Scoped to the live prose, never the version history: "corp-os-pattern is
    # the twenty-third skill" is a claim about the past and stays true.
    TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50}

    def wordnum(w):
        """Written out, because that is how the prose says it. A count in
        digits would be easier to check and would read like a changelog."""
        w = w.lower()
        if w in WORDNUM:
            return WORDNUM[w]
        if w in TENS:
            return TENS[w]
        if "-" in w:
            a, b = w.split("-", 1)
            if a in TENS and b in WORDNUM and WORDNUM[b] < 10:
                return TENS[a] + WORDNUM[b]
        return None

    for path, pattern in (
        (os.path.join(ROOT, "README.md"), r"the ([a-z]+(?:-[a-z]+)?) skills that operate on it"),
        (os.path.join(ROOT, "README.md"), r"live in ([a-z]+(?:-[a-z]+)?) skill files"),
        ("README.md", r"plus ([a-z]+(?:-[a-z]+)?) skills that operate on it"),
    ):
        if not os.path.exists(path):
            err(f"{path}: gone — the roster count was stated here and nothing "
                "else checks it")
            continue
        tx = open(path, encoding="utf-8").read().split("## Version history")[0]
        m2 = re.search(pattern, tx)
        if not m2:
            err(f"{os.path.relpath(path, ROOT)}: the sentence stating how many "
                f"skills there are no longer matches /{pattern}/ — either fix "
                "the sentence or drop this check, but do not leave a count "
                "nothing recounts")
            continue
        stated = wordnum(m2.group(1))
        if stated is None:
            err(f"{os.path.relpath(path, ROOT)}: cannot read {m2.group(1)!r} "
                "as a number")
        elif stated != len(names):
            err(f"{os.path.relpath(path, ROOT)}: says {m2.group(1)} skills, "
                f"but there are {len(names)} on disk")

    # --- plugin content changed after the last version bump
    #
    # A client caches an installed plugin by version string, so commits pushed
    # without a bump reach nobody: no error, no warning, and nothing the person
    # running it could inspect. docs/INSTALL.md establishes that and nothing
    # enforced it, which is the shape this repo converts into code.
    #
    # It reads committed history only, so it does not fire while someone is
    # mid-edit with a dirty tree -- a check that is red during normal work is
    # one everybody learns to ignore. It fires after the content is committed
    # and before it is pushed, which is the moment that matters.
    def git(*args):
        r = subprocess.run(["git", "-C", ROOT] + list(args),
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 else None

    rel_manifest = "plugins/corp-os/.claude-plugin/plugin.json"
    cur = manifest.get("version")
    if git("rev-parse", "--git-dir") and cur:
        shas = (git("log", "--format=%H", "--", rel_manifest) or "").split()
        bump = None
        for sha in shas:                     # newest first
            blob = git("show", f"{sha}:{rel_manifest}")
            if blob is None:
                break
            try:
                v = json.loads(blob).get("version")
            except ValueError:
                break
            if v != cur:
                break
            bump = sha                       # oldest commit still carrying it
        if bump:
            after = git("rev-list", f"{bump}..HEAD", "--", "plugins/corp-os/")
            if after:
                n = len(after.split())
                err(f"{n} commit(s) changed the plugin after the last version "
                    f"bump ({cur}). A client caches by version string, so "
                    "those changes reach nobody — bump the version in both "
                    "manifests, or squash them into the bump commit.")

    # --- the version on origin is the version people can actually install
    #
    # A marketplace install resolves against the pushed branch, so a release
    # that exists only locally is a release nobody has. Three consecutive
    # cost-reduction releases sat unpushed while the OS they were written to
    # make cheaper went on running the old one, and every check in this file
    # passed throughout: the repo was internally consistent and externally
    # absent. The bump check above asks whether the version was raised. This
    # one asks whether anyone received it.
    #
    # It reads the last-fetched origin ref instead of fetching, because a
    # validator that reaches the network fails offline for reasons that have
    # nothing to do with the plugin. A stale ref can make this check late; it
    # cannot make it wrong in the direction that matters.
    def semver(v):
        try:
            return tuple(int(part) for part in str(v).split("."))
        except (TypeError, ValueError):
            return None

    if git("rev-parse", "--git-dir") and cur:
        ref = next((r for r in ("origin/main", "origin/master")
                    if git("rev-parse", "--verify", "--quiet", r)), None)
        if ref is None:
            warn("no origin ref to compare against, so whether this version "
                 "has been published is unknown. Every other release check "
                 "here is about the repo; this one is about what people can "
                 "install.")
        else:
            blob = git("show", f"{ref}:{rel_manifest}")
            try:
                pub = json.loads(blob).get("version") if blob else None
            except ValueError:
                pub = None
            local_v, pub_v = semver(cur), semver(pub)
            if pub is None:
                warn(f"{ref} carries no readable plugin manifest, so the "
                     "published version is unknown.")
            elif local_v and pub_v and local_v > pub_v:
                err(f"version {cur} is not on {ref}, which still serves "
                    f"{pub}. A marketplace install resolves against the "
                    "pushed branch, so this release reaches nobody until it "
                    "is pushed.")
            elif local_v and pub_v and local_v < pub_v:
                err(f"{ref} serves {pub}, which is ahead of the local {cur}. "
                    "Pull before releasing, or the next push takes published "
                    "work back off the shelf.")

    # --- every skill declares what kind of pass it is
    #
    # A real intake run cost $40 because a mechanical pass -- fetching forty
    # transcripts and writing them back out -- ran on the most expensive model
    # available, and nothing in twenty-three skills said which ones are filing
    # and which are reasoning. The declaration is for the person choosing, and
    # for corp-os-guide when it routes.
    # capture is what decides a run's cost, so it is documented and honoured
    # It lives in records.md, not configuration.md: pull and intake are its
    # only readers and neither reads configuration.md, while the six skills
    # that do read it were paying for a block none of them uses.
    cfgdoc = open("reference/capture.md", encoding="utf-8").read()
    for term, why in (("\"capture\"", "the block that caps what a run fetches"),
                      ("Verbatim fetch", "the connector field that decides "
                       "whether skipping an item defers it or destroys it")):
        if term not in cfgdoc:
            err(f"reference/capture.md does not document {term} — {why}")
    # The two-call shape is what makes triage possible; without it recorded, a
    # skill knows it can reach a source and nothing about reaching it cheaply.
    for term, why in (("List call", "what enumerates a source without bodies"),
                      ("Fetch call", "what returns one body by id"),
                      ("Fetch command", "the script path, for a source a model "
                       "never has to carry bytes for"),
                      ("Credential", "named by reference — an OS folder gets "
                       "synced, shared and audited")):
        if term not in open("reference/records.md", encoding="utf-8").read():
            err(f"reference/records.md does not document `{term}` — {why}")
    cn = open("skills/corp-os-connect/SKILL.md", encoding="utf-8").read()
    if "List call" not in cn:
        err("corp-os-connect no longer asks for the list call. It is the single "
            "highest-value fact in a connector record: without it every pull "
            "fetches bodies it did not need")
    if "never write them" not in cn.lower() and "never writes them" not in cn.lower():
        err("corp-os-connect no longer says credentials are named and not "
            "written. connectors.md is synced, shared and handed to audits")
    for term, why in (('"body"', "how much of a kept item is written"),
                      ("excerpt", "the mode that costs what the material was "
                       "used for rather than how long it is")):
        if term not in cfgdoc:
            err(f"reference/capture.md does not document {term} — {why}")

    pl = open("skills/corp-os-pull/SKILL.md", encoding="utf-8").read()
    if "re-open a file this run just wrote" not in pl:
        err("corp-os-pull no longer forbids re-reading what it just wrote — "
            "that is the same bytes at full price, for a file nothing has "
            "changed since writing")
    # A cap and a triage list are only safe if the cutoff distinguishes "a
    # decision was made about this" from "we never got to it". Advancing past
    # both turns each into permanent invisible loss — the source may still hold
    # the item and nothing in the OS will mention it again.
    if "cutoff does not move past it" not in pl:
        err("corp-os-pull no longer distinguishes how the cutoff moves for a "
            "triage skip versus a batch remainder. Advancing past both makes "
            "capping and triage silent data loss")
    rb = open("skills/corp-os-rebuild/SKILL.md", encoding="utf-8").read()
    if "claim-record.md" not in rb:
        err("corp-os-rebuild does not read reference/claim-record.md. It "
            "re-derives claims from raw/ — without the spec for what a claim "
            "is, it is re-deriving against whatever it remembers")
    if "batch" not in pl or "list first" not in pl:
        err("corp-os-pull no longer caps the pass or lists before fetching. "
            "That is the instruction that made one intake run cost more than "
            "the connector it pulled from")

    # A mechanical declaration is a claim that nothing here needs the
    # expensive model. Three skills have now made that claim while inferring
    # tags from an existing vocabulary or proposing what to keep -- work whose
    # errors are invisible at the time and expensive later. These two markers
    # are what those cases had in common; they do not catch every kind of
    # judgment, and the ones they miss are still a reading call (§4.50).
    for d in sorted(names):
        path = f"skills/{d}/SKILL.md"
        if not os.path.exists(path):
            continue
        body = open(path, encoding="utf-8").read()
        if "> **Mechanical pass" not in body:
            continue
        for marker, why in (
                ("infer", "inferring from an existing vocabulary is judgment, "
                          "and cheap-model tagging degrades every later recall "
                          "while showing nothing at the time"),
                ("keep or skip", "choosing what to capture is the one decision "
                                 "nothing downstream can undo")):
            if marker in body:
                err(f"{d}: declares a mechanical pass and contains "
                    f"{marker!r} — {why}. Reclassify, or move that step out.")

    # corp-os-guide routes and does not act. It stated that as a prohibition
    # in one line while Step 4 said "offer to do it", and a conformance run
    # caught it opening a decision, writing a job, and never naming the skill
    # it was supposed to route to. The rule is now positive and names the two
    # files it may write; this keeps it from drifting back to a bare "never".
    gd = open("skills/corp-os-guide/SKILL.md", encoding="utf-8").read()
    if "only files this one writes" not in gd:
        err("corp-os-guide no longer states which files it may write. It is "
            "the front door: a run that does the work instead of routing "
            "skips the skill that has the rules for doing it properly")
    if "offer to do it" in gd:
        err("corp-os-guide tells itself to offer to do the work. That is the "
            "instruction that had it opening decisions rather than naming "
            "corp-os-decide — the offer is to hand off")

    # A rule stated after the step it governs is a rule the run has already
    # passed. corp-os-jobs put its write gate forty lines below "Adding a
    # job" and a conformance run wrote two job files with no proposal behind
    # either. Position is the check, not presence.
    jb = open("skills/corp-os-jobs/SKILL.md", encoding="utf-8").read()
    if "## The write gate" not in jb or "## Adding a job" not in jb:
        err("corp-os-jobs lost one of its section headings; the gate-order "
            "check cannot run")
    elif jb.index("## The write gate") > jb.index("## Adding a job"):
        err("corp-os-jobs states its write gate after the sections that "
            "write. `jobs/` is derived, so every creation, edit, split and "
            "retirement is proposed first — a rule read after the step is a "
            "rule the run has already passed")
    im = open("skills/corp-os-improve/SKILL.md", encoding="utf-8").read()
    if "writes only under `usage/`" not in im:
        err("corp-os-improve no longer says where it may write. Asked to "
            "study the usage log it wrote a claim, which arrives with no "
            "proposal behind it and no source anyone can check")

    PASSES = ("Mechanical pass", "Mixed pass", "Judgment pass")
    for d in sorted(names):
        path = f"skills/{d}/SKILL.md"
        if not os.path.exists(path):
            continue
        body = open(path, encoding="utf-8").read()
        found = [k for k in PASSES if f"> **{k}" in body]
        if not found:
            err(f"{d}: declares no pass type. One of {', '.join(PASSES)} as a "
                "blockquote under the title — a skill that does not say whether "
                "it is filing or reasoning gets run on whatever model is loaded, "
                "and the mechanical ones are the ones that move real bytes")
        elif len(found) > 1:
            err(f"{d}: declares {len(found)} pass types ({', '.join(found)}). "
                "It is one of the three.")

    # --- version parity between the plugin and the marketplace manifest
    mkt_path = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
    if os.path.exists(mkt_path):
        try:
            mkt = json.load(open(mkt_path, encoding="utf-8"))
            mv = mkt.get("metadata", {}).get("version")
            if mv != manifest.get("version"):
                err(f"version mismatch: plugin.json {manifest.get('version')!r} "
                    f"vs marketplace.json {mv!r}")
        except Exception as e:                                # noqa: BLE001
            err(f"marketplace.json unreadable: {e}")

    # --- the plugin README documents the shipped version
    readme = open("README.md", encoding="utf-8").read()
    if f"**{manifest.get('version')}**" not in readme:
        err(f"README.md has no version-history entry for "
            f"{manifest.get('version')} — a change nobody can explain later "
            "gets reverted by accident")

    # --- commands: static checks, because a command is a thin file and almost
    # everything that can be wrong with one is checkable without a model.
    cmd_dir = "commands"
    if os.path.isdir(cmd_dir):
        seen_desc = {}
        for f in sorted(os.listdir(cmd_dir)):
            if not f.endswith(".md"):
                err(f"commands/{f} is not a .md file")
                continue
            cname = f[:-3]
            text = open(os.path.join(cmd_dir, f), encoding="utf-8").read()
            m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
            if not m:
                err(f"commands/{f}: no frontmatter — without it the command has "
                    "no description, and the description is the only thing a "
                    "person sees when choosing between them")
                continue
            fm, body = m.group(1), m.group(2)
            d = re.search(r"^description:\s*(.+)$", fm, re.M)
            if not d:
                err(f"commands/{f}: no description")
                continue
            desc = d.group(1).strip()
            if len(desc) > 90:
                warn(f"commands/{f}: description is {len(desc)} chars — these "
                     "sit in a picker one line each, so long ones truncate "
                     "where nobody can see what got cut")
            key = desc.lower()[:40]
            if key in seen_desc:
                err(f"commands/{f} and commands/{seen_desc[key]}.md open with "
                    "the same description — a person choosing between them "
                    "cannot")
            seen_desc[key] = cname
            # It must reach a real skill.
            named = set(re.findall(r"`(corp-os-[a-z-]+)`", body))
            if not named:
                err(f"commands/{f}: names no skill. A command that does not "
                    "hand off is a second place for the same instructions to "
                    "live, and they will drift")
            for s in named:
                if s not in names:
                    err(f"commands/{f}: invokes unknown skill {s}")
            if "$ARGUMENTS" not in body:
                err(f"commands/{f}: never mentions $ARGUMENTS — anything a "
                    "person types after the command name is then silently "
                    "dropped")
            # The no-args path has to be decided, not left to chance.
            if not re.search(r"no argument|with none|nothing given|if the "
                             r"person gave|if given|if one|if the audience is "
                             r"not|gave nothing|empty invocation", body, re.I):
                warn(f"commands/{f}: says nothing about what happens with no "
                     "arguments. That is the path most people take first")

    # --- the guide routes to every skill
    guide = open("skills/corp-os-guide/SKILL.md", encoding="utf-8").read()
    for d in sorted(names):
        if d != "corp-os-guide" and f"`{d}`" not in guide:
            err(f"corp-os-guide does not route to {d}")

    # --- the shipped script actually runs, against a real tree.
    # Parsing build_index.py proves it imports, not that it works. The fixture
    # exercises the cases that broke it before: a custom layer, a disabled
    # layer, list-style entries, an excluded directory.
    # Two fixtures, deliberately unlike each other. fixture-os is the shipped
    # default; fixture-register is a legitimately-configured OS with jobs off,
    # renamed vocabulary, and a hand-maintained source layer. Running only the
    # first would test only the shape the model already expects.
    FIXTURES = {
        "examples/fixture-os": [
            ("**Jobs**: 2", "job count"),
            ("**Findings**: 4",
             "the claims heading uses the person's vocabulary, not the "
             "plugin's -- this config renames claim to finding"),
            ("**Decisions**: 2", "custom-layer count"),
            ("**Dashboards**: 2",
             "the dashboards registry is one file of many entry headers -- "
             "counted by header, not by file. It shipped as a directory-shaped "
             "path holding one file for five releases, which read as 1 no "
             "matter how many dashboards were registered"),
            ("dec-001", "custom-layer entries render"),
            ("· Priya Raman · by 2026-11-01",
             "custom index_line template is applied, not a bare link"),
            ("2026-08-21--note--hallway",
             "unprocessed queue reflects processed: false"),
            ("`usage/` — excluded by config",
             "config-driven scan exclusions are honored"),
            ("## Resting on evidence that has gone stale",
             "the join between an entry's decay and the things built from it. "
             "CL-0003's Verified date in the fixture is deliberately old and "
             "AR-0002 rests on it, so this case stays true as time moves "
             "forward rather than ageing out of being a case"),
            ("AR-0002 — **1 of 1** past its window",
             "the count is per-entry and says how many of how many, because "
             "1 of 1 and 2 of 9 are not the same finding"),
        ],
        "examples/fixture-register": [
            ("**Entries**: 4",
             "vocabulary rename claim -> entry reaches the heading"),
            ("**Open-Items**: 3", "the custom layer carrying the priority signal"),
            ("**Playbooks**: 2", "a layer whose role is source still renders"),
            ("oi-001", "open-item entries render"),
            ("· now", "the urgency field reaches the index line"),
            ("hand-maintained", "the playbooks index_line is applied"),
        ],
    }
    FORBIDDEN = {
        "examples/fixture-os": [
            ("glossary", "a disabled layer must be omitted, not rendered empty"),
        ],
        "examples/fixture-register": [
            ("## Jobs", "jobs is disabled here; rendering the section anyway "
                        "means the disabled-layer path is not honored"),
            ("**Claims**", "the plugin's word for a layer the person renamed"),
        ],
    }

    for fixture, expectations in FIXTURES.items():
        if not os.path.isdir(fixture):
            err(f"{fixture} is missing — build_index.py is then only "
                "syntax-checked, which has never been the failure mode")
            continue
        # A real OS carries its own copy of the script (corp-os-setup Step 3),
        # and several skills tell the model to run it. A fixture without one
        # tests the fixture rather than the skill -- that gap produced a false
        # failure once.
        # Present is not enough: it has to be the CURRENT one. All three
        # fixtures carried a 414-line build_index.py against a shipped 888 --
        # fixture-stale, which is deliberately behind, was NEWER than the two
        # that are not. Sixteen skills call scripts at the OS path, so every
        # conformance result about script behaviour was measured against a
        # script half the size of the one that ships. §4.27 is the same
        # finding one layer down: a harness that runs the wrong artifact
        # reports on the wrong artifact, confidently.
        if "fixture-stale" not in fixture:
            for script in sorted(os.listdir(os.path.join(PLUGIN, "scripts"))):
                if not script.endswith(".py"):
                    continue
                fp = os.path.join(fixture, "scripts", script)
                if os.path.exists(fp) and not filecmp.cmp(
                        os.path.join(PLUGIN, "scripts", script), fp, shallow=False):
                    err(f"{fixture}/scripts/{script} has drifted from the "
                        "shipped copy. Skills run the OS's copy, so a stale "
                        "one means every case measured something else")
        for script in ("build_index.py", "write_export.py", "log_run.py",
                       "delete_source.py"):
            if not os.path.exists(os.path.join(fixture, "scripts", script)):
                err(f"{fixture} has no scripts/{script} — corp-os-setup puts "
                    "one in every OS it scaffolds, and skills that reach for "
                    "it will fail against a fixture that does not")
        # No fixture file may be IGNORED by git. The repo ignores `raw/`,
        # `usage/log.md`, `proposals/` and `sensitive.md` so nobody commits a
        # real OS -- and the fixtures are made of exactly those. Without a
        # negation rule they commit incomplete, the build passes locally, and
        # the first person to clone gets a broken one. That failure only ever
        # shows up on someone else's machine, which is the kind worth spending
        # a check on.
        #
        # The question is "would git ignore this", not "has it been committed
        # yet" -- an uncommitted new fixture file is ordinary work in progress
        # and failing the build on it makes the check something people route
        # around.
        try:
            paths = []
            for dp, _, fn in os.walk(fixture):
                for f in fn:
                    paths.append("plugins/corp-os/" +
                                 os.path.join(dp, f).replace(os.sep, "/")
                                 .lstrip("./"))
            if paths:
                r0 = subprocess.run(["git", "check-ignore", "--stdin"], cwd=ROOT,
                                    input="\n".join(paths), capture_output=True,
                                    text=True, timeout=30)
                ignored = sorted(x.strip() for x in r0.stdout.split("\n")
                                 if x.strip())
                if ignored:
                    err(f"{fixture}: {len(ignored)} file(s) would be ignored by "
                        f"git — a clone gets a broken fixture. Add a negation "
                        f"to .gitignore: {ignored[:4]}")
        except (subprocess.TimeoutExpired, OSError):
            pass

        tmp = tempfile.mkdtemp(prefix="corpos-fixture-")
        try:
            work = os.path.join(tmp, "os")
            shutil.copytree(fixture, work)
            r = subprocess.run(
                [sys.executable, "scripts/build_index.py", work],
                capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                err(f"build_index.py failed on {fixture}: "
                    f"{(r.stderr or r.stdout).strip()[:400]}")
                continue
            idx = open(os.path.join(work, "INDEX.md"), encoding="utf-8").read()
            hp = os.path.join(work, "usage", "health.md")
            health = open(hp, encoding="utf-8").read() if os.path.exists(hp) else ""
            # The findings moved out of INDEX.md into usage/health.md, which
            # is the point: at 800 claims they were 1,029 of the index's 1,440
            # tokens and every skill read them on every run. Expectations are
            # checked against both, and then the split itself is asserted --
            # otherwise a regression that put them back would pass here.
            if not health:
                err(f"{fixture}: build_index.py wrote no usage/health.md. The "
                    "findings have to land somewhere; uncapped in a file one "
                    "skill reads is the whole trade")
            for moved in ("## Resting on evidence that has gone stale",
                          "## Arguments resting on one source",
                          "## One call from promotion", "## Open evidence"):
                if moved in idx:
                    err(f"{fixture}: {moved!r} is back in INDEX.md. Every "
                        "skill reads that file on every run and almost none "
                        "act on these; they belong in usage/health.md")
            idx = idx + "\n" + health
            for needle, why in expectations:
                if needle not in idx:
                    err(f"{fixture} render is missing {why}: {needle!r}")
            for needle, why in FORBIDDEN.get(fixture, []):
                if needle.lower() in idx.lower():
                    err(f"{fixture} render should not contain {needle!r} — {why}")
            if "WARNING" in (r.stdout or ""):
                warn(f"build_index.py warned on {fixture}: "
                     f"{r.stdout.strip()[:200]}")
            # Idempotence: a second run must find no drift.
            r2 = subprocess.run(
                [sys.executable, "scripts/build_index.py", work, "--check"],
                capture_output=True, text=True, timeout=60)
            if r2.returncode != 0:
                err(f"build_index.py is not idempotent on {fixture} — a second "
                    f"--check run reports drift: {(r2.stdout or '').strip()[:300]}")
        except subprocess.TimeoutExpired:
            err(f"build_index.py timed out on {fixture}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


    # --- fixture-stale is asserted to still be broken.
    # It is the only fixture that is deliberately wrong, and the danger with a
    # deliberately-wrong fixture is somebody tidying it: repair it and the
    # corp-os-upgrade case passes against an OS with nothing to upgrade, which
    # is worse than no case at all because it reads as coverage.
    #
    # It is kept out of the build_index execution loop above on purpose. Its
    # dashboards layer carries the pre-0.10.1 path shape, so running the
    # counter over it warns every single time, and a validator that always
    # warns has taught everyone to skip its output.
    STALE = "examples/fixture-stale"
    if not os.path.isdir(STALE):
        err(f"{STALE} is missing — corp-os-upgrade then has nothing to be "
            "tested against except a healthy OS, where it has nothing to find")
    else:
        try:
            paths = sorted(os.path.join(PLUGIN, dp, f).replace(ROOT + os.sep, "")
                           for dp, _, fns in os.walk(STALE) for f in fns)
            if paths:
                r0 = subprocess.run(["git", "check-ignore", "--stdin"], cwd=ROOT,
                                    input="\n".join(paths), capture_output=True,
                                    text=True, timeout=30)
                ig = sorted(x.strip() for x in r0.stdout.split("\n") if x.strip())
                if ig:
                    err(f"{STALE}: {len(ig)} file(s) would be ignored by git — "
                        f"a clone gets a broken fixture: {ig[:4]}")
        except (subprocess.TimeoutExpired, OSError):
            pass

        try:
            scfg = json.load(open(os.path.join(STALE, "config.json"),
                                  encoding="utf-8"))
        except (OSError, ValueError) as e:
            err(f"{STALE}/config.json unreadable: {e}")
            scfg = {}
        if scfg.get("corpos_version") == manifest.get("version"):
            err(f"{STALE} records the current version — it is supposed to be "
                "behind, and an upgrade run against it now finds nothing")
        reg = os.path.join(STALE, "dashboards", "registry.md")
        if not os.path.exists(reg):
            err(f"{STALE} no longer carries the pre-0.10.1 dashboards layout, "
                "which is the migration corp-os-upgrade must refuse to perform")
        elif sum(1 for ln in open(reg, encoding="utf-8")
                 if ln.startswith("### ")) < 2:
            err(f"{STALE}/dashboards/registry.md needs more than one entry — "
                "with one, the miscount is invisible and the fixture proves "
                "nothing")
        if os.path.exists(os.path.join(STALE, "scripts", "delete_source.py")):
            err(f"{STALE} is supposed to be missing delete_source.py — that is "
                "the 'shipped script this OS predates' case")
        a_ = os.path.join("scripts", "build_index.py")
        b_ = os.path.join(STALE, "scripts", "build_index.py")
        if os.path.exists(b_) and filecmp.cmp(a_, b_, shallow=False):
            err(f"{STALE}/scripts/build_index.py is identical to the shipped "
                "one — it is supposed to be an older copy, which is the drift "
                "corp-os-upgrade detects by content rather than by date")





    # --- the 0.14 schema rules.
    #
    # Named per file, not searched across all three. 0.16 split the data model
    # into a spine plus two record specs so a skill reads only what it needs,
    # and a check that accepts a field anywhere would not notice one drifting
    # into the file whose readers never open it -- which is the whole failure
    # the split was performed to fix.
    SPEC = {f: open("reference/" + f, encoding="utf-8").read()
            for f in ("data-model.md", "claim-record.md", "records.md")}
    for term, where, why in (
            ("Source fidelity", "claim-record.md", "the medium split out of confidence"),
            ("Retrievable", "claim-record.md", "the derived flag that makes the promotion "
                            "backlog visible"),
            ("Confidence reason", "claim-record.md", "the sibling field that replaced the "
                                  "rejected suffix"),
            ("Rests on", "claim-record.md", "the dependency field the arguments layer needs"),
            ("append-only", "data-model.md", "the first invariant, stated where every "
                            "skill's pre-flight can reach it"),
            ("external_id", "records.md", "the raw-file field dedupe reads")):
        if term not in SPEC[where]:
            elsewhere = [f for f, tx in SPEC.items() if f != where and term in tx]
            err(f"reference/{where} does not document `{term}` — {why}"
                + (f" (it is in {elsewhere[0]}, whose readers are a different set "
                   "of skills)" if elsewhere else ""))

    # --- every skill reaches the reference file that defines what it uses
    #
    # §4.48. The 0.16 split verified each FIELD is documented in the right
    # file. Nothing verified each SKILL still reaches everything it uses, and
    # corp-os-rebuild spent two releases re-deriving claims with no spec for
    # what a claim is. Converting unconditional reads into pointers is that
    # same operation performed twenty more times on purpose, so this has to
    # exist before those conversions do. A pointer counts: the test is whether
    # the file is named in the skill at all, not whether it is read every run.
    OWNS = (
        ("Rests on", "claim-record.md"),
        ("Source fidelity", "claim-record.md"),
        ("Confidence reason", "claim-record.md"),
        ("Retrievable", "claim-record.md"),
        ("external_id", "records.md"),
        ("entry_schema", "data-model.md"),
        ("index_line", "data-model.md"),
    )
    for d in sorted(names):
        sp = f"skills/{d}/SKILL.md"
        if not os.path.exists(sp):
            continue
        sbody = open(sp, encoding="utf-8").read()
        for term, owner in OWNS:
            if term in sbody and owner not in sbody:
                err(f"{d}: uses `{term}` and never names "
                    f"reference/{owner}, which defines it. A skill that "
                    "enforces a field without reaching its spec is enforcing "
                    "whatever it remembers.")

    # A reason must never be written INTO an enum value. Everything downstream
    # equality-tests confidence, so `needs_review — because x` breaks the
    # index, the export emitter, every ceiling rule and every eval assertion.
    # The proposal that suggested it was declined for exactly this reason, and
    # a doc example is how a declined idea comes back.
    for f in sorted(glob.glob("reference/*.md")) + [
            f"skills/{d}/SKILL.md" for d in sorted(names)]:
        body = open(f, encoding="utf-8").read()
        for m in re.finditer(r"\*\*Confidence\*\*\s*:\s*(\w+)\s*[—-]\s*\w",
                             body):
            err(f"{f}: a confidence value carries a reason inside it "
                f"({m.group(0)[:48]!r}). Use the `Confidence reason` field — "
                "everything downstream equality-tests this value.")

    # Both halves of the fidelity story, or neither is usable: something has to
    # record what a connector can give back, and something has to read it.
    wrote = "Verbatim fetch" in open("skills/corp-os-connect/SKILL.md",
                                     encoding="utf-8").read()
    reads = "Source fidelity" in open("skills/corp-os-claims/SKILL.md",
                                      encoding="utf-8").read()
    if wrote != reads:
        err(f"source fidelity is handled by only one side: connect records "
            f"the connector's capability={wrote}, claims reads it={reads}. "
            "Recording it and never reading it leaves the backlog invisible, "
            "which is the state this release exists to fix.")

    # migrate_schema must never invent a value it cannot derive.
    ms = open("scripts/migrate_schema.py", encoding="utf-8").read()
    if "left blank" not in ms:
        err("scripts/migrate_schema.py no longer says it leaves underivable "
            "fields blank — a plausible wrong value is the failure this whole "
            "model is built to prevent")

    # --- patterns: the shipped ones must actually bind, and must be portable.
    # A pattern that addresses a layer by NAME binds in exactly one OS -- the
    # one it was written in -- and fails everywhere else by rendering an empty
    # panel, which reads as a state rather than a defect. Shipping one like
    # that would teach the shape wrong by example, which is worse than not
    # shipping patterns at all.
    for pf in sorted(glob.glob("patterns/*.md")):
        head = re.match(r"^---\n(.*?)\n---\n",
                        open(pf, encoding="utf-8").read(), re.S)
        if not head:
            err(f"{pf}: no frontmatter, so nothing can bind it")
            continue
        fm = head.group(1)
        for key in ("kind", "requires", "target", "generator"):
            if not re.search(rf"^{key}\s*:", fm, re.M):
                err(f"{pf}: no `{key}` in frontmatter")
        # `role:` is the portable address. A requirement naming a layer
        # directly is the defect this whole mechanism exists to prevent.
        if "role:" not in fm:
            err(f"{pf}: no requirement uses `role:` — a pattern that names "
                "layers directly is not portable, and this is the exact "
                "mistake reference/patterns.md is written to prevent")
        for bad in re.findall(r"^\s*-?\s*layer\s*:\s*(\S+)", fm, re.M):
            err(f"{pf}: requires a layer by name (`{bad}`). Use role + fields.")

        # os.path.abspath, not os.path.join(ROOT, ...): this loop runs with
        # cwd at PLUGIN, so joining against the repo root produced a path that
        # does not exist, bind_pattern exited with an error instead of the word
        # REFUSED, and the check passed on every input. A check that cannot
        # fail is worse than no check, because it is counted as coverage.
        r = subprocess.run(
            [sys.executable, "scripts/bind_pattern.py",
             "--root", "examples/fixture-os", "--pattern", os.path.abspath(pf)],
            capture_output=True, text=True, timeout=60)
        if r.returncode != 0 and "REFUSED" not in (r.stdout or ""):
            err(f"{pf}: bind_pattern.py could not read it — "
                f"{(r.stderr or r.stdout).strip()[:200]}")
        if "REFUSED" in (r.stdout or ""):
            err(f"{pf} does not bind against the default fixture:\n"
                + "\n".join(l for l in r.stdout.split("\n")
                              if "MISSING" in l or "no enabled" in l))

    # --- the pattern kinds the binder accepts are actually exercised
    #
    # KINDS lists five. For two releases the fixture carried one pattern and it
    # was a dashboard, so four accepted values had no fixture, no binding and no
    # generator behind them -- the binder validating against a list it had never
    # had to honour. Same class as a check that has never been seen to fail.
    kinds_seen = set()
    for pf in sorted(glob.glob("examples/fixture-*/patterns/*.md")):
        k = re.search(r"^kind:\s*(\S+)", open(pf, encoding="utf-8").read(), re.M)
        if k:
            kinds_seen.add(k.group(1))
    if len(kinds_seen) < 2:
        err(f"the fixtures exercise only {sorted(kinds_seen) or 'no'} pattern "
            "kind(s). bind_pattern.py accepts five; a value nothing binds "
            "against is untested surface, not coverage")

    # --- a pattern's generator is the artifact, so run one
    #
    # reference/patterns.md says the script is the artifact and the output is
    # its product. Asserting a pattern binds proves the frontmatter parses; it
    # says nothing about whether the thing it points at works.
    # --- find.py returns matches, not files, and reads BOTH entry encodings
    #
    # A corpus stores entries two ways -- many per file as `### ID` blocks with
    # bold-label fields, and one per file with YAML frontmatter -- and both are
    # legitimate. A reader that handles only the first returns a confident,
    # quiet zero for every layer using the second, which is exactly how the
    # 0.15.0 evidence generator shipped reporting "0 open decisions" against a
    # fixture holding two. So the check asserts a match from each encoding.
    fp = "examples/fixture-os/scripts/find.py"
    if not os.path.exists(fp):
        err(f"{fp} is missing — it is in SHIPPED, so an OS is supposed to carry it")
    else:
        rf = subprocess.run(
            [sys.executable, os.path.abspath(fp), "--root",
             os.path.abspath("examples/fixture-os"), "--topic", "pricing", "--digest"],
            capture_output=True, text=True, timeout=60)
        out = rf.stdout or ""
        if rf.returncode != 0:
            err(f"find.py failed on the fixture: {(rf.stderr or out).strip()[:200]}")
        if "CL-0001" not in out:
            err("find.py found no `### ID` block entry for a topic the fixture "
                "plainly holds — the many-entries-per-file encoding is not read")
        if "dec-001" not in out:
            err("find.py found no frontmatter entry (dec-001 is a mid-market "
                "pricing decision). A reader that handles one encoding answers "
                "zero for every layer using the other, and says nothing about it")
        rs = subprocess.run(
            [sys.executable, os.path.abspath(fp), "--root",
             os.path.abspath("examples/fixture-os")],
            capture_output=True, text=True, timeout=60)
        if rs.returncode == 0:
            err("find.py accepted an unscoped search. Returning the whole corpus "
                "is what INDEX.md is for, and doing it here costs the caller "
                "every entry to answer a question about one")

    gen = "examples/fixture-os/scripts/build_initiative_evidence.py"
    if not os.path.exists(gen):
        err(f"{gen} is missing — the doc pattern names it as its generator, "
            "and a pattern whose generator is absent is a spec with nothing "
            "to run it")
    else:
        rg = subprocess.run(
            [sys.executable, os.path.abspath(gen),
             "--root", os.path.abspath("examples/fixture-os"), "--topic", "pricing"],
            capture_output=True, text=True, timeout=60)
        if rg.returncode != 0:
            err(f"the doc pattern's generator failed: "
                f"{(rg.stderr or rg.stdout).strip()[:200]}")
        elif "**Rests on**:" not in rg.stdout:
            err("the doc pattern's generator emitted no `Rests on` line. That "
                "line is the whole join: without it the document written from "
                "this brief stands outside the stale-grounding view")

    # --- the 0.12 rules, each checked because each was invisible before.
    dm = SPEC["claim-record.md"]
    if "placement:" not in dm:
        err("reference/data-model.md does not document `placement:` — the "
            "override that a rebuild reads instead of destroying a commitment")
    # An override is only durable if BOTH ends exist: something writes it at
    # the moment the instruction is given, and something reads it before
    # deriving. Shipping one without the other leaves the door open, which is
    # worse than neither because the record looks complete.
    wrote = "placement" in open("skills/corp-os-intake/SKILL.md",
                                encoding="utf-8").read()
    reads = "placement" in open("skills/corp-os-rebuild/SKILL.md",
                                encoding="utf-8").read()
    if wrote != reads:
        err("`placement:` is handled by only one side: "
            f"intake writes it={wrote}, rebuild reads it={reads}. An override "
            "that is written and never read, or read and never written, is "
            "not an override.")

    # The export boundary refusal has to be reachable from the skill that
    # guards it, not merely present as a script nobody calls.
    if "check_citations.py" not in open("skills/corp-os-redact/SKILL.md",
                                        encoding="utf-8").read():
        err("corp-os-redact does not call check_citations.py — the per-claim "
            "redaction it performs was mechanically correct on 836 claims in "
            "a real corpus and the boundary still leaked")

    if "stagger_decay.py" not in open("skills/corp-os-migrate/SKILL.md",
                                      encoding="utf-8").read():
        err("corp-os-migrate does not spread the decay windows — a migrated "
            "OS is then born with an unclearable first sweep")

    # --- docs/skill-map.html is generated, and has to still be current.
    # A skill map states how many skills exist and what each refuses. Committed
    # as a static file it becomes the fifth instance of the defect this repo
    # keeps finding: a fact maintained in a second place that nothing catches
    # when it drifts. So it is generated from the plugin, and this check is the
    # thing that catches it -- the same drift check build_index.py runs on an
    # INDEX. The generator also refuses to run at all if a skill on disk has
    # not been placed in a phase, which is the part a person is needed for.
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "build_skill_map.py"),
             "--check"], capture_output=True, text=True, timeout=60, cwd=ROOT)
        if r.returncode != 0:
            err("skill map: " + (r.stderr or r.stdout).strip()[:300])
    except (subprocess.TimeoutExpired, OSError) as e:
        err(f"could not run build_skill_map.py --check: {e}")

    # --- no private content.
    # The denylist is deliberately NOT in this file: a hardcoded list of real
    # names and companies, committed to a public repo, publishes exactly what
    # it exists to protect. Put one term per line in .validate-denylist at the
    # repo root (gitignored). Absent, the structural fallback still runs.
    terms = []
    dl = os.path.join(ROOT, ".validate-denylist")
    if os.path.exists(dl):
        terms = [ln.strip() for ln in open(dl, encoding="utf-8")
                 if ln.strip() and not ln.startswith("#")]
    else:
        warn("no .validate-denylist at repo root — running the structural "
             "leakage check only")

    private = (re.compile(r"\b(" + "|".join(re.escape(x) for x in terms) + r")\b", re.I)
               if terms else None)
    for dp, dn, fn in os.walk("."):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fn:
            if not f.endswith((".md", ".json", ".py")):
                continue
            fp = os.path.join(dp, f)
            for i, line in enumerate(open(fp, encoding="utf-8", errors="replace"), 1):
                if private and private.search(line):
                    err(f"private identifier leaked: {fp}:{i}")
                # Structural fallback: the worked example is anonymized by
                # construction, so a capitalized multi-word proper noun in it
                # is worth a look even when no denylist is loaded.
                if fp.startswith("./examples/") and re.search(
                        r"\b[A-Z][a-z]+ (?:Inc|LLC|Ltd|Corp)\b", line):
                    warn(f"possible company name in an example: {fp}:{i}")

    global COVERAGE
    COVERAGE = conformance_coverage(set(names))
    return report(len(names))


def conformance_coverage(skill_names):
    """(covered, total, uncovered) from the case file, not from a run report.

    A run report says which skills a particular run exercised; this says which
    skills have a case at all, which is the number that should be moving. They
    have been confused once already.
    """
    path = os.path.join(ROOT, "evals", "conformance-cases.json")
    try:
        d = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None
    cases = d.get("cases") if isinstance(d, dict) else d
    have = {c.get("skill") for c in (cases or [])}
    return len(skill_names & have), len(skill_names), sorted(skill_names - have)


def report(skill_count=0):
    for w in warnings:
        print(f"warn  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(f"\nFAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK — {skill_count} skills, {len(warnings)} warning(s)")
    if COVERAGE:
        n, total, missing = COVERAGE
        print(f"   conformance: {n}/{total} skills have a case"
              + (f" — none for {', '.join(s.replace('corp-os-', '') for s in missing)}"
                 if missing else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
