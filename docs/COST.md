# What a run costs, and how to spend less

Every number here was measured, and the command that produced it is named. Re-derive rather than trust.

---

## The shape of a bill

A session's cost is not mostly the files a skill reads. In a real usage breakdown of a working session, **54% went to the per-turn prefix** — the system prompt, every loaded tool's schema, and every installed skill's description, re-sent on every single turn. Reading and writing files was 8.8%. The connector the run was pulling from was 0.8%.

Three things follow, and they are the whole of this document.

**Turn count is a multiplier on everything.** A step that takes ten turns pays the prefix ten times. This is why filing moved into `scripts/file_raw.py` in 0.19.1: naming and deduping forty items was forty turns of arithmetic, each one re-sending the session.

**What is loaded costs even when unused.** Every connector and plugin enabled in a session contributes tool schemas to that 54%, whether the run touches them or not.

**What a skill reads is the smallest of the three**, and it is still worth managing, because it is the part that grows with the corpus.

## Run a filing pass in a lean session

`corp-os-pull` and `corp-os-intake` need the source connector and nothing else. Everything else enabled is schema re-sent on every turn of a run that will not use it.

The same session that is right for `corp-os-recall` — connectors, browser, whatever else — is the wrong one for a backlog pull.

## Cap what comes in, deliberately

The `capture` block (`reference/capture.md`) is what decides a run's cost:

- **`mode: triaged`** (default) lists items and fetches bodies only for what a person keeps. In a measured run this took the source connector to 0.8% of the bill.
- **`batch: 10`** caps items per pass. Context accumulates *within* a pass, so cost is quadratic in items; splitting into passes resets it. This is not a linear saving.
- **`body: excerpt`** writes what was cited plus a pointer instead of the whole item. It requires `Verbatim fetch` on the source, and the trade is real: **a rebuild can re-derive what was cited and cannot discover what was missed.**

## Three directories called `scripts/`

Get this wrong and a script looks missing when it is simply somewhere else. It has caused that twice.

| directory | holds | how it gets there |
|---|---|---|
| `<clone>/scripts/` | repo tooling — `validate.py`, `corpus_load.py`, `ref_load.py`, `make_fixture.py` | clone only; never copied into an OS |
| `<clone>/plugins/corp-os/scripts/` | the **shipped** scripts — `build_index.py`, `file_raw.py`, `prune_config_notes.py` and the rest | clone, or an installed plugin |
| `<an-os>/scripts/` | that OS's own copies of the shipped ones | written by `corp-os-setup`, refreshed by `corp-os-upgrade` |

Every shipped script takes `--root`, so any of them can be run straight from a clone against an OS that has not upgraded yet:

```bash
python3 <clone>/plugins/corp-os/scripts/prune_config_notes.py --root /path/to/an-os
```

Sixteen skills call the **OS's** copy, which is why `corp-os-upgrade` exists and why fixture script drift now fails the build: a stale copy means every skill measured something other than what ships.

## Measure before you optimise, and measure for free

Two scripts answer most cost questions with no model and no tokens:

```bash
# from a clone of this repo, pointed at any OS
python3 scripts/corpus_load.py /path/to/an-os --sections
```

What every skill reads on pre-flight against a real OS, and the token cost of each `INDEX.md` section. Run it against a copy of a real corpus; it is the only way to see anything that scales with corpus size.

**This is repo tooling, not an OS script.** It is not in `scaffold.py`'s `SHIPPED` list, so no OS carries a copy — run it from a clone and point it at the OS, never the other way round. It needs the plugin's `skills/` and `reference/` for the per-skill table; pass `--plugin` or set `CLAUDE_PLUGIN_ROOT` if you are running against an installed copy rather than a clone. Without it the OS-side numbers still print, and those are the ones that scale.

`build_index.py` is the opposite: every OS carries its own copy, and that copy is the one to run.

```bash
python3 /path/to/an-os/scripts/build_index.py /path/to/an-os
```

```bash
python3 scripts/make_fixture.py /tmp/big --claims 800 --files 25
```

A deterministic corpus of any size. The 800-claim version found three defects in an afternoon that had survived sixteen releases, all of them invisible at four entries: two uncapped index sections, a layer threshold counting files instead of entries, and three fixtures running a script half the size of the shipped one.

### What this found on a real 852-claim OS

Every step was a script run. No model, no tokens. Each number is the one the previous step made visible.

| | floor | what changed |
|---|---|---|
| start | **9,508** | 3,846 config + 5,662 index |
| 0.19.3 | 8,084 | a layer with its own index was listed in the root too |
| note prune | 7,345 | 783 tokens of rationale moved to the OS README |
| 0.19.7 | 6,743 | 47 of 82 entry paths were the slug of their own name |
| config rewrite | **5,501** | dead keys, `"type": "string"` everywhere, notes cut to the instruction |

**42% off what every skill pays before doing any work.** The OS share of the most expensive skill's pre-flight went from 41% to 28%.

The synthetic 800-claim fixture put the same floor at 1,541, which is why none of this was visible until someone ran it against a real corpus: eleven layers instead of five, prose in config, long entry names, and four layer roles the model does not define.

Four of the five steps came from a measurement that had already been read wrong. The per-entry cost was blamed on `index_line` templates three separate times, including once against a layer whose template is `{name} — {gist}` — two fields, nothing to remove. Splitting the line into label, path and rendered content answered it in a minute. **Read the mechanism, not the number.**

The config rewrite also fixed things that were not costs at all: a duplicate `dashboards` key silently discarding a declaration, four layers declaring roles nothing reads, `gated: true` on eight layers that no code has ever read, and three files with no role — one of them holding the only copy of the source registry.

Where it stops paying: what remains is `decisions` carrying five fields, and entry names in `topics` and `insights` that are long because they are descriptive. Both are judgment calls about someone's own data, with a ceiling of a few hundred tokens.

## Know where you are running

`/usage` in Claude Code reports session tokens, a locally computed dollar figure, cache hit rate, and a breakdown attributed to skills, plugins and MCP servers. **Cowork exposes none of this.** If a team runs corp-os in Cowork, `usage/log.md` is the only telemetry that exists and `corp-os-improve` is the only thing that reads it — which is why the friction field is not bookkeeping.

Do cost work in Claude Code. Move to Cowork for what the GUI is better at.

## Match the model to the pass

Every skill declares its pass type under its title. **Mechanical** means nothing in it needs judgment, and those can carry `model: sonnet` in frontmatter — roughly 60% cheaper per token.

Exactly one skill of twenty-three qualifies today, and the reason is worth stating: two were reclassified in 0.18.2 after a review found them inferring tags and proposing what to keep. The saving is not in routing judgment to a cheaper model. It is in moving mechanism out of the model entirely, so what is left is small and correctly expensive.

**That last sentence had no measurement behind it for seven releases. It has one now.** The full suite was run at both models on the same code (0.25.1): Sonnet 4.5 **137/163**, Opus 5 **36/40** over the seven cases repeated three times each.

On the cases both models ran, they are within a check of each other — and Sonnet won one of them. The suite-level gap is not spread across the skills; it sits almost entirely in `setup` (2/9), `intake` (5/8), `connect` (3/5), `decide`, `pattern`, `redact-strips`, `guide`, `brief` and `configure`. The skills that tie are the ones running through `propose.py`, `file_raw.py`, `build_index.py`, `friction_scan.py` and `log_run.py`.

**So model sensitivity tracks how much of a skill is still judgment, and the routing question answers itself release by release rather than once.** Three steps left the model in one week and three skills changed category. The way to make `intake` cheap is to keep moving its mechanism into `file_raw.py`, not to move it to a cheaper model — it is the one case that did the work and left none of the record.

**That measurement was run, and it came back negative.** `recall`, `rebuild` and `pull` all scored perfectly at one run each and none of them held at three. The `usage/log.md` row — the step the entire enforcement chain depends on — landed in 1 of 3, 1 of 3 and 2 of 3 across the `recall` cases, and `rebuild` wrote to `raw/` in 2 of 3. **Nothing is pinned.** A skill that reads mechanical can still be the one deciding what reaches an answer, and the single-run suite could not see the difference. Details in `BACKLOG.md` §0c.

**And the field itself is only documented for one surface.** `model:` is [specified for Claude Code](https://code.claude.com/docs/en/skills.md), accepts the `/model` values plus `inherit`, and is **silently ignored** when the value is unavailable — no error, no warning, the session simply keeps its model. It is not documented for Cowork or for the Agent SDK. So a pin is a cost optimisation that may or may not apply where a given person runs this, and nothing here is allowed to depend on it.

## What does not save money

**Trimming skill descriptions.** All twenty-three total 3,655 tokens per session, about two cents at Opus rates. They are what routes a request to the right skill among twenty-three siblings, and a misroute wastes a whole run. Do not cut them without running the routing harness.

**Capping a findings list.** `usage/health.md` is uncapped on purpose. A finding visible only when it is one of the first thirty is not visible.
