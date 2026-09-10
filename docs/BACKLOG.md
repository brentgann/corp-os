# Backlog

Known, measured, unfixed. Distinct from ARCHITECTURE §7, which holds open *questions* — things nobody knows the answer to. Everything here has an answer and has not been done.

Items leave this list by being done or by being declined in §8, never by being forgotten. Sizes are measured, not estimated, and the command that produced them is named so the number can be re-derived rather than trusted.

---

## Done in 0.19.x — the pre-flight floor, measured on a real 852-claim OS

**9,508 → 5,501 tokens**, paid by every skill on every run. 42% off, and no model tokens spent finding or fixing any of it. Full table in `COST.md`.

- **Root index split** — findings to `usage/health.md`, uncapped, owned by `corp-os-reality-check`.
- **Layer index fires on entries as well as files** — 852 claims in topic files had no entry point.
- **A layer with its own index is no longer listed in the root too** — that was 1,424 duplicated tokens.
- **`note` fields move to the OS README** (`prune_config_notes.py`), per-path, with a peer-entry warning: a note beside identical peers may be the distinction itself.
- **A path that is the slug of its own name is no longer written out** — 47 of 82 entry lines.
- **Filing moved to `scripts/file_raw.py`** — one call, not one turn per item.
- **Fixture script drift fixed and checked** — all three carried a 414-line `build_index.py` against a shipped 888.
- **`corpus_load.py`** and **`make_fixture.py`** — both free to run.
- **`model: sonnet` on `corp-os-upgrade`**; **`docs/COST.md`**.

## Open

### 0. The enforcement chain has one model-dependent link left

**Measured 2026-09-10 at 0.25.1, both models.** Sonnet 4.5, full suite: **137/163**. Opus 5, seven cases at `--repeats 3`: **36/40**, with the gate and the log row 3/3 in every case.

**On the seven cases both models ran, they are within a check of each other** — Sonnet 35/39, Opus 36/40, and Sonnet won `dashboard-hub-and-registry` 7/7 against Opus's 6/7. The suite-level gap is not spread across the skills; it is concentrated in `setup` (2/9), `intake` (5/8), `connect` (3/5), `decide` (3/5), `pattern`, `redact-strips`, `guide`, `brief` and `configure`.

Those are the skills whose mechanism is still in the model. The seven that tie are the ones where it is not: `jobs`, `improve`, `glossary`, `claims`, `pull`, `recall`, `rebuild` all run through `propose.py`, `file_raw.py`, `build_index.py`, `friction_scan.py` and `log_run.py`. **Model sensitivity tracks how much of a skill is still judgment**, which is the claim `COST.md` has made since 0.18.2 without a measurement behind it. It has one now, and it means the routing question answers itself release by release rather than once.

What it already settles is the design question 0.25.0 rests on. **The gate held 24 of 25 cases at Sonnet**, including the three skills that were 1/3 and 2/3 at Opus a release earlier. Moving it into `log_run.py` made it model-independent, which is the result that was hoped for.

**But `usage/log.md row appended` failed 9 times.** That check was 3/3 in every case and every skill at Opus, which is the entire reason the gate was put behind it. At Sonnet it is roughly 64%. The one case that failed the gate — `intake-transcript` — is the same case that skipped the close: it wrote `claims/pricing.md`, updated `INDEX.md` and `meta.json`, and ran neither `propose.py` nor `log_run.py`. **The gate is now exactly as reliable as `log_run.py`'s invocation rate, and that rate is the only model-dependent link in the chain.**

Four cases wrote nothing at all: `setup-from-empty` (12s, 0/9 of its writes, with the prompt explicitly saying "go ahead and scaffold it"), `decide-open-fork`, `connect-blind-spots`, and `pattern-adopt-refusal` closed no books. That is a different failure from skipping bookkeeping and it is not fixable by moving a step into code.

Clean at Sonnet: `recall` ×3, `rebuild`, `pull`, `redact-external`, `reality-check`, `fidelity`, `dashboard-hub`, `claims`, `glossary`, `jobs`, `improve`. Mostly the read-and-regenerate skills.

**So the cheap split does not survive contact.** "Sonnet where the tokens are" pointed at `intake` first, and `intake` is the one case that did the work and left none of the record. Two things worth doing before any routing decision:

1. ~~Opus at 0.25.1~~ — done, above.
2. **Decide whether a run's close can be made non-optional.** A `Stop` hook is the only place genuinely outside the model, and whether Cowork honours one is unverified — the same open question as item 1 below, and the same failure mode if it does not.


### 1. Verify `model:` frontmatter is honoured outside Claude Code

`corp-os-upgrade` now declares `model: sonnet`. The documentation for that field is Claude Code's. **Whether Cowork honours it is unverified**, and an ignored field is a change that reaches nobody — the failure this repo is named after by now. One run of that skill in each surface settles it.

### 2. Conformance: 152/163 at 0.19.11, and eleven things it found

First full run since 0.18.5, thirteen releases back. Was 69/79. `corp-os-guide` went **4/7 → 7/7** (0.18.6 landed), and `setup` 9/9, `upgrade` 10/10, `migrate` 10/10, `configure` 8/8 — including the hand-off §4.25 recorded as landing 2 times in 5.

**Caused by this repo's own cost work — fixed in 0.19.12:**

- `dashboard-hub-and-registry` rebuilt `dashboards/` as a directory. Passed at 7/7 for months. 0.18.4 gated the read of `reference/dashboard-patterns.md`, which carried the rule. §4.48 again.

**Two fixes from 0.18.7 did not take. Both confirmed still failing:**

- **`corp-os-improve` wrote `claims/pricing.md`** against a fixture holding one friction note, and wrote proposals from that single occurrence. 0.18.7 added *"writes only under `usage/`"* to the skill and it did not hold. The wording is not the fix; this needs the constraint somewhere a run meets before it acts, or in code.
- **`corp-os-jobs` wrote three job files with no proposal.** 0.18.7 moved the write gate above all four sections that write. It still did not fire. Same conclusion.

**Newly detected rather than newly broken** — the gate list became config-driven in 0.19.x, so these were always failing and nothing was looking:

- `corp-os-decide` wrote claims, decisions and jobs with no proposal file.
- `corp-os-glossary` wrote `glossary.md` with no proposal.

**Not results:**

- `rebuild-respects-roles` **timed out at 600s** and lost only its final log-row check. Re-run with `--timeout 900` before reading anything into it.
- `recall-load-bearing-sensitive` is now **1 pass in 4 observations** across three months. No longer plausibly a coin flip; treat it as a real failure and diagnose it. CL-0004 is the case where being wrong matters most — an answer computed around a load-bearing fact signals nothing about the omission.
- `dashboard-missing-layer` fails the same check it failed in `conformance-v11.json`. Pre-existing, not a regression.

**The pattern across the four gate failures is one pattern.** Four skills write to derived layers without persisting a proposal, and two of them have had a prose fix applied that did not work. The gate is the third invariant. A rule stated in a skill body is not holding it, and the next attempt should be a check the skill cannot pass by wording — the same move that took filing out of the model in 0.19.1.

### 3. Descriptions: measured, and deliberately not cut

3,655 tokens per session across 23 skills, roughly **two cents** at Opus rates. They are what routes among 23 siblings and a misroute wastes a whole run. The trade is bad in both directions and it stays as-is unless the routing harness says otherwise. Recorded so it is not re-proposed as an obvious win.

### 4. `raw/INDEX.md` is 14,922 tokens at 661 files

Generated because raw crosses the file threshold, and read by anything that touches the source layer. Not yet examined. It may be correct — raw is deliberately never loaded wholesale — but nothing has looked at what reads it or what it costs them.

### 5. Unconditional reference reads — closed

Kept for the rules it produced, not because work remains.

**82,894 unconditional across 23 skills, against 83,478 conditional.** Down from a true starting figure of roughly 92,969 (the 125,289 first reported was measurement error; §4.51).

Re-derive with `python3 scripts/ref_load.py`; `--skill <name>` for the sentence view, and **read that before editing** — four versions of this measurement set the work order wrong.

Six skills read nothing unconditionally: `brief`, `dashboard`, `guide`, `recall`, `redact`, `glossary`.

### What is left, and why it stays

| skill | unconditional | why it is legitimate |
|---|---|---|
| `corp-os-setup` | 9,779 | writes a config, scaffolds against the data model, runs the interrogation — three files, three things it does every run |
| `corp-os-claims` | 8,233 | the skill that writes claims, reading the claim spec |
| `corp-os-rebuild` | 8,233 | the skill that re-derives them, reading the same |
| `corp-os-pull` / `corp-os-intake` | 6,146 | data model, raw-file shape, and the capture block that decides their cost |
| `corp-os-reality-check` | 5,189 | `claim-record.md` |

Every remaining entry is a skill reading a file it needs most of. `configuration.md` and `claim-record.md` were both examined section by section against their unconditional readers and neither divides by audience; `data-model.md` is the spine already trimmed in 0.16. **Further splitting would move tokens rather than remove them.**

### Rules this item produced

- **A file's home is decided by how many skills read it unconditionally, not by subject.** Moving `capture` to `records.md` was right on subject and put the suite total *up* 1,154. Its own file was strictly better. Check the reader count before re-homing.
- **The pointer has to be gated, not just present.** "`X` is specified in `reference/y.md`" satisfies the reachability check and still pulls the whole file every run. Name the branch instead.
- **A condition governs what follows it inside its block, never what precedes it.** Both scoping mistakes came from getting this wrong in opposite directions.
- **Do not convert a read without the reachability check green** (`scripts/validate.py`).
- **Frequency is not in the table.** `setup` runs once per OS; `claims` runs constantly.

### Next

A conformance run. Four skills changed materially — `dashboard`, `setup`, `recall`, `configure` — plus `pull` and `intake` re-pointed at the capture spec, and three cases written in 0.18.2 have never executed.

### 6. Cheap and unblocked

- **Lean-session guidance in the docs.** Every connector and plugin loaded contributes tool schemas to the per-turn prefix. A filing run needs the source connector and nothing else. Documentation only.
- **`model: sonnet` on `corp-os-upgrade`.** The one skill of 23 that survived the 0.18.2 reclassification as genuinely mechanical. Frontmatter supports the field; **whether Cowork honours it is unverified**, and an ignored field is a change that reaches nobody.

### 7. Measurement is unavailable where this actually runs

Cowork exposes no per-session cost or token count. `/usage` exists only in Claude Code. So for anyone running corp-os in Cowork, `usage/log.md` is the only telemetry that exists and `corp-os-improve` is the only thing that reads it. That raises the stakes on the friction field considerably and belongs in the rollout material.
