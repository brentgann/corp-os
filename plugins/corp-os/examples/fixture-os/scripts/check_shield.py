#!/usr/bin/env python3
"""Prove a built output's screen-share shield is real and not decorative.

The shield hides sensitive content until someone asks for it, because an OS
dashboard gets opened on a shared screen and `bearing` deliberately keeps
sensitive load-bearing material in the scan path. The design rule is that the
markup ships redacted and script *reveals*, never the inverse -- render-visible
then hide-with-JS is visible whenever the script fails, loads late or is
disabled, which is exactly the moment it matters.

That rule is checkable, and checking it is the point. On a real build this test
found **three leaks in the first pass**, in a shield its author believed worked.

    python3 check_shield.py dashboards/board.html --probes usage/probes.txt
    python3 check_shield.py dashboards/board.html --probe "Dana Okafor"

The probe list is the part a person maintains: names, roles, phrases that must
not appear before a deliberate reveal. Keep it in the OS, out of the scan path,
and add to it whenever new sensitive material lands.

What it cannot check, and what still needs doing by hand:

  - Round-trip the toggle outside a browser: hidden by default, reveal
    restores the real markup, re-hide restores the placeholder. Assert on
    elements, not on appearance.
  - Diff every derived aggregation shield-up against shield-down. A count that
    differs in a way the stub count does not explain is a leak, and it is the
    one nobody predicts: results were correctly stubbed and the "who said it"
    panel counted their speakers anyway. The name is the disclosure.
"""

import argparse
import os
import re
import sys

SCRIPT_RE = re.compile(r"<script\b.*?</script\s*>", re.S | re.I)
STYLE_RE = re.compile(r"<style\b.*?</style\s*>", re.S | re.I)
# The parked markup. Both quotings are in the wild, and a shield that parks its
# content in an attribute this misses would read as clean while leaking.
DATA_REAL_RE = re.compile(r"""\sdata-real\s*=\s*(?:"[^"]*"|'[^']*')""", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>")
STORAGE_RE = re.compile(r"\b(?:local|session)Storage\b")


def visible_text(html):
    """What a reader sees with JS off and the parked content removed."""
    t = SCRIPT_RE.sub(" ", html)
    t = STYLE_RE.sub(" ", t)
    t = DATA_REAL_RE.sub(" ", t)
    t = TAG_RE.sub(" ", t)
    t = (t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
          .replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="the built HTML")
    ap.add_argument("--probes", help="file of one probe per line; # comments")
    ap.add_argument("--probe", action="append", default=[],
                    help="a single probe, repeatable")
    a = ap.parse_args()

    if not os.path.exists(a.file):
        sys.exit(f"check_shield.py: {a.file} does not exist")
    html = open(a.file, encoding="utf-8", errors="replace").read()

    probes = list(a.probe)
    if a.probes:
        if not os.path.exists(a.probes):
            sys.exit(f"check_shield.py: no probe list at {a.probes}. The list "
                     "is the part a person maintains; without it this script "
                     "can only check the mechanism, not the content.")
        for ln in open(a.probes, encoding="utf-8"):
            ln = ln.split("#")[0].strip()
            if ln:
                probes.append(ln)

    fails, warns = [], []
    text = visible_text(html)
    low = text.lower()

    # -- 1. the leak test.
    hits = [p for p in probes if p.lower() in low]
    if hits:
        for p in hits:
            i = low.index(p.lower())
            fails.append(f"LEAK: {p!r} is visible with scripts stripped\n"
                         f"      …{text[max(0, i-60):i+len(p)+60].strip()}…")
    elif probes:
        print(f"Leak test: {len(probes)} probe(s), none visible with scripts "
              "and parked markup stripped.")

    # -- 2. the mechanism has to be the right way round.
    parked = len(DATA_REAL_RE.findall(html))
    if not parked:
        if probes:
            warns.append("no `data-real` attributes found. Either this output "
                         "has nothing sensitive, or the shield renders content "
                         "visible and hides it with script — which is visible "
                         "the moment the script does not run.")
    else:
        print(f"Mechanism: {parked} element(s) ship redacted with their real "
              "markup parked.")

    # -- 3. state must not survive a session.
    if STORAGE_RE.search(html):
        fails.append("LEAK: the file references localStorage/sessionStorage. "
                     "A shield that remembers being off is a shield that is "
                     "off when someone shares their screen tomorrow. Forgetting "
                     "to re-hide is a disclosure; one extra click is an "
                     "inconvenience, and those costs are not symmetric.")

    # -- 4. a blur is not a redaction.
    if re.search(r"filter\s*:\s*blur", html, re.I):
        warns.append("a CSS blur is present. Blurred text is still in the DOM: "
                     "selectable, copyable, in a saved page, and plainly "
                     "readable if the stylesheet fails. Replace the content "
                     "rather than obscuring it.")

    # -- 5. a withheld thing should say it is withheld.
    if parked and not re.search(r"sensitive|hidden|withheld", text, re.I):
        warns.append("nothing in the visible text says anything is being "
                     "withheld. A gap that announces itself is safe; a gap "
                     "that does not is a wrong answer.")

    for w in warns:
        print(f"\nwarn  {w}")
    for f in fails:
        print(f"\n{f}")

    if fails:
        print(f"\nFAILED — {len(fails)} problem(s). The shield is not doing "
              "what it claims.")
        return 1
    print("\nShield holds, for what this can check. The toggle round-trip and "
          "the shield-up/shield-down aggregation diff are still by hand.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
