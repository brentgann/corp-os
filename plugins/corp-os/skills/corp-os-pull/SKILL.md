---
name: corp-os-pull
description: Retrieves new material from the sources registered in a Corp-OS knowledge base — meeting notes, chat threads, email, documents, issue trackers — writing each into the append-only raw layer with dedupe, then proposing what should become claims. Use when someone says "catch me up", "pull my meetings", "sync my OS", "what's new since last time", "import from Slack", or "update my OS" with connected sources present. Not for registering a new source (use corp-os-connect), not for pasted or handed-over content (use corp-os-intake), and not for answering a question about material already captured (use corp-os-recall).
---

# Corp-OS pull

> **Mixed pass** — fetching, deduping, writing and recounting are bookkeeping. Deciding which items to capture is not, and it is the one call in this suite that downstream cannot undo: nothing re-derives material that was never retrieved. Keep the mechanical half in scripts so the model is paying for the triage rather than the typing.

Executes against the connector registry. Writing to `raw/` is autonomous; everything downstream of that is proposed.

Read `${CLAUDE_PLUGIN_ROOT}/reference/records.md` for the raw file shape and `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md` for the two-layer rule. The `capture` block that decides what this run fetches and what it costs is specified in `${CLAUDE_PLUGIN_ROOT}/reference/capture.md`.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — scan and scope

Read `INDEX.md`, `jobs/INDEX.md`, `connectors.md`, and `meta.json` (for the `cutoff` map).

Then decide scope with the person if it is not obvious: all sources, or one? Since when? Default to everything since each source's recorded cutoff.

**Pass the source's `Selector` to the list call, every time, and never list outside it.** The selector is the slice; the cutoff only moves that slice forward in time. A source whose record carries no selector and is not a personal one is an unregistered crawl — stop and hand off to `corp-os-connect` rather than listing the instance to find out how big it is.

If a source has no cutoff, do not silently pull its entire history — ask for a window, because a first pull that dumps two years into `raw/` buries the material that mattered. **For a shared system, default to no backfill at all**: start from today and let the slice fill forward. What is already in a wiki has been findable there the whole time; the value of capturing it starts when someone cites it.

If nothing is registered, stop and point at `corp-os-connect`.

## Step 1 — list before you fetch

Read `capture` in `config.json`: `mode` is `triaged` (the default) or `all`, and `batch` caps how many items one pass writes.

**Retrieve the list first, never the contents.** Titles, dates, participants, `external_id` — tens of tokens per item instead of thousands. That list is enough to dedupe, enough to see what the window actually held, and enough to decide what is worth capturing. Fetching forty bodies to discover that six mattered is the single most expensive thing this suite can do, and it was the default for sixteen releases.

- **`triaged`** — present the list with a proposed keep or skip and a one-line reason each, and fetch nothing until a person confirms. Most weeks a minority of items carry anything the derived layer will ever cite; the rest are standing meetings that produced no decision and threads that resolved themselves.
- **`all`** — fetch every body. Legitimate when the archive itself is the point, and it should be a decision somebody made rather than a default they inherited.

**One rule overrides the mode, and it uses a field the connector already carries.** Triage is safe when the source can be fetched back verbatim, because a skipped item is still retrievable — that is exactly what `Verbatim fetch` in `connectors.md` records. **For a source whose connector says no verbatim fetch, capture everything regardless of mode.** Skipping there is not deferring, it is losing it, and this model's whole position is that raw material is the one thing nothing else can rebuild.

Say the consequence out loud the first time triage runs on a source: under `triaged`, `raw/` stops being a complete archive of the source and becomes a complete archive of what was chosen. That is a real trade and the person should make it knowingly.

**Never exceed `batch` in one pass.** Report what remains and offer the next. The first run after a holiday is the worst case and the one nobody sizes.

For each in-scope source, retrieve what triage kept, since its cutoff.

**Fetch sequentially, one source at a time, unless its record says otherwise.** Concurrency is how a personal knowledge base becomes noticeable traffic on someone else's system, and nothing here is urgent enough to need it. Respect the record's `Ceiling`: when a run would exceed it, stop at the ceiling, report what remains, and **do not advance the cutoff past what was not fetched**.

**Read the failure before recording it.** Three different things are not one thing:

- **Throttled** — a 429, a `Retry-After`, a quota message. The source is healthy and asking to be left alone. Mark it `throttled` with the time, stop fetching from it this run, leave its cutoff where it is, and carry on with the others. **Never mark a throttled source `broken`**: the next run would skip a working source and the person would believe they were covered on something returning nothing.
- **Broken** — missing, unauthorized, or erroring in a way that will not fix itself. Mark it `broken` with the specific failure.
- **Empty** — reachable and had nothing. That is a normal result and it is not a failure. Advance the cutoff.

**Carry on with the other sources** in every case. One dead connector must not abort the run.

Never work around a blocked or unavailable source by other means. Record it as broken and move on.

## Step 2 — dedupe before writing

Three distinct cases, and they need different handling:

- **Same item pulled again.** Match on `external_id`. Skip silently; this is routine.
- **One real event captured by two sources.** The same meeting present in both a notes tool and a calendar entry, or two attendees' separate notes on one call. Write **one** raw file, note the second capture in its source line, and do not treat the duplicate as independent corroboration. Getting this wrong inflates confidence, which is worse than losing the second copy.
- **Same content, no shared ID.** Compare date, participants, and substance. When genuinely uncertain, write it and flag the possible duplicate in the file rather than dropping material.

## Step 3 — write raw files

**Do not write these files by hand.** Hand the whole batch to the script in one call:

```bash
python3 scripts/file_raw.py --root <the OS> --items items.json
```

`items.json` is one object per kept item: `external_id`, `date`, `source`, `type`, `body`, and optionally `title`/`slug`, `person`, `also_present`, `jobs`, `tags`. The script dedupes on `external_id` against what is already filed, builds the `YYYY-MM-DD--<source>--<slug>.md` name, suffixes rather than overwrites a collision, writes the frontmatter from the spec, and reports what it filed, what was already there, and what it rejected for missing fields.

Filing an item is arithmetic and string formatting. Done in the model it is one turn per item, and every turn re-sends the whole session prefix — which is how a filing run became the most expensive thing in this suite. What stays here is the judgment: which items to keep, and what the derived layer should hold.

Pass `--cutoff` **only when the batch reached everything in the window**, with `--source` naming the connector. If anything went unreached, leave it off: the cutoff must not pass material nobody decided about.

Content goes in essentially as retrieved. **Do not summarize, condense, or rewrite.**

`capture.body` decides how much of it lands. Under `full`, all of it. Under `excerpt`, the frontmatter plus the passages the proposal actually cited plus a retrieval pointer — which means **the order changes: propose first, from the body while it is still in front of you, then write the file carrying what you cited.** Reading a body, writing it to disk, and reading it back to propose from it pays for the same content three times, and the third pass buys nothing the second did not already have.

Neither mode summarizes. An excerpt is a verbatim span with a pointer to the rest; a summary is a different object and is what Step 3 has always refused. `excerpt` and `stub` are refused outright on a source whose connector records no verbatim fetch — a pointer to something unretrievable is not a source.

Write each file in one operation and **never quote its content back in the run summary** — report the filename, the gist line and the counts. Content that passes through twice costs twice, and the second pass buys nothing a person will read. This skill places and tags material; the derived layer is where interpretation happens, and a summary written at intake time cannot be re-derived later.

For `jobs`: infer from participants, subject, and each job's evidence list. Tag generously — a raw file serving three jobs should list three. When nothing matches, leave it empty rather than forcing a job; unassigned raw material is a normal and useful state.

For `tags`: draw from the vocabulary already in use in the OS. Check recent raw files and `claims/INDEX.md` rather than inventing new categories, which is how a tag vocabulary fragments into uselessness.

## Step 4 — update the index in the same pass, always

Non-negotiable, and independent of any claim decision:

- Every new raw file appears in `INDEX.md`'s unprocessed queue with a one-line gist.
- Counts recounted by running `scripts/build_index.py` in the OS rather than by hand; a dated `meta.json` history entry added.

**The cutoff moves differently for the two ways an item can go unfetched, and conflating them loses material silently.**

- **Skipped by triage** — a decision was made about it. Record the ids in the source's connector block as `Skipped: <ids> — <date>` with the reason in one phrase, and let the cutoff pass them. They are not re-offered every run, and they are written down, which is what makes "skipping is deferring, not losing" true rather than a claim.
- **Not reached because the batch filled** — no decision was made about it. **The cutoff does not move past it.** Advance the cutoff only to the newest item this pass actually resolved, so the remainder is the first thing the next pass offers.

A cutoff that advances past everything in the window regardless turns both a cap and a triage list into permanent, invisible data loss. The source may still hold it; nothing in the OS will ever mention it again.

A run that reports what it found only in chat, without updating `INDEX.md`, has not finished. Waiting on the claims decision before updating the index is a bug, not caution — the index describes what is in `raw/`, and that is already true.

## Step 5 — propose claims, do not write them

**Propose from what is already in context. Never re-open a file this run just wrote** — it is the same bytes at full price, and nothing has changed between writing and reading it. Under `capture.body: excerpt` this step runs *before* Step 3 for that reason.

Read what was pulled against the open evidence lists in `jobs/`. Lead with what actually moved a job:

> Three of these bear on job-004's open question about whether the churn preceded the price change.

Then write the proposal to `proposals/PROPOSAL-<date>-<slug>.md` before presenting it — headline first, then each proposed claim with full provenance and an explicit recommendation (enrich, create, flag as conflict, decline). Hand the actual claim writing to `corp-os-claims` rather than reimplementing it here. A pull whose findings live only in the chat leaves no record of what the gate saw.

Propose only what earns a claim. A pull of twelve meetings might yield four claims, and saying so plainly is better than manufacturing twelve. Thin material stays in `raw/` where it is still searchable and still available to a future rebuild.

If sensitivity tracking is on, flag anything personnel-adjacent, comp-related, or under NDA as `sensitive` at proposal time — not later.

## Step 6 — after confirmation

Write confirmed claims, flip `processed: true` on the raw files they drew from, update the affected jobs' evidence lists (strike what is now answered), recount, and log.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-pull --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

- One row in `usage/log.md`. Real friction in the friction field: "four files could not be assigned to any job" or "two of five claims were proposed from a single unverified mention" is the signal `corp-os-improve` mines.
- A short report: what was pulled per source, what was skipped and why, which connectors failed, which jobs moved, and what is still sitting unprocessed.
