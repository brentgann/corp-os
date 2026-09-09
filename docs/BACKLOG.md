# Backlog

Known, measured, unfixed. Distinct from ARCHITECTURE §7, which holds open *questions* — things nobody knows the answer to. Everything here has an answer and has not been done.

Items leave this list by being done or by being declined in §8, never by being forgotten. Sizes are measured, not estimated, and the command that produced them is named so the number can be re-derived rather than trusted.

---

## 1. Unconditional reference reads — gating done, splitting done

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

## 2. Skill descriptions

**3,655 tokens loaded into every session**, whether corp-os is invoked or not. Median 153 per skill against 38 for a comparable public collection. The gap is largely disambiguation across 23 siblings, which is load-bearing, so the target is roughly 2,400 rather than parity.

Verified by the **routing** harness (~15 min), not conformance. Independent of item 1; both can run the same afternoon.

## 3. Conformance coverage: 20/23

Missing `corp-os-audit`, `corp-os-company`, `corp-os-contribute`. Each is a fixture problem, not a harness problem:

- **`company`** — no shipped fixture declares a company layer. Cheapest of the three.
- **`audit`** — needs a fixture representing someone else's non-corp-os system, which is a different artifact from the two that ship.
- **`contribute`** — its deliverable leaves the OS entirely, so there is nothing in the tree to assert on without plugin source and a prior diagnosis.

The three cases added in 0.18.2 are **written and never run.** The harness spawns real model runs and costs real money.

## 4. `corp-os-pull`'s bookkeeping belongs in code

The largest remaining lever and deliberately not batched with items 1 and 2. Dedupe, filename construction, frontmatter assembly, recount and cutoff arithmetic are all done by a model, one turn at a time, and every turn re-sends the whole session prefix.

Held back because batching is correct only up to the point where a red run stops telling you which change caused it. Twenty read conversions plus a structural rewrite of the highest-volume skill is past that line. Its own release, after items 1 and 2 are green.

## 5. Cheap and unblocked

- **Lean-session guidance in the docs.** Every connector and plugin loaded contributes tool schemas to the per-turn prefix. A filing run needs the source connector and nothing else. Documentation only.
- **`model: sonnet` on `corp-os-upgrade`.** The one skill of 23 that survived the 0.18.2 reclassification as genuinely mechanical. Frontmatter supports the field; **whether Cowork honours it is unverified**, and an ignored field is a change that reaches nobody.

## 6. Measurement is unavailable where this actually runs

Cowork exposes no per-session cost or token count. `/usage` exists only in Claude Code. So for anyone running corp-os in Cowork, `usage/log.md` is the only telemetry that exists and `corp-os-improve` is the only thing that reads it. That raises the stakes on the friction field considerably and belongs in the rollout material.
