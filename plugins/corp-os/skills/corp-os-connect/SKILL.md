---
name: corp-os-connect
description: Registers a data source in a Corp-OS knowledge base — establishing how it connects (MCP connector, API token, browser session, export file, or manual paste), what it feeds, which jobs it serves, its cadence, and critically what it is blind to. Use when someone says "connect my meeting notes", "hook up Slack", "add a data source", "what's feeding my OS", "why isn't this pulling", or wants to set up automatic input. Not for actually retrieving data from an already-registered source (use corp-os-pull) and not for one-off pasted content (use corp-os-intake).
---

# Corp-OS connect

> **Mixed pass** — recording the protocol and cadence is bookkeeping; the blind-spots question is not. Worth the better model, and worth keeping the mechanical half in scripts so the model is paying for the judgment rather than the typing.

Configures and audits what feeds the OS. This skill establishes the contract; `corp-os-pull` executes against it.

Read the connector registry section of `${CLAUDE_PLUGIN_ROOT}/reference/records.md` and the plugin's `CONNECTORS.md` for how tool categories work.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — enumerate what is actually available

Before asking the person anything, check what connectors, MCP servers, and tools exist in this environment. Then confirm against that list rather than asking them to recall it — this environment knows its own tool inventory better than the person does, and a wrong guess here produces a registry entry that silently never works.

Read the existing `connectors.md` if there is one.

## Step 1 — which shape is this?

Before the rest of the fields, settle which shape it is, because the answer changes most of them.

**A queried source** — a warehouse, a metrics store, session analytics — has no list worth walking and no meaningful cutoff. Register `Access: query` with a query interface and a read-only role, `Cadence: on demand`, and no selector: it is scoped per question rather than per slice. It is never pulled. Do not give it a schedule; a schedule against a warehouse is a standing bill for answers to questions nobody asked.

Then say plainly what it is for: **it exists to test a hypothesis, and what lands in `raw/` is the question, the statement, the result and the run date** — a measurement, not the data. Ask whether the person's questions of it recur, because a question asked three times is a query worth storing and a candidate for a dashboard panel.

**A listed source** — meetings, mail, a wiki space, a tracker — takes the seven fields below plus a selector and a cutoff.

Registering a warehouse as a listed source is the mistake worth catching here. It reads as a connector like any other and produces a run that asks for everything since Tuesday.

## Step 2 — the fields, which depend on the shape

Every source needs **Category, Protocol, Auth, Scope, Feeds, Serves jobs, Cadence, Blind spots**. A **listed** source also needs **Selector, List call, Fetch call, Verbatim fetch, Limits, Ceiling**. A **queried** one needs **Query interface** instead, and no selector or cutoff.

Skipping any of them produces a registry that looks complete and is not — and the count has grown, so do not go from memory. Step 5 checks the record against its own shape:

- **Category** — the generic kind: meeting notes, chat, email, documents, issue tracker, CRM, warehouse, calendar, web. Category matters more than product, because a Corp-OS built around "Granola" breaks when the person switches tools, and one built around "meeting notes" does not.
- **Protocol** — MCP connector, direct API with a token, browser session, periodic export, or manual. Be specific; "it's connected" is not a protocol.
- **Auth** — where credentials live. Never copy a token into the OS folder. Record the mechanism, not the secret.
- **Feeds** — which `source` and `type` values this lands as in `raw/`. This is what makes dedupe and rebuild work.
- **Selector** — which slice of the system this is, in the system's own terms: a CQL query, a JQL filter, a board, a label, a segment. `n/a` only when the source is already scoped to one person. **For anything an organisation shares, a source with no selector is the whole instance, and registering it is registering a crawl.** Do not accept "Confluence" as a source; ask which space, and register that. Three spaces are three sources, each with its own cutoff, cadence, blind spots and jobs.

  If the person cannot name the slice yet, that is the finding, and the right move is to stop and work it out rather than register the system and sort it later. Nothing about a wholesale registration gets narrower on its own — the cutoff only moves it forward in time.
- **Serves jobs** — job IDs. A source serving no job is a source worth declining; say so.
- **Cadence** — daily, weekly, on demand, or event-driven. Match the person's honest upkeep budget from setup, not their aspirational one.
- **Blind spots** — what this source structurally cannot see.
- **Scope** — what the credential can do. **Read-only unless something genuinely requires otherwise**, because this suite only ever reads from a source. Ask for the narrower token; in a shared workspace it is the difference between a tool that stays installed and one an administrator removes.
- **Limits and ceiling** — the source's published rate limit if it has one, and a local per-run ceiling well under it. Ask what the system is, who else hits it, and whether anyone would notice this traffic. For a shared system like an issue tracker or a wiki, the honest ceiling is small: a knowledge base is not a crawler.

## Step 3 — find the cheap call, not just the connection

A source almost always has two reads: one that **enumerates** and one that **returns a body**. They differ in cost by roughly two orders of magnitude, and a registry that records only the protocol tells a skill it can reach the source and nothing about how to reach it cheaply — so the skill fetches everything, which is exactly how one intake run cost more than the connector it pulled from.

Ask for both, and record them:

- **List call** — what enumerates. Include the arguments that narrow it: the one that caps results, the one that takes a date, the one that selects fields.
- **Fetch call** — what returns a body, by id.
- **Verbatim fetch** — can the original be pulled back later, by id, unchanged? This one field decides whether skipping an item during triage defers it or destroys it, and `corp-os-pull` reads it before it reads the capture mode.

If the source can be reached by a **script** rather than through a model — an export on disk, an API with a token in the environment — record a `Fetch command` instead. Bytes fetched by a script never enter a context, and that is the difference between a capture run costing dollars and costing nothing.

**Name credentials, never write them.** `env GRANOLA_TOKEN`, not the token. This file gets synced, shared, and handed to an audit.

If the person does not know whether a list call exists, that is worth two minutes of looking. It is the single highest-value fact in the record.

## Step 4 — probe it once, bounded, before trusting any of it

A registration is a set of claims about a system, and every one of them can be wrong in a way that reads fine on the page. The selector can name a space that exists and is not the one they meant. The list call can return a different shape than its documentation. The credential can have more scope than anyone intended.

So run it once, deliberately small:

- **Listed source** — one list call, with the selector, capped at ten. Show what came back: titles, dates, who wrote them. Then ask the only question that matters: **is this the slice you meant?** A wrong selector is obvious in ten rows and invisible in a registry entry.
- **Queried source** — one statement with a `LIMIT`, against the read-only role. It either runs or it does not, and if it does not, that is better found now than inside a hypothesis.

Fetch nothing. Write nothing to `raw/`. The probe exists to check the contract, not to capture, and a first pull is a separate decision made with `corp-os-pull`.

If the probe returns a great deal more than expected, that is the finding, and the answer is a narrower selector rather than a bigger ceiling.

## Step 5 — check the record against its own shape

```bash
python3 scripts/check_connector.py --root <the OS>
```

Shape-aware: it knows a queried source needs a query interface and must not carry a cutoff, that a listed one needs its call pair and a selector unless it is personal, and that a credential is named by reference and never written. Fix what it names before moving on — a registry that looks complete and is not is the specific failure this whole step exists for.

## Step 6 — the blind-spots question, asked properly

Ask it directly for every source: *what would this source never tell you?*

Meeting notes only capture calls the person joined. Chat search only reaches channels they are in. A CRM reflects what reps entered, not what customers said. An issue tracker shows what got filed, not what got decided in a hallway.

This field is the difference between an OS that knows its own edges and one that treats silence as absence. It is also the field that later explains why an evidence item never got answered — which is why it belongs in the registry rather than in someone's head.

## Step 7 — decline sources deliberately

Not every available source belongs in the OS. Write a `status: not-connected` entry with the reason for anything considered and declined. A declined source with a recorded reason is a real artifact: it stops the question being reopened every month, and it tells a future rebuild that the absence was a choice.

## Step 8 — for a source that already exists, look at what it produced

Before adjusting a registered source, run it:

```bash
python3 scripts/source_yield.py --root <the OS>
```

Per source: raw files captured, how many any derived entry cites, how many of those serve a job. **Triage decides per item on metadata, which is the weakest evidence available. This is the strongest — what the last two hundred items from that source actually turned into — and it was already on disk.**

Read it as a ratio and not a score. Three claims per hundred files is not a failing source; it may be narrow and precious. It is asking one question: does the `Selector` still describe what you wanted? A slice that yields almost nothing is usually a slice chosen by what was easy to query rather than by what anyone needed.

Three answers, and the last is a real one: **narrow the selector**, **lengthen the cadence**, or **decline the source**. What there is never a reason to do is delete what was captured — `raw/` is append-only, and the fix is to stop capturing, not to remove.

## Step 9 — auditing an existing registry

When asked "what's feeding my OS" or "why isn't this working," check each entry against reality rather than reporting the registry back:

- Is the connector still present in this environment?
- Is `last pull` older than the stated cadence? Mark `stale`.
- Did the protocol change under it — a connector replaced, a token expired, an export format changed? Mark `broken` with what specifically failed.
- Are there jobs whose evidence lists nothing in the registry can serve? That is the most useful finding an audit produces: a known gap, rather than a vague sense of missing information.

## Step 10 — cadence and scheduling

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

Measured, in a real corpus: 599 entries were single-source summaries whose transcripts were still fetchable through the same connector that produced them, and **zero had taken that route** — because nothing in the record said the route existed. `corp-os-claims` reads these two fields to set `Source fidelity` without asking — when a source's fidelity is not obvious from these two fields, its spec is in `${CLAUDE_PLUGIN_ROOT}/reference/claim-record.md` —, and `build_index.py` turns them into a visible backlog.

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
