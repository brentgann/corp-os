#!/usr/bin/env python3
"""What each skill reads from reference/, and whether it pays for it every run.

An unconditional read costs on every invocation of that skill whether or not
the branch needing it fires. A read behind a condition costs only when the
branch does. This ranks the difference so the work order comes from a number
rather than an impression.

The detector is SENTENCE-scoped on purpose. Two earlier versions set the work
order wrong and both failures were the same shape (§4.51):

  line-start   -- scored a read conditional only if the clause OPENED with a
                  conditional word. corp-os-guide trails its condition ("read
                  those if the person is asking how the system is structured")
                  and was ranked worst in the suite while already correct.
  paragraph    -- required every reference-bearing sentence in a paragraph to
                  be gated. corp-os-setup's pre-flight is two sentences, one
                  gated and one not, so its already-conditional jtbd read was
                  counted as unconditional.

A metric built to rank work will rank work that does not exist. Read the skill
before editing it.

    python3 scripts/ref_load.py            # ranked
    python3 scripts/ref_load.py --skill X  # one skill, sentence by sentence
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "corp-os")
FM = re.compile(r"^---\s*\n.*?\n---\s*\n", re.S)
REF = re.compile(r"reference/([a-z0-9-]+\.md)")
# "per the" and "offer to" are gates in this repo's voice: both introduce a
# branch the run may not take.
COND = re.compile(r"\b(if|when|whenever|unless|where|only|should you|for anyone"
                  r"|in the case|per the|offer to|asking how)\b", re.I)


def tok(s):
    return round(len(s) / 4)


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n(?=[-*|#])", text) if s.strip()]


def scan(skill_dir, sizes):
    body = FM.sub("", open(os.path.join(skill_dir, "SKILL.md"),
                           encoding="utf-8").read(), count=1)
    uncond, cond, detail = set(), set(), []
    # A condition governs what FOLLOWS it inside its own block, not what
    # precedes it. That one rule separates the two cases a flat sentence scan
    # gets wrong in opposite directions: corp-os-dashboard's bullet opens
    # "If a pattern needs a layer this OS has not declared" and the read sits
    # in the next sentence (gated); corp-os-setup's pre-flight commands two
    # reads and only then gates a third (the first two are not gated).
    for block in re.split(r"\n\s*\n", body):
        gate = False
        for s in sentences(block):
            if COND.search(s):
                gate = True
            hits = REF.findall(s)
            if not hits:
                continue
            (cond if gate else uncond).update(hits)
            detail.append((gate, hits, " ".join(s.split())[:110]))
    # A file commanded without a gate anywhere IS read every run, even when
    # another sentence also gates it. The reverse subtraction understates:
    # corp-os-setup gates one configuration.md read and commands another in
    # Step 3, which happens on every run.
    cond -= uncond
    return uncond, cond, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill")
    a = ap.parse_args()
    sizes = {os.path.basename(f): tok(open(f, encoding="utf-8").read())
             for f in glob.glob(os.path.join(PLUGIN, "reference", "*.md"))}
    rows = []
    for d in sorted(glob.glob(os.path.join(PLUGIN, "skills", "*"))):
        name = os.path.basename(d)
        if a.skill and a.skill not in name:
            continue
        u, c, detail = scan(d, sizes)
        rows.append((name, sum(sizes.get(x, 0) for x in u),
                     sum(sizes.get(x, 0) for x in c), sorted(u), detail))
    if a.skill:
        for name, un, cn, U, detail in rows:
            print(f"{name}: {un} unconditional, {cn} conditional\n")
            for gated, hits, text in detail:
                print(f"  [{'cond' if gated else 'UNCOND'}] "
                      f"{','.join(h.replace('.md','') for h in hits)}\n     {text}")
        return 0
    rows.sort(key=lambda r: -r[1])
    print(f"{'skill':26}{'uncond':>8}{'cond':>7}  paid every run")
    for name, un, cn, U, _ in rows:
        if un or cn:
            print(f"{name:26}{un:>8}{cn:>7}  "
                  f"{','.join(x.replace('.md','') for x in U)}")
    print(f"\nunconditional {sum(r[1] for r in rows)}   "
          f"conditional {sum(r[2] for r in rows)}   "
          f"zero-unconditional {sum(1 for r in rows if r[1]==0)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
