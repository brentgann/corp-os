#!/usr/bin/env python3
"""Run skills against a real OS and check what they actually did to it.

Everything else in this repo checks that a skill *says* the right thing.
validate.py greps for the pre-flight block; the routing eval measures which
skill a query reaches. Neither has ever watched a skill run.

This does. Each case gets a throwaway copy of examples/fixture-os, one skill,
and a prompt. Afterwards the runner reads the filesystem and asks what the
architecture's cross-cutting rules claim: did the review gate leave a proposal
file behind before anything entered the derived layer? did the index get
updated in the same pass as the write? did the usage-log row get appended? did
anything touch raw/, which is append-only?

Those last two are the ones worth the trouble. "Does usage/log.md get written
in practice" has sat in the open-questions list since 0.2.0 with no way to
answer it, and the entire improvement flywheel depends on the answer.

    python3 evals/run_conformance.py                    # all cases
    python3 evals/run_conformance.py --case intake      # one
    python3 evals/run_conformance.py --keep             # leave the trees for inspection

Each run works only inside its own temp copy of a synthetic fixture, passed as
the single --add-dir. Never point --fixture at a real OS.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "corp-os")
FIXTURE = os.path.join(PLUGIN, "examples", "fixture-os")
CASES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conformance-cases.json")

FRAME = """You are running one skill against one knowledge base, as if a person asked you to.

The skill you are running is at {skill}. Read it and follow it.
The knowledge base it operates on is at {os_root}. That is the OS the skill
refers to; treat it as the person's own folder and work in place. Everything
you read or write for this task stays inside {os_root}.

`${{CLAUDE_PLUGIN_ROOT}}` in the skill resolves to {plugin}.

The person is present at the keyboard for this run. When the skill tells you to
propose something and wait for confirmation, write the proposal exactly as the
skill describes, then take the confirmation as given and carry on — they said
yes. Do not skip the proposal step itself; the proposal is what they are
confirming.

Several skills correctly stop to ask a question before proceeding — which
window to brief on, how to classify an ambiguous piece of material. Ask it,
then answer it yourself with the most reasonable reading, say plainly what you
assumed, and continue to the end of the skill. Do not end your turn waiting for
a reply; there is nobody to send one, and a run that stops there has left the
OS untouched.{answers}

Their request:

{prompt}
"""


def digest(root):
    """path -> sha256, for every file under root. Cheap way to see what moved."""
    out = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root)
            try:
                out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
            except OSError:
                pass
    return out


def check(case, before, after, work, output=""):
    """Score one run against the cross-cutting rules, and say why each matters."""
    added = sorted(set(after) - set(before))
    changed = sorted(k for k in set(after) & set(before) if after[k] != before[k])
    removed = sorted(set(before) - set(after))
    results = []

    def hit(name, ok, why, detail=""):
        results.append({"check": name, "passed": bool(ok), "why": why,
                        "detail": detail})

    # -- raw/ is append-only. The one rule whose violation loses source material.
    # The `processed` flag is the single sanctioned exception (data-model.md):
    # it is bookkeeping about the file, not part of what was said. So a changed
    # raw file passes only if `processed` is the only thing that moved.
    def only_processed_flipped(rel):
        p = os.path.join(work, rel)
        try:
            txt = open(p, encoding="utf-8").read()
        except OSError:
            return False
        return "processed: true" in txt

    touched_raw = [f for f in changed if f.startswith("raw/")
                   and not only_processed_flipped(f)]
    # Deletion under a stated retention obligation is sanctioned (data-model,
    # "Retention"). A case that asks for one declares it; every other case
    # treats a removal as the violation it is.
    gone = [f for f in removed if f.startswith("raw/")]
    if case.get("allow_raw_delete"):
        hit("raw deletion happened under the retention path", bool(gone),
            "the case asked for a deletion under a stated obligation; a run "
            "that talked about it and deleted nothing has not exercised the "
            "sequence at all",
            "nothing was deleted" if not gone else "")
    else:
        touched_raw += gone
    hit("raw stays append-only", not touched_raw,
        "an edited raw file destroys the only thing a rebuild can restore "
        "from; flipping `processed` is the one sanctioned edit, and deletion "
        "only under a declared retention obligation",
        f"touched: {touched_raw}" if touched_raw else "")

    # -- the usage log row. The open question since 0.2.0.
    hit("usage/log.md row appended", "usage/log.md" in changed + added,
        "the friction field is the whole improvement flywheel; a skill that "
        "skips it under pressure makes corp-os-improve blind",
        "")

    # -- the gate leaves a record. Stated this way rather than as "must not
    # write", because these runs are told the person confirms -- so a write is
    # legitimate and a write with no proposal behind it is not. This is the
    # rule as data-model.md actually states it: the proposal is a file, written
    # before anything is presented, and it is what the person confirmed.
    # Which layers the gate covers is the OS's decision, not this file's.
    # Hardcoding it got `connectors` wrong -- it is role: record in both
    # fixtures, data-model.md says record layers are written freely, and
    # pull-broken-connector demanded the write in one assertion and failed it
    # in another. It also silently ignored fixture-register's renamed
    # vocabulary, checking `claims/` against an OS whose derived layer is
    # `open-items/`. config.json is the authority; every skill reads it first
    # and so does this now.
    FALLBACK = ("claims/", "jobs/", "decisions/", "glossary", "company/")
    try:
        cfg = json.load(open(os.path.join(work, "config.json"), encoding="utf-8"))
        derived = [n for n, L in (cfg.get("layers") or {}).items()
                   if isinstance(L, dict) and L.get("role") == "derived"
                   and L.get("enabled") is not False]
        DERIVED = tuple(x for n in derived for x in (f"{n}/", f"{n}.md")) or FALLBACK
    except Exception:                                         # noqa: BLE001
        DERIVED = FALLBACK
    entered = [f for f in added + changed if f.startswith(DERIVED)
               and not f.endswith("INDEX.md")]
    proposed = [f for f in added if f.startswith("proposals/")]
    hit("derived-layer writes have a proposal behind them",
        not entered or bool(proposed),
        "a proposal that lives only in chat dies with the session and leaves "
        "no record of what the gate saw -- the declines especially, which are "
        "the only trace of what someone chose not to know",
        f"wrote {entered} with no proposal file" if entered and not proposed else "")

    for spec in case.get("expect_added", []):
        m = [f for f in added if f.startswith(spec["prefix"])]
        # An optional `contains` narrows by filename rather than by exact path.
        # Asserting a path tests the convention a run happened to follow; when
        # the run's convention turned out to be better than the skill's, the
        # skill changed and the check moved to the name.
        if spec.get("contains"):
            m = [f for f in m if spec["contains"].lower() in os.path.basename(f).lower()]
        if spec.get("exclude_prefix"):
            m = [f for f in m if not f.startswith(spec["exclude_prefix"])]
        need = spec.get("min_count", 1)
        hit(spec["name"], len(m) >= need, spec["why"],
            f"added {len(m)}, needed {need}: {m}" if len(m) < need else "")

    for spec in case.get("expect_changed", []):
        m = [f for f in changed if f.startswith(spec["prefix"])]
        hit(spec["name"], bool(m), spec["why"], f"changed: {m}" if m else "unchanged")

    for spec in case.get("expect_untouched", []):
        m = [f for f in changed + added + removed if f.startswith(spec["prefix"])]
        hit(spec["name"], not m, spec["why"], f"touched: {m}" if m else "")

    # -- every raw file this run added must be findable from INDEX.md.
    # Checking for a chosen keyword tested the slug the run happened to pick;
    # what the scan contract actually requires is that the file is reachable
    # from the index at all, by name. An entry that exists as a file and not in
    # its INDEX is a broken contract, not a minor omission.
    # INDEX.md lists the *unprocessed* queue, not every raw file -- a file the
    # same run went on to process correctly drops off it. So the check is
    # scoped to files still carrying `processed: false`. (The first version of
    # this check ignored that and failed a run that had done everything right;
    # it encoded a wrong idea of what the index holds.)
    # README.md is not an entry -- build_index.py's md_files() excludes it and
    # INDEX.md from every layer, because they describe the folder rather than
    # living in it. The scaffolder writes raw/README.md, so without this the
    # check fails every corp-os-setup run for the sin of documenting the layer.
    new_raw = [f for f in added if f.startswith("raw/") and f.endswith(".md")
               and os.path.basename(f) not in ("README.md", "INDEX.md")]
    if new_raw:
        idx_path = os.path.join(work, "INDEX.md")
        idx = open(idx_path, encoding="utf-8").read() if os.path.exists(idx_path) else ""
        still_queued = []
        for f in new_raw:
            try:
                body = open(os.path.join(work, f), encoding="utf-8").read()
            except OSError:
                continue
            if "processed: true" not in body:
                still_queued.append(f)
        missing = [f for f in still_queued
                   if os.path.splitext(os.path.basename(f))[0] not in idx]
        hit("unprocessed raw files are reachable from INDEX.md", not missing,
            "a file that exists but is missing from the queue is invisible to "
            "every later run's scan, and the person's queue silently "
            "under-reports",
            f"not in the index: {missing}" if missing else "")

    # "Not regenerated" is a different claim from "not written to at all". A
    # record layer legitimately grows -- a rebuild files its own proposal there
    # -- while rewriting or removing what is already in it is the violation.
    # The first version conflated them and failed a correct run.
    for spec in case.get("expect_unmodified", []):
        m = [f for f in changed + removed if f.startswith(spec["prefix"])]
        hit(spec["name"], not m, spec["why"], f"rewritten: {m}" if m else "")

    # For a skill whose deliverable is the answer rather than a file, the
    # answer is the only place a check can look.
    for spec in case.get("expect_output", []):
        ok = spec["needle"].lower() in (output or "").lower()
        hit(spec["name"], ok, spec["why"],
            "" if ok else f"{spec['needle']!r} absent from the answer")
    for spec in case.get("forbid_output", []):
        bad = spec["needle"].lower() in (output or "").lower()
        hit(spec["name"], not bad, spec["why"],
            f"{spec['needle']!r} present" if bad else "")

    # A file must NOT contain something -- the export-boundary check.
    for spec in case.get("file_lacks", []):
        fp = os.path.join(work, spec["file"])
        txt = open(fp, encoding="utf-8").read() if os.path.exists(fp) else None
        if txt is None:
            hit(spec["name"], False, spec["why"], f"{spec['file']} was never written")
        else:
            bad = spec["needle"].lower() in txt.lower()
            hit(spec["name"], not bad, spec["why"],
                f"{spec['needle']!r} survived into {spec['file']}" if bad else "")

    # Every file newly added under a prefix must contain the needle. For a
    # schema whose required FORM is the thing under test -- a job statement is
    # "When ..., I want to ..., so I can ..." -- when the filename cannot be
    # predicted. Asserting the same string against the answer tests narration.
    for spec in case.get("expect_added_contains", []):
        files = [f for f in added if f.startswith(spec["prefix"])
                 and not f.endswith("INDEX.md")]
        bad = [f for f in files
               if spec["needle"].lower() not in
               open(os.path.join(work, f), encoding="utf-8", errors="ignore").read().lower()]
        hit(spec["name"], bool(files) and not bad, spec["why"],
            "nothing was added under that prefix" if not files
            else (f"missing {spec['needle']!r}: {bad}" if bad else ""))

    for spec in case.get("expect_contains", []):
        p = os.path.join(work, spec["file"])
        txt = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
        ok = spec["needle"].lower() in txt.lower()
        hit(spec["name"], ok, spec["why"], "" if ok else f"{spec['needle']!r} absent")

    return results, {"added": added, "changed": changed, "removed": removed}


def run(case, model, timeout, keep, fixture):
    # Eleven releases of measuring pass rates and never once measuring what it
    # costs to ask. "How long does conformance take" had no answer in any of
    # the four run files.
    started = time.time()
    tmp = tempfile.mkdtemp(prefix=f"conf-{case['id']}-")
    work = os.path.join(tmp, "os")
    if case.get("fixture") == "empty":
        # corp-os-setup starts from nothing, so its case has to as well.
        # Everything else here checks what a skill did to an OS; this one
        # checks whether what came out *is* one.
        os.makedirs(work)
    else:
        shutil.copytree(fixture, work)
    before = digest(work)
    skill = os.path.join(PLUGIN, "skills", case["skill"], "SKILL.md")
    ans = case.get("answers")
    prompt = FRAME.format(
        skill=skill, os_root=work, plugin=PLUGIN, prompt=case["prompt"],
        answers=("\n\nIf it helps, the person would say: " + ans) if ans else "")
    try:
        r = subprocess.run(
            # --allowedTools Bash is not a convenience. Without it,
            # `acceptEdits` auto-approves file edits and nothing else, so every
            # `python3 scripts/...` invocation in every skill was answered with
            # "This command requires approval" and never ran. Verified directly:
            # a bare `python3 scripts/build_index.py` inside the workspace was
            # blocked, and adding the plugin to --add-dir did not change it,
            # because the gate is the tool, not the path.
            #
            # For eleven releases this harness was measuring what the model
            # could produce BY HAND in place of a script it was told to run --
            # a log row it wrote itself passes a check that looks for a log row.
            # Everything the record says about a shipped script landing a step
            # was measured through that. See ARCHITECTURE §4.27.
            ["claude", "-p", prompt, "--model", model,
             "--permission-mode", "acceptEdits",
             "--allowedTools", "Bash", "--add-dir", tmp],
            capture_output=True, text=True, timeout=timeout, cwd=tmp)
        err = None if r.returncode == 0 else (r.stderr or r.stdout)[:300]
        transcript = (r.stdout or "")[-8000:]
    except subprocess.TimeoutExpired:
        err, transcript = "timed out", ""
    after = digest(work)
    results, diff = check(case, before, after, work, transcript)
    if keep:
        open(os.path.join(tmp, "transcript.txt"), "w", encoding="utf-8").write(transcript)
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return {"id": case["id"], "skill": case["skill"], "error": err,
            "seconds": round(time.time() - started, 1),
            "results": results, "diff": diff, "workdir": tmp if keep else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-opus-5")
    ap.add_argument("--case", default=None,
                    help="comma-separated substrings; a case runs if any "
                         "matches its id. Plain substrings, not a regex")
    ap.add_argument("--fixture", default=FIXTURE,
                    help="disposable OS to copy per run; never a real one")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--repeats", type=int, default=1,
                    help="runs per case. A close-out step that lands 3 times in "
                         "5 is not a pass and not a failure -- it is a rate, and "
                         "a single run cannot tell those apart")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(CASES),
                                                  "runs", "conformance.json"))
    a = ap.parse_args()

    cases = json.load(open(CASES, encoding="utf-8"))["cases"]
    if a.case:
        wanted = [s.strip() for s in a.case.split(",") if s.strip()]
        cases = [c for c in cases if any(w in c["id"] for w in wanted)]
    if not cases:
        print("no cases matched --case")
        return 1

    print(f"{len(cases)} cases, {a.workers} at a time, model {a.model}\n", flush=True)
    out = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        # A case may name its own fixture. Two shapes ship: the default, and a
        # jobs-off OS with renamed vocabulary and a hand-maintained source
        # layer. Running everything against the shape the model already expects
        # tests the easy half.
        futs = {}
        for c in cases:
            for _ in range(a.repeats):
                fx = (a.fixture if not c.get("fixture")
                      else "" if c["fixture"] == "empty"
                      else os.path.join(PLUGIN, c["fixture"]))
                futs[ex.submit(run, c, a.model, a.timeout, a.keep, fx)] = c
        # A run that could not START is not a run that failed. Every check
        # here reads the filesystem, so a case whose `claude` invocation never
        # executed scores whatever the fixture already contained, and the
        # summary adds those up into a number that looks like a result.
        # Observed: a restricted `claude` shim accepting only
        # `claude -p "<prompt>"` rejected all 25 cases in 0s, and the report
        # came back "83/160 checks passed" with a full per-case breakdown.
        # §4.27 is the same failure a layer down -- a harness reporting
        # confidently on something it never ran.
        for f in as_completed(futs):
            res = f.result()
            out.append(res)
            if res["error"] and "only `claude -p" in str(res["error"]):
                for g in futs:
                    g.cancel()
                print("\nABORTED: this environment's `claude` accepts only "
                      "`claude -p \"<prompt>\"` and rejects the flags every "
                      "case needs\n(--model, --add-dir, --permission-mode). "
                      "Nothing executed.\n\nNo report written: these checks "
                      "read the filesystem, so untouched fixtures would\nhave "
                      "scored as a result. Run this where the full CLI is "
                      "available.", flush=True)
                return 2
            n = sum(1 for x in res["results"] if x["passed"])
            print(f"  {res['id']}: {n}/{len(res['results'])}"
                  f"  {res.get('seconds', 0):.0f}s"
                  + (f"  ERROR {res['error']}" if res["error"] else ""), flush=True)

    # Collapse repeats into a rate per check.
    if a.repeats > 1:
        merged = {}
        for r in out:
            m = merged.setdefault(r["id"], {"id": r["id"], "skill": r["skill"],
                                            "error": r["error"], "runs": 0,
                                            "tally": {}, "why": {},
                                            "diff": r["diff"]})
            m["runs"] += 1
            for x in r["results"]:
                m["tally"][x["check"]] = m["tally"].get(x["check"], 0) + int(x["passed"])
                m["why"][x["check"]] = x["why"]
        out = []
        for m in merged.values():
            m["results"] = [
                {"check": k, "passed": v == m["runs"], "rate": v / m["runs"],
                 "why": m["why"][k],
                 "detail": "" if v == m["runs"] else f"{v}/{m['runs']} runs"}
                for k, v in m["tally"].items()]
            out.append(m)

    out.sort(key=lambda r: r["id"])
    total = sum(len(r["results"]) for r in out)
    passed = sum(1 for r in out for x in r["results"] if x["passed"])

    shapes = sorted({c.get("fixture", "examples/fixture-os") for c in cases}
                    - {"empty"}) or ["an empty directory"]
    L = ["# Conformance", "",
         f"Model `{a.model}` · {len(out)} cases · each against a fresh copy of "
         + ", ".join(f"`{s}`" for s in shapes), "",
         f"**{passed}/{total} checks passed**", ""]
    for r in out:
        n = sum(1 for x in r["results"] if x["passed"])
        L += [f"## `{r['id']}` — {r['skill']} ({n}/{len(r['results'])})", ""]
        if r["error"]:
            L += [f"> run error: {r['error']}", ""]
        for x in r["results"]:
            mark = "PASS" if x["passed"] else (
                f"**{x['rate']:.0%}**" if "rate" in x else "**FAIL**")
            L.append(f"- {mark} — {x['check']}"
                     + (f" · {x['detail']}" if x["detail"] and not x["passed"] else ""))
        d = r["diff"]
        L += ["", f"  <sub>added {len(d['added'])}, changed {len(d['changed'])}, "
                  f"removed {len(d['removed'])}</sub>", ""]
        fails = [x for x in r["results"] if not x["passed"]]
        if fails:
            L += ["  Why these matter:", ""]
            for x in fails:
                L.append(f"  - **{x['check']}** — {x['why']}")
            L.append("")

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"model": a.model, "passed": passed, "total": total, "runs": out},
              open(a.out, "w", encoding="utf-8"), indent=2)
    md = "\n".join(L) + "\n"
    open(os.path.splitext(a.out)[0] + ".md", "w", encoding="utf-8").write(md)
    print("\n" + md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
