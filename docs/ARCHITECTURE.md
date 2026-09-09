# Corp-OS — architecture and decision record

The working document for this project. It records what Corp-OS is, every consequential decision and the reasoning behind it, what has been tested and how, and what is still open. Written so a session that has never seen this repo can pick it up cold and make correct changes.

**Status:** v0.11.0 · 21 skills · 9 reference specs · 6 shipped scripts · 8 commands · 3 eval harnesses · 3 fixtures
**Last substantive change:** the schema work, and the first release where an existing OS has to change shape — which is what the upgrade path built in 0.11.0 was for.

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

Because it is optional, **nothing may treat its presence as evidence that an OS exists.** See §4.10; that mistake shipped in 0.5.0 and is the only path in the suite that destroys a working system.

---

## 2. Repository layout

```
corp-os/
├── .claude-plugin/marketplace.json   # marketplace manifest (points at plugins/corp-os)
├── .validate-denylist                # gitignored; private terms the leakage check greps for
├── plugins/corp-os/                  # the plugin itself
│   ├── .claude-plugin/plugin.json
│   ├── README.md                     # user-facing; the "what and why"
│   ├── CONNECTORS.md                 # tool-category conventions
│   ├── commands/*.md                 # 8 slash commands over the daily path
│   ├── skills/<name>/SKILL.md        # 23 skills
│   ├── reference/*.md                # 10 shared specs, referenced via ${CLAUDE_PLUGIN_ROOT}
│   ├── scripts/*.py                  # 11 -- 9 of them copied into each user's OS
│   │                                 #   scaffold.py and upgrade_os.py are the two that
│   │                                 #   are not: a stale upgrader cannot report itself stale
│   └── examples/
│       ├── config-worked-example.json  # a real config, anonymized
│       ├── fixture-os/                 # a synthetic OS the build runs the script against
│       ├── fixture-register/           # jobs off, renamed vocabulary, a rebuild trap
│       └── fixture-stale/              # two releases behind, asserted to STAY broken
├── evals/                            # three harnesses -- commands, routing, conformance -- and every run
├── scripts/validate.py               # pre-package checks
├── scripts/build_skill_map.py        # regenerates docs/skill-map.html from the plugin
├── build.sh                          # validate + package to dist/corp-os.plugin
├── docs/INSTALL.md                   # installing, both kinds of update, and releasing
├── docs/skill-map.html               # generated; validate.py fails if it has drifted
└── docs/ARCHITECTURE.md              # this file
```

**Conventions.** `Corp-OS` is the product name in prose; `corp-os-*` is the identifier form for skills and never gets title-cased. **All twenty-three skills carry the prefix** — `improve-corp-os` was renamed to `corp-os-improve` in 0.6.0, because the prefix is what lets someone guess a skill name instead of consulting the guide, and one exception costs that for the whole suite. Reference files are shared across skills and addressed as `${CLAUDE_PLUGIN_ROOT}/reference/<file>.md` — never a relative path, which breaks once the plugin is installed elsewhere.

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

A layer must also declare an `entry_schema` and an `index_line` before it may be enabled at all — see §4.9.

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

This is why every index carries a **one-line descriptor** per entry rather than a bare link. A bare link forces a second read; a one-liner answers most questions outright. Since 0.6.0 a layer cannot be enabled without an `index_line`, so the degradation this used to allow is no longer reachable by configuration — only by hand-editing a config past the validator.

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

The unsourced set gets a one-time **disposition pass** in `corp-os-reality-check` — keep as an assumption, retire, or backfill — and then stops being carried. It is bucket 2 of eight, deliberately separate from the overdue list.

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

### 4.9 No layer is enabled without a schema

**Decision (0.6.0):** a layer may only be `enabled` if it declares an `entry_schema` and an `index_line`. This applies to shipped layers and custom ones alike, and it removed `people/` and `topics/` from the default scaffold.

**Why:** both were being scaffolded by `corp-os-setup`, rendered by `build_index.py`, and read by `corp-os-recall` for meeting prep — while `data-model.md` specified a record shape for jobs, claims, raw files, connectors and `meta.json`, and nothing at all for a person or a topic. No skill owned writing either one.

A layer in that state is worse than an absent layer, and worse in a way that is hard to see: it exists, it appears in `INDEX.md`, other skills read it, and it fills with whatever shape the first session to touch it invented. That is precisely the drift the review gate and the scan contract exist to prevent, reintroduced through the scaffold.

The rule has a second effect worth keeping: it forces "what is one entry, and what does one line of it look like in the index" to be answered before the folder exists rather than discovered at forty entries. Anyone who wants a person layer still gets one — the `relationship` profile in `configuration.md` carries the full declaration, and person records are explicitly a *readable view* whose correctness lives in claims, the same way a company record does.

### 4.10 An optional layer is never an existence test

**Decision (0.6.0):** a Corp-OS root is `INDEX.md` + `meta.json`, confirmed by `config.json`. Nothing else.

**Why:** 0.5.0 made jobs optional and shipped both entry-point skills still detecting a root by the presence of `jobs/`. An OS running the `register` profile — jobs off, urgency tiering carrying the priority signal, exactly the configuration §4.2 argued for — read as no OS at all. `corp-os-guide` routed its owner to setup, and `corp-os-setup`'s guard against re-scaffolding over a live OS never fired.

Every other failure in this system degrades quality. This one destroys a working system, and it was introduced by the same release that made the configuration legitimate. That pairing is the general lesson: **when something becomes optional, every place that assumed it is a defect until proven otherwise.** `validate.py` now greps for the pattern.

### 4.11 The cross-cutting rules are enforced, not instructed

**Decision (0.6.0):** pre-flight, config-first, the usage-log row, and the detection rule are checked by `validate.py`. A skill missing one fails the build.

**Why:** §5 of this document has claimed since 0.2.0 that every skill obeys them. When measured, pre-flight was in 5 of 18 and config-first in 13 of 18 — and the absences clustered on exactly the skills where the rules matter most: `intake` and `pull` write to `raw/`, `reality-check` rewrites confidence across the corpus, `redact` decides what leaves the building. All four had neither rule.

A rule that lives in nineteen files by design will drift out of some of them. Writing it down once more does not fix that; the check does. The one sanctioned exemption is `corp-os-audit`, which assesses someone else's system and so has no `usage/log.md` to write to — it is named in `LOG_ROW_EXEMPT` rather than left looking like an oversight.

### 4.12 The leakage denylist lives outside the repo

**Decision (0.6.0):** `validate.py` reads private terms from a gitignored `.validate-denylist`, and falls back to a structural check when absent.

**Why:** the denylist was a hardcoded regex of real personal and company names, committed to a repo whose `plugin.json` points at a public GitHub URL. The check worked; it also published, in one grep-able line, the list of people and companies considered sensitive enough to guard against — more than any single accidental mention would have leaked.

---

### 4.13 A decision layer, because a claim cannot carry an open one

**Decision (0.7.0):** `corp-os-decide` and an optional `decisions` layer, holding forks that have **not** been decided.

**Why:** a `decision` claim records a call that was made. Nothing held the ones that had not been, and the gap kept surfacing — §7.8 carried it as open across three releases, and the audit rubric's own grammatical-form test names "a live fork the person picks between" as a category wanting its own home.

The reason it needs its own shape rather than a claim with a status field is that the two rot differently. **A claim rots by going stale, and a sweep catches it. An open decision rots by going quiet, and nothing catches that.** A decision nobody is tracking does not feel like a problem — it feels like flexibility — right up until the option that mattered has expired and the choice was made by default. That is why `owner` and `decide_by` are required on the record and have no equivalent on a claim, and why the standing review leads with what is past its date and says which option is winning by inaction.

`reversibility` earns its place separately: it sets how much evidence is worth gathering. A reversible call made quickly and corrected beats a one-way call made slowly on the same information, and treating both alike is how a month goes into something that could have been tried in an afternoon.

### 4.14 The trigger-collision question, measured — and answered against the model

**Decision (0.7.0):** `evals/` holds a routing harness: the whole skill roster in front of a model, a query a real person would type, one pick recorded, three repeats.

**Why:** nineteen skills operating on the same object in the same vocabulary for the same person is exactly the shape that produces colliding descriptions, and collision is invisible from reading them — each one looks clear on its own. §7.1 named four likely pairs across three releases and nobody had checked.

**The result went against the prediction.** All four predicted pairs scored 100%: `reality-check` vs `audit`, `configure` vs `rebuild`, "add this" across `intake`/`jobs`/`glossary`, and `pull` vs `improve`. The descriptions discriminate. That settles the merge question on collision grounds — see §8.

What did fail was the newest skill. `corp-os-decide` shipped with "we went with X" and "why did we decide that" in its trigger-phrase list, and duly absorbed queries belonging to `corp-os-claims` and `corp-os-recall`. Its *body* had the boundary stated correctly. **The body is not what routes**, and that is the durable lesson: a skill can be internally correct and still be reached for the wrong things, and only a roster-level test shows it. Moving the counterexamples into explicit not-for position and leading with the tense test took the second run to 100%.

One query was relabelled between runs rather than counted as a miss, and the reason is written into the query itself. A 100% score should be read as *the set is now too easy*, not as routing solved; `evals/README.md` names where the harder cases are.

### 4.15 `processed` is the one sanctioned edit to a raw file

**Decision (0.8.0):** the `processed` flag in raw frontmatter may be flipped to `true`. Nothing else in a raw file is ever edited.

**Why:** this was a live contradiction, not a new rule. `data-model.md` had said raw is "never edited, never summarized in place, never deleted" since 0.1.0, and `corp-os-claims`, `corp-os-pull` and `corp-os-intake` had all instructed flipping `processed: true` for just as long. Both statements shipped in the same plugin for four releases and nobody noticed, because reading either one alone is convincing.

The conformance harness noticed on its first run, by watching a skill edit a raw file and checking it against the invariant.

The flag stays on the file rather than moving to the index because a rebuild reads `raw/` wholesale and has to be able to tell what was already worked; putting that state only in a derived index makes the index authoritative over the source layer, which inverts the model. The invariant is about *what was said* — body, speaker, date, anything citable. Bookkeeping about the file is not part of that.

The general lesson is about how the contradiction survived: an instruction that appears to contradict an invariant does not announce itself. It gets read in whichever direction the reader arrives from, and both readings feel correct. §9 now says to grep for the invariant when adding an instruction that touches a source layer.

### 4.16 Skills are run, not just read

**Decision (0.8.0):** `evals/run_conformance.py` runs a skill against a throwaway copy of the fixture OS and then reads the filesystem to see what it did.

**Why:** every other check in this repo verifies that a skill *says* the right thing. `validate.py` greps for the pre-flight block. The routing eval measures which skill a query reaches. Neither had ever watched one run, and §6 had carried "not tested: every skill's actual behavior in a session" since 0.1.0.

The first run answered a question open since 0.2.0 — **does `usage/log.md` actually get written?** It does, in every case. It also found what reading could not:

- `corp-os-intake` writing the raw file, recounting `meta.json`, filing the proposal, appending the log row — and leaving out the index entry, four runs out of four. By the time the interesting work is done, the bookkeeping feels finished. The fix is a re-read and confirm step, because "remember to do it" was already there and was not enough.
- `corp-os-brief` skipping its dated `meta.json` history entry — the only write a brief makes, and the one that gives the next brief a window.
- The `processed` contradiction above.

**Two of its own assertions were wrong, and that is recorded rather than quietly corrected.** In the first full run `corp-os-intake` and `corp-os-brief` wrote nothing at all — because both correctly refuse to proceed without a person, one asking how to classify ambiguous material and the other asking for a window. Reading that as failure would have "fixed" two skills that were right. And "every new raw file appears in `INDEX.md`" failed a run that had done everything right, because the index lists the *unprocessed queue* and a file processed in the same run drops off it. Both fixes are in the case file with the reason attached. An eval that has never been wrong about the thing it measures has not been looked at hard enough.

### 4.17 Routing is not this suite's risk

**Finding (0.8.0), recorded so it is not re-investigated by reflex.** Three routing iterations, 58 queries, three repeats each. Iteration 3 deliberately added the categories a 100% score should make anyone suspicious of: the person's own renamed vocabulary, phrasings carrying no Corp-OS words at all, mid-conversation fragments, and queries touching two skills where the expected answer is whichever goes first. Every category scored 100%.

The responsible conclusion is not "make the set harder again." It is that nineteen descriptions written to disambiguate each other **do** disambiguate, and eval effort belongs where defects are actually turning up — conformance found three on its first run. §7 is ordered accordingly.

### 4.18 Sensitivity is two axes, and one flag made the OS wrong

**Decision (0.9.0):** every derived entry carries `sensitivity` (the export class) and `bearing` (`incidental` / `load_bearing`). Placement follows `bearing`, not `sensitivity`.

**Why.** The operator said it plainly: a Corp-OS has one person in it, and sensitivity exists so that material does not cross into a multi-person system — not so the person is kept from their own knowledge. And there are layers to it. Some sensitive material's sensitivity is irrelevant to the analysis. Some of it is what makes the analysis correct.

The shipped model had one flag and one behavior: anything `sensitive` went to `sensitive.md`, outside the scan path. That encodes an assumption — that sensitive material is never needed for the daily job — and when the assumption is false the quarantine does not produce a gap. **It produces a confidently wrong answer.** The person does not hear "I don't know about that"; they hear a conclusion computed without the fact that would have changed it, with nothing in the answer signalling an omission. A visible gap is recoverable. An answer that is wrong for an invisible reason is not, and it is worse than never having captured the fact.

So `bearing` decides placement. `incidental` sensitive material quarantines as before. `load_bearing` sensitive material stays in the scan path, marked, and is stripped at the export boundary by `corp-os-redact` — which is the only place confidentiality was ever really enforced anyway, since a quarantine file protects nothing the moment the folder is shared.

**Which way to fail.** Default to `load_bearing` when it is unclear. The errors are not symmetric: wrongly quarantining produces silent wrong answers, while wrongly retaining just gives `corp-os-redact` one more thing to strip — visible, recoverable, and caught by a skill built for it. Same reasoning as a new layer defaulting to `role: source`.

**What `bearing` does not do:** it never affects what may leave. If anything, load-bearing sensitive material is the most dangerous kind at an export boundary, because it is load-bearing precisely by changing conclusions.

### 4.19 The tombstone, invented by a run

**Decision (0.9.0):** a raw file destroyed under a retention obligation is replaced by a tombstone at the same path with a `.deleted.md` suffix — original frontmatter, date, obligation, and the count of entries re-cited. No content from the deleted file.

**Why it is here at all:** nobody designed it. A conformance run asked to carry out a retention deletion invented it unprompted, and it is better than what the spec had. Without one, deletion leaves a hole, and a later rebuild reading `raw/` cannot distinguish "never captured" from "destroyed under obligation" — two situations calling for opposite responses. It also gives the `no source` entries left behind a traceable reason rather than the appearance of sloppiness.

Recorded here mostly as evidence for a claim `corp-os-audit` makes about other people's systems and had never had to face about itself: **anyone running a real system solves problems the model has not.** That turns out to include a model running itself.

### 4.20 One operator, settled

**Decision (0.9.0):** Corp-OS is for one person. Not a limitation awaiting a fix.

**Why:** it had sat in §7 across four releases as "multi-person raises questions this model does not answer." The operator settled it: one person is the intended use case, and sharing is an *export* event handled by `corp-os-redact`, not a mode the OS runs in. That is a cleaner boundary than a shared OS would be, and it is what makes §4.18 coherent — the person sees everything in their own OS precisely because the confidentiality boundary sits at the edge, not inside.

### 4.21 Close-out steps are where instruction stops working

**Finding (0.9.0), not yet a fix.** Across five full conformance runs, the checks that fail are almost always the last step of a skill: `corp-os-brief`'s dated `meta.json` history entry, `corp-os-recall` proposing before writing to an evidence list, `corp-os-redact`'s private log. Never the interesting judgment — always the bookkeeping after it.

`corp-os-redact` is the clearest case. It produced its log under four different names across five runs — `redaction-log`, `redaction-record`, `.redaction-log`, `.LEDGER` — and once not at all. The instruction is present, concrete, explained, and was strengthened twice; the second rewrite moved the log from the end of the skill to the beginning, so it accumulates during the sweep rather than being written up afterward. Variance persists.

The general form is worth naming because it will keep recurring: **a stated filename is not achieving determinism.** Somewhere past "say it clearly and say why", more instruction stops buying reliability. Where every run reinvents the same artifact slightly differently, the fix is a script the skill calls — the way `build_index.py` took the index out of the model's hands entirely and turned "the index is stale" into a thirty-second deterministic operation.

**So two more scripts ship**, both added because measurement demanded them rather than because anyone designed them in.

`scripts/write_export.py` takes the cleaned text and the removal list and writes both files with fixed names, and **it refuses to write the cleaned copy without the log** — one call writes both or neither. That refusal is the design: a guarantee no instruction could make, in the one place where the output that goes missing is the one that makes redaction reviewable rather than a black box.

`scripts/log_run.py` writes the `usage/log.md` row and the dated `meta.json` history entry together, and refuses a blank friction field. It exists because `corp-os-brief` wrote its history entry in **one run out of three** — the same shape of failure, at the same point in a run, in a skill with nothing to do with redaction. Sixteen skills now call it; `corp-os-recall` and `corp-os-guide` call it without `--event`, since they change nothing on disk.

**The general rule these establish, alongside `build_index.py`: a step that has to happen every time, that nothing else will catch if it is skipped, belongs in code.** None of the three exercises judgment — `build_index.py` recounts, `write_export.py` writes what it is handed, `log_run.py` records words the caller supplies, including the friction, which is the one field a script could never invent. The judgment stays with the skill. The bookkeeping that kept getting dropped does not.

**The measured delta.** Re-run at three repeats after the two scripts landed: **68/75 checks at 100% → 73/75.** `corp-os-brief`'s history entry 33% → 100%; redaction's two outputs 67% → 100% and 0% → 100%. The one judgment fix moved too — `corp-os-recall` surfacing a load-bearing sensitive claim went 67% → 100%, and so did the guard against the over-correction that fix caused, which showed up as a *new* 67% in the same run and needed a second sentence naming the other edge.

**What is still not fixed, and what that says.** `corp-os-configure`'s delete sequence sits at **67%** on keeping `raw/` append-only: one run in three still edits the original rather than writing a tombstone beside it and deleting. It has now had two instruction passes, including one that says in as many words *never edit the original into a tombstone — two operations, in that order, on two different paths*. By the rule this release established, the next move is not a third rewrite. It is `delete_source.py`, doing the five steps deterministically: enumerate the citing entries, re-cite them, record the ceiling, log it, write the tombstone, unlink. That is §7.1, and it is the clearest case in the suite for the pattern, because it is also the only sequence whose failure destroys source material.

**What a script cannot fix.** `corp-os-recall` surfaced a load-bearing sensitive claim in two runs out of three — the other third withheld it, apparently out of a reflex that sensitive means hide. That is judgment, not bookkeeping, so there is nothing to hand to code; it took a sharper instruction naming the reflex and why it is wrong. Whether that worked is measurable, which is the point of keeping rates rather than pass/fail.

The measurement lesson stands on its own: `run_conformance.py --repeats` exists because a single run cannot tell a defect from variance, and most of the "failures" that survived to the end of this release were the latter.

### 4.22 `delete_source.py` — the third confirmation

**Decision (0.10.0):** the retention-delete sequence is a script.

**Why:** it held at **67%** after two instruction passes, the second of which said in as many words *never edit the original into a tombstone — two operations, in that order, on two different paths*. One run in three still edited the raw file. With the script: **8/8 checks at 100% across three repeats.**

That is the third time the same rule has held (`build_index.py`, `write_export.py`, `log_run.py`, now this), and this was the case with the most at stake — the only remaining failure that destroys source material rather than degrading quality.

Two details worth keeping. The script is `--dry-run` by default and `--apply` refuses without `--reason`, because the decision belongs to the person and the count is what makes it decidable: *"this destroys the source behind fourteen entries, all of which drop to `no source`"* is something someone can weigh. And re-citing is scoped to the citing entry rather than the file — an earlier draft demoted every `confirmed` claim in any file that merely contained one, which would have destroyed confidence that was never in question, silently, in a script whose entire purpose is not destroying things silently. Found by testing it before shipping it, which is the only reason it did not ship.

### 4.23 Commands, and the loop that made them cheap

**Decision (0.10.0):** eight slash commands, and `evals/run_commands.py`.

The commands cover the moments that recur and where a person would not otherwise reach the skill: `/corp-os` (the entry point), `capture`, `recall`, `brief`, `catchup`, `open`, `check`, `share`. Named for the moment rather than the skill — someone reaching for the export boundary is thinking "share this", not "redact". Deliberately absent: setup, configure, rebuild, audit, improve. Those are rare and deliberate, you ask for them by name, and `run_routing.py` shows they land at 100% that way. A command for every skill is surface area with no return.

**The harness matters more than the commands.** Conformance takes half an hour because every case runs a whole skill against a whole OS. A command does not need that: it is a thin file whose only job is reaching the right skill with the right scope, which one short call can answer. The sweep runs in **about a minute**, and that is a different way of working — a minute is a loop you stay inside, thirty is a loop you leave and come back to, and wording is exactly the kind of thing that needs the first.

It paid immediately. Four of the five things the first runs surfaced were the harness rather than the commands, found and fixed inside a minute each: the model answering "that skill isn't installed here" when asked a routing question; the picker cases scoring 0% while picking correctly every time, because they answered in command names and the scorer wanted skill names. And three cases were **removed rather than fixed** — they asked whether `configure`, `rebuild` and `audit` are reachable without a command, which is a routing question that `run_routing.py` already answers at 100%. Contorting a harness to ask a question another one asks better makes both worse.

**What it settled.** §7 carried "do the slash commands earn their place?" as an open question. Seven `picker` cases — plain English, roster only, nothing but eight one-liners to choose between — land at 100% across three repeats. Eight descriptions about the same knowledge base are distinguishable. The roster earns its place, and that is measured rather than argued.

**The static half is not an afterthought.** `validate.py` checks what needs no model: description length (they sit one line each in a picker), no two descriptions opening alike, every command naming a real skill, `$ARGUMENTS` handled, and the no-args path stated rather than left to chance. That last one caught two commands that never said what an empty invocation does — the path most people take first.

### 4.24 The first bug found by using it

**Reported (0.10.1):** day one of a real OS. Three dashboards registered, `INDEX.md` reporting one, no warning.

`build_index.py` branches its counting on the *shape* of a layer's declared path: ending in `/` means one file per entry, ending in `.md` means one file of many headers. The shipped model put the registry at `dashboards/registry.md` — a directory-shaped path over a single-file-shaped layer. With one dashboard registered both readings give 1, so it was invisible for five releases and only appeared on the second entry. Dashboards were also absent from `DEFAULT_LAYERS`, which is the same gap: the layer nobody counted is the layer nobody noticed was miscounted.

**Fixed** by moving the registry to a root-level `dashboards.md`, beside `glossary.md`, `connectors.md` and `design.md`. The bug existed only because dashboards broke a convention the other three already kept, and the consistency is the actual repair.

**And argued back.** The report explicitly declined a generic path/shape check in `build_index.py`, on the grounds that the layout fix removes the class more cheaply than a heuristic needing its own maintenance. That is right about the shipped layers and wrong about the ones that matter: `corp-os-configure` Step 3 walks people through declaring custom layers *with their own paths*, so the class recurs on shapes no layout fix reaches. The check is in, with the disagreement recorded in a comment beside it. It survives the objection because it is not a heuristic — a directory path holding exactly one file with more than one entry header is an exact condition — and because it warns rather than fails.

Adding it exposed a second one immediately: a layer whose path points at a file *inside* a directory left that directory in the "undeclared directories" list, so anyone following the new warning's advice earned a second complaint for the same layer. Fixed in the same pass. A warning that makes the tree noisier when obeyed is a warning people learn to skip.

**Also from the same report:** a home/index dashboard as the eighth pattern, gated on a second dashboard already existing, and a hand-off to `corp-os-configure` from `corp-os-intake` and `corp-os-dashboard` when material implies a layer that has not been declared.

### 4.25 A hand-off that instruction does not reach

`dashboard-missing-layer` asks for a stakeholder map against an OS with no person layer. Five runs, three behaviors: one declared `people/` with role, schema, `index_line`, `order_by` and decay behind a written proposal; one filed the proposal and built the view from what already existed; three built the view and mentioned the gap only in the answer, where it died with the session. **2/5.**

The first two versions of this case's assertion were wrong about the skill rather than the reverse, which is now the fifth time in this suite. v1 checked that the answer contained the string `corp-os-configure` — it failed the run that did everything right and simply never said the name. v2 checked that `config.json` changed — that picks a winner between two legitimate paths. What survives is what both correct runs did and no incorrect one did: leave a proposal behind, and leave no layer in the incomplete-index banner.

A wording pass making the proposal requirement explicit was tried and measured at **0/2**, and reverted. Prose that does not move the number is churn, and §4.21's rule does not apply here: this is not a close-out step a script can take over. Deciding a layer is warranted is judgment, and the runs that miss it leave nothing mechanical to catch — no dangling reference, no undeclared directory, because they infer the view from layers that do exist. Recorded as an open number rather than patched a third time.

### 4.26 Updating the plugin updated nobody's OS

**Decision (0.11.0):** `upgrade_os.py`, the fifth shipped script, and `corp-os-upgrade`, the twentieth skill.

Every Corp-OS carries its own copies of the shipped scripts. That is deliberate twice over: an OS should keep working when the plugin is not loaded, and sixteen skills call `log_run.py` at the OS path rather than the plugin path, so the OS has to have one. The consequence went unnoticed for eleven releases. **Updating the plugin updates nothing inside anyone's OS.** 0.10.1 fixed how `build_index.py` counts a single-file layer; every OS built before it kept the copy that counts wrong, and there was no mechanism, no warning, and no release note that would have told anyone.

Three parts, and the split between them is the decision:

**Bookkeeping goes in the script.** Comparing four files, copying what differs, stamping a version, appending a history row. It has to happen every time, nothing else catches it when skipped, so it is code — the same rule that produced `build_index.py`, `write_export.py`, `log_run.py` and `delete_source.py`. The comparison is by **content, not mtime**: a copy restored from a backup has a new date and old behavior, and the date is the thing a person would naturally check.

**Judgment stays in a skill, and the skill hands it on.** A layout migration moves the person's own files. `upgrade_os.py` detects and names them and refuses to perform them, and `corp-os-upgrade` routes them to `corp-os-configure`, which already treats a migration as a migration: enumerate, plan, confirm. The temptation here is sharper than anywhere else in the suite, because the fix is one `mv` and the person literally asked to bring the folder in line. That is precisely why the script is not allowed to do it.

**Migrations are detected from disk, never from the recorded version.** Every OS built before this release records no version at all, and those are exactly the ones that need the check. A migration keyed on a version string would have been invisible to its entire audience.

**Two smaller bugs of the same species, found while fixing this one.** `scaffold.py` hard-coded the version it stamped into every OS it created, and it was already a release stale — it reads `plugin.json` now, because a wrong recorded version is worse than none once something compares against it. And `corp-os-setup` carried a prose list of the scripts to copy that said *"both shipped scripts"* and named two, three releases after there were four. The list is deleted rather than corrected: `scaffold.py` already does the copying, so the prose was duplicating a fact it had no way to keep. What survives is a validator check that the two remaining copies of that list — `scaffold.py`'s `SHIPPED` and `upgrade_os.py`'s — still agree.

**A third fixture, asserted to stay broken.** `fixture-stale` is an OS two releases behind: an older `build_index.py`, no `delete_source.py`, version `0.9.0`, and the pre-0.10.1 dashboards layout. The validator asserts all four are *still wrong*, because the failure mode for a deliberately-broken fixture is somebody tidying it — and a repaired fixture leaves the upgrade case passing against an OS with nothing to upgrade, which reads as coverage and is worse than no case at all. It is also kept out of the `build_index` execution loop on purpose: running the counter over it warns every time, and a validator that always warns has taught everyone to skip its output.

### 4.27 No script had ever run in a conformance run

**Found (0.11.0):** while diagnosing why `corp-os-upgrade` wrote nothing at all.

The harness invokes `claude -p ... --permission-mode acceptEdits`. That auto-approves file edits and **nothing else**. Every `python3 scripts/...` invocation, in every skill, in every conformance run since the harness was written, was answered with `This command requires approval` and never executed.

Verified three ways before believing it: the plugin-root path, a bare relative path with the workspace as cwd, and with the plugin directory added to `--add-dir`, which changed nothing because the gate is the tool rather than the path. `--allowedTools Bash` fixes it, confirmed by watching `build_index.py` actually print its output.

**What this invalidates, and what it does not.** The file-level outcomes were real: a check that looked for a `usage/log.md` row was looking at a real file that really had a row. What was never measured is *what put it there*. The model, told to run a script and blocked from running it, wrote the row by hand — competently, which is why nothing looked wrong. So every claim in this record of the form "the script landed the step" was measuring the model imitating the script's output. §4.21 and §4.22 are written as if the script ran. They should be read as: with the script present and the instruction pointing at it, the outcome improved. That is a weaker and different claim.

**What it cost.** `setup-from-empty` sat at 2/9–3/10 across six runs and three configurations, and §7 carried it as the top open question with the diagnosis that the skill "loses structure to vocabulary." `corp-os-setup` Step 3 runs `scaffold.py`, which had never once executed. Three instruction passes were made against a harness defect, and one of them wrote a paragraph into the skill explaining a failure that was not happening. With the fix: **9/10, twice.** The remaining failure was the universal raw-file check counting `raw/README.md` as an entry — the scaffolder writes it, and `build_index.py`'s own `md_files()` has always excluded `README.md` and `INDEX.md` from every layer. The check now excludes them too.

**The lesson is not "check the permission mode."** It is that this suite spent six runs and three rewrites treating a consistent, plausible failure as evidence about the skill, without once testing the instrument. The harness had been trusted because it had found real defects — which it had, and which made it harder to suspect. A number that will not move after two honest attempts is evidence about the measurement at least as often as about the thing measured, and the cost of checking is one minute.

### 4.28 The skill map is generated, because a written one would go stale

**Decision (0.11.1):** `scripts/build_skill_map.py` &rarr; `docs/skill-map.html`, checked by `validate.py`.

A one-page map of the suite is the thing a new operator wants and the thing a maintainer keeps re-deriving in their head. Written by hand and committed, it is also a file that states how many skills exist, what each does, what each refuses, and what the eval numbers are — every one of which is a fact already true somewhere else.

This project has now found that same defect four times: `corp-os-setup` saying *"both shipped scripts"* three releases after there were four; `scaffold.py` hard-coding a version that was stale within one release; `corpos_version` living in six files with six different values; and a dashboards registry that counted 1 for five releases. A static skill map would have been the fifth, and it would have gone wrong the same week someone added a skill.

So the page is generated. Descriptions are parsed out of the frontmatter that already holds them — and split three ways, because a description already carries three separate things: what the skill does, the phrases that should reach it, and what it refuses. The counts are `len()`. The command roster reads the command files and resolves which skill each names. What each script makes deterministic is its own docstring. Which scripts an OS carries is read from `scaffold.py`'s `SHIPPED`, the same single source the upgrade path uses. The invariants are parsed from the README, so the page says *five* because it counted them. Even the eval figures are read from the committed run reports, because a page that hard-codes **100%** keeps saying it after the number moves.

**What is declared by hand is the part that is judgment.** Which phase a skill belongs to cannot be derived from anything, so it is stated once, in the generator, and the generator **refuses to run** if a skill on disk has not been placed. Add a twenty-second skill and the build fails until someone decides where it goes. That is the correct amount of friction: placing it takes ten seconds, and it is the only part of the page a person is needed for.

**The phases themselves are a claim worth arguing with.** Thirteen skills form a loop — Capture, Curate, Consult, Correct, Release — and the other eight act on the OS rather than on what it holds, so they are not a sequence and are not numbered. That split is not invented for the page; it is the one already made in &sect;4.23, when the command set deliberately left out `setup`, `configure`, `rebuild`, `audit` and `improve` as rare and deliberate enough to name.

**The page and the published artifact are the same bytes.** `--fragment` emits the head-less form an Artifact wants; `docs/skill-map.html` is the standalone document a browser opens off disk. One template, so the shared link and the repo cannot drift.

### 4.29 What an audit of a real OS found that eleven releases of evals did not

**Release 0.12.0.** Every prior finding in this record came from the suite: a check that fired, a rate that would not move, a harness that lied. 0.12.0 came from someone running the thing on 220 sources and 836 claims for a day and then auditing it. The findings are a different species, and the difference is worth stating because it says what the suite is blind to.

The evals measure **whether a skill does what it says**. They cannot measure **whether the model can hold the thing being built**. Every 0.12.0 finding is the second kind: a field that cannot express what an operator needs, a boundary that is correct per entry and wrong in aggregate, an instruction with nowhere durable to live.

**The one that destroys something.** An operator gave an instruction that overrides the schema — content that must not reach a particular person record, with no pointer left anywhere. Placement is schema-driven, and regeneration is safe *because* placement is schema-driven, so the override was unrepresentable and got written into a derived file outside the scan path. A rebuild — the operation this suite *recommends* when a derived layer tangles — would have honoured the schema, violated the instruction, and had the raw source still sitting there as justification. `placement:` in raw frontmatter fixes it, and the validator fails unless both ends exist: intake writing it and rebuild reading it. An override written and never read is not an override.

**The one that was correct everywhere and wrong anyway.** Sensitivity is set per entry; the thing being protected is the source text. The model mints entries per topic, so one quote yields several entries across several files written by several passes, and nothing reconciles their classifications. Per-entry redaction was mechanically correct on all 836 claims and the export still leaked: it withheld the sensitive member as a stub and emitted the byte-identical quote in full, twice. **Every per-entry check passes on that corpus.** `check_citations.py` clusters on the quote and refuses.

**The one nobody had noticed was structural.** A migration verifies everything on the day it runs, so every decay window fires on the same day: 79 entries, then 71, then 410. The rubric already said a backlog nobody can clear teaches people to skip the sweep entirely, so a migrated OS was born with its central discipline pre-broken — and every teammate migrating into their own OS gets the same phase, so a team reaches its cliffs together and concludes collectively that the machinery was decorative. Neither the audit nor the packet listed it as a model finding; both had it as a local scheduling problem.

**And the fix that was wrong the first time.** The plan said spread the `Verified` dates. Writing the script made it obvious that this falsifies a record in a system whose entire premise is provenance — asserting a review happened on a day no review happened, with every count and sweep downstream inheriting it. The **window** is the policy choice and the date is the fact, so the window is what varies. `stagger_decay.py` never touches a verification date.

### 4.30 Two proposals from the packet were declined, and one was promoted

Worth recording because the packet is a good document and these are the parts to argue with.

**A reason suffix on an enum breaks every parser.** S5 is right that `needs_review` covers three situations — thin source, genuinely contested, and a paraphrase that cannot satisfy a verbatim requirement — and that a sweep cannot triage them apart. But the proposed `needs_review — explicitly an open unknown` puts free text inside a value that `build_index.py`, the export emitter, every ceiling rule and every eval assertion equality-tests. Sibling fields carry the same information at no migration cost. The packet's own argument against the prior system's compact tag applies one level further than it took it.

**F7 proposed the approach measured as failing.** Its diagnosis is the best-evidenced thing in the document — zero usage rows after a full-day migration — and its fix, *"make the row a required output of the operations themselves"*, is more instruction aimed at the least-attended moment of a run. That is what §4.21 and §4.22 exist to record. Its own "cheaper interim" was the real answer and is what shipped: `build_index.py` says when the log has no rows while the derived layer is full. **The detector, not the instruction.**

**And one correction that changed what got built.** The packet listed F5 (render `rests_on` as *N claims / M sources*) and S1 (an argument-across-claims layer) as independent deltas. `rests_on` does not exist in the shipped model — not in `data-model.md`, not in any skill, not in any script. It is the reporting operator's own convention. So F5 is not a rendering fix to an existing field; it is part of the schema of a field that has to be introduced first. They are one proposal, deferred together.

### 4.31 Patterns, and the one rule that makes them portable

**Decision (0.13.0):** a pattern layer, `bind_pattern.py`, and `corp-os-pattern`.

Every mechanism in this suite up to now served one operator. Patterns are the first that exists because of a problem that only appears with more than one: five people produce five dashboards with five palettes and five ideas about what a panel owes the reader, and nothing in the model prevented it.

**The load-bearing decision is how a requirement is addressed.** A pattern names the **role** a layer plays and the **fields** it reads, never the layer's name. `claims/` binds in exactly one OS — the one the pattern was written in — and fails everywhere else by rendering an empty panel, which reads as a state rather than a defect and so nobody investigates it. `role: derived, fields: [citation, confidence]` binds in an OS that calls them findings.

That is not an argument, it is a test, and the register fixture is the test: it renamed `claim` to `entry` and disabled `jobs`. The shipped job-board pattern, unmodified, **bound its claims requirement anyway and refused its jobs requirement precisely** — *"no enabled layer with role `derived` looks like `jobs`"*. Portability demonstrated and the limit demonstrated in the same run.

**Three outcomes and no fourth.** Bound; bound with drops, named out loud; or refused with the missing role stated. A refusal hands off to `corp-os-configure`. What a binding never does is degrade quietly, because the failure mode of this whole class of tool is an empty panel that looks like an answer.

**The test of whether it earned its place is that `corp-os-dashboard` got smaller.** It carried nine composition rules as prose that a model had to hold on every build; the dashboard write-up would have added nine more. They are pattern fields and shared composition rules now, checked once at bind time. If the dashboard skill had grown, the design was wrong.

**A pack is `upgrade_os.py`'s problem one layer up,** and it reuses that mechanism rather than inventing a second: teammates carry copies of files someone else maintains, copies drift, and updating the pack updates nobody's OS. Compare by content, record the version, report the drift, refuse to migrate. A local edit shows as drift rather than being overwritten — someone who diverged on purpose should be told they did, not corrected.

### 4.32 The screen-share shield

**Reported from a real build, and it is the sharpest instance of a tension this model creates deliberately.**

`bearing` keeps `sensitive` + `load_bearing` material in the scan path on purpose, because quarantining it produces confidently wrong answers rather than visible gaps (§4.18). A dashboard reads the scan path. **So the moment a dashboard is genuinely useful is also the moment it is dangerous**, and that follows from the model working as designed rather than from anyone's mistake.

**Redact in the markup; let script reveal.** The inverse — render visible, hide with JS — is visible whenever the script fails, loads late, or is disabled, which is exactly the moment it matters. The rule is mechanically checkable and `check_shield.py` checks it: strip every `<script>` block and every parked attribute, reduce to visible text, grep for known probes. **On the build that produced this rule, that test found three leaks in a shield its author believed worked.**

**Default hidden, every load, no persistence.** Forgetting to re-hide before sharing is a disclosure; one extra click is an inconvenience. Not symmetric, so fail toward the recoverable one — the same reasoning that makes `load_bearing` the default. The script greps for `localStorage` for this reason.

**Sensitivity has to be declared, and it is not only on claims.** Decisions inherit from what they rest on — 6 of 18 in one OS, none of which reading the decision records would have caught. A person record is sensitive only when their role or status *is* the protected fact: 2 of 53, and over-applying it hides most of a directory for nothing.

**The aggregation leak is the one nobody predicts.** A search view stubbed its sensitive hits correctly, and the *"who said it"* panel counted their speakers anyway: **three speakers with the shield down, two with it up.** The name is the disclosure. Every derived summary is computed over the filtered set, never the raw one, and this is the easiest thing in the whole design to get wrong because each individual result looks correctly redacted.

**A shield is not a boundary.** The shield protects a screen; a redacted build protects a file that leaves. Both ship and neither implies the other — and a redacted build filters once at the data-load boundary, because per-panel filtering is how a view added later arrives without the filter. One implementation filtered only its search index while three other views rendered the same material in place, disclosed it honestly in three places, and disclosure is not a fix.

### 4.33 A check that could not fail

Worth recording because it nearly shipped.

The validator gained a check that every shipped pattern binds against the default fixture. It passed. It also passed when the pattern was deliberately broken — because the subprocess was handed a path built against the repo root while the loop runs with cwd at the plugin, so `bind_pattern.py` exited with a file-not-found error rather than the word the check greps for.

A check that cannot fail is worse than no check, because it is counted as coverage. The only reason it surfaced is the repo's own rule: negative-test every check you add, by reintroducing the defect and confirming it fires. It did not fire, and that is the entire value of the rule.

### 4.34 One enum was carrying three questions

**Decision (0.14.0):** `source_fidelity`, separate from `confidence`.

Confidence was answering three independent things at once: how faithful is the *medium* (a quote, a paraphrase, a reconstruction, or the original is gone), how many independent sources exist, and is the claim contested. Two of those are about evidence and one is about the recording.

**What the collapse made invisible.** In the reporting corpus, **599 of 836 claims** were single-source summaries parked one step below the top value, and the config documented two routes upward — a second recording, or pulling the verbatim transcript through the same connector that produced the summary. The second is one API call. **Zero claims had taken it.** Meanwhile 60 claims sat lower because their originals genuinely no longer exist, and nothing distinguished the two populations. A ceiling that is *elective* looked exactly like one that is *permanent*, so it was treated as permanent.

Splitting the medium out makes the difference expressible, and the index renders it as **One call from promotion** — a count of what is one step from being stronger, which is a different and more actionable object than a list of what is weak.

**Why it is read rather than judged.** Fidelity is a property of the source, so `corp-os-connect` records each connector's `Medium` and `Verbatim fetch` and `corp-os-claims` reads them. Deciding it per entry would reintroduce exactly the per-entry judgment the field exists to remove, and `retrievable` is derived rather than stored so that disconnecting a source changes the backlog instead of leaving a field lying.

### 4.35 F5 and S1 were one proposal

The packet listed them separately: render `rests_on` as *N claims / M sources*, and add an argument-across-claims layer. But `rests_on` did not exist anywhere in the shipped model — not in `data-model.md`, not in a skill, not in a script. It was the reporting operator's own convention, and the audit says so in passing when it notes the claims layer had no `entry_schema` at all.

So the rendering rule was not a fix to an existing field. It was **part of the schema of a field that had to be introduced first**, and they ship together or not at all.

The rendering rule is the interesting half. A supporting-entry count reads as evidence breadth and does not measure it: entries are minted at whatever granularity a pass chose, so one conversation that yielded nine contributes nine. Measured: an argument resting on **nine entries that all traced to a single meeting** — one data point wearing a number that looked like breadth. It renders as two numbers always, and the index lists any argument whose distinct-source count is 1.

Deliberately **not** restored: the prior system's hand-set signal-strength rating, dropped in its migration as decorative. Its actual function was counting independent witnesses, which is derived for free and cannot go stale. A hand-set number that measures something derivable is a second source of truth with extra steps.

### 4.36 The line a schema migration draws

**Decision (0.14.0):** `migrate_schema.py`, and the division of labour with `corp-os-upgrade`.

`upgrade_os.py` has named migrations and refused to perform them since 0.11.0, on the grounds that moving someone's files is judgment. 0.14 is the first release that gives it anything to name, and it needed the other half: something that performs the migrations that are *not* judgment.

The line: **a field whose value is derivable is bookkeeping; a field whose value is a judgment is not.** `source_fidelity` is derivable from the connector record, so it is filled mechanically. What no connector record answers is **left blank and counted**, because a blank field someone can see is honest and a plausible wrong value is the failure this whole model exists to prevent. The validator fails if that sentence ever leaves the script.

Two more things were deliberately not made mechanical. `aliases` reads both the bare-string and object shapes, because requiring the object form would break every existing person record and the goal is to make an unconfirmed merge *visible*, not to force a migration. And nothing auto-promotes on `retrievable`: the point of making a route visible is that someone takes it, not that a number rises. Promotion still needs a person and an actual fetch.

### 4.37 A reason belongs beside a value, never inside it

The packet proposed letting a confidence value carry its own justification: `needs_review — explicitly an open unknown`. The observation behind it is right — one label covers a thin source, a genuinely contested reading, and a paraphrase that cannot satisfy a verbatim requirement, and a sweep cannot triage them apart.

The form is wrong, and it is a technical objection rather than a stylistic one: everything that reads confidence equality-tests that string, including `build_index.py`, the export emitter, every ceiling rule and every eval assertion in the suite. `Confidence reason` as a sibling field carries the same information at no migration cost.

The packet's own argument against the prior system's compact tag — unparseable, un-greppable — applies one level further than it took it. The validator now greps every reference doc and skill for a reason written inside a confidence value, because a declined idea comes back through a doc example.

### 4.38 The suite found a missing gate, in the skill whose job is removing things

The `fidelity-backlog` case was written to test the promotion backlog. It found something else.

The cross-cutting check that every derived-layer write has a proposal behind it **failed on three of the first four runs of `corp-os-reality-check`** — one of them rewriting fourteen files and filing nothing. Reading the skill afterwards: it had no gate step at all. Not a weak one, none. It has shipped that way since 0.1.

That is the worst skill in the suite to be missing it. A sweep is the operation most likely to *remove* things — retire an entry, downgrade a confidence, drop an assumption — and the declines are the valuable part of the gate's record: the only trace of what someone deliberately chose not to keep. A retirement that happened in conversation and nowhere else is indistinguishable, six months later, from something that was never there.

Step 1.5 was added and the check went to **2/2**. Nothing about this was visible to review; it took a cross-cutting assertion running against a skill nobody suspected.

**And in the same case, a needle that measured nothing.** `fetch` in the answer scored 1/2, then 2/2, then 0/2 across three batches. That spread is a coin flip on a word, not a skill behaving inconsistently: a run can treat the backlog as entirely actionable while writing *"pull the transcript"* or *"the original is still available"*. Removed, with the evidence stated — the fourth time this suite has checked for vocabulary and called it behaviour.

What is left unmeasured, said plainly rather than papered over: whether the backlog is *framed* as actionable. That is a quality judgment about an answer and this harness cannot see it. The safety-critical half — nothing promoted without an actual fetch — is checkable, and has held on every run.

### 4.39 The version pin, and the two things called "update"

**Decision (0.14.1):** `docs/INSTALL.md`, and a version bump for a documentation-only change.

Two failures sit in the same place and neither announces itself.

**The first is the pin.** A client caches an installed plugin by **version string**, at `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, and a cache hit never touches the network. So a release that ships new commits without bumping `plugin.json` reaches nobody: no error, no warning, and nothing the person running it could inspect to find out. It is the worst shape of failure this project keeps meeting — correct on the maintainer's disk, wrong everywhere else, and silent in both directions. The rule it produces is one line: **the version is bumped on every release, or the release did not happen.** That is also why this documentation change has a version. `plugins/corp-os/README.md` ships *inside* the plugin, so correcting it without a bump would have corrected it for nobody, which would have been a joke at the expense of the file being added.

**The second is the ambiguity in the word.** §4.26 established that updating the plugin updates nothing inside anyone's OS, and shipped `corp-os-upgrade` to close it. What it did not do was say so anywhere a person looks *before* they have a problem. The install instructions were four lines pointing at a `.plugin` file — which, checked against the client's actual documented surface, is not an install path at all. `dist/corp-os.plugin` is a zip of the plugin directory: useful for proving the package is well-formed and for attaching an exact copy to a release, and not something any client installs. Telling people to install it was telling them to do something that does not work.

So `docs/INSTALL.md` leads with the distinction rather than burying it: **updating the plugin replaces the skills; updating your OS brings the folder in line with them; doing the first does nothing to the second.** Both READMEs now carry the short form and link to it.

**And two stated counts had gone stale, which is this project's oldest defect showing up again.** The repository README said nineteen skills three releases after there were twenty-three; the plugin README said twenty-one. The list is now long enough to be its own argument: *"both shipped scripts"* three releases after there were four, a hard-coded version stale within one release, `corpos_version` in six files with six values, a registry that counted 1 for five releases, a skill map that §4.28 caught before it shipped, and now two README sentences that were not caught at all. Every one is a fact that was already true on disk, retyped somewhere nothing recounts. `validate.py` counts the skill directories and reads the number out of the prose, and it fails on drift in either direction — including when the sentence is reworded so the pattern stops matching, because a check that silently stops checking is the same defect one level up. Two skills were also missing from the plugin README's own tables: shipped, described in the version history, and absent from the list somebody actually reads.

The alternative was to generate the counts the way `docs/skill-map.html` is generated. Rejected for prose: a README whose sentences are assembled reads like a changelog, and the sentence *"a folder of markdown files plus twenty-three skills that operate on it"* is doing rhetorical work that a rendered number would not. Checking a hand-written sentence keeps the prose and removes the drift, which is the right trade wherever the prose is the point.

### 4.40 Decay was modelled on the claim and not on what is built from it

**Decision (0.15.0):** `build_index.py` renders **Resting on evidence that has gone stale**, and `Rests on` is generalized off the arguments layer.

This came from an audit of a second, independently built skill set rather than from this one's own usage, which is what `corp-os-audit`'s tenth dimension exists to produce. The audited system had aimed a whole skill at a related problem — a figure repeated until it feels settled, traced back before it carries weight — and looking for the equivalent here found a different hole next door.

**The hole.** Every claim carries a decay window and `corp-os-reality-check` sweeps them. Nothing carries decay for the *things built from claims*. `dashboards.md` has shipped since 0.10.1 recording a dashboard's URL, owning job and source files; the claims behind it decay underneath it and the registry says nothing. A dashboard registered in March off four claims, two past their window in June, is indistinguishable from one refreshed yesterday. The same exposure appears the moment anyone declares a layer for authored documents that cite the corpus, which is the case that surfaced it.

Every field needed to detect this was already on disk. This is the third time that has been the finding — open evidence across jobs, arguments resting on one source, and now this — and the pattern is worth naming: **the defects that survive longest here are joins nobody performed, not facts nobody recorded.** A view is cheaper than a field, and this repo keeps discovering it needed the view.

**Why `Rests on` rather than a new field.** 0.14.0 introduced it for the arguments layer, and a second citation field for record layers would have been the same concept under two names with two parsers, which is how they drift apart. So it is generalized, one parser reads it, and both views that consume it apply wherever it appears. The constraint that keeps it honest is *bounded*: an output built from a whole layer has nothing to list and keeps `Source files`. Listing a folder in `Rests on` would render as breadth that was never measured, which is precisely the failure §4.31's `N entries / M sources` rendering exists to prevent.

**What is reported, and what deliberately is not.** An entry declaring no decay window is not the same as one whose window is `none`, and neither is stale. A cited entry that was never verified is counted separately in the same line, because *aged* and *never confirmed* are different weaknesses and a single number would hide which one you have.

### 4.41 A binder validating against a list it never had to honour

**Decision (0.15.0):** a second pattern kind in the fixture, with a generator the validator executes.

`bind_pattern.py` has accepted five `kind` values since 0.13.0. The fixture carried one pattern and it was a `dashboard`, so four of those values had no fixture, no binding and no generator behind them. That is the same defect as §4.33's check that could not fail: surface counted as coverage without ever having been exercised.

`doc-initiative-evidence` is the second kind, and it is a real pattern rather than a test double — it renders the evidence brief someone reads before writing a spec, which is what the audit's own comparison kept pointing at. Its generator lives in the fixture, and the validator runs it and asserts it emits the `Rests on` line, because §4.31 already established that a pattern's script is the artifact and asserting the frontmatter parses says nothing about whether the thing it names works.

One check earned its keep immediately. The first negative test of the generator assertion was written with `sed`, the substitution silently failed to match, and the test passed while proving nothing. Re-running it with an assertion that the string was actually found is what turned a green result into a real one.

### 4.42 The version pin, enforced

**Decision (0.15.0):** `validate.py` fails when plugin content has been committed since the last version bump.

0.14.1 documented that a client caches an installed plugin by version string and that commits without a bump reach nobody, silently. Documenting it was the fix for a person reading the docs; it did nothing for the person who does not. This repo's own rule is that a step which has to happen every time and that nothing else catches belongs in code, and this is one — with the aggravating property that its failure is invisible from the inside by construction.

The design decision inside the check is *when* it fires. Reading the working tree would make it red during normal editing, and a check that is red while someone works is one everybody learns to ignore — the same reasoning that removed the `note`-key warning in 0.12.0. So it reads committed history only: find the newest commit still carrying the current version, and fail if anything under `plugins/corp-os/` has been committed after it. That is quiet during the work and loud between committing and pushing, which is the only moment the answer can still change.


### 4.43 Seventeen skills read one file for one section of it

**Decision (0.16.0):** `data-model.md` splits into a spine, `claim-record.md` and `records.md`.

The house style says a skill states the reason for every non-obvious instruction, and that is right for a skill: it is read once, under pressure, by something that will otherwise rationalize the rule away. A **reference spec re-read on every run has different economics**, and nobody had priced it. `data-model.md` reached 6,857 words carrying the reasoning for every field it defines, and seventeen skills named it. `corp-os-connect` needs 118 words of connector registry.

The split is mechanical and the enforcement is not. A check that accepted a schema field *anywhere* in the three files would not notice one drifting into the spine, whose readers are a different set of skills — so the check names the file each field belongs to and, when it misses, says which file it found it in instead. That is the difference between a check that guards the split and one that merely counts words.

The trim is deliberately not done here. Moving the *why* out of the reference and into this file is a further cut of roughly 2,500 words from the claim record, and it is a judgment about what a maintainer needs at runtime versus what belongs in the record. Worth doing; worth doing separately from a refactor that changed nothing.

### 4.44 The scan contract is correct and does not scale

**Decision (0.16.0):** `find.py`, the eleventh shipped script.

`INDEX.md` → layer index → detail file is the right order to *look*. It is the wrong unit to *read*. A question about one entry costs the file that contains it — 156 tokens per claim on a real shape, so a forty-entry topic file costs all forty — and the index is read on every run while growing linearly with the corpus. Neither cost is visible until the corpus is large, at which point it is the dominant per-run expense and structural.

`find.py` applies the rule this repo has applied nine times already: **selecting by id, job, topic, confidence or decay state is bookkeeping; what the matches mean is judgment.** It returns matches rather than files, and `--digest` renders one line per entry at about a fifth the cost — usually enough to decide which ones are needed in full.

Two refusals are load-bearing. It rejects an unscoped search, because returning the corpus is what the index is for. And it never returns from `proposals/`: unreviewed material arriving in the same shape as reviewed material is the exact failure the gate exists to prevent, and a search tool is the easiest place to reintroduce it by accident.

### 4.45 Two entry encodings, and a reader that silently saw half

**Found while building §4.44.** A corpus stores entries two ways, both legitimate and both in the shipped fixture: many per file as `### ID — statement` blocks with bold-label fields, and one per file with its fields in YAML frontmatter. `build_index.py` has always handled both. The evidence generator shipped in 0.15.0 handled one.

Against a fixture holding two open decisions it reported **"0 open decisions"**. No error, no warning, and the number looked plausible enough that it passed review — including mine, in the release notes. It surfaced only because a second tool was written over the same corpus and disagreed.

The general form is worth naming: **a reader that silently halves its input is worse than one that crashes**, because the output is well-formed and the omission is invisible. It is the same class as the harness that never ran a script (§4.27) and the dashboards registry that counted 1 for five releases (§4.24) — correct-looking output produced by a component that was never exercised against the case it got wrong. The validator now asserts a match from each encoding, which is the cheapest possible guard and would have caught it on the day.


### 4.46 The system could not see its own cost

**Decision (0.17.0):** `capture` in config, a pass declaration on every skill, and measured volume in the usage log.

A single intake run over two connectors cost **$40**. Sixteen releases of eval harnesses, a validator and an improvement loop would not have caught it, and the reason is structural: **`usage/log.md` recorded friction and nothing else**, so a run that moved forty transcripts through the model left the same row as one that answered a question. `corp-os-improve` could rank skills by friction and by no other dimension, because no other dimension was recorded.

The cost itself came from an instruction that is correct. `corp-os-pull` says content goes in as retrieved, do not summarize or rewrite — right for fidelity, and honourable only by re-emitting every byte as output, which is priced several times input. Add *"retrieve everything since its cutoff"* with no cap and the worst case is unbounded by design.

**This is §4.21's rule broken in the largest case in the suite.** A step that has to happen every time, that nothing else catches, belongs in code — and nine of them were moved there. Copying bytes from a connector into a file is that step at the highest volume in the system, and it stayed with the model because it does not present as a step. It presents as content.

Three things changed, and the ordering matters. **Triage before fetch** is the cut that costs no fidelity for what is kept: retrieve the list, decide, fetch what survives. **A batch cap** bounds the worst case, which is always the first run after a holiday. **A recorded model and a measured byte count** make the next instance visible in the log rather than in an invoice.

**The safety rule fell out of a field that already existed.** Triage is only safe where the material is retrievable, and `connectors.md` has recorded `Verbatim fetch` since 0.14 for a different reason — the promotion backlog. So a source without one captures everything regardless of mode. That is the second time a field added for one purpose answered a question nobody had asked yet, and it is an argument for recording properties of sources rather than conclusions about them.

**What is measured, not what is claimed.** `log_run.py` stats the files it is handed rather than accepting a token count, because a model cannot observe its own usage and a number it made up would be exactly the fabrication this model exists to prevent. Bytes written are a proxy, they are honest, and they track the expensive half of the bill.


### 4.47 Behind MCP the read is fixed and the write is not

**Decision (0.18.0):** `capture.body`, the two-call connector shape, and a ban on re-reading what a run just wrote.

The obvious fix for §4.46 was to take the bytes out of the model: let a script fetch and write, and the content never enters a context. That works for an export on disk or an API with a token, and it does not work for the two sources that actually cost the money, because both are reached through MCP — a model calls the tool and the result lands in its context by construction.

So the cost splits into a part that cannot be avoided and a part that was never examined. **Input is fixed:** the body arrives because the tool call returns it. **Output was tripled:** the model re-emitted the body to write the raw file, then re-opened that file to propose claims from it. Two of those three passes bought nothing — the second is a copy, and the third reads a file that has not changed since the model wrote it, one step earlier, in the same run.

Removing the third pass is free and was simply never noticed. Removing the second requires deciding **what `raw/` is actually for**, which is a real question with a real trade:

- If it is an archive, the body has to land in full, and a rebuild can find claims the first pass missed.
- If it is a citable record, it needs the passages that were cited plus a way back to the rest — and a rebuild can re-derive what was cited but **cannot discover what was missed.**

That is not a question this model should answer on anyone's behalf, so it is `capture.body`, with `full` the default wherever the answer is unknowable. The guard is the same field that guarded triage: `excerpt` and `stub` require a verbatim fetch, because the first invariant is the one layer nothing else can rebuild and a pointer at something unretrievable does not satisfy it.

**The registry knew the protocol and not the shape.** Recording `Protocol: MCP` tells a skill it can reach a source. It says nothing about the fact that almost every source has an enumerate call and a fetch call differing by two orders of magnitude in cost — so the skill did the only thing the record described and fetched everything. `List call` and `Fetch call` are now first-class, and this is the third time a missing property of a source turned out to be the cause of an expensive behaviour downstream. The pattern is worth naming: **record what a source is, not just that it is connected.**


### 4.48 Optimising for cost introduced three quality defects, one of them silent

**Found (0.18.1) by asking whether any of the cost work reduced capability.** It had, in three places, and the pattern is worth more than the fixes.

**A new mechanism met an old one and nobody checked the seam.** Triage and the batch cap were added in 0.17. The source cutoff was written years earlier, when every in-window item was always fetched, so advancing it unconditionally was correct. It stopped being correct the moment an item could go unfetched on purpose — and both new paths fell behind it. The release note claimed skipping was deferring rather than losing; the cutoff made that a false statement on the day it was written.

The repair is a distinction the old design never needed: **a triage skip is a decision and gets recorded, a batch remainder is not a decision and holds the cutoff.** Same class as §4.15, where "never edited" and "flip `processed: true`" both shipped and could not both be true — a new rule laid over an old one, each defensible alone.

**A refactor can remove a capability without touching the skill that had it.** §4.43 split the data model and routed each skill to what it needed. `corp-os-rebuild` was routed to the spine, which is correct for the layer rules it enforces and wrong for the fact that it re-derives claims and therefore needs the claim spec. The file-aware check added in that release verifies each *field* is documented in the right file; nothing verified that each *skill* still reaches everything it uses. Those are different checks and only one existed.

**A classification is a judgment and mine was wrong.** `corp-os-intake` was labelled mechanical because filing is what it looks like. It also infers job tags and draws from an existing tag vocabulary, and the skill's own text warns that inventing categories fragments that vocabulary. Cheap-model tagging degrades every later recall and shows nothing at the time.

The general lesson is the one this repo keeps paying for: **a change justified by one dimension has to be checked against the others, and cost is the easiest dimension to optimise blindly** because its feedback is immediate and quality's is not. The $40 was visible in a day. Losing a week of skipped meetings would have been visible in a quarter, if ever.


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
| `corp-os-decide` | The forks not yet decided: options, a person as owner, a `decide_by` date, what they block. |
| `corp-os-reality-check` | Eight-bucket sweep: overdue, unsourced-disposition, unverified, contradictions, aging assumptions, orphans, identities, cohort escapes. |
| `corp-os-glossary` | Terms, acronyms, and especially metric definitions with competing definitions kept visible. |
| `corp-os-company` | Employer / counterparty / competitor research, always searched, never recalled. |
| `corp-os-recall` | Answer with provenance; enrich what the person is working on. The payoff skill. |
| `corp-os-dashboard` | Render only what the OS holds; surface the uncomfortable numbers. |
| `corp-os-brief` | The operating rhythm. Schedulable. |
| `corp-os-rebuild` | Re-derive `derived` layers only, from the full corpus. |
| `corp-os-redact` | Make something shareable; quarantine at source; log reclassifications. |
| `corp-os-improve` | Mine the usage log; propose config / hygiene / model changes with counts. |
| `corp-os-audit` | Ten-dimension audit of any system; propose what to build; find what it has that the model lacks. |

### Cross-cutting rules every skill obeys — and the validator now proves it

- **Pre-flight** — confirm the OS is accessible now, not recalled. **The files outrank memory**; where they conflict, memory gets corrected. One identical `## Pre-flight` section in all nineteen; `corp-os-audit` carries the variant phrased for someone else's system.
- **Read `config.json` first**, and speak the person's labels back to them.
- **Never detect an OS by an optional layer.** `INDEX.md` + `meta.json`, confirmed by `config.json`.
- **Write freely** to `raw/`, indexes, and `usage/log.md`. **Propose** everything entering a `derived` layer.
- **Recount programmatically**, never hand-increment.
- **Close out with `scripts/log_run.py`** — the `usage/log.md` row with honest friction, and the dated `meta.json` history entry, in one call. That friction field is the entire improvement flywheel: `corp-os-improve` refuses to propose anything without a count attached. `corp-os-audit` is the one exemption, and it is named as one.

Adding a twentieth skill means satisfying all of these or the build fails. That is the intent, and `corp-os-decide` was the first skill added under it.

---

## 6. What has actually been tested

Being explicit, because much of this is unexercised.

**Verified:**

- `build_index.py` against a structure-only mirror of a real 214-source system with a config using **none** of the model's default layer names. It rendered 137 items across four urgency levels, 63 glossary terms across five groups, 15 questions across a four-state ladder, 18 themes, 20 tier entries, 45 people. Building that surfaced **four real bugs** in the script — it assumed `jobs` existed; could not handle single-file layers; counted list-style entries as zero; missed `title` in frontmatter. All fixed; the config ships anonymized at `examples/config-worked-example.json`.
- Custom-layer rendering, disabled-layer omission, missing-`index_line` warnings, undeclared-directory warnings, config-driven scan exclusions.
- `build_index.py --check` against a minimal no-config tree, exercising the reduced `DEFAULT_LAYERS` after `people`/`topics` were removed.
- `scripts/validate.py` passes: frontmatter, name/directory match, cross-references, `${CLAUDE_PLUGIN_ROOT}` targets, step ordering, leakage.
- **`build_index.py` is now executed by the build**, not merely parsed. `validate.py` copies `examples/fixture-os/` to a temp dir, runs the script against it, and asserts the counts, the custom layer's rendered `index_line`, the unprocessed queue, config-driven exclusions, the omission of the disabled layer, and that a second `--check` run finds no drift. Building the fixture immediately caught a real bug: an unrecognized key under `scan` fell back to defaults silently and rendered a plausible, wrong "not in the scan path" section. It is a warning now.
- **`corp-os-reality-check` at 6/6 after a real fix.** The `fidelity-backlog` case caught a missing review gate in the skill that removes things (§4.38): three of four runs rewrote the derived layer with no proposal behind it, one of them across fourteen files. With the gate step, 2/2.
- **`corp-os-pattern` at 6/6 across two repeats**, against the register fixture where the pattern deliberately cannot bind. Its first assertion forbade adding anything under `patterns/`, and failed at 50% because a run wrote `patterns/pack.json` — recording which pack the OS is on, which is Step 4 of the skill in as many words. The check forbade what the skill instructs; that is the eighth time in this suite an assertion has been wrong about a skill rather than the reverse.
- **The routing eval at 23 skills**: 77 queries × 3 repeats, **100%**, including the three-way near-miss set — `pattern` against `configure`, `contribute` and `dashboard` — that the docket named as a risk *before* patterns shipped rather than after. `evals/runs/routing-v6.md`.
- **`corp-os-migrate` at 10/10 across two repeats**, on the third version of its case. The first staged nothing on disk and then asserted files would be written; the second checked the answer for the string `retriev`, which a run can miss while distinguishing the populations perfectly; the third asserted a first pass files source and stops, which is stricter than the rule the skill states. Three wrong assertions, one working skill, and the corrections are in the case's own note.
- **The routing eval at 22 skills**: 71 queries × 3 repeats, **100%**, including a four-way near-miss set built to pull `corp-os-migrate` toward `setup`, `intake`, `pull` and `audit` — the neighbourhood a bulk import sits in. `evals/runs/routing-v5.md`.
- **The routing eval at 20 skills**: 64 queries × 3 repeats, **100%**, including three near-miss pairs written to pull `corp-os-upgrade` toward `configure`, `rebuild` and `setup`. `evals/runs/routing-v4.md`.
- **The whole conformance suite re-run under the fixed harness** (§4.27), the first numbers in this repo where the shipped scripts actually executed: **114/122 across 19 cases, 16 skills and 3 fixtures**, at one repeat — a baseline, not rates. `setup-from-empty` 9/9 and `upgrade-stale-os` 10/10 replace 3/10 and 5/10. The eight remaining failures are the honest starting point for the next round rather than a regression, because there is no comparable earlier number to regress from.
- **The routing eval**, three times. 44 queries × 3 repeats at first, then 58 after hardening: 93%, then 100%, then 100% over the harder set. Every run is committed under `evals/runs/` — the reports, not just the scores, because the confusion table is the part that says *which* pair collided.
- **The command harness**, five times inside twenty minutes, ending at **100% over 23 cases × 3 repeats** including seven picker cases. Cheap enough that four of its five early findings were about the harness itself and were fixed in the same sitting.
- **The upgrade path**, against a fixture built to be broken: an older counter copy, a missing script, a stale version and the pre-0.10.1 layout. The script was exercised in both directions before the skill existed — dry run, apply, re-run for idempotence, the migration performed by hand, and the counter then reading 3 where it had read 1.
- **The dashboard pair**, added after the first real-use defect report. `dashboard-hub-and-registry` at **7/7** — the registry entry lands in the root file and no `dashboards/` directory is recreated. `dashboard-missing-layer` at **4/5**, deliberately (§4.25).
- **The conformance harness**, ten times across five rounds of fixes, the last three at three repeats so the numbers are rates rather than coin flips. Six skills — `intake`, `claims`, `decide`, `recall`, `reality-check`, `brief` — each run against a fresh copy of the fixture, then scored on what changed on disk. Twelve cases across nine skills and two fixture shapes. 27/35 on the first full run; 68/75 checks at 100% when rates replaced pass/fail; 73/75 after the scripts landed. Six real defects, one model contradiction, and four of the harness's own assertions corrected along the way. `evals/runs/conformance-rates-after.md` is the current state, and `conformance-rates-before.md` is kept beside it because the delta is the evidence.
- **Every 0.6.0 validator check was negative-tested** — the defect it guards against was reintroduced, the check was confirmed to fire, and the tree restored. Checks covered: missing `## Pre-flight`, a skill that stops reading `config.json`, an optional layer used as an existence test, a stated count that no longer matches its headings, plugin/marketplace version parity, a missing version-history entry, and the guide dropping a skill from its routing table. A check that has never been seen to fail is not a check.

**Not tested:** the thirteen skills with no conformance case. Six is a start, not coverage, and the ones missing include every skill with an irreversible path — `rebuild` refusing to touch a non-`derived` layer, `configure`'s five-step delete sequence, `redact` never modifying the original. Those are where a behavioral defect costs something that cannot be recovered, so they are next.

Also untested: whether a skill fires *at all* in a live session, competing with everything else a person has installed and with the model's own inclination to just do the task. The routing eval measures whether the descriptions can be told apart from each other, which is a different question. `skill-creator`'s `run_eval.py` covers the other one, per skill.

And untested by construction: the setup interrogation, which needs a person who did not design it.

---

## 7. Open questions

Ordered by how much they would change. Items keep leaving this list by being answered rather than argued: `usage/log.md` does get written, routing is not this suite's risk (§4.17), `sensitive.md` was insufficient and is now two axes (§4.18), multi-person is out of scope rather than unresolved (§4.20), and eight commands are distinguishable rather than too many (§4.23).

1. **Every conformance number predates the harness fix.** Until 0.11.0 no shipped script had ever executed in a run (§4.27), so each one measured the model producing a script's output by hand. The two cases re-run so far both moved: `setup-from-empty` 3/10 → 9/9, `upgrade-stale-os` 5/10 → 10/10. The rest of the suite needs re-measuring before any figure in §6 is quoted again, and the script-landed-it claims in §4.21 and §4.22 need re-reading as the weaker claim they actually support.
2. **Six skills still have no conformance case.** The irreversible paths are now covered — `rebuild` leaves a `role: source` layer alone in every run, the delete sequence re-cites before destroying, and redaction never touches the original. What is left is the input side (`pull`, `connect`, `company`, `glossary`) and the meta skills. `corp-os-setup` is the interesting one: it starts from nothing, so its case begins with an empty directory, and the only machine-checkable claim is that what comes out is a valid OS.
3. **The fixtures are three shapes.** The default, a register-profile OS, and one deliberately two releases behind. Still missing: an OS mid-migration with a cohort ceiling being actively worked, and one large enough that the scan contract is doing real work rather than being trivially satisfiable at four entries. Fixture work, not harness work — the runner already takes `--fixture`.
4. **Does the setup interrogation land?** Nine areas, never run on anyone who did not design it. The likely failure is abandonment partway, and no check catches that. A conformance case could at least establish that a run started from nothing produces a valid scaffold, which is weaker but not nothing.
5. **`corp-os-decide` has been tested on one axis.** It survives the roster and one conformance case; whether it fires in a session full of other installed skills is unmeasured.
6. **The `corp-os-configure` hand-off lands 2 times in 5** (§4.25). Not a bookkeeping step, so not scriptable; three instruction passes have not moved it. The next honest move is a person watching a real session take that path, not a fourth wording.
7. **Should `build_index.py` be able to repair, not just report?** It flags undeclared directories, missing `index_line`s and unknown config keys. Auto-fixing would cross the bookkeeping/judgment line that makes it safe to run casually — probably keep as-is.
8. ~~**Does an urgency-tiered layer need ordered rendering?**~~ Done: a layer declares `order_by` and `build_index.py` sorts by that field's declared enum. `now` renders above `watching`. The script reads what the config already said rather than deciding what is urgent, so it stays bookkeeping.
9. **Nothing tells a person their OS is behind.** `corp-os-upgrade` works once someone runs it, and `corp-os-guide` routes "something looks wrong since I updated" to it. Nobody is told unprompted. The cheapest fix is `build_index.py` — it runs constantly and already reads `config.json` — printing a line when the recorded version is behind the plugin's. It was left out of 0.11.0 because the script has no business knowing where the plugin is, and a version check that guesses at a path is worse than none.
10. **Which commands get used?** Whether the eight are *distinguishable* is settled (§4.23). Whether all eight get reached for in practice is a usage question, and `corp-os-improve` should be able to answer it from the log — which now gets written reliably enough to trust.

## 8. Deliberately rejected

Recorded so they do not get re-proposed.

- **Auto-promoting claims past a corroboration threshold.** Removes the review gate, which is the load-bearing part.
- **Renumbering claim IDs on rebuild.** Breaks every external reference.
- **Backfilling provenance retroactively.** Nobody does it; recommending it wastes the recommendation.
- **Shipping role templates or domain vocabulary.** Content-agnosticism is the portability guarantee.
- **A numeric composite audit score.** Invites arguing with the number instead of fixing the gap.
- **`build_index.py` reading `raw/`.** Would make it judgment rather than bookkeeping, and unsafe to run casually.
- **Recommending a rebuild in an audit.** Nobody rebuilds a working system on an audit's advice.
- **Keeping `people/` as a schemaless default** so `corp-os-recall`'s meeting-prep path had a folder to read. A layer that exists to satisfy a reader, with no writer and no spec, is how drift enters through the front door. See §4.9.
- **Documenting the cross-cutting rules harder instead of checking them.** Tried for four releases; measured at 5 of 18. See §4.11.
- **Merging `connect` + `pull`, or folding `glossary` into `claims`, on collision grounds.** Measured at 100% on both pairs. There may still be an argument for merging on surface-area grounds — nineteen is a lot — but the collision argument is dead and should not come back without new eval data.
- **A single sensitivity flag.** Tried for eight releases. It cannot serve both the export boundary and the scan path, and the failure it produces is invisible — see §4.18.
- **Trusting a skill because it reads correctly.** `corp-os-intake` reads perfectly and dropped its index entry four runs out of four. The instruction was already there; adding emphasis to it would not have helped, and only running it showed that.
- **Relabelling a failed eval query to make the number go up.** Done once, in 0.7.0, and the reason is written into the query itself precisely because doing it silently is how an eval stops meaning anything. The bar for the next one is the same: the model has to have been right and the label wrong, and the justification goes in the file.

---

## 9. How to make a change here

1. Change the **reference spec** first if the change is to the model — `data-model.md` or `configuration.md`. Skills defer to those; a skill that contradicts a spec is a bug.
2. Update **every skill that touches the changed behavior.** Cross-cutting rules live in many files by design; grep before assuming one edit covers it.
3. **If the change makes something optional, grep for everywhere that assumed it.** §4.10 is what happens when this step is skipped.
4. Update the plugin **`README.md` version history** with what changed and why. `validate.py` fails without an entry for the shipped version.
5. **Bump the version in both manifests, even for a documentation change to the plugin.** The client caches an installed plugin by version string, so new commits without a bump reach nobody, silently. `validate.py` fails if the two version fields disagree; nothing anywhere fails if you forget to move them together. `docs/INSTALL.md` is the full procedure and the file to hand somebody who asks how to install or update this.
6. Run `python3 scripts/validate.py`, then `./build.sh`.
7. **A wording change means `evals/run_commands.py`** — a minute, and it is the only loop short enough to actually use while writing.
8. **Negative-test any check you add.** Reintroduce the defect, confirm the check fires, restore. A check that has never been seen to fail is not a check.
9. **An instruction that touches a source layer means grepping the invariant it sits under.** "Never edited" and "flip `processed: true`" both shipped for four releases and could not both be true. A contradiction like that does not announce itself; it gets read in whichever direction the reader arrives from. See §4.15.
10. **Adding a skill means placing it on the map.** `scripts/build_skill_map.py` will not render until the new skill is in a phase or on the workbench, and `validate.py` runs it. Everything else on that page regenerates itself.
11. **Changing a skill's behavior means adding or rerunning its conformance case** — `python3 evals/run_conformance.py --case <id>`. If the skill has no case, that is the moment to write one. `validate.py` prints the coverage on every run — the bar is one case per skill, adopted from a smaller suite that already meets it, and the number to move is the one in the case file rather than the one in a run report.
12. **Adding or rewording a skill description means rerunning `evals/run_routing.py`.** Add coverage queries for the new skill and at least one query that should route *elsewhere* but sits near it. `corp-os-decide` shipped with a description that swallowed two other skills' queries and it took the eval, not review, to see it.
13. If the change came from real use, write an **improvement packet** per `reference/improvement-packet.md` — and apply its config test first: *if it could have been a config setting, it is not a model change.*

---

## 10. Session handoff

To resume cold:

- Read this file, then `plugins/corp-os/reference/data-model.md` and `configuration.md`. Those three are the whole model.
- Read one skill end-to-end for the house style — `corp-os-claims` is the most representative.
- `python3 scripts/validate.py` verifies the tree is intact — including executing `build_index.py` against `examples/fixture-os/`; `./build.sh` packages it.
- `python3 evals/run_routing.py --repeats 3` measures whether the descriptions still tell each other apart — roughly fifteen minutes, worth it after any description change.
- `python3 evals/run_conformance.py` runs six skills against a disposable copy of the fixture and checks what they did to it. Slower, and the one that finds real defects. `evals/README.md` says what each harness does and does not measure.
- §7 is the work queue. §8 is the do-not-relitigate list.

**House style for skill bodies.** Imperative, addressed to Claude. Every non-obvious instruction states its reason — an instruction whose rationale is missing gets rationalized away under pressure. Name the failure mode being prevented, not just the correct behavior. Under 3000 words; detail goes to `reference/`. No hedging, no "you should".
