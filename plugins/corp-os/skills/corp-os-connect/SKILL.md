---
name: corp-os-connect
description: Registers a data source in a Corp-OS knowledge base — establishing how it connects (MCP connector, API token, browser session, export file, or manual paste), what it feeds, which jobs it serves, its cadence, and critically what it is blind to. Use when someone says "connect my meeting notes", "hook up Slack", "add a data source", "what's feeding my OS", "why isn't this pulling", or wants to set up automatic input. Not for actually retrieving data from an already-registered source (use corp-os-pull) and not for one-off pasted content (use corp-os-intake).
---

# Corp-OS connect

Configures and audits what feeds the OS. This skill establishes the contract; `corp-os-pull` executes against it.

Read the connector registry section of `${CLAUDE_PLUGIN_ROOT}/reference/records.md` and the plugin's `CONNECTORS.md` for how tool categories work.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — enumerate what is actually available

Before asking the person anything, check what connectors, MCP servers, and tools exist in this environment. Then confirm against that list rather than asking them to recall it — this environment knows its own tool inventory better than the person does, and a wrong guess here produces a registry entry that silently never works.

Read the existing `connectors.md` if there is one.

## Step 1 — establish the contract for each source

Per source, all seven fields. Skipping any of them produces a registry that looks complete and is not:

- **Category** — the generic kind: meeting notes, chat, email, documents, issue tracker, CRM, warehouse, calendar, web. Category matters more than product, because a Corp-OS built around "Granola" breaks when the person switches tools, and one built around "meeting notes" does not.
- **Protocol** — MCP connector, direct API with a token, browser session, periodic export, or manual. Be specific; "it's connected" is not a protocol.
- **Auth** — where credentials live. Never copy a token into the OS folder. Record the mechanism, not the secret.
- **Feeds** — which `source` and `type` values this lands as in `raw/`. This is what makes dedupe and rebuild work.
- **Serves jobs** — job IDs. A source serving no job is a source worth declining; say so.
- **Cadence** — daily, weekly, on demand, or event-driven. Match the person's honest upkeep budget from setup, not their aspirational one.
- **Blind spots** — what this source structurally cannot see.

## Step 2 — the blind-spots question, asked properly

Ask it directly for every source: *what would this source never tell you?*

Meeting notes only capture calls the person joined. Chat search only reaches channels they are in. A CRM reflects what reps entered, not what customers said. An issue tracker shows what got filed, not what got decided in a hallway.

This field is the difference between an OS that knows its own edges and one that treats silence as absence. It is also the field that later explains why an evidence item never got answered — which is why it belongs in the registry rather than in someone's head.

## Step 3 — decline sources deliberately

Not every available source belongs in the OS. Write a `status: not-connected` entry with the reason for anything considered and declined. A declined source with a recorded reason is a real artifact: it stops the question being reopened every month, and it tells a future rebuild that the absence was a choice.

## Step 4 — auditing an existing registry

When asked "what's feeding my OS" or "why isn't this working," check each entry against reality rather than reporting the registry back:

- Is the connector still present in this environment?
- Is `last pull` older than the stated cadence? Mark `stale`.
- Did the protocol change under it — a connector replaced, a token expired, an export format changed? Mark `broken` with what specifically failed.
- Are there jobs whose evidence lists nothing in the registry can serve? That is the most useful finding an audit produces: a known gap, rather than a vague sense of missing information.

## Step 5 — cadence and scheduling

If a source has a recurring cadence, offer to set up a scheduled run of `corp-os-pull` for it. Recurring pulls plus a scheduled brief are what keep a low-upkeep OS alive, and they are the specific fix for the person whose last system died of neglect.

Follow `${CLAUDE_PLUGIN_ROOT}/reference/scheduling.md` for which mechanism to use and what a scheduled run has to carry to stand on its own. The failure it prevents is silent: a schedule that never fires looks exactly like a schedule that fired and found nothing.

Do not schedule anything without asking.

## The write gate

`connectors.md` is derived-layer: propose, confirm, then write. Update `meta.json`'s `cutoff` map when adding a source that supports incremental pulls.

## Two fields that decide what claims from this source can ever become

Ask both, and record both in `connectors.md`:

- **Medium** — what this source produces by default: `verbatim`, `summary`, or `mixed`.
- **Verbatim fetch** — whether the original text can be pulled back on demand.

They are different questions and the second is the one that matters. A notetaker that writes summaries but keeps transcripts is a source whose entries are **one call from a higher confidence**; a notetaker that discards them is not. Without the distinction both look identical in the record, and neither gets acted on.

Measured, in a real corpus: 599 entries were single-source summaries whose transcripts were still fetchable through the same connector that produced them, and **zero had taken that route** — because nothing in the record said the route existed. `corp-os-claims` reads these two fields to set `Source fidelity` without asking, and `build_index.py` turns them into a visible backlog.

If the person does not know whether verbatim fetch is available, write `unknown` rather than guessing. An unknown that is written down gets checked; a guess that reads as fact does not.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-connect --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

- A row in `usage/log.md`.
- A plain statement of what is now connected, what is deliberately not, and — if anything is `broken` or `stale` — the one specific thing to fix first.
