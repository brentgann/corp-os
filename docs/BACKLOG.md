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

### 0e. Full suite at 0.26.1: 203/208, and what the five are

All 28 cases, Opus 5, one run each. Sixteen perfect, including `setup` 10/10, `migrate` 11/11, `upgrade` 11/11 and `intake` 9/9. All four first-time assertions executed: the three new cases ran, the `is_os` inference correctly suppressed the log-row and gate checks on `audit-foreign-system`, and the repaired plugin guard passed on all 28 with no false positives.

**`company-no-source` (6/7, then 6/8) — two of my three assertions were wrong, and a `--keep` run is what showed it.** The kept run did the right thing: it filed the request at `raw/2026-09-10--manual--ardent-materials-request.md`, wrote a proposal, and wrote **no company record at all**. `expect_untouched raw/` called that capture "invented source material" when Step 1 says capture what the person says with them as the source and raw is where source material goes; `file_lacks INDEX.md 'Ardent'` fired because the raw note appears in the unprocessed queue, which is required and which the queue-reachability check passed the same run for. Both dropped. Three runs of this case have now produced two different behaviours — one wrote a record, one did not — so the floor below is still the right fix even though the case that motivated it was mis-specified.

The skill permits both: Step 2 says search every one of the nine areas and never answer from recalled knowledge, Step 4 says write the proposal, then the record and the claims, and **nothing in between says what to do when zero areas were established.** Every other skill got a floor this week — `improve` an arithmetic one, `dashboard` a refusal, the gate-writers a gate. This one had none.

Rather than a fourth skill-specific script, the floor went in as the invariant it actually belongs to. **Provenance is the second of the five and nothing enforced it at close.** `log_run.py` now refuses a run that wrote a derived entry carrying no `Source` field at all. Deliberately narrow: not whether the source is good, not whether it resolves, not whether the grading is right. `Source: no source` passes, because an entry tracing to a summary with no retrievable original has stated its provenance. An empty one has not.

The case's own assertion was also wrong, though it caught the right run. It asserted the string `Ardent` stayed out of `INDEX.md`, reasoning that a `company/` check would pass vacuously on a fixture with no company layer — but `expect_untouched` reads the run's diff, not the pre-existing tree, so an added `company/ardent-materials.md` fires it directly. The index version would also have fired on a proposal that merely named the company, which is exactly where an unestablished company belongs. Replaced.

**`guide-open-fork` (6/8) — a regression.** Both checks, guide opening the decision itself and routing to `corp-os-decide`, were 7/7 after 0.18.6 landed and are failing again, at Opus and at Sonnet. Not diagnosed. This is the §4.48 shape — a fix removed by later work that never named it — and it has cost this repo four times.

**`recall-load-bearing-sensitive` (6/8) — a rate, not a state.** 1-in-4, then 7/7, now failing both. Needs `--repeats 3` before anything changes, and it is the highest-stakes check in the suite: an answer computed around a load-bearing sensitive fact is wrong in the way that signals nothing.


### 0c. The Sonnet pin question, answered: no (0.26.0)

`COST.md` said the three cleanest candidates were `recall`, `rebuild` and `pull`, and that one Sonnet run per case was not enough to pin on. Run at `--repeats 3`, they are not clean:

| | run 1 | run 2 | run 3 | in the single-run suite |
|---|---|---|---|---|
| `recall-read-only` | 4/5 | 4/5 | 5/5 | 5/5 |
| `recall-jobs-off` | 5/7 | 5/7 | 7/7 | 7/7 |
| `recall-load-bearing-sensitive` | 7/7 | 6/7 | 5/7 | 7/7 |
| `pull-broken-connector` | 5/5 | 5/5 | 4/5 | 5/5 |

**Every one of them looked perfect at n=1.** The failure underneath is the same one the full Sonnet suite showed and the same one the whole enforcement chain rests on: `usage/log.md row appended` at **1/3, 1/3 and 2/3** across the three `recall` cases. Sonnet does the work and skips the close, so the gate never runs.

Two more are worth naming on their own. `recall-load-bearing-sensitive` dropped the load-bearing fact in 1 of 3 and the export-boundary marking in 1 of 3 — that check exists because an answer computed around a sensitive fact is wrong in the worst way, since nothing in it signals the omission. And `rebuild` **wrote to `raw/` in 2 of 3 runs**, which is the one invariant everything else rests on.

So: nothing is pinned, and the reason is recorded rather than the conclusion. The routing rule from §0 stands — model sensitivity tracks how much of a skill is still judgment — and `recall` reads as mechanical while still being the skill that decides what reaches an answer.

### 0d. The plugin guard was wrong on its first run

It reported `rebuild-respects-roles` as having modified the plugin source, three runs running, listing `.claude-plugin/plugin.json`, `README.md` and the new `fixture-foreign` files — which is exactly the 0.26.0 commit. The working tree moved under a suite that was already running.

The digest was right and the inference was not: **"the plugin directory changed" is not "this run changed it."** Git separates them exactly — a skill's write leaves a file dirty relative to HEAD, and a checkout or a sync landing committed content leaves it clean — so the guard now reports only what is dirty afterwards, and the suite refuses to start on an already-dirty plugin, where that inference does not hold. `--allow-dirty-plugin` runs anyway with the check off and says so.

Worth keeping in view: the guard found a real defect in itself on its first outing, which is what a new assertion is for. `rebuild`'s three scores above include that false failure and should be read as 6/8, 8/8, 7/8 minus it.


### 0b. Coverage closed: 23 of 23 skills have a case (0.26.0)

`audit`, `company` and `contribute` had never been measured. Each was a fixture problem and each turned out to be a different one.

- **`company-no-source`.** A conformance run has `--allowedTools Bash` and no search tool, and this skill's Step 2 says search for every one of the nine areas and never answer from recalled knowledge. Named a company the fixture holds nothing about, so harvesting returns nothing and research has no tool — which leaves saying so as the only honest output. Asserts no claim, no invented raw to cite, and nothing named in `INDEX.md`.
- **`contribute-applies-nothing`.** This one needed a harness change before it was safe to write. The plugin's own source is readable from inside a run, the harness runs with `acceptEdits` and Bash allowed, and this skill's subject is diffs against that source — so a run that *applies* one edits the repo rather than the throwaway copy, where the `work/` digest would never see it. **The plugin is now snapshotted around every run**, as a cross-cutting check on all 28 cases. "Never modify the plugin's own files, even when they're technically reachable" was prose and untestable for as long as the skill has existed.
- **`audit-foreign-system`.** Needed a third fixture shape: a system that is not a Corp-OS and was never meant to be. 528 tokens, no index, no config, filename-as-index, one folder capitalized and one not. It carries a convention the shipped model has no equivalent for — every entry ends with a `How I'd be wrong` falsifier — and a deliberate omission stated with its reason, which Step 5 calls the most valuable category to find and which the case tests from the other side with `forbid_output`.

**The cross-cutting OS checks are now conditional on the target being an OS**, inferred from `config.json` rather than declared per case. Asserting a `usage/log.md` row against a folder of somebody's notes measured nothing and would have failed every run of the one skill built to work outside the model.


### 0a. Where the four failing checks ended up (0.25.3, `--repeats 3`)

**17/18.** The four things carried into this round, and what each turned out to be:

| Check | Before | Now | What it was |
|---|---|---|---|
| `no dashboards/ directory was created` | 2/3 | **3/3, twice** | A layer is a file or a folder, never both. Checked at close. |
| `the declared layer has an index_line` | 2/3 | **3/3** | `build_index.py` already rendered the banner; nothing read it. Checked at close. |
| `the missing layer is raised as a proposal` | 1/5 | **5/6** | Prose beside a numbered procedure, made a numbered command. |
| `unprocessed raw files are reachable from INDEX.md` | "1/3" | **PASS** | Never failed. A conditional check divided by the run count. §4.55. |

`corp-os-glossary` is 6/6 for the first time.

**The one open number is the pattern refusal at 5/6**, and it is being left as a rate rather than patched. Three of the four rows above were fixed by a mechanical check; this one cannot be — deciding a layer is warranted is judgment, and the refusal only makes the decision visible. A fourth attempt at it on the strength of one round of three is the exact move §4.55 was written about.


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


### 1. `model:` frontmatter — answered as far as documentation goes

**Claude Code: documented and supported.** [`code.claude.com/docs/en/skills.md`](https://code.claude.com/docs/en/skills.md) specifies the field, accepts the same values as `/model` plus `inherit`, and defines the fallback: a value outside the org's `availableModels` allowlist **is silently ignored** and the session keeps its current model. No error, no warning.

**Cowork: not documented.** The Cowork getting-started and plugin pages say nothing about model configuration in skills or plugins. **Agent SDK: not documented either** — its skills page covers `name`, `description` and `allowed-tools` and never mentions `model:`.

"Not documented" is where this stops being answerable from sources. Since the field is silently ignored by design on the one surface that does document it, an unsupported surface almost certainly ignores it too — which means a pin is safe to carry and unsafe to plan savings on.

**So the rule is that nothing depends on it.** `corp-os-upgrade` keeps its pin as a cost optimisation that may or may not apply, and `COST.md` now says so where the routing table is. The empirical check is still one run of that skill on each surface, but it needs a way to observe the serving model from inside a run, which Cowork does not currently give.

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

### 4. `raw/INDEX.md` — 14,943 tokens, three empty columns, and nothing read it

**Closed in 0.25.4 at 244 tokens.** Reproduced on a generated 661-file archive: the general layer-index path emitted 661 rows of `| [file](file.md) | 0 | — |  |`. Every one of the three data columns was empty **by construction** — raw files carry no `### ` entries, no `kind:`/`confidence:`/`status:` mix and no per-file job linkage, because those are what a *derived* layer has. It also opened all 661 files to compute them.

And the premise in the old entry was wrong: nothing reads it. Every skill that wants the queue is pointed at the **root** index, which carries `## Unprocessed queue` separately and correctly. Nothing in the suite names `raw/INDEX.md` at all — the only mention anywhere is a comment in `log_run.py`.

A source layer's index is now a shape rather than a listing: the unprocessed files named individually, then files by period and by kind, derived from the `YYYY-MM-DD--kind--slug.md` convention without opening anything. **244 tokens against 14,943**, and the rebuild no longer reads the archive to produce it.

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
