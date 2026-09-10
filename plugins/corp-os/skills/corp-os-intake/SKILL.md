---
name: corp-os-intake
description: Takes material a person pastes, uploads, or hands over directly — a transcript, a chat thread, a document, an email, a personal note, a screenshot of something — and files it into a Corp-OS knowledge base's append-only raw layer with the right type and job tags, then proposes what should become claims. Use when someone says "add this", "log this", "capture this conversation", "here's a transcript", "save this note", or attaches a file and wants it in their OS. Not for retrieving from a connected source (use corp-os-pull) and not for answering a question about material already captured (use corp-os-recall).
---

# Corp-OS intake

> **Mixed pass** — naming, writing and recounting are bookkeeping; inferring which jobs a piece of material serves, and drawing tags from the vocabulary already in use rather than inventing new ones, is not. Tagging badly is invisible on the day and degrades every recall afterwards, so this is not the place to economise.

Most real context does not arrive through an API. Someone pastes a thread, forwards a doc, or types a note after a hallway conversation. That material deserves the same discipline as a connector pull: filed as-is, typed correctly, job-tagged, and never treated as reviewed knowledge until a person says so.

Read `${CLAUDE_PLUGIN_ROOT}/reference/records.md` for the raw file shape and `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md` for the two-layer rule. The `capture` block that decides what this run fetches and what it costs is specified in `${CLAUDE_PLUGIN_ROOT}/reference/capture.md`.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — scan

Read the OS `README.md` (for its actual conventions, which may differ from the shipped spec), `INDEX.md`, and `jobs/INDEX.md`. Check a couple of recent raw files to match the frontmatter and tag vocabulary in use.

No OS? Point at `corp-os-setup`. Do not scaffold one inline.

## Step 1 — classify what was handed over

Set `type` and `source` from what the content actually is:

- **transcript** — multiple named speakers in back-and-forth.
- **thread** — short bursts, mentions, informal chat shape.
- **document** — structured prose with headings, a spec, a report, a deck's text.
- **note** — first-person, single voice: a post-call summary, a personal log.
- **call** — a synchronous conversation the person is reconstructing from memory.
- **research** — material gathered from outside sources.
- **web** — content from a page.

When genuinely ambiguous, just ask. The person is right there, which is the whole difference from an automatic pull where a bad guess surfaces much later.

For an uploaded file, read it before filing it. Never file a document based on its filename.

## Step 2 — check for a duplicate

No connector ID to match on, so the check is literal: does this look like content already in a recent raw file — same date, same people, substantially the same text?

Two cases worth distinguishing:

- **Accidental re-paste.** Ask; do not write a second file.
- **A second person's capture of the same event.** Write one file and note the second capture explicitly in the source line. Two captures of one conversation are not two pieces of evidence, and treating them as such is how confidence gets quietly inflated.

## Step 2.5 — if it is more than a handful, cap the pass

`capture.batch` in `config.json` applies here too. Someone handing over a folder of forty documents is the same run as an uncapped pull, and it costs the same. File up to `batch`, report what remains, and offer the next pass.

Where the material is a bundle rather than one item, list it first — names, dates, kinds — and confirm what is in scope before reading any of it in full.

## Step 3 — file it

Write `raw/YYYY-MM-DD--<source>--<slug>.md` with full frontmatter and a `> Source:` line saying how it was captured — pasted transcript, forwarded email, uploaded doc, typed from memory. Typed-from-memory is worth marking, because it caps every claim drawn from it at `reconstructed` rather than `confirmed`.

Content in essentially as given. Do not summarize or clean it up. Fix nothing but obviously broken formatting.

For a note the person is writing now, capture their words rather than a polished version of them — a paraphrase loses the hedges, and the hedges are usually the honest part.

Job tags: infer from the open evidence lists in `jobs/`. Empty is acceptable.

## Step 4 — update the index, unconditionally

Run `scripts/build_index.py` in the OS. It reads `processed: false` off the frontmatter you just wrote and renders the queue entry itself, which is why the file needs that flag set correctly more than it needs a hand-written line. If the OS has no copy of the script, add the queue entry and the count by hand instead.

Then **open `INDEX.md` and confirm the new file is actually in it.** Not a formality: measured against a fixture, this is the step this skill drops. The raw file gets written, `meta.json` gets recounted, the proposal gets filed, the log row gets appended — and the index entry is missing, because by that point the interesting work is done and the bookkeeping feels finished. A file that exists and is not in its index is invisible to every later run's scan, so the person's queue silently under-reports and the material they handed over never resurfaces.

Add a dated `meta.json` history entry.

All of this happens in the same pass as the write, regardless of what happens with claims. Reporting the addition only in chat is not finishing the job.

## Step 5 — propose claims

Read the material against the open evidence lists and say plainly whether it moved anything:

> This answers job-002's open question about who owns the migration decision.

Then write the proposal to `proposals/PROPOSAL-<date>-<slug>.md` and present it — each claim with full provenance and an explicit recommendation (enrich an existing claim, create a new one, flag a conflict, decline). Hand the writing to `corp-os-claims`.

**If the person gives an instruction about where derived content may live** — *"this stays out of her person record"*, *"file it but leave no pointer"* — write it into the raw file's frontmatter as `placement:`, per `${CLAUDE_PLUGIN_ROOT}/reference/claim-record.md`. An instruction recorded only in a derived file, or only in the conversation, is one a rebuild will not read: regeneration is schema-driven, so it faithfully re-derives the content the person asked you not to produce. That is the one failure in this suite that destroys a commitment rather than degrading an answer, and the override has to live with the source it governs.

**If the material's natural shape does not fit any layer that exists**, do not force it into a claim just because `claims/` is what is there. A directory of people, a set of live decisions, a register of obligations — each has its own shape, and a claim distorts it. Hand off to `corp-os-configure` to declare the layer properly first, then come back and propose entries into it.

A layer improvised inline skips the interrogation that catches shape mistakes — the wrong `role`, a missing `index_line`, a path that looks like a directory but behaves like a single grouped file. That last one shipped in this plugin for five releases and silently undercounted the moment a second entry landed. The interrogation exists because those errors are cheap to prevent and expensive to unpick.

Three honest outcomes, and thin is the most common:

- **Substantive** — propose the claims.
- **Thin** — say so. It is filed, tagged, and searchable, and a future rebuild can still use it. Manufacturing a claim from thin material is the failure mode that makes a claims layer untrustworthy.
- **Contradicts something known** — this is the highest-value case. Do not overwrite the existing claim. Surface the conflict, cite both sides, and hand off to `corp-os-reality-check`.

If the OS has no claims layer yet, the filed raw file plus the updated queue *is* the deliverable. Say what was added and stop.

## Step 6 — after confirmation

Write confirmed claims, flip `processed: true`, update affected job evidence lists, recount, log.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-intake --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

It also refuses to close a run that put something in a derived layer with no proposal file behind it, and names the files and the `propose.py` call that repairs the record. The gate is checked here because this is the step that never gets skipped — three attempts at stating it nearer the write got it to one run in three.

- **`INDEX.md` re-read and the new file confirmed present in it.** Check it rather than assuming it; see Step 4.
- A `usage/log.md` row with the honest friction.
- What was added, how it was typed and tagged, which jobs it touched, and the one thing worth doing next.
