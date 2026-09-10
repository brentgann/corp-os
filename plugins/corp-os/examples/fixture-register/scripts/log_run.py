#!/usr/bin/env python3
"""Close out a skill run: the usage-log row and the meta.json history entry.

Every skill in this suite ends the same two ways -- a row in usage/log.md
carrying the honest friction, and, for anything that changed the OS, a dated
entry in meta.json's history. Both are bookkeeping nothing else will catch if
they are skipped, and both are at the end of a run, which measurement says is
exactly where they get dropped: corp-os-brief wrote its history entry in one
run out of three.

So they leave the model's hands, the same way build_index.py took the index
and write_export.py took redaction's log. One call writes both. It exercises
no judgment -- the caller supplies the words, including the friction, which is
the one field a script could never invent.

    python3 scripts/log_run.py --skill corp-os-brief \\
        --scope "since 2026-08-20" \\
        --friction "no prior brief recorded; had to ask for a window" \\
        --event "weekly brief covering 2026-08-20 to 2026-09-05"

Omit --event for a run that changed nothing (a recall, a brief that found
nothing) and only the log row is written. Omit --friction and it refuses:
"none" is a real answer and an empty one is not, and that field is the entire
input to corp-os-improve.
"""

import argparse
import glob
import time
import json
import re
import os
import sys
from datetime import date

HEADER = ("| date | skill | model | volume | scope | friction |\n"
          "|---|---|---|---|---|---|\n")

# Cost was invisible for sixteen releases: a run that moved forty transcripts
# through the model and one that answered a question left identical rows, so
# corp-os-improve could rank skills by friction and by nothing else. A real
# intake run cost $40 and the log recorded it the same as a $0.40 recall.
#
# What is recorded is what can be MEASURED, not what can be claimed. A model
# cannot observe its own token count, so writing one here would be the exact
# fabrication this suite refuses everywhere else. Bytes written are measurable,
# they are the output half of the bill, and output is priced several times
# input -- so raw/ bytes track the dominant cost closely enough to rank by.


# -- the gate, checked at the one step that never gets skipped.
#
# The review gate is the third invariant and it is a FILE. Three releases tried
# to make it happen by placement -- a rule near the procedure (0.18.7), a
# command instead of a rule (0.20.0), a numbered step inside the list (0.24.0).
# Measured across three runs each, the three skills that write derived material
# went 0/3 -> 2/3, 0/3 -> 1/3, 0/3 -> 1/3. Better, and nowhere near reliable.
#
# The mechanism is visible in the failures: propose.py is TWO commands with a
# human turn between them, and the runs are told up front that the person
# confirms. With consent already in hand the procedure reads as satisfied, so
# steps collapse and the file is never written. The model's model of the step
# is consent; the invariant's is record.
#
# So the check moves to the step that measurement says is 3/3 in every case
# and every skill: this one. A run that put something in a derived layer and
# left no proposal behind gets its log row written -- that invariant is not
# traded for this one -- and then a non-zero exit naming the files and the
# exact command to repair it.
#
# "Modified during this run" is decided against the mtime usage/log.md carried
# BEFORE this call, which is the previous run's stamp. A fresh copy of an OS
# has every file at one mtime, so nothing there reads as new; a file the run
# actually wrote is minutes newer. config.json stands in when there is no log
# yet, and when there is neither the check does not guess.

def _gate_reference(root):
    # The window is "since the last run that closed clean", stored rather than
    # inferred. Inferring it from usage/log.md's mtime worked once and then
    # cleared itself: this call stamps that file, so a second call with the
    # proposal still missing saw nothing new and passed. A check a bare retry
    # defeats is not a check.
    try:
        meta = json.load(open(os.path.join(root, "meta.json"), encoding="utf-8"))
        v = meta.get("gate_closed_at")
        if isinstance(v, (int, float)):
            return float(v)
    except (OSError, ValueError):
        pass
    for rel in ("usage/log.md", "config.json", "meta.json"):
        p = os.path.join(root, rel)
        try:
            return os.path.getmtime(p)
        except OSError:
            continue
    return None


def _write_gate_mark(root, value):
    mp = os.path.join(root, "meta.json")
    try:
        meta = json.load(open(mp, encoding="utf-8"))
    except (OSError, ValueError):
        return
    meta["gate_closed_at"] = round(value, 3)
    try:
        with open(mp, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
            f.write("\n")
    except OSError:
        pass


def _close_gate(root):
    """Advance the window — only ever called when a run closed clean."""
    _write_gate_mark(root, time.time())


def _pin_gate(root, since):
    """Freeze the window on a failed close.

    Without this the fallback reference — usage/log.md's mtime — is refreshed
    by the row this very call wrote, so on an OS that has never closed a run
    cleanly the second attempt saw nothing new and passed. Writing the window
    we actually used makes the failure survive a bare retry on a fresh OS the
    same way it already did on an established one.
    """
    _write_gate_mark(root, since)



def _touched_since(root, cfg, since, role="derived"):
    out = []
    for name, spec in (cfg.get("layers") or {}).items():
        if not spec.get("enabled") or spec.get("role") != role:
            continue
        path = (spec.get("path") or name).rstrip("/")
        full = os.path.join(root, path)
        # A layer is a folder of entries or a single file, and a config that
        # names neither -- `"glossary": {"role": "derived"}` -- is both until
        # something writes. Checking only the folder is how corp-os-glossary
        # stayed at 2/3 while the two skills beside it went to 3/3: the entries
        # go in `glossary.md` at the root, the check globbed `glossary/*.md`,
        # and the gate was silent on the one layer shaped that way.
        cands = ([full] if path.endswith(".md")
                 else glob.glob(os.path.join(full, "*.md")) + [full + ".md"])
        for f in cands:
            if os.path.basename(f) in ("INDEX.md", "README.md"):
                continue
            try:
                if os.path.getmtime(f) > since + 1:
                    out.append(os.path.relpath(f, root))
            except OSError:
                pass
    return sorted(out)



def _changed_outside(root, scope, since):
    """Files changed since `since` that are not under `scope`."""
    scope = scope.strip("/") + "/"
    skip = {"usage/log.md", "meta.json", "INDEX.md"}
    out = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in (".git", "__pycache__", "scripts")]
        for fn in fns:
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, root)
            if rel.startswith(scope) or rel in skip:
                continue
            try:
                if os.path.getmtime(full) > since + 1:
                    out.append(rel)
            except OSError:
                pass
    return sorted(out)



def _layer_paths(cfg):
    for name, spec in (cfg.get("layers") or {}).items():
        if not isinstance(spec, dict) or not spec.get("enabled"):
            continue
        yield name, spec, (spec.get("path") or name).rstrip("/")


def check_shape(root, cfg, since):
    """A layer is a file or a folder, and never both.

    `dashboards` was a directory holding one file for five releases, and that
    shape made the index report 1 however many dashboards were registered.
    The layout fix removed it and the rule went into prose; a run recreated
    the directory in 1 of 3 afterwards. The collision is visible on disk, so
    it does not need to be remembered.

    Only fires on a collision this run created — an OS that already carries
    one has a migration to do, not a run to block.
    """
    out = []
    for name, spec, path in _layer_paths(cfg):
        if path.endswith(".md"):
            other = os.path.join(root, path[:-3])
            kind = "a folder"
        else:
            other = os.path.join(root, path + ".md")
            kind = "a file"
        if not os.path.exists(other):
            continue
        stamps = [os.path.getmtime(other)]
        if os.path.isdir(other):
            stamps += [os.path.getmtime(f)
                       for f in glob.glob(os.path.join(other, "*"))]
        if max(stamps) > since + 1:
            out.append((name, path, os.path.relpath(other, root), kind))
    return out


def check_queue(root, cfg, since):
    """Raw written this run has to be reachable from an index.

    A source file that exists and is in no index is invisible to every later
    run's scan, and the person's queue silently under-reports. `processed`
    material is out of the queue by definition and is not checked.

    Both the root index and the layer's own are consulted: a small OS lists
    raw entries at the root, and one over the file threshold replaces that
    with a pointer to `raw/INDEX.md`. Checking only the root would fail every
    large OS for doing the right thing.
    """
    idx = ""
    for cand in [os.path.join(root, "INDEX.md")]:
        try:
            idx += open(cand, encoding="utf-8").read()
        except OSError:
            pass
    missing = []
    for name, spec, path in _layer_paths(cfg):
        if spec.get("role") != "source" or path.endswith(".md"):
            continue
        sub = os.path.join(root, path, "INDEX.md")
        try:
            layer_idx = idx + open(sub, encoding="utf-8").read()
        except OSError:
            layer_idx = idx
        for f in glob.glob(os.path.join(root, path, "*.md")):
            base = os.path.basename(f)
            if base in ("INDEX.md", "README.md"):
                continue
            try:
                if os.path.getmtime(f) <= since + 1:
                    continue
                if "processed: true" in open(f, encoding="utf-8").read():
                    continue
            except OSError:
                continue
            if os.path.splitext(base)[0] not in layer_idx:
                missing.append(os.path.relpath(f, root))
    return sorted(missing)




# `no source` and its neighbours are sanctioned values (check_citations.py
# carries the same set): an entry that traces to a summary with no retrievable
# original says so, and that is provenance, not the absence of it.
NOT_A_CITATION = {"no source", "no raw file", "none", "n/a", ""}


def check_provenance(root, cfg, since):
    """A derived entry written this run says where it came from.

    Provenance is the second of the five invariants and nothing enforced it
    at close. What that permits is the worst artefact this suite can produce:
    a record that looks like knowledge, reaches INDEX.md, and is read and
    believed by every later run, with nothing behind it anyone can check.

    Deliberately narrow. It asks only whether a `Source` field is PRESENT --
    not whether the source is good, not whether it resolves, not whether the
    grading is right. An entry that says `Source: no source` passes, because
    that is a stated provenance and this is not the skill that judges it.
    Anything stricter would need to fetch, and a check that fetches is a
    check that fails offline.
    """
    bad = []
    for name, spec, path in _layer_paths(cfg):
        if spec.get("role") != "derived":
            continue
        full = os.path.join(root, path)
        cands = ([full] if path.endswith(".md")
                 else glob.glob(os.path.join(full, "*.md")) + [full + ".md"])
        for f in cands:
            if os.path.basename(f) in ("INDEX.md", "README.md"):
                continue
            try:
                if os.path.getmtime(f) <= since + 1:
                    continue
                body = open(f, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if not body.strip():
                continue
            found = re.findall(r"^[-*]?\s*\**Source\**\s*:\s*(.*?)\s*$",
                               body, re.I | re.M)
            if not found:
                bad.append(os.path.relpath(f, root))
    return sorted(bad)


def check_index_banner(root):
    """The layer-declared-without-an-index_line signature, read off the index.

    build_index.py already renders a banner for it and lists that layer's
    entries as bare links. Measured at 2 of 3 in `dashboard-missing-layer`,
    where a run declares a layer to serve a rendering and skips the
    interrogation that would have asked what an entry line says. The banner
    is the machine-visible half of a shape mistake, so there is no reason
    for a person to be the one who notices it.
    """
    try:
        body = open(os.path.join(root, "INDEX.md"), encoding="utf-8").read()
    except OSError:
        return []
    return [ln.strip() for ln in body.split("\n")
            if "Incomplete index" in ln]


def check_gate(root, since):
    """Returns (ungated_files, layer_hint). Empty list means nothing to say."""
    if since is None:
        return [], None
    try:
        cfg = json.load(open(os.path.join(root, "config.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return [], None
    entered = _touched_since(root, cfg, since)
    if not entered:
        return [], None
    proposed = [f for f in glob.glob(os.path.join(root, "proposals", "*.md"))
                if os.path.getmtime(f) > since + 1]
    if proposed:
        return [], None
    hint = entered[0].split("/")[0].replace(".md", "")
    return entered, hint


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True)
    ap.add_argument("--scope", required=True,
                    help="what the run covered, in a few words")
    ap.add_argument("--friction", required=True,
                    help="where it hurt. 'none' is a real answer; blank is not. "
                         "This field is the whole input to corp-os-improve, "
                         "which refuses to propose anything without a count "
                         "behind it")
    ap.add_argument("--event", default=None,
                    help="dated meta.json history entry. Omit only when the "
                         "run changed nothing on disk")
    ap.add_argument("--model", default=None,
                    help="the model this run used. Recorded, never inferred — "
                         "it is how a mechanical pass running on an expensive "
                         "model becomes visible in the log rather than in a bill")
    ap.add_argument("--wrote", nargs="*", default=[],
                    help="files this run created or rewrote, relative to the OS "
                         "root. Their size is measured here rather than "
                         "estimated: bytes written are the output half of the "
                         "cost, and output is the expensive half")
    ap.add_argument("--items", type=int, default=None,
                    help="how many source items the run processed")
    ap.add_argument("--os-root", default=".")
    ap.add_argument("--scope-under", default=None,
                    help="the one directory this skill writes in. Given, a "
                         "run that changed anything outside it fails to close "
                         "— corp-os-improve says it writes only under usage/ "
                         "and wrote a claim in one run of three")
    ap.add_argument("--gate-note", default=None,
                    help="why derived-layer files changed during this run "
                         "without a proposal behind them — a hand edit by the "
                         "person, a migration, a repair. Recorded in the log "
                         "row. Without it, an ungated write fails this call")
    a = ap.parse_args()

    if not a.friction.strip():
        print("ERROR: --friction is empty. Write 'none' if there genuinely was "
              "none — a blank field and an honest 'none' are different data.",
              file=sys.stderr)
        return 1

    today = date.today().isoformat()
    root = a.os_root

    # Read before the row below stamps usage/log.md.
    gate_since = _gate_reference(root)

    # -- usage/log.md
    log = os.path.join(root, "usage", "log.md")
    os.makedirs(os.path.dirname(log), exist_ok=True)
    existing = ""
    if os.path.exists(log):
        existing = open(log, encoding="utf-8").read()
    if "| date | skill | scope |" in existing:
        # A log written before 0.17 has four columns. Widen the old rows rather
        # than starting a second table: corp-os-improve reads the whole file,
        # and two tables under one heading is a parsing problem it should never
        # have to have.
        out = []
        for ln in existing.split("\n"):
            if ln.startswith("| date | skill | scope |"):
                out.append(HEADER.split("\n")[0])
            elif re.match(r"^\|\s*-+\s*\|", ln):
                out.append(HEADER.split("\n")[1])
            elif re.match(r"^\|\s*\d{4}-\d{2}-\d{2}\s*\|", ln):
                c = ln.split("|")
                out.append("|".join(c[:3] + [" - ", " - "] + c[3:]))
            else:
                out.append(ln)
        existing = "\n".join(out)
    if "| date |" not in existing:
        existing = (existing.rstrip() + "\n\n" if existing.strip() else
                    "# Usage log\n\n") + HEADER
    # Volume: measured from disk, so it cannot be wrong in the flattering
    # direction. A run that names no files and no items records "-", which is
    # honest and still distinguishes it from one that moved a megabyte.
    written = 0
    for rel in a.wrote:
        try:
            written += os.path.getsize(os.path.join(root, rel))
        except OSError:
            pass
    bits = []
    if a.items is not None:
        bits.append(f"{a.items} item{'' if a.items == 1 else 's'}")
    if written:
        bits.append(f"{written / 1024:.0f}KB written" if written >= 1024
                    else f"{written}B written")
    volume = " · ".join(bits) or "-"

    friction = a.friction
    if a.gate_note:
        friction = f"{friction} · gate: {a.gate_note}"
    row = (f"| {today} | {a.skill} | {a.model or '-'} | {volume} "
           f"| {a.scope.replace('|', '/')} "
           f"| {friction.replace('|', '/')} |\n")
    with open(log, "w", encoding="utf-8") as f:
        f.write(existing.rstrip("\n") + "\n" + row)

    # -- meta.json history
    wrote_event = False
    meta_path = os.path.join(root, "meta.json")
    if a.event:
        if not os.path.exists(meta_path):
            print(f"ERROR: --event given but {meta_path} does not exist. The "
                  "log row was still written; fix the path and re-run with "
                  "--event alone.", file=sys.stderr)
            return 1
        try:
            meta = json.load(open(meta_path, encoding="utf-8"))
        except ValueError as e:
            print(f"ERROR: {meta_path} is not valid JSON ({e}). The log row was "
                  "written; meta.json was left alone rather than overwritten.",
                  file=sys.stderr)
            return 1
        meta.setdefault("history", []).append({"date": today, "event": a.event})
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
            f.write("\n")
        wrote_event = True

    print(f"logged {a.skill} in usage/log.md"
          + (" and meta.json history" if wrote_event else
             " (no history entry — nothing changed on disk)"))

    # -- everything a close can catch, collected and reported together.
    #
    # These ran in sequence at first, each returning on the first problem it
    # found. That hid the others: a run that tripped the queue check never
    # saw the gate error behind it, fixed the index, and closed on a second
    # call that had already lost the window. One report, one exit, every
    # problem the run actually has.
    problems = []
    if gate_since is not None:
        try:
            _cfg = json.load(open(os.path.join(root, "config.json"),
                                  encoding="utf-8"))
        except (OSError, ValueError):
            _cfg = None

        if a.scope_under:
            stray = _changed_outside(root, a.scope_under, gate_since)
            if stray:
                problems.append(
                    [f"corp-os declares that {a.skill} writes only under "
                     f"{a.scope_under.rstrip('/')}/, and this run changed:",
                     stray,
                     "Those belong to whichever skill owns that layer, with "
                     "its citation and gate\nrules. Undo them and say what "
                     "you found instead — a run that reaches\noutside its "
                     "scope has answered a question nobody asked."])

        if _cfg:
            clash = check_shape(root, _cfg, gate_since)
            if clash:
                problems.append(
                    ["a layer is a file or a folder, never both. This run "
                     "created:",
                     [f"{other}   — `{name}` is declared as {path}, so "
                      f"{kind} of that name is a second, competing copy of it"
                      for name, path, other, kind in clash],
                     "Move what is in it to the declared path and remove the "
                     "duplicate. A registry\nsplit across both shapes "
                     "reports the count of whichever one the index reads."])

            orphans = check_queue(root, _cfg, gate_since)
            if orphans:
                problems.append(
                    ["this run wrote source material that no index reaches:",
                     orphans,
                     "A file in the queue and in no index is invisible to "
                     "every later scan, and\nthe person's queue "
                     "under-reports without ever looking wrong. Recount:\n"
                     f"\n  python3 scripts/build_index.py --root {a.os_root}"])

            unsourced = check_provenance(root, _cfg, gate_since)
            if unsourced:
                problems.append(
                    ["this run wrote derived entries that say where nothing "
                     "came from:",
                     unsourced,
                     "Provenance is the second invariant. An entry with no "
                     "`Source` at all reaches\nINDEX.md and is read and "
                     "believed by every later run with nothing behind it\n"
                     "anyone can check. `Source: no source` is a real answer "
                     "— an entry tracing to\na summary with no retrievable "
                     "original says so, and that is provenance. An\nempty "
                     "one is not.\n\nIf nothing could be established at all, "
                     "the entry is a question rather than a\nrecord, and the "
                     "proposal is where a question belongs."])

            banner = check_index_banner(root)
            if banner:
                problems.append(
                    ["a layer was declared without an `index_line`, and "
                     "INDEX.md says so:",
                     banner,
                     "build_index.py renders that banner and lists the "
                     "layer's entries as bare\nlinks. It is the signature "
                     "of a layer declared without the interrogation\nthat "
                     "catches shape mistakes. corp-os-configure carries it; "
                     "the worked\ndeclarations are in "
                     "reference/configuration.md."])

        ungated, hint = check_gate(root, gate_since)
        if ungated and not a.gate_note:
            problems.append(
                ["this run wrote derived-layer material and left no proposal "
                 "behind it:",
                 ungated,
                 "The gate is a file, not a conversation — the conversation "
                 "ends and the file\nis what is left, the declines above "
                 "all. Write it now, with what was\nactually proposed and "
                 "what was held back:\n"
                 f"\n  python3 scripts/propose.py --root {a.os_root} "
                 f"--layer {hint} --slug <batch> \\\n    --headline "
                 "\"<the one thing here that matters>\" \\\n    --item "
                 "\"<create|enrich|decline> · <id> · <what>\" \\\n    "
                 "--not-proposing \"<what was held back, and why>\"\n"
                 f"\n  python3 scripts/propose.py --root {a.os_root} "
                 "--record <the file it wrote> \\\n    --outcome "
                 "\"<item>: confirmed\"\n"
                 "\nIf those files were not this run's doing — a hand edit, "
                 "a migration, a\nrepair — say so and the run closes clean:"
                 "  --gate-note \"<why>\""])

    if problems:
        n = len(problems)
        print(f"\nERROR: this run cannot close — {n} thing"
              f"{'' if n == 1 else 's'} to put right.", file=sys.stderr)
        for i, (headline, items, remedy) in enumerate(problems, 1):
            print(f"\n[{i}/{n}] {headline}\n", file=sys.stderr)
            for f in items[:8]:
                print(f"  {f}", file=sys.stderr)
            if len(items) > 8:
                print(f"  … and {len(items) - 8} more", file=sys.stderr)
            print(f"\n{remedy}", file=sys.stderr)
        _pin_gate(root, gate_since)
        return 2


    _close_gate(root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
