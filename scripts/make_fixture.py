#!/usr/bin/env python3
"""Generate a corp-os large enough that the scan contract does real work.

ARCHITECTURE §7.4 has carried "a fixture large enough that the scan contract
is doing real work rather than being trivially satisfiable at four entries"
as an open question. Every cost defect that scales with corpus size is
invisible below it, which is why two uncapped index sections and a layer
threshold that counts files instead of entries both survived sixteen
releases.

Deterministic (seeded), costs nothing to run, and produces a tree that
build_index.py and corpus_load.py read exactly as they read a real one.

    python3 scripts/make_fixture.py /tmp/big --claims 800 --files 25
    python3 scripts/corpus_load.py /tmp/big --sections
"""
import argparse
import json
import os
import random
import shutil
import sys
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "plugins", "corp-os", "examples", "fixture-os")

TOPICS = ["pricing", "support", "onboarding", "renewals", "integrations",
          "security", "reporting", "billing", "migration", "mobile",
          "permissions", "search", "notifications", "api", "sso", "audit",
          "exports", "imports", "quotas", "latency", "uptime", "roadmap",
          "competition", "pipeline", "churn"]
KINDS = ["fact", "assumption", "decision", "signal"]
CONF = ["needs_review", "corroborated", "confirmed"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dest")
    ap.add_argument("--claims", type=int, default=800)
    ap.add_argument("--files", type=int, default=25)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--stale-pct", type=int, default=35,
                    help="share of sourced claims already past their window")
    a = ap.parse_args()
    rnd = random.Random(a.seed)
    today = date.today()

    if os.path.exists(a.dest):
        shutil.rmtree(a.dest)
    shutil.copytree(BASE, a.dest)
    for f in os.listdir(os.path.join(a.dest, "claims")):
        if f != "INDEX.md":
            os.remove(os.path.join(a.dest, "claims", f))

    topics = (TOPICS * ((a.files // len(TOPICS)) + 1))[:a.files]
    per = [a.claims // a.files] * a.files
    for i in range(a.claims - sum(per)):
        per[i] += 1

    n, raws = 0, []
    for ti, topic in enumerate(topics):
        lines = [f"# {topic.title()}", ""]
        for _ in range(per[ti]):
            n += 1
            cid = f"CL-{n:04d}"
            sourced = rnd.random() > 0.18
            days = rnd.choice([30, 60, 90, 180])
            age = (rnd.randint(days + 1, days + 220) if rnd.randint(1, 100) <= a.stale_pct
                   else rnd.randint(0, max(1, days - 1)))
            ver = today - timedelta(days=age)
            rid = f"raw/{ver.isoformat()}--meeting--{topic}-{n:04d}.md"
            if sourced:
                raws.append((rid, topic, ver, n))
            lines += [
                f"### {cid} — {topic.title()} finding {n}",
                f"- **Statement**: Synthetic claim {n} about {topic}, generated "
                f"to give the scan contract something to carry.",
                f"- **Kind**: {rnd.choice(KINDS)}",
                f"- **Jobs**: job-{rnd.randint(1, 3):03d}",
                f"- **Confidence**: {rnd.choice(CONF)}",
            ]
            if sourced:
                lines += [
                    "- **Source fidelity**: summary",
                    f"- **Source**: {rid}",
                    f'- **Citation**: "Synthetic line {n}." — Person {n % 40}, '
                    f"{ver.isoformat()}",
                    f"- **Decay**: {days}d",
                    f"- **Verified**: {ver.isoformat()}",
                ]
            else:
                lines += ["- **Source**: no source",
                          "- **Confidence reason**: migrated without provenance"]
            lines.append("")
        open(os.path.join(a.dest, "claims", f"{topic}.md"), "w",
             encoding="utf-8").write("\n".join(lines))

    for rid, topic, ver, i in raws:
        p = os.path.join(a.dest, rid)
        open(p, "w", encoding="utf-8").write(
            "---\n"
            f"source: meeting-notes\nperson: Person {i % 40}\n"
            f"date: {ver.isoformat()}\ntype: meeting\n"
            f"jobs: [job-{(i % 3) + 1:03d}]\ntags: [{topic.title()}]\n"
            f"external_id: syn-{i:05d}\nprocessed: true\n---\n\n"
            f"Synthetic source {i} for {topic}.\n")

    # Arguments that rest on a bounded set, some of it stale -- the two
    # cross-cutting sections exist for exactly this and no fixture has ever
    # given them anything to find.
    args_dir = os.path.join(a.dest, "arguments")
    os.makedirs(args_dir, exist_ok=True)
    al = ["# Arguments", ""]
    for k in range(1, 41):
        rests = [f"CL-{rnd.randint(1, n):04d}" for _ in range(rnd.randint(1, 6))]
        al += [f"### AR-{k:04d} — Synthetic argument {k}",
               f"- **Statement**: Conclusion {k}, built across entries.",
               "- **Kind**: argument",
               f"- **Confidence**: {rnd.choice(CONF)}",
               f"- **Rests on**: {', '.join(sorted(set(rests)))}",
               f"- **Timing**: {(today - timedelta(days=rnd.randint(1, 200))).isoformat()}",
               ""]
    open(os.path.join(args_dir, "arguments.md"), "w", encoding="utf-8").write("\n".join(al))

    mp = os.path.join(a.dest, "meta.json")
    try:
        m = json.load(open(mp, encoding="utf-8"))
    except Exception:                                          # noqa: BLE001
        m = {}
    m.setdefault("history", []).append(
        {"date": today.isoformat(),
         "what": f"synthetic fixture: {a.claims} claims across {a.files} files"})
    json.dump(m, open(mp, "w", encoding="utf-8"), indent=2)

    print(f"wrote {a.dest}: {n} claims across {a.files} files, "
          f"{len(raws)} raw files, 40 arguments")
    print(f"next: python3 {os.path.join(a.dest, 'scripts', 'build_index.py')} {a.dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
