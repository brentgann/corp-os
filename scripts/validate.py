#!/usr/bin/env python3
"""Validate the corp-os plugin before packaging.

Checks structure, frontmatter, cross-references, step numbering, and that no
private content has leaked in. Exits non-zero on any error.
"""
import ast
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "corp-os")

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def main():
    os.chdir(PLUGIN)

    # --- manifest
    try:
        manifest = json.load(open(".claude-plugin/plugin.json"))
    except Exception as e:                                    # noqa: BLE001
        err(f"plugin.json unreadable: {e}")
        return report()
    if not re.fullmatch(r"[a-z0-9-]+", manifest.get("name", "")):
        err(f"plugin name not kebab-case: {manifest.get('name')!r}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
        err(f"version not semver: {manifest.get('version')!r}")

    # --- skills
    names = set(os.listdir("skills"))
    for d in sorted(names):
        path = f"skills/{d}/SKILL.md"
        if not os.path.exists(path):
            err(f"{d}: no SKILL.md")
            continue
        text = open(path, encoding="utf-8").read()
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not fm:
            err(f"{d}: no frontmatter")
            continue
        block = fm.group(1)
        name = re.search(r"^name:\s*(\S+)", block, re.M)
        desc = re.search(r"^description:\s*(.+)$", block, re.M)
        if not name or name.group(1) != d:
            err(f"{d}: frontmatter name does not match directory")
        if not desc:
            err(f"{d}: no description")
        elif len(desc.group(1)) < 80:
            warn(f"{d}: description is thin ({len(desc.group(1))} chars) — "
                 "descriptions are the trigger, so they need real phrases")

        words = len(text.split())
        if words > 3000:
            warn(f"{d}: SKILL.md is {words} words — over the 3000 guidance, "
                 "consider moving detail to reference/")

        for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`)]+)", text):
            if not os.path.exists(ref):
                err(f"{d}: broken plugin-root reference -> {ref}")

        steps = [int(x) for x in re.findall(r"^## Step (\d+)", text, re.M)]
        if steps != sorted(steps):
            err(f"{d}: step headings out of order: {steps}")

    # --- cross-references resolve to real skills
    corpus = "".join(
        open(f"skills/{d}/SKILL.md", encoding="utf-8").read() for d in names
    ) + open("README.md", encoding="utf-8").read()
    for ref in sorted(set(re.findall(r"`(corp-os-[a-z-]+|improve-corp-os)`", corpus))):
        if ref not in names:
            err(f"reference to unknown skill: {ref}")

    # --- shipped assets parse
    try:
        ast.parse(open("scripts/build_index.py", encoding="utf-8").read())
    except SyntaxError as e:
        err(f"build_index.py syntax error: {e}")
    for p in ("examples/config-worked-example.json",):
        try:
            json.load(open(p, encoding="utf-8"))
        except Exception as e:                                # noqa: BLE001
            err(f"{p}: {e}")

    # --- no private content
    private = re.compile(
        r"\b(gannos|planhub|arash|arosh|kareem|emilie|mourad|procore|trimble)\b", re.I
    )
    for dp, dn, fn in os.walk("."):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fn:
            if not f.endswith((".md", ".json", ".py")):
                continue
            fp = os.path.join(dp, f)
            for i, line in enumerate(open(fp, encoding="utf-8", errors="replace"), 1):
                if private.search(line):
                    err(f"private identifier leaked: {fp}:{i}")

    return report(len(names))


def report(skill_count=0):
    for w in warnings:
        print(f"warn  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(f"\nFAILED — {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK — {skill_count} skills, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
