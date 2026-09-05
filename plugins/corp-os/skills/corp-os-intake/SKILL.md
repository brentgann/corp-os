---
name: corp-os-intake
description: Takes material a person pastes, uploads, or hands over directly — a transcript, a chat thread, a document, an email, a personal note, a screenshot of something — and files it into a Corp-OS knowledge base's append-only raw layer with the right type and job tags, then proposes what should become claims. Use when someone says "add this", "log this", "capture this conversation", "here's a transcript", "save this note", or attaches a file and wants it in their OS. Not for retrieving from a connected source (use corp-os-pull) and not for answering a question about material already captured (use corp-os-recall).
---

# Corp-OS intake

Most real context does not arrive through an API. Someone pastes a thread, forwards a doc, or types a note after a hallway conversation. That material deserves the same discipline as a connector pull: filed as-is, typed correctly, job-tagged, and never treated as reviewed knowledge until a person says so.

Read `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md` for the raw file shape and the two-layer rule.

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

## Step 3 — file it

Write `raw/YYYY-MM-DD--<source>--<slug>.md` with full frontmatter and a `> Source:` line saying how it was captured — pasted transcript, forwarded email, uploaded doc, typed from memory. Typed-from-memory is worth marking, because it caps every claim drawn from it at `reconstructed` rather than `confirmed`.

Content in essentially as given. Do not summarize or clean it up. Fix nothing but obviously broken formatting.

For a note the person is writing now, capture their words rather than a polished version of them — a paraphrase loses the hedges, and the hedges are usually the honest part.

Job tags: infer from the open evidence lists in `jobs/`. Empty is acceptable.

## Step 4 — update the index, unconditionally

Add the file to `INDEX.md`'s unprocessed queue with a one-line gist. Recount `meta.json`. Add a dated history entry.

This happens in the same pass as the write, regardless of what happens with claims. Reporting the addition only in chat is not finishing the job.

## Step 5 — propose claims

Read the material against the open evidence lists and say plainly whether it moved anything:

> This answers job-002's open question about who owns the migration decision.

Then write the proposal to `proposals/PROPOSAL-<date>-<slug>.md` and present it — each claim with full provenance and an explicit recommendation (enrich an existing claim, create a new one, flag a conflict, decline). Hand the writing to `corp-os-claims`.

Three honest outcomes, and thin is the most common:

- **Substantive** — propose the claims.
- **Thin** — say so. It is filed, tagged, and searchable, and a future rebuild can still use it. Manufacturing a claim from thin material is the failure mode that makes a claims layer untrustworthy.
- **Contradicts something known** — this is the highest-value case. Do not overwrite the existing claim. Surface the conflict, cite both sides, and hand off to `corp-os-reality-check`.

If the OS has no claims layer yet, the filed raw file plus the updated queue *is* the deliverable. Say what was added and stop.

## Step 6 — after confirmation

Write confirmed claims, flip `processed: true`, update affected job evidence lists, recount, log.

## Every run ends with

- A `usage/log.md` row with the honest friction.
- What was added, how it was typed and tagged, which jobs it touched, and the one thing worth doing next.
