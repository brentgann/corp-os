# corp-os improvement packet — 2026-09-09

## Origin

- **Produced by**: corp-os-audit
- **Operator role shape**: build-heavy — the audited system serves a product org shipping software through a defined process
- **OS age**: not applicable, see note
- **Scale**: not applicable, see note
- **Anonymized**: yes — no claim bodies, person names, company records or citations from either system

**Note on shape.** This audit studied an **independently built skill set and its
architecture**, not a populated corpus. The audited system ships with its
knowledge layer empty on purpose, so there is no usage log to quote and no entry
counts to report. That weakens the friction evidence below and strengthens the
structural evidence: what a second team arrived at without reference to this
model is the most reliable signal an audit of this kind produces, and it is what
`corp-os-audit`'s tenth dimension exists to capture.

Where a finding lacks a frequency, it says so rather than dressing a hunch as a
count. Two findings that would otherwise appear here are held back for exactly
that reason and are listed under **Not recommended**.

---

## Friction observed

### F1 — An output built from claims inherits their decay, and nothing says so

- **Frequency**: not measured. See "what would measure it" below.
- **Evidence**: structural, and present in a shipped layer today. `dashboards.md`
  registers a published dashboard with its source files and owning job. Every
  claim behind that dashboard carries a decay window. Nothing joins the two, so a
  dashboard built in March off four claims, two of which went past their window in
  June, reads exactly like one refreshed yesterday. The same exposure appears the
  moment anyone declares a layer for authored documents that cite the corpus —
  a spec, a brief, a memo — which is the case this audit was prompted by.
- **Diagnosis**: decay is modelled on the **claim** and surfaced at
  `corp-os-reality-check` time. It is not modelled on **things built from claims**,
  and there is no view that reports one. This is the same class as the finding
  that produced *open evidence across every job*: the data was all present and no
  single view assembled it.
- **Proposed change**: `build_index.py` renders a cross-cutting section for
  **outputs whose grounding has decayed** — any entry in a `record` layer carrying
  citations, listed with the count of cited entries now past their window. Derived
  from what is on disk, so it cannot go stale itself.
- **Affects**: `scripts/build_index.py`, `reference/data-model.md` (the record-layer
  citation convention), `corp-os-dashboard` (say it at refresh time)
- **Confidence this generalizes**: high — nothing about it is role-specific. Any
  operator who publishes anything from the corpus has it.
- **What would measure it**: the count of registered dashboards whose cited claims
  are past decay, at the moment the view first runs. That number is the frequency
  evidence this entry is missing, and it can only be produced by building the view.

---

## Structures the audited system has

The most valuable section, and here it is comparative rather than inventive: three
things a second system built that this model does not have.

### S1 — A provenance chain, distinct from both decay and fidelity

- **What it is**: a skill that fires before a status or figure is relied on, and
  traces it back to an actual documented source rather than accepting that it has
  been repeated long enough to feel settled.
- **Why it emerged**: figures acquire authority by repetition. Each restatement
  cites the previous one, and no link in the chain is wrong, so nothing in the
  record looks broken.
- **What this model already covers, and what it does not**: `Decay` covers *time*.
  `Source fidelity` covers *medium* — whether the record is a quote, a paraphrase,
  a reconstruction, or gone. Neither covers **chain depth**: a claim can be freshly
  verified, cite a real source, and still bottom out in another summary rather than
  anything primary. That is a third axis, and this model has no field, no view and
  no skill for it.
- **Generalizes to**: every role shape. A number nobody can trace is as corrosive
  to a controller as to a product manager.
- **Recommendation**: hold until one real instance is on record in an operator's
  own corpus, then build it as a skill rather than a field — tracing is judgment
  and the answer is a conversation, not a value. Noted here so the next packet
  that finds an instance can cite this entry rather than rediscovering the gap.

### S2 — A first-class record for what the corpus does not know

- **What it is**: a layer for unanswered questions, known gaps, and recurring
  themes not yet solid enough to be claims — distinguishing the three, carrying two
  fields claims do not have (**who could answer it**, and **what would make it
  urgent**), and accumulating repeats on one entry so a theme earns weight rather
  than spawning duplicates.
- **Why it emerged**: onboarding produces more questions than facts, and the
  audited system named that explicitly as the reason.
- **What this model already covers, and what it does not**: job records carry
  *What I still need to know* with a five-state answer ladder, and `corp-os-decide`
  holds open forks with owners and dates. Between them they cover a question
  **attached to a job** and a **decision** somebody has to make. What has nowhere to
  live is an open question attached to no job and blocking no decision, which is
  most of what a person accumulates in their first month.
- **Recommendation**: **this is a config finding, not a model change** — see
  Not recommended. The concept is expressible as a declared layer with its own
  `entry_schema`. It is recorded here because the *routing* gap is real even though
  the structural one is not.

### S3 — Eval cases split by what they test, one per skill, gates not naming the skill

- **What it is**: every skill has exactly one case; cases are tagged `gate` or
  `routing`; gate cases deliberately do not name the skill in the prompt, so
  recognizing the situation is part of what is under test. The suite states its
  weighting outright: a skill that produces slightly worse output is a small
  problem, one that merges unredacted material or invents a number is the failure
  the whole system exists to prevent.
- **Why it matters here**: this model reached the same conclusion — its most
  valuable conformance finding was a missing review gate — but its coverage is
  uneven, at **15 of 23 skills**, and its cases are not tagged by what they test.
- **Recommendation**: adopt the bar, not the harness. One case per skill, and mark
  each case as gate or routing so a fast subset can run on a wording change.

---

## Structures shipped but unused

### U1 — Four of five pattern kinds have never been exercised

- **Created**: 0.13.0, with `KINDS = {dashboard, export, deck, doc, brief}` in
  `bind_pattern.py`.
- **Times exercised since**: `dashboard` only. The fixture carries one pattern and
  it is a dashboard, so four accepted values have no implementation, no fixture and
  no binding assertion behind them.
- **Why unused**: nothing has needed them yet, which is legitimate. The cost is
  that the binder validates against a list it has never had to honour, and this
  repo has a standing rule about checks never seen to work.
- **Recommendation**: add one `doc` pattern to `examples/fixture-os` and assert its
  binding. `doc` first because it is the kind the next real pattern will use. Do
  not remove the other three — an unexercised enum value is cheaper to test than to
  re-add.

---

## Model deltas

Concrete proposed edits, each traceable to an entry above.

- Render **outputs whose grounding has decayed** as a cross-cutting index section:
  any `record`-layer entry carrying citations, with a count of cited entries past
  their window. (F1)
- State the record-layer citation convention in `reference/data-model.md`, so the
  view above has a declared shape to read rather than a guessed one. (F1)
- Have `corp-os-dashboard` report decayed grounding at refresh time, in the same
  breath as the recount. (F1)
- Add one `doc`-kind pattern to `examples/fixture-os` and a binding assertion for
  it in `validate.py`. (U1)
- Adopt one conformance case per skill as the coverage bar, and tag existing cases
  `gate` or `routing`. (S3)
- **Not yet**: a provenance-chain skill. Recorded, with the trigger stated. (S1)

---

## Not recommended

Things considered and rejected, with the reason, so the next packet does not
re-propose them.

- **A PRD, spec, or any document-authoring skill in the core plugin.** Fails
  content-agnosticism outright: the field model that makes such a skill useful is
  domain vocabulary pinned to whatever system is downstream of it. The audited
  system's own model carries market-segment and marketplace-role fields that mean
  nothing outside its industry, and its skill states that where the two disagree,
  the downstream schema wins. A spec layer is `config.json` and a spec pattern
  belongs in a pack; neither is a model change.

- **An open-question layer as a model change (S2).** Fails the config test. The
  concept is expressible today as a declared layer with `who_could_answer` and
  `urgency_trigger` in its `entry_schema`, which is exactly what the config test
  exists to catch. The *routing* half — that no shipped skill would think to write
  there — is a real gap, but it is a gap in a layer nobody has declared yet, and
  proposing a model change for it now would be building for a shape that does not
  exist in any operator's OS.

- **An "already shipped this" overlap check.** General in a product org and weak
  for a single operator: "have I already looked into this" is a recall query, not a
  distinct judgment, and this model already answers it.

- **A companion-plugin conformance kit** — an exported subset of `validate.py`, a
  namespace rule, and version-compatibility reporting for skill sets built by
  others on top of this one. The shape is right and the bar is not met: **one**
  companion exists. Build it when a second starts, and treat the first as the
  reference implementation — the places where its author had to guess what the rule
  was are the specification. One cheap piece is worth doing now regardless, and it
  is listed as a build item rather than a model change: state the write contract
  outward, in `reference/`, so a companion has something to obey.

---

# Appendix — build-process defects

**Not packet material.** These are defects in this repository rather than in the
model, so they carry no operator evidence and travel nowhere. They are recorded
here because the audit session surfaced them and losing them would be worse than
filing them in the wrong shape. Route through `corp-os-contribute`.

### B1 — The version bump is documented and unenforced

`docs/INSTALL.md` establishes that a client caches an installed plugin by version
string, so commits pushed without a bump reach nobody, with no error and nothing
inspectable from the inside. That is a rule with nothing behind it, which is the
exact shape this repo converts into code.

`validate.py` can be git-aware: find the last commit that changed the `version` in
`plugin.json`, and fail if anything under `plugins/corp-os/` has changed since. The
mechanism is fully traced — one near-miss in the session that wrote the file
explaining the failure, caught only because the explanation was fresh — and
`corp-os-contribute`'s bar is one fully-traced mechanism rather than a frequency.

### B2 — State the write contract outward

One section in `reference/`, saying what a skill from outside this plugin must
obey when it operates on a Corp-OS: append-only into `raw/`, propose and never
write into any `derived` layer, free rein in its own `record` layers. All three are
already true internally. Writing them down costs a section and is what makes the
first companion buildable without guessing.
