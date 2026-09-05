#!/usr/bin/env python3
"""Measure whether nineteen similar skill descriptions can be told apart.

Every skill in this suite operates on the same object, in the same vocabulary,
for the same person. That is what makes the descriptions collide, and collision
is invisible from reading them -- each one looks clear on its own. This harness
puts the whole roster in front of a model, hands it a query a real person would
type, and records which single skill it picks.

What this measures: whether the descriptions are *discriminable from each
other*. That is the question nineteen near-neighbours raise.

What it does not measure: end-to-end triggering in a live session, where a
skill competes with everything else installed and with the model's own ability
to just do the task. skill-creator's run_eval.py covers that, one skill at a
time. Use this to find which pairs collide; use that to tune a single
description once you know which one to fix.

    python3 evals/run_routing.py --repeats 3
    python3 evals/run_routing.py --repeats 5 --filter decide
    python3 evals/run_routing.py --dry-run          # print the roster and exit
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "plugins", "corp-os", "skills")
SET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "routing-set.json")

PROMPT = """You are choosing which skill to invoke for a user's request.

Here are the skills available to you, each with the description its author wrote:

{roster}

The user says:

<query>
{query}
</query>

Reply with exactly one line: the name of the single skill you would invoke, or
the word `none` if no skill above fits and you would just answer directly.
No explanation, no punctuation, nothing else."""


def load_roster():
    """name -> description, straight from the shipped frontmatter."""
    out = {}
    for d in sorted(os.listdir(SKILLS)):
        p = os.path.join(SKILLS, d, "SKILL.md")
        if not os.path.exists(p):
            continue
        fm = re.match(r"^---\n(.*?)\n---\n", open(p, encoding="utf-8").read(), re.S)
        if not fm:
            continue
        desc = re.search(r"^description:\s*(.+)$", fm.group(1), re.M)
        out[d] = desc.group(1).strip() if desc else ""
    return out


def ask(query, roster_text, model, timeout):
    try:
        r = subprocess.run(
            ["claude", "-p", PROMPT.format(roster=roster_text, query=query),
             "--model", model],
            capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if r.returncode != 0:
        return "ERROR"
    line = (r.stdout or "").strip().splitlines()
    if not line:
        return "EMPTY"
    return line[-1].strip().strip("`.*_ ").lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=3,
                    help="runs per query; routing is stochastic, so 1 is noise")
    ap.add_argument("--model", default="claude-opus-5")
    ap.add_argument("--filter", default=None,
                    help="substring match on a query's `probes` field")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(SET), "results.json"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    roster = load_roster()
    roster_text = "\n".join(f"- {n}: {d}" for n, d in roster.items())
    if a.dry_run:
        print(roster_text)
        print(f"\n{len(roster)} skills")
        return 0

    queries = json.load(open(SET, encoding="utf-8"))["queries"]
    if a.filter:
        queries = [q for q in queries if a.filter in (q.get("probes") or "")]
    if not queries:
        print("no queries matched --filter")
        return 1

    jobs = [(q, i) for q in queries for i in range(a.repeats)]
    print(f"{len(queries)} queries x {a.repeats} repeats = {len(jobs)} calls, "
          f"{a.workers} at a time, model {a.model}\n", flush=True)

    picks = defaultdict(list)
    done = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(ask, q["query"], roster_text, a.model, a.timeout): q
                for q, _ in jobs}
        for f in as_completed(futs):
            q = futs[f]
            picks[q["id"]].append(f.result())
            done += 1
            if done % 10 == 0 or done == len(jobs):
                print(f"  {done}/{len(jobs)}", flush=True)

    # ---- score
    rows, confusion = [], Counter()
    for q in queries:
        got = picks[q["id"]]
        exp = q["expect"]
        hits = sum(1 for g in got if g == exp)
        rows.append({
            "id": q["id"], "query": q["query"], "expect": exp,
            "probes": q.get("probes"), "picks": got,
            "rate": hits / len(got) if got else 0.0,
            "majority": Counter(got).most_common(1)[0][0] if got else None,
        })
        for g in got:
            if g != exp:
                confusion[(exp, g)] += 1

    overall = sum(r["rate"] for r in rows) / len(rows)
    by_probe = defaultdict(list)
    for r in rows:
        if r["probes"]:
            by_probe[r["probes"]].append(r["rate"])

    unstable = [r for r in rows if 0 < r["rate"] < 1]
    failed = [r for r in rows if r["rate"] == 0]

    # ---- report
    L = ["# Routing eval", "",
         f"Model `{a.model}` · {len(queries)} queries × {a.repeats} repeats · "
         f"{len(roster)} skills on the roster", "",
         f"**Overall routing accuracy: {overall:.0%}**", ""]

    L += ["## By collision pair", "",
          "The pairs the audit named as likely to collide, plus the coverage set.", "",
          "| probe | queries | accuracy |", "|---|---|---|"]
    for k in sorted(by_probe, key=lambda x: sum(by_probe[x]) / len(by_probe[x])):
        v = by_probe[k]
        L.append(f"| {k} | {len(v)} | {sum(v)/len(v):.0%} |")

    if confusion:
        L += ["", "## Where it went instead", "",
              "Every miss, as expected → chosen. A pair appearing repeatedly is a "
              "real description collision; a one-off is usually an ambiguous query.",
              "", "| expected | chosen instead | times |", "|---|---|---|"]
        for (e, g), n in confusion.most_common():
            L.append(f"| `{e}` | `{g}` | {n} |")

    if failed:
        L += ["", "## Queries that never routed correctly", ""]
        for r in failed:
            L.append(f"- **{r['id']}** — expected `{r['expect']}`, always got "
                     f"`{r['majority']}`\n  > {r['query'][:180]}")

    if unstable:
        L += ["", "## Unstable", "",
              "Split across repeats. These matter more than they look: a query that "
              "routes correctly two times in three is one a real person hits wrong "
              "a third of the time.", ""]
        for r in sorted(unstable, key=lambda x: x["rate"]):
            L.append(f"- **{r['id']}** — {r['rate']:.0%} to `{r['expect']}`, "
                     f"also picked {sorted(set(p for p in r['picks'] if p != r['expect']))}")

    md = "\n".join(L) + "\n"
    json.dump({"model": a.model, "repeats": a.repeats, "overall": overall,
               "rows": rows,
               "confusion": [{"expected": e, "chosen": g, "count": n}
                             for (e, g), n in confusion.most_common()]},
              open(a.out, "w", encoding="utf-8"), indent=2)
    open(os.path.splitext(a.out)[0] + ".md", "w", encoding="utf-8").write(md)
    print("\n" + md)
    print(f"wrote {a.out} and {os.path.splitext(a.out)[0]}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
