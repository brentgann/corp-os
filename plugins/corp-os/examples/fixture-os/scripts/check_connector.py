#!/usr/bin/env python3
"""Check every connector record against the shape it declares.

A registry that looks complete and is not is the specific failure
corp-os-connect exists to prevent, and the field count has grown past what
anyone checks from memory: eight fields for every source, six more for a
listed one, a different one for a queried one. Nothing was verifying it.

Shape-aware on purpose. A queried source needs a query interface and must NOT
carry a cutoff or a selector -- it is scoped per question. A listed one needs
its call pair, and a selector unless it is already personal. Applying one
checklist to both is how a warehouse gets registered as something to walk.

    python3 scripts/check_connector.py --root .

Exits non-zero if anything is missing, so it can gate a first pull.
"""
import argparse
import os
import re
import sys

EVERY = ["Category", "Protocol", "Auth", "Scope", "Feeds", "Serves jobs",
         "Cadence", "Blind spots"]
LISTED = ["Selector", "List call", "Fetch call", "Verbatim fetch", "Limits",
          "Ceiling"]
QUERIED = ["Query interface"]
# A secret in this file is the failure that cannot be undone by editing it:
# connectors.md gets synced, shared and handed to audits.
SECRETISH = re.compile(
    r"(?:token|secret|password|api[_-]?key|bearer)\s*[:=]\s*\S{8,}", re.I)


def blocks(text):
    out, name, buf = [], None, []
    for line in text.split("\n"):
        if line.startswith("### "):
            if name:
                out.append((name, "\n".join(buf)))
            name, buf = line[4:].strip(), []
        elif name:
            buf.append(line)
    if name:
        out.append((name, "\n".join(buf)))
    return out


def field(body, name):
    m = re.search(rf"^[-*]?\s*\*\*{re.escape(name)}\*\*\s*:\s*(.+?)\s*$",
                  body, re.I | re.M)
    return m.group(1).strip() if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    path = os.path.join(os.path.abspath(a.root), "connectors.md")
    if not os.path.exists(path):
        sys.exit(f"no connectors.md in {a.root} — run corp-os-connect first")

    text = open(path, encoding="utf-8").read()
    srcs = blocks(text)
    if not srcs:
        sys.exit("connectors.md has no `### ` source blocks")

    problems = 0
    for name, body in srcs:
        gaps, notes = [], []
        access = (field(body, "Access") or "").lower()
        proto = (field(body, "Protocol") or "").lower()
        queried = access.startswith("query")
        # A third shape, and the one most likely to be mis-flagged: a hallway
        # conversation typed up afterwards has no system to call, nothing to
        # throttle and no slice to select. Holding it to the listed checklist
        # produces six findings about a source that is correctly configured.
        manual = ("manual" in proto or "paste" in proto
                  or access.startswith(("manual", "export")))

        need = list(EVERY)
        if queried:
            need += QUERIED
        elif not manual:
            need += LISTED
        for f in need:
            if not field(body, f):
                gaps.append(f)

        if queried:
            for f in ("Selector", "Cutoff", "Last pull"):
                v = field(body, f)
                if v and v.lower() not in ("n/a", "none", "-"):
                    notes.append(f"`{f}: {v}` — a queried source is scoped per "
                                 "question, not per slice or since a date")
            cad = (field(body, "Cadence") or "").lower()
            if cad and not any(w in cad for w in ("demand", "hoc", "event")):
                notes.append(f"`Cadence: {field(body, 'Cadence')}` — a schedule "
                             "against a warehouse bills for answers to "
                             "questions nobody asked")
        elif manual:
            if (field(body, "Verbatim fetch") or "").lower().startswith("y"):
                notes.append("manual paste with `Verbatim fetch: yes` — "
                             "if it could be fetched back it would not be "
                             "manual, and claims from here can reach "
                             "`confirmed` on a fetch that does not exist")
        else:
            sel = field(body, "Selector")
            if sel and sel.lower().startswith(("n/a", "none")) and \
                    "personal" not in sel.lower() and "my own" not in sel.lower():
                notes.append("`Selector: n/a` without saying the source is "
                             "already personal — for anything shared, no "
                             "selector means the whole instance")

        scope = (field(body, "Scope") or "").lower()
        if scope and "read" not in scope and "n/a" not in scope:
            notes.append(f"`Scope: {field(body, 'Scope')}` — this suite only "
                         "ever reads; a wider token is risk with no use")

        cred = field(body, "Credential") or ""
        if SECRETISH.search(body):
            notes.append("looks like it contains a credential VALUE. "
                         "connectors.md is synced, shared and handed to "
                         "audits — name it by reference and rotate this one")
        elif cred and not re.search(r"env |vault|keychain|connector|oauth|n/a",
                                    cred, re.I):
            notes.append(f"`Credential: {cred}` — name where it lives, not "
                         "what it is")

        if gaps or notes:
            problems += 1
            print(f"\n{name}  "
                  f"[{'queried' if queried else 'manual' if manual else 'listed'}]")
            for g in gaps:
                print(f"  missing   {g}")
            for n in notes:
                print(f"  check     {n}")

    print(f"\n{len(srcs)} source(s), {problems} with something to fix."
          if problems else
          f"\n{len(srcs)} source(s), all complete for their shape.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
