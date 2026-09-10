#!/usr/bin/env python3
"""Resolve a pattern's requirements against an OS, or say exactly what is missing.

A pattern is a portable spec for producing an output. Portable is the hard
word: an operator renames their vocabulary, so a pattern that says `claims/`
binds in exactly one OS -- the one it was written in -- and fails everywhere
else by rendering an empty panel. Nothing detects that, because an empty panel
looks like a state rather than a defect.

So a requirement names the **role** a layer plays and the **fields** the
pattern reads, and this resolves them against the receiving OS's config. It
either binds, or it names the missing role and field in the same breath. That
is the whole difference between a pattern being shareable and being shareable
and honest.

    python3 bind_pattern.py --root ~/work-os --pattern patterns/x.md
    python3 bind_pattern.py --root ~/work-os --all
    python3 bind_pattern.py --root ~/work-os --all --strict   # exit 1 on a refusal

`--strict` is what a build calls. Plain reporting is what a person calls when
they are deciding whether to adopt a pack.
"""

import argparse
import glob
import json
import os
import re
import sys

# Only the keys this script acts on. A pattern may carry others -- the prose
# below the frontmatter is for whoever builds the thing -- but an unknown key
# in the machine-read half is worth saying out loud rather than ignoring,
# because a misspelled `requires` binds vacuously and reports success.
KNOWN = {"name", "kind", "pack", "requires", "produces", "target", "shield",
         "generator", "note"}
KINDS = {"dashboard", "export", "deck", "doc", "brief"}
TARGETS = {"local", "artifact", "redacted-artifact"}


def die(msg):
    sys.exit(f"bind_pattern.py: {msg}")


def parse_pattern(path):
    """Frontmatter only, and deliberately a small hand parser.

    The shape is fixed and shallow -- scalars plus one list of two-or-three-key
    mappings -- so a dependency to read it would be the only dependency in the
    suite. If the shape ever needs to grow past this, that is the signal the
    shape grew too far.
    """
    text = open(path, encoding="utf-8", errors="replace").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        die(f"{path} has no frontmatter — a pattern's machine-read half is "
            "what makes it bindable")
    out, reqs, cur = {}, [], None
    for raw in m.group(1).split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if indent == 0 and line.endswith(":") and line[:-1] == "requires":
            cur = "requires"
            continue
        if indent == 0 and ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
            cur = None
            continue
        if cur == "requires":
            if line.startswith("- "):
                reqs.append({})
                line = line[2:].strip()
            if not reqs:
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                v = v.strip()
                if v.startswith("[") and v.endswith("]"):
                    v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
                elif v.lower() in ("true", "false"):
                    v = v.lower() == "true"
                reqs[-1][k.strip()] = v
    out["requires"] = reqs
    unknown = sorted(set(out) - KNOWN)
    return out, unknown


def load_config(root):
    p = os.path.join(root, "config.json")
    try:
        return json.load(open(p, encoding="utf-8"))
    except OSError:
        die(f"{root} has no config.json — there is nothing to bind against")
    except ValueError as e:
        die(f"{root}/config.json is not valid JSON ({e})")


def schema_fields(spec):
    """entry_schema is a list in some OSes and a dict in others. Both are in
    the wild, both are legitimate, and a binder that understands only one of
    them refuses correct patterns."""
    es = spec.get("entry_schema")
    if isinstance(es, dict):
        return {k.lower() for k in es}
    if isinstance(es, list):
        return {str(x).lower() for x in es}
    return None                      # declared nothing; not the same as empty


def spec_label(spec):
    """A layer may name what it is, when its directory name does not."""
    return spec.get("label") or spec.get("kind") or ""


def resolve(req, cfg):
    """Find an enabled layer playing this role and carrying these fields."""
    want_role = (req.get("role") or "").strip()
    want = [f.lower() for f in (req.get("fields") or [])]
    label = (req.get("label") or "").strip().lower()

    candidates = []
    for name, spec in (cfg.get("layers") or {}).items():
        if not spec.get("enabled") or spec.get("role") != want_role:
            continue
        candidates.append((name, spec))
    if not candidates:
        return None, f"no enabled layer has role `{want_role}`"

    # A label disambiguates when several layers share a role, which is the
    # common case for `derived`. It is NOT a soft hint: if it matches nothing,
    # that is a miss, and falling back to every candidate is how a `person`
    # requirement silently binds to the jobs layer and reports success. A false
    # bind is worse than a refusal, because a refusal gets read.
    if label:
        candidates = [c for c in candidates
                      if label in c[0].lower()
                      or label in str(spec_label(c[1])).lower()]
        if not candidates:
            return None, (f"no enabled layer with role `{want_role}` looks "
                          f"like `{label}`")

    unchecked = []
    for name, spec in candidates:
        fields = schema_fields(spec)
        if fields is None:
            unchecked.append(name)
            continue
        missing = [f for f in want if f not in fields]
        if not missing:
            return name, None
    if unchecked:
        # Weaker than a real bind, and it says so. Most layers in the wild
        # declare no entry_schema, and refusing them all would make the whole
        # mechanism unusable on real OSes -- but calling it a clean bind would
        # be a lie about how much was actually checked.
        return unchecked[0], (f"`{unchecked[0]}` declares no entry_schema, so "
                              f"{', '.join(want) or 'its fields'} could not be "
                              "verified")
    names = ", ".join(n for n, _ in candidates)
    return None, (f"layer(s) with role `{want_role}` ({names}) do not carry "
                  f"{', '.join(want)}")


def bind(root, path, cfg):
    pat, unknown = parse_pattern(path)
    name = pat.get("name") or os.path.basename(path)[:-3]
    result = {"name": name, "path": path, "bound": [], "dropped": [],
              "refused": [], "warnings": []}

    for k in unknown:
        result["warnings"].append(f"unknown frontmatter key `{k}` — it is "
                                  "being ignored, which is worth checking if "
                                  "you expected it to do something")
    if pat.get("kind") and pat["kind"] not in KINDS:
        result["warnings"].append(f"kind `{pat['kind']}` is not one of "
                                  f"{', '.join(sorted(KINDS))}")
    if pat.get("target") and pat["target"] not in TARGETS:
        result["warnings"].append(f"target `{pat['target']}` is not one of "
                                  f"{', '.join(sorted(TARGETS))}")
    gen = pat.get("generator")
    if gen and not os.path.exists(os.path.join(root, gen)):
        result["warnings"].append(f"generator `{gen}` is not in this OS — "
                                  "adopt the pack's scripts/ as well as its "
                                  "patterns, or the pattern is a spec with "
                                  "nothing to run it")
    if not pat["requires"]:
        result["warnings"].append("declares no requirements, so it binds "
                                  "against anything — including an OS that "
                                  "cannot render it")

    for req in pat["requires"]:
        layer, why = resolve(req, cfg)
        desc = (f"role `{req.get('role')}`"
                + (f" carrying {', '.join(req.get('fields') or [])}"
                   if req.get("fields") else ""))
        if layer and not why:
            result["bound"].append((desc, layer))
        elif layer and why:
            result["bound"].append((desc, layer))
            result["warnings"].append(why)
        elif req.get("optional"):
            result["dropped"].append((desc, why))
        else:
            result["refused"].append((desc, why))
    return result


def report(r):
    head = ("REFUSED" if r["refused"]
            else "BOUND, with drops" if r["dropped"] else "BOUND")
    print(f"\n{head} — {r['name']}")
    for desc, layer in r["bound"]:
        print(f"  ok       {desc}  ->  {layer}")
    for desc, why in r["dropped"]:
        print(f"  dropped  {desc}\n           {why}")
        print("           The panel it feeds is omitted and said out loud. "
              "An empty panel would be a bug.")
    for desc, why in r["refused"]:
        print(f"  MISSING  {desc}\n           {why}")
    for w in r["warnings"]:
        print(f"  warn     {w}")
    if r["refused"]:
        print("  Declare the missing layer through corp-os-configure, or take "
              "the pack without this pattern. Both are answers; rendering it "
              "anyway is not.")




def _registry_rows(root, cfg):
    """Rows in the dashboard registry, however this OS spells it."""
    spec = (cfg.get("layers") or {}).get("dashboards") or {}
    path = (spec.get("path") or "dashboards.md").rstrip("/")
    full = os.path.join(root, path)
    if os.path.isdir(full):
        for f in sorted(glob.glob(os.path.join(full, "*.md"))):
            if os.path.basename(f) not in ("README.md", "INDEX.md"):
                yield f
        return
    try:
        body = open(full, encoding="utf-8").read()
    except OSError:
        return
    # One dashboard is a heading with several bullets under it, so counting
    # bullets says "two" for an OS that has one. Headings first, table rows
    # only if the registry is written that way instead.
    heads = [ln for ln in body.split("\n") if re.match(r"^#{2,4}\s+\S", ln)]
    if heads:
        for ln in heads:
            yield ln
        return
    for ln in body.split("\n"):
        if re.match(r"^\s*\|", ln) and "---" not in ln \
                and not re.match(r"^\s*\|\s*(name|dashboard)\s*\|", ln, re.I):
            yield ln


def want(root, cfg, phrase):
    """Is there an adopted pattern for what was asked for?

    Measured over five runs, `dashboard-missing-layer` built the view three
    times from layers that happened to exist and mentioned the gap only in
    the answer, where it died with the session. Nothing on disk was wrong
    afterwards, which is why no check caught it and why two wording passes
    did not move it -- the second measured 0/2 and was reverted.

    The branch it takes is real and it is already in the skill as prose: "if
    the OS has no pattern for what they want, that is corp-os-pattern's job."
    Here it is a command with an exit code instead. Matching is deliberately
    loose and deliberately not clever: a shared word between the request and
    an adopted pattern's name or declared `kind` is enough to offer it, and
    the decision stays with whoever is reading.
    """
    spec = (cfg.get("layers") or {}).get("patterns") or {}
    sub = (spec.get("path") or "patterns").rstrip("/")
    paths = [p for p in sorted(glob.glob(os.path.join(root, sub, "*.md")))
             if os.path.basename(p) not in ("README.md", "INDEX.md")]

    # The hub is the one view that is this skill's own rather than an adopted
    # pattern: it renders the registry, not a layer, so there is nothing for
    # it to be missing. Refusing it would be this check inventing the exact
    # failure it exists to stop. Both conditions are required -- the wording,
    # and the two registered dashboards the hub is gated on anyway, so a
    # single-dashboard OS asking for "one page" still gets the normal answer.
    HUB = ("one page", "start from", "hub", "home page", "landing",
           "every morning", "right link", "all of them", "index page")
    if sum(1 for ln in _registry_rows(root, cfg)) >= 2 \
            and any(h in phrase.lower() for h in HUB):
        print("The hub is this skill's own view, built from the registry "
              "rather than from a\nlayer, so it needs no adopted pattern. "
              "Build it thin and thicken it later.")
        return 0

    words = {w for w in re.split(r"[^a-z0-9]+", phrase.lower()) if len(w) > 3}
    hits = []
    for p in paths:
        try:
            meta = parse_pattern(p)[0]
        except SystemExit:
            continue
        name = str(meta.get("name") or os.path.basename(p)[:-3]).lower()
        hay = set(re.split(r"[^a-z0-9]+", name)) | {str(meta.get("kind") or "")}
        if words & hay:
            hits.append((p, meta))

    if hits:
        print(f"{len(hits)} adopted pattern(s) match \"{phrase}\":\n")
        for p, meta in hits:
            print(f"  {os.path.relpath(p, root)}   {meta.get('name') or ''}")
        print("\nBind one before building:\n\n  python3 scripts/"
              f"bind_pattern.py --root {root} --pattern "
              f"{os.path.relpath(hits[0][0], root)}")
        return 0

    have = ", ".join(os.path.basename(p)[:-3] for p in paths) or "none"
    print(f"\nREFUSED: this OS has no adopted pattern for \"{phrase}\".",
          file=sys.stderr)
    print(f"It carries: {have}\n", file=sys.stderr)
    print("Building it by hand here is the failure this refusal exists for. "
          "A view rendered\nfrom whichever layers happened to exist, with "
          "the gap named only in the answer,\nleaves nothing behind: the "
          "session ends and so does the finding.\n", file=sys.stderr)
    print("Two answers, and no third:\n", file=sys.stderr)
    print("  1. Author the pattern — corp-os-pattern, so the second person "
          "does not start\n     from nothing.\n", file=sys.stderr)
    print("  2. Record the gap where it survives, then build what the OS "
          "can actually\n     support:\n", file=sys.stderr)
    print(f"     python3 scripts/propose.py --root {root} --layer patterns "
          "--slug <slug> \\\n       --headline \"<what they asked for, and "
          "what this OS would need>\" \\\n       --item \"<declare|author"
          "|decline> · <id> · <what>\" \\\n       --not-proposing \"<the "
          "panels being dropped, and why>\"\n", file=sys.stderr)
    return 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="the OS root")
    ap.add_argument("--pattern", help="one pattern file")
    ap.add_argument("--want",
                    help="what the person asked for, in their words. Finds "
                         "the adopted pattern that serves it, or refuses. A "
                         "view this OS has no pattern for is not a view to "
                         "build by hand")
    ap.add_argument("--all", action="store_true",
                    help="every pattern in the OS's patterns/ layer")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any pattern is refused")
    a = ap.parse_args()

    root = os.path.expanduser(a.root)
    cfg = load_config(root)

    if a.want:
        return want(root, cfg, a.want)

    if a.pattern:
        paths = [a.pattern if os.path.isabs(a.pattern)
                 else os.path.join(root, a.pattern)]
    elif a.all:
        spec = (cfg.get("layers") or {}).get("patterns") or {}
        sub = (spec.get("path") or "patterns").rstrip("/")
        paths = sorted(glob.glob(os.path.join(root, sub, "*.md")))
        paths = [p for p in paths
                 if os.path.basename(p) not in ("README.md", "INDEX.md")]
        if not paths:
            print(f"No patterns in {sub}/. Nothing to bind.")
            return 0
    else:
        die("pass --pattern <file> or --all")

    results = [bind(root, p, cfg) for p in paths]
    for r in results:
        report(r)

    refused = [r for r in results if r["refused"]]
    print(f"\n{len(results)} pattern(s): {len(results) - len(refused)} bound, "
          f"{len(refused)} refused.")
    return 1 if (a.strict and refused) else 0


if __name__ == "__main__":
    sys.exit(main())
