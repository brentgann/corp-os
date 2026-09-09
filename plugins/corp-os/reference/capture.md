# Capture

The `config.json` block that decides what a run fetches and what it costs. Its only readers are `corp-os-pull` and `corp-os-intake`; it lives in its own file because every other home charged skills that do not use it. Read with the raw-file shape in `${CLAUDE_PLUGIN_ROOT}/reference/records.md`, which it decides the contents of.

## How much comes in, and what that costs

```json
"capture": {
  "mode": "triaged",
  "body": "full",
  "batch": 10
}
```

The block that decides what a pull or a bulk intake costs, and it exists because nothing did. An uncapped run against a week of meetings fetches every body and writes every one back out; output is the expensive half of a bill, so a mechanical filing run became the most expensive thing in the suite while leaving the same usage-log row as a recall.

**`mode`**

- **`triaged`** (default) — retrieve the list first, propose keep or skip per item with a reason, and fetch bodies only for what a person confirms. `raw/` then holds a complete archive of *what was chosen*, not of the source.
- **`all`** — fetch everything in the window. Right when the archive itself is the deliverable, and it should be chosen rather than inherited.

**One rule overrides `mode`, and it reads a field the connector registry already carries.** Triage is only safe where the source can be fetched back verbatim: a skipped item is deferred, not lost. So for any source whose `Verbatim fetch` is absent, `corp-os-pull` captures everything regardless of mode. Skipping there is destruction, and raw material is the one layer nothing can rebuild.

**`body`** — how much of a kept item is written to `raw/`. This is the one that decides what a run costs when the source can only be reached through a model, because the body enters a context on the way in and is written back out on the way to disk, and output is the expensive half.

- **`full`** (default where there is no verbatim fetch) — the whole thing, as retrieved. A complete archive, and a rebuild can find claims the first pass missed.
- **`excerpt`** — frontmatter, the passages that were actually cited, and a retrieval pointer. Cost is proportional to what the material was *used for* rather than to how long it is. **A rebuild can re-derive what was cited and cannot discover what was missed** — that is the trade, and it is a real one.
- **`stub`** — frontmatter and the pointer only. Citations are fetched live. Cheapest, and it makes `raw/` a manifest rather than an archive.

`excerpt` and `stub` require `Verbatim fetch` on the source's connector record and are refused without it. A stub pointing at something unretrievable is not a source, and the first invariant is the one thing nothing else can rebuild.

The ordering this implies is worth stating: under `excerpt`, claims are proposed from the body **while it is still in context**, and the raw file is written afterward carrying what the proposal cited. Reading a body, writing it to disk, and then reading it back to propose from it pays for the same content three times.

**`batch`** caps items per pass, in both pull and intake. The run reports what remains and offers the next. The first run after a holiday is the worst case and the one nobody sizes.

**What this does not do:** it does not summarize, condense or rewrite anything it captures. Fidelity of what lands is untouched; the only question this block answers is how much lands, and how much it costs to decide.
