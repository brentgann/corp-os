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

For reference, at 800 claims the pre-flight floor every skill pays on every run is **1,541 tokens**, down from 2,513 before 0.19.0.

## Know where you are running

`/usage` in Claude Code reports session tokens, a locally computed dollar figure, cache hit rate, and a breakdown attributed to skills, plugins and MCP servers. **Cowork exposes none of this.** If a team runs corp-os in Cowork, `usage/log.md` is the only telemetry that exists and `corp-os-improve` is the only thing that reads it — which is why the friction field is not bookkeeping.

Do cost work in Claude Code. Move to Cowork for what the GUI is better at.

## Match the model to the pass

Every skill declares its pass type under its title. **Mechanical** means nothing in it needs judgment, and those can carry `model: sonnet` in frontmatter — roughly 60% cheaper per token.

Exactly one skill of twenty-three qualifies today, and the reason is worth stating: two were reclassified in 0.18.2 after a review found them inferring tags and proposing what to keep. The saving is not in routing judgment to a cheaper model. It is in moving mechanism out of the model entirely, so what is left is small and correctly expensive.

## What does not save money

**Trimming skill descriptions.** All twenty-three total 3,655 tokens per session, about two cents at Opus rates. They are what routes a request to the right skill among twenty-three siblings, and a misroute wastes a whole run. Do not cut them without running the routing harness.

**Capping a findings list.** `usage/health.md` is uncapped on purpose. A finding visible only when it is one of the first thirty is not visible.
