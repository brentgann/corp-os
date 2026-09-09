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
    WORDNUM = {"three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
               "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
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

    # --- the 0.12 rules, each checked because each was invisible before.
    dm = open("reference/data-model.md", encoding="utf-8").read()
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

    return report(len(names))


def report(skill_count=0):
    for w in warnings:
        print(f"warn  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(f"\nFAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK — {skill_count} skills, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
