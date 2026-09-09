# Backlog

Known, measured, unfixed. Distinct from ARCHITECTURE §7, which holds open *questions* — things nobody knows the answer to. Everything here has an answer and has not been done.

Items leave this list by being done or by being declined in §8, never by being forgotten. Sizes are measured, not estimated, and the command that produced them is named so the number can be re-derived rather than trusted.

---

## 1. Unconditional reference reads

**85,879 tokens read unconditionally across 23 skills, against 90,846 behind a condition.** An unconditional read costs on every invocation of that skill whether or not the branch needing it fires. Conditional now exceeds unconditional; it did not when this list was written.

Re-derive with `python3 scripts/ref_load.py`. Add `--skill <name>` for the sentence-by-sentence view, and **read that before editing anything** — four successive versions of this measurement set the work order wrong, all recorded in §4.51.

Six skills sit at zero: `brief`, `dashboard`, `guide`, `recall`, `redact`, `glossary`.

| skill | unconditional | reads every run |
|---|---|---|
| `corp-os-setup` | 10,463 | configuration, data-model, interrogation |
| `corp-os-claims` | 8,878 | claim-record, data-model |
| `corp-os-rebuild` | 8,878 | claim-record, data-model |
| `corp-os-reality-check` | 5,834 | claim-record |
| `corp-os-configure` | 5,696 | configuration |
| `corp-os-migrate` | 5,696 | configuration |

**`claims` and `rebuild` are next, and they are the same 8,878.** Both read `claim-record.md` and `data-model.md` on every run, and both have a real case for it: claims is the skill that writes claims, rebuild is the skill that re-derives them. Neither is obviously gateable, which makes them the point where this item stops paying and item 1b starts.

**1b. Split `configuration.md` and `claim-record.md`.** At 5,725 and 5,857 they are the two largest reference files and between them account for most of what is left above. Six of the seven remaining skills read one of them whole to use part of it. This is the 0.16 split applied one level down, and it is a different piece of work from gating a read.

**Frequency is not in the table and has to be applied by hand.** `setup` runs once per OS; `claims` runs constantly. The ranking above is per-run cost, not annual.

**The pointer has to be gated, not just present.** A pointer phrased as a statement ("`X` is specified in `reference/y.md`") satisfies the reachability check and still pulls the whole file every run. The form that works names the branch.

**Do not convert a read without the reachability check green** (`scripts/validate.py`).

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
