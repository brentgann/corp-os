#!/usr/bin/env python3
"""A fast loop for slash commands.

The conformance harness takes ten minutes because every case runs a whole
skill against a whole OS. Commands do not need that. A command is a thin
prompt file whose entire job is to reach the right skill and hand it the right
scope -- so the question is narrow, and a narrow question can be asked with one
short call instead of a full session.

Each check is a single `claude -p` that shows the command roster and one thing
a person typed, and asks which command fires and what it does first. About
fifteen seconds each, the whole sweep in two minutes, which is the difference
between iterating on wording and waiting on it.

What this does NOT tell you: whether the skill behind the command works. That
is run_conformance.py's job and it is slower for good reasons. This one answers
"does /corp-os-brief with no arguments reach corp-os-brief and scope itself
sensibly", which is the whole surface area a command actually has.

    python3 evals/run_commands.py                  # the full sweep
    python3 evals/run_commands.py --repeats 3      # rates
    python3 evals/run_commands.py --filter noargs
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
COMMANDS = os.path.join(ROOT, "plugins", "corp-os", "commands")
SKILLS = os.path.join(ROOT, "plugins", "corp-os", "skills")
SET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "command-set.json")

PROMPT = """A person is working in a tool where these slash commands are available:

{roster}

They typed:

    {typed}

Here is the full text of the command file that matches what they typed, if one does:

{body}

If they did not type a command at all, decide which one from the roster they
would reach for, and answer with the skill behind it.

All nineteen `corp-os-*` skills are installed and available in this session,
and so is their knowledge base. Do not check; assume they are there. The
question is which one this input reaches, not whether it exists.

Answer in exactly two lines and nothing else:

SKILL: the name of the `corp-os-*` skill this invokes, or `none` if no command
       above matches. It must be one of the corp-os skills or the word `none`;
       other skills may be installed and are not the question here.
FIRST: in under fifteen words, the first thing you would actually do

Do not do the task. Do not explain. Two lines."""


def load_commands():
    out = {}
    if not os.path.isdir(COMMANDS):
        return out
    for f in sorted(os.listdir(COMMANDS)):
        if not f.endswith(".md"):
            continue
        text = open(os.path.join(COMMANDS, f), encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        fm, body = (m.group(1), m.group(2)) if m else ("", text)
        desc = re.search(r"^description:\s*(.+)$", fm, re.M)
        named = re.findall(r"`(corp-os-[a-z-]+)`", body)
        out["/" + f[:-3]] = {
            "description": desc.group(1).strip() if desc else "",
            "body": body.strip(),
            "raw": text,
            # The skill this command hands off to -- the first one it names.
            "skill": named[0] if named else None,
        }
    return out


def ask(typed, roster_text, body, model, timeout):
    try:
        r = subprocess.run(
            ["claude", "-p", PROMPT.format(roster=roster_text, typed=typed,
                                           body=body or "(no command matched)"),
             "--model", model],
            capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", ""
    if r.returncode != 0:
        return "ERROR", ""
    txt = r.stdout or ""
    skill = re.search(r"SKILL:\s*(\S+)", txt)
    first = re.search(r"FIRST:\s*(.+)", txt)
    return ((skill.group(1).strip().strip("`.") .lower() if skill else "UNPARSED"),
            (first.group(1).strip() if first else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-opus-5")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--filter", default=None, help="substring match on `probes`")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(SET), "runs",
                                                  "commands.json"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    cmds = load_commands()
    if not cmds:
        print("no commands found"); return 1
    roster_text = "\n".join(f"- {n}: {c['description']}" for n, c in cmds.items())
    if a.dry_run:
        print(roster_text); print(f"\n{len(cmds)} commands"); return 0

    cases = json.load(open(SET, encoding="utf-8"))["cases"]
    if a.filter:
        cases = [c for c in cases if a.filter in (c.get("probes") or "")]
    if not cases:
        print("no cases matched --filter"); return 1

    jobs = [(c, i) for c in cases for i in range(a.repeats)]
    print(f"{len(cases)} cases x {a.repeats} = {len(jobs)} calls, "
          f"{len(cmds)} commands, model {a.model}\n", flush=True)

    picks, firsts = defaultdict(list), defaultdict(list)
    done = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {}
        for c, _ in jobs:
            body = cmds.get(c.get("command", ""), {}).get("raw", "")
            futs[ex.submit(ask, c["typed"], roster_text, body, a.model,
                           a.timeout)] = c
        for f in as_completed(futs):
            c = futs[f]
            s, first = f.result()
            picks[c["id"]].append(s)
            if first:
                firsts[c["id"]].append(first)
            done += 1
            if done % 5 == 0 or done == len(jobs):
                print(f"  {done}/{len(jobs)}", flush=True)

    rows, misses = [], Counter()
    for c in cases:
        got = picks[c["id"]]
        # A case may accept more than one answer. `/corp-os` handing straight
        # off to the right skill is as correct as naming the guide -- the
        # command file tells it to route rather than explain, so insisting on
        # `corp-os-guide` would be scoring the label, not the behavior.
        # Answering with the command name instead of the skill behind it is a
        # right answer in the wrong currency -- the picker cases chose the
        # correct command every time and scored zero until this existed.
        # Anything that resolves to the expected skill counts.
        ok = {c["expect_skill"], *c.get("also_ok", [])}
        for cname, meta in cmds.items():
            if meta.get("skill") in ok:
                ok.add(cname.lstrip("/"))
                ok.add(cname)
        exp = c["expect_skill"]
        hits = sum(1 for g in got if g in ok)
        rows.append({"id": c["id"], "typed": c["typed"], "command": c.get("command"),
                     "expect": exp, "probes": c.get("probes"), "picks": got,
                     "rate": hits / len(got) if got else 0.0,
                     "firsts": firsts[c["id"]]})
        for g in got:
            if g not in ok:
                misses[(exp, g)] += 1

    overall = sum(r["rate"] for r in rows) / len(rows)
    L = ["# Commands", "",
         f"Model `{a.model}` · {len(cases)} cases × {a.repeats} · "
         f"{len(cmds)} commands", "",
         f"**{overall:.0%} reached the intended skill**", "",
         "## Roster", "", roster_text, ""]
    bad = [r for r in rows if r["rate"] < 1]
    if bad:
        L += ["## Did not land", "", "| case | typed | expected | got |",
              "|---|---|---|---|"]
        for r in sorted(bad, key=lambda x: x["rate"]):
            L.append(f"| {r['id']} | `{r['typed'][:44]}` | `{r['expect']}` | "
                     f"{', '.join('`%s`' % p for p in sorted(set(r['picks'])))} |")
        L.append("")
    L += ["## First action, as reported", "",
          "The line worth reading. A command can reach the right skill and "
          "still open on the wrong move.", ""]
    for r in rows:
        if r["firsts"]:
            L.append(f"- **{r['id']}** — {r['firsts'][0]}")
    md = "\n".join(L) + "\n"
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"model": a.model, "repeats": a.repeats, "overall": overall,
               "rows": rows}, open(a.out, "w", encoding="utf-8"), indent=2)
    open(os.path.splitext(a.out)[0] + ".md", "w", encoding="utf-8").write(md)
    print("\n" + md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
