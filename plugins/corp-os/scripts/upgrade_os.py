#!/usr/bin/env python3
"""Bring an existing Corp-OS up to date with the installed plugin.

Every OS carries its own copies of the shipped scripts — `corp-os-setup`
puts them there, and sixteen skills call them at the OS path rather than the
plugin path. That is deliberate: an OS should keep working when the plugin is
not loaded. The cost is that updating the plugin updates nothing inside anyone's
OS. 0.10.1 fixed how `build_index.py` counts a single-file layer; every OS
created before it kept the copy that counts wrong, and nothing anywhere would
have said so.

Re-copying four files and stamping a version is bookkeeping — it has to happen
every time, nothing else catches it when it is skipped, so it belongs here
rather than in an instruction. Deciding whether to move someone's registry file
is not bookkeeping, so this script names layout migrations and refuses to
perform them. `corp-os-configure` handles a migration as a migration:
enumerate, plan, confirm.

    python3 upgrade_os.py --root ~/work-os              # report only
    python3 upgrade_os.py --root ~/work-os --apply      # copy and stamp

Dry-run by default, for the same reason `delete_source.py` is: the count is
what makes the decision decidable.
"""

import argparse
import filecmp
import json
import os
import re
import shutil
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(HERE)

# The scripts an OS carries its own copy of. Kept in step with scaffold.py's
# SHIPPED by a validator check -- these two lists drifting apart is exactly the
# defect this script exists to clean up after, and it would be absurd to
# reintroduce it here.
SHIPPED = ("build_index.py", "write_export.py", "log_run.py",
           "delete_source.py", "check_citations.py", "stagger_decay.py",
           "bind_pattern.py", "check_shield.py", "migrate_schema.py",
           "find.py")


def plugin_version():
    """The one place the version is true. Everything else copies from here."""
    p = os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json")
    try:
        return json.load(open(p, encoding="utf-8")).get("version")
    except OSError:
        return None


def entry_headers(path, marker="### "):
    try:
        return sum(1 for ln in open(path, encoding="utf-8")
                   if ln.startswith(marker))
    except OSError:
        return 0


# ---------------------------------------------------------------- migrations
# A migration is detected from what is ON DISK, never from the recorded
# version. An OS that never recorded one -- which is every OS built before
# 0.11.0 -- would otherwise be invisible to this, and those are precisely the
# ones that need it.

def m_dashboards_registry(root, cfg):
    """0.10.1 — the registry moved to a root-level dashboards.md."""
    old = os.path.join(root, "dashboards", "registry.md")
    if not os.path.exists(old) or os.path.exists(os.path.join(root, "dashboards.md")):
        return None
    n = entry_headers(old)
    return {
        "id": "dashboards-registry",
        "since": "0.10.1",
        "covers": os.path.join("dashboards", "registry.md"),
        "what": "`dashboards/registry.md` moves to a root-level `dashboards.md`.",
        "why": (f"`build_index.py` counts a directory-shaped path by file, so this "
                f"registry reports 1 no matter how many dashboards are in it. "
                f"There are {n} here."),
        "how": ("`mv dashboards/registry.md dashboards.md && rmdir dashboards`, "
                "then point `layers.dashboards.path` at `dashboards.md` if "
                "config.json declares that layer."),
    }


def m_path_shape(root, cfg, covered=()):
    """Generic: a directory path over a single file of many entries.

    Skips anything a named migration above already reported. Two entries for
    one file is how a report earns the reputation of crying wolf, and this one
    only gets read when someone is already reluctant to be reading it.
    """
    out = []
    for name, spec in (cfg.get("layers") or {}).items():
        if not spec.get("enabled"):
            continue
        declared = (spec.get("path") or name).rstrip("/")
        if declared.endswith(".md"):
            continue
        d = os.path.join(root, declared)
        if not os.path.isdir(d):
            continue
        files = [f for f in sorted(os.listdir(d)) if f.endswith(".md")
                 and f.upper() != "INDEX.MD"]
        if len(files) != 1:
            continue
        rel = os.path.join(declared, files[0])
        if rel in covered:
            continue
        n = entry_headers(os.path.join(d, files[0]))
        if n > 1:
            out.append({
                "id": f"path-shape:{name}",
                "since": "0.10.1",
                "covers": rel,
                "what": (f"layer `{name}` declares `{declared}/` but holds one "
                         f"file, `{files[0]}`, with {n} entries in it."),
                "why": ("A directory path is counted by file, so this layer "
                        "reports 1. The index has been under-reporting it."),
                "how": (f"Either point `layers.{name}.path` at "
                        f"`{declared}/{files[0]}`, or split the file so each "
                        "entry is its own file. Which one depends on how the "
                        "person actually works in it."),
            })
    return out


# Named migrations run first; the generic shape check runs last and defers to
# anything they already covered.
def m_source_fidelity(root, cfg):
    """0.14.0 — the medium split out of confidence."""
    import glob as _g
    n = 0
    for name, spec in (cfg.get("layers") or {}).items():
        if not spec.get("enabled") or spec.get("role") != "derived":
            continue
        path = (spec.get("path") or name).rstrip("/")
        full = os.path.join(root, path)
        files = ([full] if path.endswith(".md")
                 else _g.glob(os.path.join(full, "*.md")))
        for f in files:
            if os.path.basename(f) in ("README.md", "INDEX.md"):
                continue
            try:
                body = open(f, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            heads = body.count(spec.get("entry_marker", "### "))
            has = body.lower().count("**source fidelity**")
            n += max(0, heads - has)
    if not n:
        return None
    return {
        "id": "source-fidelity",
        "since": "0.14.0",
        "covers": None,
        "what": f"{n} derived entr{'y' if n == 1 else 'ies'} carry no "
                "`Source fidelity`.",
        "why": ("Confidence was carrying three questions at once, so a ceiling "
                "that is elective looked exactly like one that is permanent. "
                "In the corpus that reported it, 599 entries sat one connector "
                "call from a higher confidence and zero had taken it."),
        "how": ("`python3 scripts/migrate_schema.py --migration source_fidelity` "
                "fills what the connector records already answer and leaves "
                "the rest blank. Register each source's `Medium` and "
                "`Verbatim fetch` in connectors.md first — that is what makes "
                "the fill possible, and it is a corp-os-connect conversation."),
    }


def m_alias_provenance(root, cfg):
    """0.14.0 — an assumed merge must not look like a confirmed one."""
    import glob as _g
    spec = None
    for name, sp in (cfg.get("layers") or {}).items():
        if sp.get("enabled") and "person" in name.lower() or name.lower() == "people":
            spec = (name, sp)
            break
    if not spec:
        return None
    name, sp = spec
    path = (sp.get("path") or name).rstrip("/")
    bare = 0
    for f in _g.glob(os.path.join(root, path, "*.md")):
        try:
            body = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        m = re.search(r"^aliases:\s*\[(.*?)\]", body, re.M)
        if m and m.group(1).strip():
            bare += len([x for x in m.group(1).split(",") if x.strip()])
    if not bare:
        return None
    return {
        "id": "alias-provenance",
        "since": "0.14.0",
        "covers": None,
        "what": f"{bare} alias(es) are bare strings, so a merge nobody "
                "confirmed is indistinguishable from one somebody did.",
        "why": ("`aliases` is the field deduplication reads. In one corpus, "
                "three entries from a single quote disagreed about a name "
                "resolution while both renderings were already in `aliases` — "
                "the unconfirmed merge had been promoted into the field that "
                "decides whether two people are one."),
        "how": ("Convert to `{alias, resolved_by, resolved_on}` for the ones "
                "somebody actually confirmed, and leave the rest bare. Bare "
                "still parses and now means unresolved, which is the point — "
                "this is not a migration to complete, it is a distinction to "
                "start making."),
    }


NAMED = (m_dashboards_registry, m_source_fidelity, m_alias_provenance)


def detect_migrations(root, cfg):
    found = []
    for fn in NAMED:
        r = fn(root, cfg)
        if r:
            found.append(r)
    covered = {m["covers"] for m in found if m.get("covers")}
    found.extend(m_path_shape(root, cfg, covered))
    return found


# ------------------------------------------------------------------- scripts

def script_state(root):
    """(missing, drifted, current) — by content, not by mtime.

    mtime says when a file was touched; content says whether it is the one
    that has the fix in it. A copy restored from a backup has a new mtime and
    old behavior.
    """
    missing, drifted, current = [], [], []
    for s in SHIPPED:
        src = os.path.join(HERE, s)
        dst = os.path.join(root, "scripts", s)
        if not os.path.exists(src):
            continue
        if not os.path.exists(dst):
            missing.append(s)
        elif filecmp.cmp(src, dst, shallow=False):
            current.append(s)
        else:
            drifted.append(s)
    return missing, drifted, current


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="the OS folder")
    ap.add_argument("--apply", action="store_true",
                    help="copy the scripts and stamp the version")
    a = ap.parse_args()

    root = os.path.expanduser(a.root)
    if not os.path.exists(os.path.join(root, "meta.json")):
        sys.exit(f"{root} does not look like a Corp-OS (no meta.json). This "
                 "upgrades an existing one; corp-os-setup creates one.")

    cfg_path = os.path.join(root, "config.json")
    cfg = {}
    if os.path.exists(cfg_path):
        try:
            cfg = json.load(open(cfg_path, encoding="utf-8"))
        except ValueError as e:
            sys.exit(f"config.json is not valid JSON ({e}). Fix that first — "
                     "every skill reads it, so nothing else is safe until it "
                     "parses.")

    have = plugin_version()
    was = cfg.get("corpos_version")
    missing, drifted, current = script_state(root)
    migrations = detect_migrations(root, cfg)

    print(f"OS:     {root}")
    print(f"        records version {was or '(none recorded)'}")
    print(f"Plugin: {have or '(unknown)'}")
    print()

    if missing:
        print(f"MISSING — {len(missing)} shipped script(s) the OS does not have:")
        for s in missing:
            print(f"  {s}")
        print("  Skills that call these fail against this OS.")
        print()
    if drifted:
        print(f"STALE — {len(drifted)} script(s) differ from the installed plugin:")
        for s in drifted:
            print(f"  {s}")
        print("  These are shipped bookkeeping, not content: --apply overwrites")
        print("  them. If any was edited on purpose, save that copy first.")
        print()
    if current and not missing and not drifted:
        print(f"Scripts: all {len(current)} current.")
        print()

    if migrations:
        print(f"MIGRATIONS — {len(migrations)} structural change(s) this OS "
              "has not taken:")
        for m in migrations:
            print(f"\n  [{m['since']}] {m['id']}")
            print(f"    {m['what']}")
            print(f"    {m['why']}")
            print(f"    {m['how']}")
        print("\n  This script does not perform these. Moving someone's files")
        print("  is a migration, not bookkeeping — hand it to corp-os-configure,")
        print("  which enumerates the blast radius and asks first.")
        print()

    if not a.apply:
        todo = len(missing) + len(drifted)
        if todo or migrations:
            print(f"Dry run. Re-run with --apply to copy {todo} script(s) and "
                  "stamp the version." if todo else "Dry run. Nothing to copy.")
            if migrations:
                print("Migrations stay for corp-os-configure either way.")
        else:
            print("Nothing to do." if was == have else
                  f"Scripts current; only the recorded version is behind. "
                  f"--apply stamps it to {have}.")
        return 0

    # ------------------------------------------------------------- apply
    copied = []
    for s in missing + drifted:
        os.makedirs(os.path.join(root, "scripts"), exist_ok=True)
        shutil.copy2(os.path.join(HERE, s), os.path.join(root, "scripts", s))
        copied.append(s)

    if have and os.path.exists(cfg_path):
        cfg["corpos_version"] = have
        open(cfg_path, "w", encoding="utf-8").write(
            json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")

    meta_path = os.path.join(root, "meta.json")
    try:
        meta = json.load(open(meta_path, encoding="utf-8"))
    except (OSError, ValueError):
        meta = None
    if meta is not None:
        bits = []
        if copied:
            bits.append(f"{len(copied)} script(s) refreshed")
        if was != have:
            bits.append(f"version {was or 'unrecorded'} -> {have}")
        if migrations:
            bits.append(f"{len(migrations)} migration(s) outstanding")
        meta.setdefault("history", []).append({
            "date": date.today().isoformat(),
            "event": "upgrade: " + (", ".join(bits) if bits else "no change"),
        })
        json.dump(meta, open(meta_path, "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)

    print(f"Copied {len(copied)} script(s)." if copied else "No scripts to copy.")
    if have:
        print(f"Recorded version is now {have}.")
    if copied:
        print("Run `python3 scripts/build_index.py` next — a refreshed counter "
              "may report different numbers than the old one did, and that "
              "difference is the point.")
    if migrations:
        print(f"\n{len(migrations)} migration(s) still outstanding. They are "
              "listed above; corp-os-configure performs them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
