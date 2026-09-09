# Backlog

Known, measured, unfixed. Distinct from ARCHITECTURE §7, which holds open *questions* — things nobody knows the answer to. Everything here has an answer and has not been done.

Items leave this list by being done or by being declined in §8, never by being forgotten. Sizes are measured, not estimated, and the command that produced them is named so the number can be re-derived rather than trusted.

---

## Done in 0.19.x

- **Root index split.** Findings moved to `usage/health.md`, uncapped, owned by `corp-os-reality-check`. At 800 claims: INDEX.md 1,440 → 468, pre-flight floor 2,513 → 1,541.
- **Layer index fires on entries as well as files.** 800 claims in 25 topic files had no entry point; `claims/INDEX.md` now generates.
- **Filing moved into `scripts/file_raw.py`.** Dedupe, naming, frontmatter, cutoff — one call instead of one turn per item.
- **Fixture script drift fixed and checked.** All three carried a 414-line `build_index.py` against a shipped 888.
- **`scripts/corpus_load.py`** and **`scripts/make_fixture.py`** — both free to run.
- **`model: sonnet` on `corp-os-upgrade`**, the one skill of 23 that is genuinely mechanical.
- **`docs/COST.md`** — session guidance and what does not save money.

## Open

### 1. Verify `model:` frontmatter is honoured outside Claude Code

`corp-os-upgrade` now declares `model: sonnet`. The documentation for that field is Claude Code's. **Whether Cowork honours it is unverified**, and an ignored field is a change that reaches nobody — the failure this repo is named after by now. One run of that skill in each surface settles it.

### 2. Conformance has not run since any of this

The last run was 69/79 on 0.18.5, and everything since has changed the skills, the scripts, the fixtures and the harness. That number is not a baseline for anything.

`--repeats 5 --case recall-load-bearing-sensitive` first: it is a rate, not a result (§7.2), it costs about eight minutes, and §4.28 records three wording passes made against `corp-os-configure` before anyone established its rate.

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
