---
name: corp-os-pull
description: Retrieves new material from the sources registered in a Corp-OS knowledge base — meeting notes, chat threads, email, documents, issue trackers — writing each into the append-only raw layer with dedupe, then proposing what should become claims. Use when someone says "catch me up", "pull my meetings", "sync my OS", "what's new since last time", "import from Slack", or "update my OS" with connected sources present. Not for registering a new source (use corp-os-connect), not for pasted or handed-over content (use corp-os-intake), and not for answering a question about material already captured (use corp-os-recall).
---

# Corp-OS pull

Executes against the connector registry. Writing to `raw/` is autonomous; everything downstream of that is proposed.

Read `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md` for the raw file shape and the two-layer rule.

## Step 0 — scan and scope

Read `INDEX.md`, `jobs/INDEX.md`, `connectors.md`, and `meta.json` (for the `cutoff` map).

Then decide scope with the person if it is not obvious: all sources, or one? Since when? Default to everything since each source's recorded cutoff. If a source has no cutoff, do not silently pull its entire history — ask for a window, because a first pull that dumps two years of meetings into `raw/` buries the material that mattered.

If nothing is registered, stop and point at `corp-os-connect`.

## Step 1 — pull, source by source

For each in-scope source, retrieve everything since its cutoff. Handle each source's failure honestly: if a connector is missing, unauthorized, or erroring, mark it `broken` in `connectors.md` with the specific failure and **carry on with the other sources**. One dead connector must not abort the run.

Never work around a blocked or unavailable source by other means. Record it as broken and move on.

## Step 2 — dedupe before writing

Three distinct cases, and they need different handling:

- **Same item pulled again.** Match on `external_id`. Skip silently; this is routine.
- **One real event captured by two sources.** The same meeting present in both a notes tool and a calendar entry, or two attendees' separate notes on one call. Write **one** raw file, note the second capture in its source line, and do not treat the duplicate as independent corroboration. Getting this wrong inflates confidence, which is worse than losing the second copy.
- **Same content, no shared ID.** Compare date, participants, and substance. When genuinely uncertain, write it and flag the possible duplicate in the file rather than dropping material.

## Step 3 — write raw files

One file per source item, named `YYYY-MM-DD--<source>--<slug>.md`, with the full frontmatter from the spec: `source`, `person`, `also_present`, `date`, `type`, `jobs`, `tags`, `external_id`, `processed: false`.

Content goes in essentially as retrieved. **Do not summarize, condense, or rewrite.** This skill places and tags material; the derived layer is where interpretation happens, and a summary written at intake time cannot be re-derived later.

For `jobs`: infer from participants, subject, and each job's evidence list. Tag generously — a raw file serving three jobs should list three. When nothing matches, leave it empty rather than forcing a job; unassigned raw material is a normal and useful state.

For `tags`: draw from the vocabulary already in use in the OS. Check recent raw files and `claims/INDEX.md` rather than inventing new categories, which is how a tag vocabulary fragments into uselessness.

## Step 4 — update the index in the same pass, always

Non-negotiable, and independent of any claim decision:

- Every new raw file appears in `INDEX.md`'s unprocessed queue with a one-line gist.
- `meta.json` counts recounted programmatically; `cutoff` advanced per source; a dated `history` entry added.

A run that reports what it found only in chat, without updating `INDEX.md`, has not finished. Waiting on the claims decision before updating the index is a bug, not caution — the index describes what is in `raw/`, and that is already true.

## Step 5 — propose claims, do not write them

Read what was pulled against the open evidence lists in `jobs/`. Lead with what actually moved a job:

> Three of these bear on job-004's open question about whether the churn preceded the price change.

Then write the proposal to `proposals/PROPOSAL-<date>-<slug>.md` before presenting it — headline first, then each proposed claim with full provenance and an explicit recommendation (enrich, create, flag as conflict, decline). Hand the actual claim writing to `corp-os-claims` rather than reimplementing it here. A pull whose findings live only in the chat leaves no record of what the gate saw.

Propose only what earns a claim. A pull of twelve meetings might yield four claims, and saying so plainly is better than manufacturing twelve. Thin material stays in `raw/` where it is still searchable and still available to a future rebuild.

If sensitivity tracking is on, flag anything personnel-adjacent, comp-related, or under NDA as `sensitive` at proposal time — not later.

## Step 6 — after confirmation

Write confirmed claims, flip `processed: true` on the raw files they drew from, update the affected jobs' evidence lists (strike what is now answered), recount, and log.

## Every run ends with

- One row in `usage/log.md`. Real friction in the friction field: "four files could not be assigned to any job" or "two of five claims were proposed from a single unverified mention" is the signal `improve-corp-os` mines.
- A short report: what was pulled per source, what was skipped and why, which connectors failed, which jobs moved, and what is still sitting unprocessed.
