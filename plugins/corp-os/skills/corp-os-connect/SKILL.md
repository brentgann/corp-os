---
name: corp-os-connect
description: Registers a data source in a Corp-OS knowledge base — establishing how it connects (MCP connector, API token, browser session, export file, or manual paste), what it feeds, which jobs it serves, its cadence, and critically what it is blind to. Use when someone says "connect my meeting notes", "hook up Slack", "add a data source", "what's feeding my OS", "why isn't this pulling", or wants to set up automatic input. Not for actually retrieving data from an already-registered source (use corp-os-pull) and not for one-off pasted content (use corp-os-intake).
---

# Corp-OS connect

Configures and audits what feeds the OS. This skill establishes the contract; `corp-os-pull` executes against it.

Read the connector registry section of `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md` and the plugin's `CONNECTORS.md` for how tool categories work.

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

Do not schedule anything without asking.

## The write gate

`connectors.md` is derived-layer: propose, confirm, then write. Update `meta.json`'s `cutoff` map when adding a source that supports incremental pulls.

## Every run ends with

- A row in `usage/log.md`.
- A plain statement of what is now connected, what is deliberately not, and — if anything is `broken` or `stale` — the one specific thing to fix first.
