#!/usr/bin/env python3
"""
Deterministic INDEX.md regenerator and drift checker for a corp-os.

Recounts what is actually on disk, rewrites INDEX.md's listings and counts to
match, and reports any drift it corrected.

Config-driven: reads config.json for which layers exist, what they are called,
each layer's index_line template, and what is excluded from the scan path. A
custom layer with an index_line renders exactly like a shipped one. Falls back
to the shipped defaults when there is no config.

It does NOT read raw/ content, does NOT retag anything, and does NOT touch the
derived layer's substance. Bookkeeping, not judgment. Safe to run after any
manual edit; a full re-derivation is corp-os-rebuild's job, not this script's.

Usage:
    python3 scripts/build_index.py [os_root] [--check]

    --check   report drift and exit non-zero if any; write nothing.
"""

import glob
import json
import os
import re
import sys
from datetime import date, timedelta

FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def frontmatter(path):
    """Parse flat scalar keys out of a file's YAML frontmatter. Lists -> []."""
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return {}
    m = FM.match(text)
    if not m:
        return {}
    out, key = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^\s*-\s+", line) and key:
            out.setdefault(key + "__list", []).append(
                line.strip().lstrip("-").strip().strip("\"'")
            )
            continue
        m2 = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m2:
            key, val = m2.group(1), m2.group(2).strip().strip("\"'")
            if val:
                out[key] = val
    return out


# Only layers with a declared index_line are enabled here. A layer that is
# enabled without one degrades the scan contract silently, so people/ and
# topics/ are no longer shipped defaults -- an OS that wants either declares it
# in config.json with its own entry_schema and index_line. See
# reference/configuration.md, "No layer is enabled without a schema".
DEFAULT_LAYERS = {
    "raw":       {"enabled": True, "role": "source"},
    "jobs":      {"enabled": True, "role": "derived",
                  "index_line": "{id} — {statement}"},
    "claims":    {"enabled": True, "role": "derived"},
    "company":   {"enabled": False, "role": "derived",
                  "index_line": "{company} — {relationship}"},
    "proposals": {"enabled": True, "role": "record"},
    # Path is the file, not a directory. The registry is one file holding many
    # entries, and the counting strategy below branches on that shape -- see
    # the path/shape warning in survey().
    "dashboards": {"enabled": True, "role": "record", "path": "dashboards.md"},
}


def load_config(root):
    """config.json is the authority; shipped defaults fill the gaps."""
    path = os.path.join(root, "config.json")
    cfg = {}
    if os.path.exists(path):
        try:
            cfg = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"WARNING: config.json unreadable ({e}) — using defaults.")
            cfg = {}
    layers = dict(DEFAULT_LAYERS)
    for name, spec in (cfg.get("layers") or {}).items():
        merged = dict(layers.get(name, {}))
        merged.update(spec or {})
        layers[name] = merged
    cfg["layers"] = layers
    return cfg


def _plural(word):
    """Enough pluralization for a heading. Not a linguistics engine."""
    if word.endswith("y") and not word.endswith(("ay", "ey", "iy", "oy", "uy")):
        return word[:-1] + "ies"
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    return word + "s"


def _lbl(name, layers, cfg=None):
    """A layer's display name, in the person's words.

    Order: the layer's own `label`, then the vocabulary rename for the term
    this layer holds, then the key. The vocabulary step is the one that
    matters -- an OS that renamed `claim` to `entry` was still getting a
    heading that said "Claims", which is the plugin talking over the person in
    the one file every skill reads first.
    """
    spec = (layers.get(name) or {})
    if spec.get("label"):
        return spec["label"]
    vocab = ((cfg or {}).get("vocabulary") or {})
    # config.vocabulary keys are singular terms ("claim"), layers are plural
    # concepts ("claims"); match either spelling.
    for key in (name, name[:-1] if name.endswith("s") else name):
        if vocab.get(key):
            return _plural(str(vocab[key])).replace("_", " ").title()
    return name.replace("_", " ").title()


def _slug(s):
    """The filename an entry named `s` would have. Must match how entries are
    actually named for the derivable-path check below to fire at all."""
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")


def render_line(template, fm, fallback):
    """Fill an index_line template from frontmatter. Missing keys degrade to
    the literal placeholder being dropped, never to a crash."""
    if not template:
        return fallback
    out = template
    for key, val in fm.items():
        out = out.replace("{" + key + "}", str(val))
    out = re.sub(r"\s*[-—·|]?\s*\{[a-zA-Z_][\w-]*\}", "", out)
    return out.strip(" -—·|") or fallback


def md_files(root, sub):
    d = os.path.join(root, sub)
    if not os.path.isdir(d):
        return []
    return sorted(
        f for f in glob.glob(os.path.join(d, "*.md"))
        if os.path.basename(f) not in ("README.md", "INDEX.md")
    )


def count_headers(path, marker="### "):
    """Count entries in a file. `marker` is per-layer configurable because
    layers legitimately differ: heading-per-entry ("### "), list-per-entry
    ("- **"), or bold-term-per-entry ("**"). Assuming one shape silently
    reports zero for the others."""
    if not os.path.exists(path):
        return 0
    return sum(
        1 for line in open(path, encoding="utf-8", errors="replace")
        if line.startswith(marker)
    )


def survey(root, cfg):
    """Everything on disk, for every enabled layer including custom ones."""
    s = {}
    s["_single"] = {}
    for name, spec in cfg["layers"].items():
        if not spec.get("enabled", False):
            continue
        path = (spec.get("path") or name).rstrip("/")
        if path.endswith(".md"):
            # A whole layer living in one file (gaps.md, themes.md). Count its
            # entry headers, and its group headers if it declares a grouping.
            full = os.path.join(root, path)
            marker = spec.get("entry_marker", "### ")
            groups = {}
            if os.path.exists(full):
                for line in open(full, encoding="utf-8", errors="replace"):
                    m = re.match(r"^## (.+?)(?:\s*\((\d+)\))?\s*$", line)
                    if m:
                        groups[m.group(1).strip()] = 0
                        cur = m.group(1).strip()
                    elif line.startswith(marker) and groups:
                        groups[cur] = groups.get(cur, 0) + 1
            s["_single"][name] = {
                "path": path,
                "entries": count_headers(full, marker),
                "groups": groups,
                "in_scan": spec.get("in_scan_path", True),
            }
            continue
        # A directory-shaped path holding one grouped file is the mismatch that
        # shipped for five releases: `dashboards/registry.md` counted files (1)
        # where it meant to count entry headers (3), and stayed silent because
        # both readings agree while there is only one entry.
        #
        # The packet that found it argued against a generic check, on the
        # grounds that fixing the layout removes the problem more cheaply than
        # a heuristic needing its own maintenance. Fair for `dashboards`, and
        # the layout is fixed. But `corp-os-configure` Step 3 walks people
        # through declaring custom layers with their own paths, so the class
        # recurs on shapes no layout fix reaches. The condition here is exact
        # rather than heuristic -- one .md in the directory, and it carries
        # entry headers -- and it warns rather than fails, which is the right
        # weight for "this is probably not what you meant".
        entries = md_files(root, path)
        if len(entries) == 1 and count_headers(entries[0]) > 1:
            print(f"WARNING: layer '{name}' declares a directory path "
                  f"('{spec.get('path') or name}') but holds one file with "
                  f"{count_headers(entries[0])} entry headers. It is being "
                  "counted as 1. If it is really one file of many entries, "
                  f"point its path at the file itself.")
        s[name] = entries
    s.setdefault("raw", md_files(root, "raw"))
    s.setdefault("claims", [])
    s["claim_entries"] = sum(count_headers(f) for f in s.get("claims", []))
    gspec = cfg["layers"].get("glossary") or {}
    s["glossary_terms"] = count_headers(
        os.path.join(root, gspec.get("path", "glossary.md")),
        gspec.get("entry_marker", "### "))
    s["unprocessed"] = [
        f for f in s["raw"]
        if str(frontmatter(f).get("processed", "false")).lower() != "true"
    ]
    s["unlisted"] = sorted(
        d for d in os.listdir(root)
        if os.path.isdir(os.path.join(root, d))
        and not d.startswith((".", "_"))
        and d not in ("scripts", "usage")
        # A layer whose path points at a file inside a directory
        # (`decisions/registry.md`) still declares that directory. Without the
        # first component, following the path/shape warning above earns a
        # spurious "undeclared directory" complaint for the same layer -- which
        # is how a warning becomes something people route around.
        and d not in {(sp.get("path") or n).rstrip("/").split("/")[0]
                      for n, sp in cfg["layers"].items()}
        and d not in {"archive", "_archive"}
    )
    # A hand-made *file* at the root is invisible in a way a directory is not.
    # `sensitive.md` was declared nowhere except as a string in the scan
    # exclusion list, so it had no role, nothing knew it was a layer, and a
    # rebuild would have re-derived over content that existed only there. The
    # undeclared-directory check could not see it because it is a file.
    # Being in `excluded_from_scan` is NOT a declaration. That is precisely
    # the state the reporting OS was in -- `sensitive.md` named only as a
    # string in the exclusion list, so it had no role and nothing knew it was
    # a layer. Counting exclusion as declaration would reproduce the bug this
    # check exists to find.
    declared_files = {(sp.get("path") or n).rstrip("/")
                      for n, sp in cfg["layers"].items()}
    s["unlisted_files"] = sorted(
        f for f in os.listdir(root)
        if os.path.isfile(os.path.join(root, f))
        and f.endswith(".md")
        and f not in ("INDEX.md", "README.md")
        and not f.startswith((".", "_"))
        and f not in declared_files
    )
    # -- the usage log, which is the one file whose emptiness is invisible.
    # Not an mtime comparison: a fresh clone stamps every file with the
    # checkout time, so mtimes would make every clone look stale. The
    # unambiguous condition is the one that actually happened -- a full
    # migration built six layers and left the log with zero rows.
    derived = sum(len(v) for k, v in s.items()
                  if isinstance(v, list) and k not in
                  ("raw", "unprocessed", "unlisted", "unlisted_files"))
    log = os.path.join(root, "usage", "log.md")
    rows = 0
    if os.path.exists(log):
        rows = sum(1 for ln in open(log, encoding="utf-8", errors="replace")
                   if re.match(r"^\|\s*\d{4}-\d{2}-\d{2}\s*\|", ln))
    s["log_rows"] = rows
    s["log_silent"] = bool(derived and rows == 0)
    return s


# ------------------------------------------------ rests_on breadth (F5 + S1)
# A list of supporting entry ids reads as evidence breadth and does not measure
# it. Entries are minted at whatever granularity a pass chose, so one
# conversation that yielded nine contributes nine. Measured in a real corpus:
# an argument resting on nine entries that all traced to a single meeting. The
# number looked like breadth and was one data point.
#
# So it renders as two numbers, always, and the ratio is the signal.
RESTS_RE = re.compile(r"^[-*]?\s*\*\*Rests on\*\*\s*:\s*(.+?)\s*$", re.I | re.M)
SRC_RE = re.compile(r"^[-*]?\s*\*\*Source\*\*\s*:\s*(.+?)\s*$", re.I | re.M)
FID_RE = re.compile(r"^[-*]?\s*\*\*Source fidelity\*\*\s*:\s*(\w+)", re.I | re.M)


def entry_blocks(path, marker="### "):
    """(id, body) per entry. Shared by everything that reads entry fields."""
    out, cur, buf = [], None, []
    try:
        lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    except OSError:
        return out
    for ln in lines:
        if ln.startswith(marker):
            if cur:
                out.append((cur, "\n".join(buf)))
            cur, buf = ln[len(marker):].split("—")[0].strip(), [ln]
        elif cur:
            buf.append(ln)
    if cur:
        out.append((cur, "\n".join(buf)))
    return out


def source_map(root, cfg):
    """entry id -> set of raw paths it cites, across every derived layer."""
    m = {}
    for name, spec in (cfg.get("layers") or {}).items():
        if not spec.get("enabled") or spec.get("role") != "derived":
            continue
        path = (spec.get("path") or name).rstrip("/")
        full = os.path.join(root, path)
        files = ([full] if path.endswith(".md")
                 else [f for f in md_files(root, path)])
        for f in files:
            for eid, body in entry_blocks(f, spec.get("entry_marker", "### ")):
                srcs = set()
                for s in SRC_RE.findall(body):
                    for tok in re.split(r"[,;]| and ", s):
                        tok = tok.strip().split(" — ")[0].strip()
                        if tok.startswith("raw/"):
                            srcs.add(tok)
                m[eid] = srcs
    return m


def rests_ids(body):
    """The entry ids in a Rests on list, or []. One parser, because two
    readers of the same field is how they drift apart."""
    ids = []
    for line in RESTS_RE.findall(body):
        ids += [x.strip() for x in re.split(r"[,;]", line) if x.strip()]
    return ids


def breadth(body, smap):
    """(n entries, m distinct sources) for one Rests on list."""
    ids = rests_ids(body)
    if not ids:
        return None
    srcs = set()
    for i in ids:
        srcs |= smap.get(i, set())
    return len(ids), len(srcs)


# ------------------------------------------------ grounding that went stale
# Decay is modelled on the claim and swept by corp-os-reality-check. It is not
# modelled on the things BUILT from claims, and nothing joined the two -- so a
# dashboard registered in March off four claims, two of which went past their
# window in June, reads exactly like one refreshed yesterday. Same class as the
# finding that produced "Open evidence": every field was already on disk and no
# view assembled them.
DECAY_RE = re.compile(r"^[-*]?\s*\*\*Decay\*\*\s*:\s*(\S+)", re.I | re.M)
VERIFIED_RE = re.compile(r"^[-*]?\s*\*\*Verified\*\*\s*:\s*(\d{4}-\d{2}-\d{2})",
                         re.I | re.M)


def decay_state(body, today):
    """'stale' | 'never' | 'fresh' | 'durable' | None.

    None means the entry declares no decay window at all, which is not the same
    as a durable one and must not be reported as either.
    """
    m = DECAY_RE.search(body or "")
    if not m:
        return None
    win = m.group(1).strip().rstrip(".,").lower()
    if win in ("none", "never", "-", "n/a"):
        return "durable"
    d = re.fullmatch(r"(\d+)\s*d", win)
    if not d:
        return None                      # an unparseable window is not a claim
    v = VERIFIED_RE.search(body or "")
    if not v:
        return "never"
    try:
        y, mo, dy = (int(x) for x in v.group(1).split("-"))
        due = date(y, mo, dy) + timedelta(days=int(d.group(1)))
    except ValueError:
        return None
    return "stale" if due < today else "fresh"


def entry_bodies(root, s, cfg):
    """entry id -> body, across every enabled layer. The lookup table the
    Rests on lists are resolved against."""
    out = {}
    for name, spec in (cfg.get("layers") or {}).items():
        if not spec.get("enabled") or not isinstance(s.get(name), list):
            continue
        for f in s[name]:
            for eid, body in entry_blocks(f, spec.get("entry_marker", "### ")):
                out.setdefault(eid, body)
    return out


def stale_grounding(root, s, cfg, today):
    """(id, n_stale, n_never, n_cited, relpath) for anything resting on
    evidence that has gone stale underneath it.

    Deliberately not restricted to one layer role. An argument and a registered
    dashboard have the same exposure, and the field they declare it with is the
    same field.
    """
    bodies = entry_bodies(root, s, cfg)
    out = []
    for name, spec in (cfg.get("layers") or {}).items():
        if not spec.get("enabled") or not isinstance(s.get(name), list):
            continue
        for f in s[name]:
            for eid, body in entry_blocks(f, spec.get("entry_marker", "### ")):
                ids = rests_ids(body)
                if not ids:
                    continue
                states = [decay_state(bodies.get(i), today) for i in ids]
                n_stale = states.count("stale")
                n_never = states.count("never")
                if n_stale or n_never:
                    out.append((eid, n_stale, n_never, len(ids),
                                os.path.relpath(f, root)))
    return sorted(out)


def retrievable_backlog(root, cfg):
    """Entries whose medium is a summary and whose source can still be fetched.

    Not a count of what is weak -- a count of what is one call from being
    stronger, which is a different and actionable thing. In the corpus that
    produced this, that number was 599 and nobody could see it.
    """
    conn = os.path.join(root, "connectors.md")
    fetchable = set()
    if os.path.exists(conn):
        cur = None
        for ln in open(conn, encoding="utf-8", errors="replace"):
            if ln.startswith("### "):
                cur = ln[4:].strip().lower()
            m = re.match(r"^[-*]?\s*\*\*Verbatim fetch\*\*\s*:\s*(\w+)", ln, re.I)
            if m and cur and m.group(1).lower() in ("yes", "true"):
                fetchable.add(cur)
    if not fetchable:
        return 0
    n = 0
    for name, spec in (cfg.get("layers") or {}).items():
        if not spec.get("enabled") or spec.get("role") != "derived":
            continue
        path = (spec.get("path") or name).rstrip("/")
        files = ([os.path.join(root, path)] if path.endswith(".md")
                 else md_files(root, path))
        for f in files:
            for _eid, body in entry_blocks(f, spec.get("entry_marker", "### ")):
                fid = FID_RE.search(body)
                if not fid or fid.group(1).lower() != "summary":
                    continue
                src = SRC_RE.search(body)
                blob = (src.group(1).lower() if src else "")
                if any(c in blob for c in fetchable):
                    n += 1
    return n


# --------------------------------------------------------- open evidence (F4)
# A job's evidence list is where "what do I still not know" lives, and it was
# the one structure with no declared shape: in the corpus that reported it, 33
# of 42 items carried one of four prose status markers that appeared in no
# config, no schema and no index, and not one carried a date. So nothing could
# group them, sort them or surface them, and the single ranked view of open
# items -- the question a decision-heavy operator asks most -- had no home.
#
# Both spellings parse, because the prose one is what every existing OS holds:
#     - Whether the churn started before the price change — `signal exists`
#     - Whether the churn started before the price change — `open` · opened 2026-08-04
EVIDENCE_RE = re.compile(
    r"^[-*]\s+(?P<text>.+?)\s+[—-]\s+`(?P<status>[^`]+)`"
    r"(?:\s*·\s*opened\s+(?P<opened>\d{4}-\d{2}-\d{2}))?"
    r"(?:\s*·\s*moved\s+(?P<moved>\d{4}-\d{2}-\d{2}))?\s*$")


def open_evidence(root, s, cfg):
    """Evidence items across every job, with the job they serve.

    Resolved values are declarable, because an operator renames vocabulary.
    Anything not named as resolved is open, which is the safe direction: a
    status nobody declared should show up needing attention rather than
    silently vanish from the one view that exists to catch it.
    """
    spec = cfg["layers"].get("jobs") or {}
    if not spec.get("enabled"):
        return []
    vocab = cfg.get("vocabulary") or {}
    done = {v.lower() for v in vocab.get("evidence_resolved",
                                         ["answered", "resolved", "closed"])}
    out = []
    for f in s.get("jobs", []):
        fm = frontmatter(f)
        jid = fm.get("id") or os.path.basename(f)[:-3]
        for line in open(f, encoding="utf-8", errors="replace"):
            m = EVIDENCE_RE.match(line.rstrip())
            if not m:
                continue
            if m.group("status").strip().lower() in done:
                continue
            out.append({"job": jid, "text": m.group("text").strip(),
                        "status": m.group("status").strip(),
                        "opened": m.group("opened"),
                        "moved": m.group("moved")})
    # Oldest first: elapsed time is the ranking signal for a layer about what
    # has not been settled, and an item with no date sorts last rather than
    # first, because an undated item is not evidence of age.
    out.sort(key=lambda e: (e["opened"] is None, e["opened"] or ""))
    return out


# ------------------------------------------------------ per-layer index (F3)
GEN_MARK = "<!-- generated by build_index.py — do not edit below this line -->"


def write_layer_index(root, name, files, spec, cfg, threshold):
    """A grouped summary for a layer too large to list entry by entry.

    The root index deliberately emits a bare count for a layer of hundreds,
    which is right -- a per-entry listing there would swamp the scan contract.
    The consequence nobody designed was that such a layer then has NO
    enumerated entry point at all, so its contents are reachable only by grep.
    The reasoning that a hand-kept count in a second place goes wrong is
    correct; the conclusion to carry no counts was the wrong half. Generate
    them instead.
    """
    # The threshold counted FILES while the problem this function exists for
    # is about ENTRIES. 800 claims grouped into 25 topic files is 25 < 40, so
    # the layer with the most in it was the one that got no index -- exactly
    # the "reachable only by grep" case named two paragraphs up. Either count
    # crossing is enough.
    entries = sum(count_headers(f, spec.get("entry_marker", "### "))
                  for f in files)
    if len(files) < threshold and entries < threshold:
        return None
    idx = os.path.join(root, (spec.get("path") or name).rstrip("/"), "INDEX.md")
    preamble = ""
    if os.path.exists(idx):
        existing = open(idx, encoding="utf-8", errors="replace").read()
        preamble = existing.split(GEN_MARK)[0].rstrip()
    if not preamble:
        preamble = f"# {_lbl(name, cfg['layers'], cfg)}"

    marker = spec.get("entry_marker", "### ")
    enums = [k for k in ("kind", "confidence", "status") if k]
    rows, totals = [], {"entries": 0}
    for f in sorted(files):
        n = count_headers(f, marker)
        body = open(f, encoding="utf-8", errors="replace").read()
        mixes = {}
        for field in enums:
            vals = re.findall(rf"^[-*]?\s*\**{field}\**\s*:\s*`?([\w-]+)",
                              body, re.I | re.M)
            if vals:
                c = {}
                for v in vals:
                    c[v.lower()] = c.get(v.lower(), 0) + 1
                mixes[field] = ", ".join(f"{k} {v}" for k, v in
                                         sorted(c.items(), key=lambda x: -x[1]))
        unjobbed = len(re.findall(r"^[-*]?\s*\**jobs?\**\s*:\s*`?none",
                                  body, re.I | re.M))
        rows.append((os.path.basename(f)[:-3], n, mixes, unjobbed))
        totals["entries"] += n

    L = [preamble, "", GEN_MARK, "",
         f"_{len(files)} files · {totals['entries']} entries · regenerated "
         f"{date.today().isoformat()}._", "",
         "| group | entries | mix | unjobbed |", "|---|---|---|---|"]
    for base, n, mixes, unjobbed in rows:
        mix = " · ".join(f"{k}: {v}" for k, v in mixes.items()) or "—"
        L.append(f"| [{base}]({base}.md) | {n} | {mix} | "
                 f"{unjobbed if unjobbed else ''} |")
    L.append("")
    open(idx, "w", encoding="utf-8").write("\n".join(L))
    return idx


def render_index(root, s, cfg):
    """Build INDEX.md. Every entry gets a one-line descriptor -- that is what
    makes the scan contract work; a bare link forces a second read."""
    layers = cfg["layers"]
    scan = cfg.get("scan") or {}
    # A misspelled key here fails silently and renders a plausible but wrong
    # "not in the scan path" section, so say so rather than falling back mutely.
    for k in scan:
        # `note` is accepted here because it is accepted in every other config
        # block, and the inconsistency was not cosmetic: this warned on every
        # single run of every OS carrying a documented scan block, and a
        # warning that always fires is what teaches people to skip the one
        # that matters. In the corpus that reported it, the ignored warning
        # was a real undeclared directory.
        if k not in ("excluded_from_scan", "stop_early", "order", "note",
                     "per_layer_index_threshold"):
            print(f"WARNING: config scan.{k} is not a key this script knows — "
                  "check reference/configuration.md; it is being ignored.")
    # Notes in config.json are read by every skill on every run. In a real OS
    # they were 1,627 tokens -- 42% of the file, 17% of the pre-flight floor --
    # and configuration.md's own precedence list already puts "the
    # human-readable explanation of why the config is shaped the way it is" in
    # the OS README, not here. Warned rather than enforced: it is the person's
    # config, and prune_config_notes.py moves them without losing any.
    def _notes(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "note" and isinstance(v, str):
                    yield v
                else:
                    yield from _notes(v)
        elif isinstance(o, list):
            for v in o:
                yield from _notes(v)

    ntok = sum(round(len(v) / 4) for v in _notes(cfg))
    if ntok > 400:
        print(f"NOTE: config.json carries ~{ntok} tokens of prose `note` "
              "fields, read by every skill on every run. "
              "`python3 scripts/prune_config_notes.py --root .` moves them to "
              "this OS's README without losing any.")

    excluded = scan.get("excluded_from_scan", ["sensitive.md", "raw/_archive/"])
    L = [
        "# corp-os — Index",
        "",
        "Scan this first. Most questions should be answerable from this file "
        "alone; open a detail file only when the one-liners here are not enough.",
        "",
        f"_Regenerated {date.today().isoformat()} by scripts/build_index.py "
        "(counts and listings only — no retagging)._",
        "",
        "## Counts",
        "",
        f"- **Raw files**: {len(s['raw'])} ({len(s['unprocessed'])} unprocessed)",
    ]
    if s.get("jobs"):
        L.insert(-1, f"- **{_lbl('jobs', layers, cfg)}**: {len(s['jobs'])}")
    if s.get("claim_entries"):
        L.append(f"- **{_lbl('claims', layers, cfg)}**: {s['claim_entries']}")
    for name in sorted(k for k in s if isinstance(s.get(k), list)
                       and k not in ("raw", "jobs", "claims", "unprocessed",
                                     "unlisted")):
        if s[name]:
            L.append(f"- **{_lbl(name, layers, cfg)}**: {len(s[name])}")
    for name, meta in sorted(s.get("_single", {}).items()):
        if not meta["in_scan"]:
            continue
        detail = ""
        if meta["groups"]:
            detail = " (" + ", ".join(f"{k.lower()} {v}"
                                      for k, v in meta["groups"].items()) + ")"
        L.append(f"- **{_lbl(name, layers, cfg)}**: {meta['entries']}{detail}")
    if s["glossary_terms"] and "glossary" not in (s.get("_single") or {}):
        L.append(f"- **Glossary terms**: {s['glossary_terms']}")
    L.append("")

    # One section per enabled file-per-entry layer, shipped or custom, each
    # rendered through its own index_line template.
    missing_template = []
    derivable = [0]
    for name in ["jobs"] + sorted(k for k in s if isinstance(s.get(k), list)
                                  and k not in ("raw", "jobs", "claims",
                                                "unprocessed", "unlisted")):
        files = s.get(name) or []
        if not files:
            continue
        spec = layers.get(name, {})
        if spec.get("role") == "record":
            continue
        # A layer big enough to get its own INDEX.md gets a count and a
        # pointer here, not its entries. `raw` and `claims` were exempted by
        # NAME, which reads as a size rule and is not one: in a real OS a
        # people layer of 54 was rendered in full in the root AND in its own
        # generated index -- 1,424 tokens duplicated into the file every skill
        # reads on every run. The rule is the same one write_layer_index uses,
        # so the two cannot disagree.
        thr = ((cfg.get("scan") or {}).get("per_layer_index_threshold") or 40)
        n_entries = sum(count_headers(f, spec.get("entry_marker", "### "))
                        for f in files)
        if len(files) >= thr or n_entries >= thr:
            rel = os.path.join((spec.get("path") or name).rstrip("/"),
                               "INDEX.md")
            L += [f"## {_lbl(name, layers, cfg)}", "",
                  f"**{n_entries}** entr{'y' if n_entries == 1 else 'ies'} "
                  f"across {len(files)} file{'' if len(files) == 1 else 's'} — "
                  f"listed in [{rel}]({rel}). Too many to scan here without "
                  "swamping every other layer.", ""]
            continue
        template = spec.get("index_line")
        if not template:
            missing_template.append(name)
        # A layer can declare which field orders it, and the order that
        # field's values take. An urgency-tiered layer carrying the priority
        # signal is the case that needs it: sorted by filename, a `now` item
        # can sit below a `watching` one in the file every skill reads first,
        # which defeats the point of tiering it. Ordering by a declared enum is
        # deterministic, so it stays on the bookkeeping side of the line -- the
        # script is not deciding what is urgent, only reading what the config
        # already said.
        order_by = spec.get("order_by")
        if order_by:
            # entry_schema is a dict in some OSes and a list of field names in
            # others. Both are legitimate and both are in the wild; assuming
            # the dict form crashed the whole index the first time a config
            # used the list form with order_by. A list declares names without
            # values, so there is no ordering to read -- fall back to
            # alphabetical rather than failing.
            es = spec.get("entry_schema")
            values = []
            if isinstance(es, dict):
                spec_field = es.get(order_by)
                if isinstance(spec_field, dict):
                    values = spec_field.get("values") or []
            rank = {v: i for i, v in enumerate(values)}
            files = sorted(
                files,
                key=lambda f: (rank.get(frontmatter(f).get(order_by), len(rank)),
                               os.path.basename(f)))

        L += [f"## {_lbl(name, layers, cfg)}", ""]
        for f in files:
            fm = frontmatter(f)
            fallback = os.path.basename(f)[:-3].replace("-", " ")
            label = (fm.get(spec.get("label_field", "")) or fm.get("id")
                     or fm.get("title") or fm.get("name") or fm.get("company")
                     or fallback)
            line = render_line(template, fm, "")
            if line.startswith(label):
                line = line[len(label):].lstrip(" -—·|")
            rel = os.path.relpath(f, root)
            # A path that is exactly the slug of the label restates it. The
            # name is then charged twice -- once as the label, once inside its
            # own path -- and hyphenated slugs tokenize badly, so the copy
            # costs more than the original. Measured on a real OS: 1,004
            # tokens of path against 720 of label across 82 entries, 24% of
            # INDEX.md. The convention is stated once in the header instead,
            # and any entry whose filename does NOT follow it keeps its link,
            # so nothing becomes unreachable.
            base = os.path.basename(rel)[:-3]
            if base == _slug(label):
                derivable[0] += 1
                L.append(f"- **{label}**" + (f" — {line}" if line else ""))
            else:
                L.append(f"- **[{label}]({rel})**" +
                         (f" — {line}" if line else ""))
        L.append("")

    if derivable[0]:
        L += ["> **Paths follow the name.** An entry listed without a link "
              "lives at `<layer>/<its name, lowercased and hyphenated>.md` — "
              f"{derivable[0]} of them here. Spelling that out per entry "
              "restates the name in a form that costs more than the name. "
              "Anything whose filename does not follow the convention keeps "
              "its link.", ""]

    if missing_template:
        L += ["> **Incomplete index.** These layers have no `index_line` in "
              "`config.json`, so their entries are listed as bare links and "
              "cannot be scanned without opening each file: "
              + ", ".join(f"`{m}`" for m in missing_template)
              + ". Run corp-os-configure to give each one a template.", ""]

    for name, meta in sorted(s.get("_single", {}).items()):
        if not meta["in_scan"] or not meta["groups"]:
            continue
        L += [f"## {_lbl(name, layers, cfg)}", "",
              f"{meta['entries']} entries in [`{meta['path']}`]({meta['path']}), "
              "grouped as:", ""]
        for g, n in meta["groups"].items():
            L.append(f"- **{g}** — {n}")
        L.append("")

    if s["unprocessed"]:
        L += ["## Unprocessed queue", "",
              "Raw material not yet folded into the derived layer.", ""]
        for f in s["unprocessed"]:
            fm = frontmatter(f)
            rel = os.path.relpath(f, root)
            gist = fm.get("gist") or fm.get("type", "")
            L.append(f"- [{os.path.basename(f)[:-3]}]({rel})" +
                     (f" — {gist}" if gist else ""))
        L.append("")

    # -- The health report. It used to live in INDEX.md, which every skill
    # reads on every run, and at 800 claims it was 1,029 of that file's 1,440
    # tokens: 71% of the index every skill pays for, to carry findings almost
    # none of them act on. Capping the lists was the obvious fix and the wrong
    # one -- these sections exist to make problems visible, and finding #31 is
    # the one nobody goes looking for. So they move out whole and uncapped,
    # and INDEX.md keeps a line saying they exist.
    H = [
        "# Health",
        "",
        "Generated by `build_index.py` alongside `INDEX.md`. Findings about "
        "the corpus rather than an inventory of it: what rests on too little, "
        "what has decayed underneath something built from it, and what could "
        "be promoted cheaply. `corp-os-reality-check` is the skill that acts "
        "on this file.",
        "",
        "Nothing here is truncated. A finding that is only visible when it is "
        "one of the first thirty is not visible.",
        "",
    ]
    # -- rests_on breadth, wherever it appears.
    smap = source_map(root, cfg)
    thin = []
    for name, spec in cfg["layers"].items():
        if not spec.get("enabled") or not isinstance(s.get(name), list):
            continue
        for f in s[name]:
            for eid, body in entry_blocks(f, spec.get("entry_marker", "### ")):
                b = breadth(body, smap)
                if b and b[1] <= 1:
                    thin.append((eid, b[0], b[1], os.path.relpath(f, root)))
    if thin:
        H += ["## Arguments resting on one source", "",
              "Not wrong, and not the same object as one resting on nine. "
              "Only the record can tell them apart, so it says so.", ""]
        for eid, n, m, rel in sorted(thin):
            H.append(f"- {eid} — **{n} entr{'y' if n == 1 else 'ies'} / "
                     f"{m} source{'' if m == 1 else 's'}** · "
                     f"[{os.path.basename(rel)[:-3]}]({rel})")
        H.append("")

    # -- grounding that decayed underneath something built from it.
    stale = stale_grounding(root, s, cfg, date.today())
    if stale:
        H += ["## Resting on evidence that has gone stale", "",
              "Decay is carried by the entry, and swept by "
              "corp-os-reality-check. What is listed here is the join nothing "
              "else performs: the things **built from** those entries, which "
              "inherit the staleness and say nothing about it. A view "
              "published in March off four entries, two of them past their "
              "window in June, reads exactly like one refreshed yesterday.", ""]
        for eid, n_st, n_nv, n_all, rel in stale:
            bits = []
            if n_st:
                bits.append(f"**{n_st} of {n_all}** past its window")
            if n_nv:
                bits.append(f"**{n_nv}** never verified")
            H.append(f"- {eid} — {' · '.join(bits)} · "
                     f"[{os.path.basename(rel)[:-3]}]({rel})")
        H += ["", "Re-verify what it rests on, or retire it. An output nobody "
              "re-grounds is the same defect as a claim nobody re-checks, one "
              "layer up.", ""]

    back = retrievable_backlog(root, cfg)
    if back:
        H += ["## One call from promotion", "",
              f"**{back}** entr{'y is a summary' if back == 1 else 'ies are summaries'} "
              "whose source still exposes a verbatim fetch. Pulling the "
              "original is the cheapest confidence this OS can buy, and a "
              "ceiling that looks permanent gets treated as permanent — in "
              "the corpus that surfaced this, the number was 599 and nothing "
              "showed it.", ""]

    ev = open_evidence(root, s, cfg)
    if ev:
        H += ["## Open evidence", "",
              "What the jobs still need, oldest first. One list, because the "
              "alternative is the same question spread across every job file.",
              ""]
        for e in ev[:30]:
            age = f" · opened {e['opened']}" if e["opened"] else ""
            H.append(f"- {e['text']} — `{e['status']}` · {e['job']}{age}")
        if len(ev) > 30:
            H.append(f"- _…and {len(ev) - 30} more._")
        H.append("")

    health = [x for x in H if x.startswith("## ")]
    if health:
        L += ["## Health", "",
              "`usage/health.md` carries " +
              ", ".join(x[3:].lower() for x in health) +
              ". Regenerated with this file; read it when the task is the "
              "state of the corpus rather than its contents.", ""]

    L += ["## Not in the scan path", ""]
    for x in excluded:
        L.append(f"- `{x}` — excluded by config. Open only when the task "
                 "specifically requires it.")
    L += ["- `raw/` — source of truth, but never loaded wholesale. "
          "corp-os-rebuild is the sole exception.", ""]

    if s.get("unlisted"):
        L += ["", "> **Directories on disk but not in `config.json`**: "
              + ", ".join(f"`{d}/`" for d in s["unlisted"])
              + ". Every skill treats config as the authority, so these are "
              "invisible to all of them. Declare or remove them.", ""]
    return "\n".join(L), "\n".join(H)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_only = "--check" in sys.argv
    root = os.path.abspath(args[0]) if args else os.getcwd()

    if not os.path.isdir(os.path.join(root, "raw")):
        sys.exit(f"No raw/ found in {root} — is this a corp-os root?")

    cfg = load_config(root)
    s = survey(root, cfg)
    counted = {
        "claims": s["claim_entries"],
        "raw": len(s["raw"]),
        "unprocessed": len(s["unprocessed"]),
        "glossary_terms": s["glossary_terms"],
    }
    for name in s:
        if isinstance(s.get(name), list) and name not in (
                "raw", "claims", "unprocessed", "unlisted"):
            counted[name] = len(s[name])
    for name, meta in (s.get("_single") or {}).items():
        counted[name] = meta["entries"]

    meta_path = os.path.join(root, "meta.json")
    drift = []
    meta = {}
    if os.path.exists(meta_path):
        meta = json.load(open(meta_path, encoding="utf-8"))
        stored = meta.get("counts", {})
        for k, actual in counted.items():
            if k in stored and stored[k] != actual:
                drift.append((k, stored[k], actual))

    if drift:
        print("Drift found (meta.json vs. disk):")
        for k, was, now in drift:
            print(f"  {k:16s} meta={was:<6} actual={now:<6} ({now - was:+d})")
    else:
        print("No count drift.")

    if check_only:
        sys.exit(1 if drift else 0)

    index_md, health_md = render_index(root, s, cfg)
    open(os.path.join(root, "INDEX.md"), "w", encoding="utf-8").write(index_md)
    os.makedirs(os.path.join(root, "usage"), exist_ok=True)
    open(os.path.join(root, "usage", "health.md"), "w",
         encoding="utf-8").write(health_md)

    threshold = ((cfg.get("scan") or {}).get("per_layer_index_threshold") or 40)
    made = []
    for name, spec in cfg["layers"].items():
        if not spec.get("enabled") or not isinstance(s.get(name), list):
            continue
        made_path = write_layer_index(root, name, s[name], spec, cfg, threshold)
        if made_path:
            made.append(os.path.relpath(made_path, root))

    if meta:
        meta.setdefault("counts", {}).update(counted)
        meta["generated_at"] = date.today().isoformat()
        json.dump(meta, open(meta_path, "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)

    parts = [f"{counted['raw']} raw ({counted['unprocessed']} unprocessed)"]
    for k in sorted(k for k in counted
                    if k not in ("raw", "unprocessed", "glossary_terms")):
        if counted[k]:
            parts.append(f"{counted[k]} {k}")
    print("INDEX.md regenerated: " + ", ".join(parts) + ".")
    if made:
        print("Per-layer index regenerated: " + ", ".join(made)
              + f" (layers at or over {threshold} files or entries).")
    if s.get("unlisted"):
        print("Undeclared directories (invisible to every skill): "
              + ", ".join(s["unlisted"]))
    if s.get("unlisted_files"):
        print("Undeclared files (no role, and a rebuild does not know they "
              "exist): " + ", ".join(s["unlisted_files"])
              + "\n  Declare each in config.json layers with a role. Listing "
                "it in scan.excluded_from_scan is not a declaration -- that "
                "keeps it out of the scan path and still leaves it roleless. "
                "A file holding the only copy of something, that nothing "
                "knows is a layer, is how a rebuild destroys it.")
    if s.get("log_silent"):
        print(f"usage/log.md has no rows, and the derived layer holds "
              f"{sum(len(v) for k, v in s.items() if isinstance(v, list) and k not in ('raw','unprocessed','unlisted','unlisted_files'))} "
              "entries. corp-os-improve reads that file and only that file; "
              "with no rows it is blind. Close runs with scripts/log_run.py.")
    if s["unprocessed"]:
        print("Unprocessed material is waiting — run corp-os-claims to work the queue.")


if __name__ == "__main__":
    main()
