# Corp-OS — architecture and decision record

The working document for this project. It records what Corp-OS is, every consequential decision and the reasoning behind it, what has been tested and how, and what is still open. Written so a session that has never seen this repo can pick it up cold and make correct changes.

**Status:** v0.5.0 · 18 skills · 8 reference specs · 1 shipped script
**Last substantive change:** renamed from JobOS; configuration layer added; jobs made optional.

---

## 1. What this is

A portable personal work OS: a folder of markdown files, plus a plugin of skills that operate on it. Someone installs the plugin, runs `corp-os-setup`, answers an interrogation, and gets a knowledge base shaped to their actual work — which then ingests meetings and documents, builds citable claims, answers recall questions with provenance, renders dashboards, and watches how it is being used so its own structure can be improved from evidence.

It is content-agnostic by construction. No role templates, no domain vocabulary, no starter taxonomy ships with it. The vocabulary comes from the person's own captured material.

### The five invariants

Everything else is configurable. These are not:

1. **An append-only source layer.** Existence in it means *said*, not *true*.
2. **Provenance on derived entries** — source, date, verbatim citation, confidence.
3. **A review gate** in front of the derived layer.
4. **An index that can be scanned** rather than a corpus that must be loaded.
5. **Something that removes things.**

Invariant 5 is the one most systems lack and the one that decides whether the thing survives two years. Everything additive is easy; the removal rule is what stops unbounded growth.

### What is deliberately *not* invariant

The **jobs layer** — the model's own organizing idea — is optional. See §4.2. This was the most important design change in the project's history and it came from evidence against the model.

---

## 2. Repository layout

```
corp-os-skills/
├── .claude-plugin/marketplace.json   # marketplace manifest (points at plugins/corp-os)
├── plugins/corp-os/                  # the plugin itself
│   ├── .claude-plugin/plugin.json
│   ├── README.md                     # user-facing; the "what and why"
│   ├── CONNECTORS.md                 # tool-category conventions
│   ├── skills/<name>/SKILL.md        # 18 skills
│   ├── reference/*.md                # 8 shared specs, referenced via ${CLAUDE_PLUGIN_ROOT}
│   ├── scripts/build_index.py        # shipped into each user's OS
│   └── examples/config-worked-example.json
├── scripts/validate.py               # pre-package checks
├── build.sh                          # validate + package to dist/corp-os.plugin
└── docs/ARCHITECTURE.md              # this file
```

**Conventions.** `Corp-OS` is the product name in prose; `corp-os-*` is the identifier form for skills and never gets title-cased. Reference files are shared across skills and addressed as `${CLAUDE_PLUGIN_ROOT}/reference/<file>.md` — never a relative path, which breaks once the plugin is installed elsewhere.

**`build.sh` gotcha, already handled:** it zips to a temp dir and copies in with `cat >` rather than `mv`. Synced and mounted filesystems commonly permit writes but refuse deletes, and `mv -f` needs an unlink.

---

## 3. The data model

Full spec: `plugins/corp-os/reference/data-model.md`. Summary of the shapes and the reasoning.

### 3.1 Layers and roles

Every layer declares a **role**, and this is the field that destroys data when wrong:

| Role | Meaning | Rebuild behavior |
|---|---|---|
| `source` | its own truth | never touched |
| `derived` | regenerable from source | overwritten, by design |
| `record` | an audit trail of what happened | never regenerated, eventually archived |

`corp-os-rebuild` refuses to touch anything not `derived`, and a new layer defaults to `source` until someone explicitly says otherwise. That is the safe failure direction: a `source` layer mislabeled `derived` gets overwritten with nothing to restore from, and it is the only failure mode in the whole system that loses data rather than degrading quality.

### 3.2 The claim

The unit of knowledge. Fields, and why each exists:

- **`kind`** — `fact` / `decision` / `theme` / `assumption` / `constraint` / `metric` / `preference` / `identity`. Separating `fact` from `assumption` is load-bearing: an assumption promoted to fact stops being questioned, which is the most expensive error the system can hold.
- **`confidence`** — `confirmed` / `needs_review` / `reconstructed` / `disputed` / `retired`. Evidentiary standing, not importance. Two people's notes on the same call are **one** source, not corroboration — getting this wrong silently inflates confidence.
- **`citation`** — verbatim, with speaker and date. `no source` is a **sanctioned literal**; see §4.3.
- **`decay`** — when this needs re-checking. This is what makes drift correctable on a schedule instead of by accident.
- **`jobs`**, **`sensitivity`**, **`relations`**.

Claim IDs are globally sequential and **never renumbered**, including by a rebuild — external references (dashboards, sent documents, prior briefs) depend on them holding still.

### 3.3 Update blocks vs. superseding

A claim that develops gets a dated update block inside it, carrying its own confidence and citation. A claim that stops being true gets retired and replaced.

The rule: **update block when the claim is still true and now known in more detail; new claim when it is no longer true.** Forcing everything through atomic claims plus supersede links makes the development of an understanding nearly unreadable, which was the original design and was wrong.

### 3.4 Persisted proposals

The review gate writes `proposals/PROPOSAL-<date>-<slug>.md` **before** presenting anything — headline first, then per-item recommendations that are actual recommendations ("enrich the existing entry rather than duplicate", "flag as a conflict rather than resolve"), then what is deliberately *not* being proposed.

After review, the outcome per item is appended. **The declines are the valuable part** — the only record of what someone deliberately chose not to know.

### 3.5 `sensitive.md`

A quarantine file deliberately outside the scan path, with a one-line pointer left in the original file. A sensitivity *flag* alone protects nothing: a flagged entry sitting inline still loads on every scan and still travels when that file gets shared. Captured, never suppressed.

### 3.6 The scan contract

`INDEX.md` → `jobs/INDEX.md` → `claims/INDEX.md` → specific detail files, stopping as soon as there is enough. `raw/` is never loaded wholesale; `corp-os-rebuild` is the sole exception.

This is why every index carries a **one-line descriptor** per entry rather than a bare link. A bare link forces a second read; a one-liner answers most questions outright. A custom layer without an `index_line` template degrades this one layer at a time, so `build_index.py` flags it.

---

## 4. Decisions, with reasoning

Each of these was a real fork. Recorded so a future session does not silently reverse one.

### 4.1 Jobs-to-be-done as the default organizing primitive

**Decision:** organize by outcome rather than subject, by default.

**Why:** it buys three things subject-organization cannot — an intake priority signal (a job declares what it still needs to know), a relevance signal for recall, and a stopping rule (when a job retires, material serving only it retires with it).

### 4.2 …but jobs are optional, and there is a test

**Decision:** `layers.jobs.enabled: false` is supported and sometimes correct.

**Why — this is the most important entry in this document.** An agent was asked to cluster a real 137-item corpus into 3–7 candidate jobs, without looking at the existing subject taxonomy first. Six of seven clusters mapped nearly 1:1 onto topic files that already existed. Roughly 25 of 92 entries fit two clusters equally well.

A clustering exercise that independently rediscovers the taxonomy already in use is a taxonomy of **subjects**. Forcing jobs onto that material costs a migration and buys nothing.

**The shipped test**, now in `reference/jtbd-patterns.md` and enforced by `corp-os-audit` and `corp-os-jobs`: cluster into candidate jobs *without looking at the subject taxonomy first*, then compare. Tells that the material is subject-shaped — clusters reproduce the existing taxonomy; a quarter or more of entries cross-assign; clusters are named after domains rather than decisions.

When jobs are off, something must still carry the priority signal and the removal rule — usually urgency tiering plus decay. **If neither substitute is present, the OS has no stopping rule.** That is the one configuration worth arguing against.

### 4.3 `no source` as a sanctioned citation value

**Decision:** an explicit literal for "no retrievable original exists."

**Why:** demanding a citation with no honest way to say none exists pressures toward the worst possible outcome — an invented one. An unsourced claim that says so is honest and correctable; a fabricated citation is undetectable downstream. The instruction "never repair this by manufacturing a citation" is in `corp-os-claims` verbatim.

### 4.4 `decay.applies_to: "sourced"` by default

**Decision:** decay applies only to entries with a retrievable citation, unless configured otherwise.

**Why:** decay assumes re-verification is possible. Measured against a real corpus, ~74 entries had no retrievable source of any kind — roughly a third. For those, decay can only ever ratchet downward: flagged stale, never re-confirmable. Applied wholesale it produces a permanently unclearable backlog, **which is how someone learns to skip the sweep entirely**, taking the resolvable items with it.

The unsourced set gets a one-time **disposition pass** in `corp-os-reality-check` — keep as an assumption, retire, or backfill — and then stops being carried. It is bucket 2, deliberately separate from the overdue list.

### 4.5 Retention: `delete` is a claim-integrity event

**Decision:** four policies (`keep` / `archive` / `summarize_then_archive` / `delete`); `delete` requires a stated obligation and a five-step sequence.

**Why:** most people asking for a raw TTL want `archive` — out of the scan path, still on disk, reversible, costs nothing. Actual deletion is legitimate under a retention schedule, NDA, or deletion right, but it is not file management. Deleting a source file without first re-citing the claims that depend on it leaves claims pointing at files that do not exist — **worse than `no source`, because they still look sourced** and nothing downstream can tell.

The sequence, enforced in `corp-os-configure`: find every citing claim → re-cite to `no source` and lower confidence → record a cohort ceiling → log it → then delete.

`measure_from` defaults to `frontmatter_date`, never mtime: a sync or restore changes mtime on everything at once, tripping every TTL simultaneously.

### 4.6 Cohort confidence ceilings

**Decision:** a batch entering from a structurally weaker source carries a ceiling recorded in config *and* marked in the raw frontmatter.

**Why:** per-claim confidence is insufficient. Without a ceiling, one careless pass promotes an entire migration cohort of summaries to `confirmed` and nothing afterward can tell which were ever really sourced. Marking the raw frontmatter too means a rebuild rediscovers the ceiling rather than depending on a README being read.

### 4.7 Configuration as a default profile, not a schema

**Decision:** `config.json` is the authority every skill reads first. Layers, roles, vocabulary, decay, retention, gate strictness, and entirely new layers with their own field schemas.

**Why:** the genuinely universal parts of this model are the five invariants. Everything else was a reasonable guess about a stranger's work. Being unable to rename "claim" is a real reason someone abandons a system — the word is wrong in several fields.

Precedence: `config.json` → the OS's own `README.md` → shipped defaults. A config contradicting the README is a bug to surface, not resolve silently: one is stale and only the person knows which.

### 4.8 Bookkeeping separated from judgment

**Decision:** `build_index.py` recounts and rewrites the index, reads nothing from `raw/`, and retags nothing.

**Why:** it makes "the index is stale" a thirty-second fix rather than a reason to schedule a rebuild. It is safe to run after any manual edit precisely because it exercises no judgment.

### 4.9 The model must argue against itself

**Decision:** `corp-os-audit` may not score outcome-orientation from the absence of a jobs layer without running the clustering test, and may not recommend decay without first checking whether entries can be re-verified.

**Why:** an audit carried out by someone holding a model will find what the model predicts. Both of these were caught by that failure mode in real use, and both recommendations were wrong. A model that only ever confirms itself is not measuring anything.

---

## 5. The skills

| Skill | Job |
|---|---|
| `corp-os-guide` | Explain and route. Never does the work itself. |
| `corp-os-setup` | Nine-area interrogation, then scaffold + `config.json` + first dashboard. |
| `corp-os-configure` | Reshape later: vocabulary, layers, custom layers, decay, retention, gate. |
| `corp-os-jobs` | Add / sharpen / split / retire jobs. Refuses to add them to subject-shaped material. |
| `corp-os-connect` | Register a source: protocol, cadence, jobs served, **blind spots**. |
| `corp-os-pull` | Retrieve from registered sources with three-case dedupe. |
| `corp-os-intake` | File pasted or handed-over material. |
| `corp-os-claims` | Raw → reviewed claims. The longest skill; the fields are where it earns its keep. |
| `corp-os-reality-check` | Eight-bucket sweep: overdue, unsourced-disposition, unverified, contradictions, aging assumptions, orphans, identities, cohort escapes. |
| `corp-os-glossary` | Terms, acronyms, and especially metric definitions with competing definitions kept visible. |
| `corp-os-company` | Employer / counterparty / competitor research, always searched, never recalled. |
| `corp-os-recall` | Answer with provenance; enrich what the person is working on. The payoff skill. |
| `corp-os-dashboard` | Render only what the OS holds; surface the uncomfortable numbers. |
| `corp-os-brief` | The operating rhythm. Schedulable. |
| `corp-os-rebuild` | Re-derive `derived` layers only, from the full corpus. |
| `corp-os-redact` | Make something shareable; quarantine at source; log reclassifications. |
| `improve-corp-os` | Mine the usage log; propose config / hygiene / model changes with counts. |
| `corp-os-audit` | Ten-dimension audit of any system; propose what to build; find what it has that the model lacks. |

### Cross-cutting rules every skill obeys

- **Pre-flight** — confirm the OS is accessible now, not recalled. **The files outrank memory**; where they conflict, memory gets corrected.
- **Read `config.json` first**, and speak the person's labels back to them.
- **Write freely** to `raw/`, indexes, and `usage/log.md`. **Propose** everything entering the derived layer.
- **Recount programmatically**, never hand-increment.
- **Append one `usage/log.md` row per run** with honest friction. That field is the entire improvement flywheel — `improve-corp-os` refuses to propose anything without a count attached.

---

## 6. What has actually been tested

Being explicit, because much of this is unexercised.

**Verified:**

- `build_index.py` against a structure-only mirror of a real 214-source system with a config using **none** of the model's default layer names. It rendered 137 items across four urgency levels, 63 glossary terms across five groups, 15 questions across a four-state ladder, 18 themes, 20 tier entries, 45 people. Building that surfaced **four real bugs** in the script — it assumed `jobs` existed; could not handle single-file layers; counted list-style entries as zero; missed `title` in frontmatter. All fixed; the config ships anonymized at `examples/config-worked-example.json`.
- Custom-layer rendering, disabled-layer omission, missing-`index_line` warnings, undeclared-directory warnings, config-driven scan exclusions.
- `scripts/validate.py` passes: frontmatter, name/directory match, cross-references, `${CLAUDE_PLUGIN_ROOT}` targets, step ordering, private-identifier leakage.

**Not tested:** every skill's actual behavior in a session. No skill has been run end-to-end against a live OS. Trigger accuracy across 18 similar descriptions is unmeasured and is the most likely real-world problem — see §7.

---

## 7. Open questions

Ordered by how much they would change.

1. **Trigger collision across 18 skills.** Descriptions were written to disambiguate, but this is unmeasured. `skill-creator` has an eval harness; running it on the most collision-prone pairs (`intake` vs `pull` vs `claims`; `configure` vs `rebuild` vs `improve`) is the highest-value next test.
2. **Is 18 skills too many?** Candidates to merge: `connect` + `pull`; `glossary` into `claims`. Argument against merging: triggers differ meaningfully. Decide from eval data, not taste.
3. **Does the setup interrogation actually land?** Nine areas is long. It has never been run on someone who did not design it. The most likely failure is people abandoning partway.
4. **Does `usage/log.md` get written in practice?** The entire improvement flywheel depends on every skill remembering to append a row. If it turns out to be skipped under pressure, the mechanism needs to be structural rather than instructed.
5. **Is `sensitive.md` sufficient**, or does sensitive material need its own encrypted or separately-permissioned store?
6. **Should `build_index.py` be able to repair, not just report?** Currently it flags undeclared directories and missing `index_line`s. Auto-fixing would cross the bookkeeping/judgment line that makes it safe — probably keep as-is.
7. **Multi-person / team OS.** Everything here assumes one operator. Shared ownership raises questions this model does not answer: who reviews, whose decay windows, how sensitivity works across people.
8. **No `corp-os-decide`.** A decision log with owner, date, and what it unblocks kept surfacing as a real need. Currently claims of kind `decision` carry it, which may be enough — or may be under-served.

---

## 8. Deliberately rejected

Recorded so they do not get re-proposed.

- **Auto-promoting claims past a corroboration threshold.** Removes the review gate, which is the load-bearing part.
- **Renumbering claim IDs on rebuild.** Breaks every external reference.
- **Backfilling provenance retroactively.** Nobody does it; recommending it wastes the recommendation.
- **Shipping role templates or domain vocabulary.** Content-agnosticism is the portability guarantee.
- **A numeric composite audit score.** Invites arguing with the number instead of fixing the gap.
- **`build_index.py` reading `raw/`.** Would make it judgment rather than bookkeeping, and unsafe to run casually.
- **Recommending a rebuild in an audit.** Nobody rebuilds a working system on an audit's advice.

---

## 9. How to make a change here

1. Change the **reference spec** first if the change is to the model — `data-model.md` or `configuration.md`. Skills defer to those; a skill that contradicts a spec is a bug.
2. Update **every skill that touches the changed behavior.** Cross-cutting rules (pre-flight, config-first, the write gate, the usage-log row) live in many files by design; grep before assuming one edit covers it.
3. Update the plugin **`README.md` version history** with what changed and why. A change nobody can explain later gets reverted by accident.
4. Run `python3 scripts/validate.py`, then `./build.sh`.
5. If the change came from real use, write an **improvement packet** per `reference/improvement-packet.md` — and apply its config test first: *if it could have been a config setting, it is not a model change.*

---

## 10. Session handoff

To resume cold:

- Read this file, then `plugins/corp-os/reference/data-model.md` and `configuration.md`. Those three are the whole model.
- Read one skill end-to-end for the house style — `corp-os-claims` is the most representative.
- `./build.sh` verifies the tree is intact.
- §7 is the work queue. §8 is the do-not-relitigate list.

**House style for skill bodies.** Imperative, addressed to Claude. Every non-obvious instruction states its reason — an instruction whose rationale is missing gets rationalized away under pressure. Name the failure mode being prevented, not just the correct behavior. Under 3000 words; detail goes to `reference/`. No hedging, no "you should".
