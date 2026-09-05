---
name: corp-os-jobs
description: Adds, sharpens, splits, re-scopes, or retires the jobs to be done in a Corp-OS knowledge base, and keeps each job's evidence list current so intake and recall have a priority signal. Use when someone says "add a job", "I have a new thing I'm working on", "this job is too big", "sharpen my job statement", "what am I even trying to do here", "close this out", or when a job's evidence list needs updating. Not for setting up an OS from scratch (use corp-os-setup) and not for capturing source material (use corp-os-intake).
---

# Corp-OS jobs

Jobs are the organizing primitive. Everything else in the OS hangs off them, which means a sloppy job record degrades intake priority, recall relevance, and every dashboard at once. This skill is where that quality is enforced.

Read `${CLAUDE_PLUGIN_ROOT}/reference/jtbd-patterns.md` and the job record section of `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md` first.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — scan

Read the OS `README.md`, `INDEX.md`, and `jobs/INDEX.md`. Read the specific job records in play. Never load `raw/`.

If there is no OS, say so and point at `corp-os-setup`.

## Before adding jobs to an OS that has none

If this OS has `layers.jobs.enabled: false`, or has an open-items layer already carrying the priority signal, do not just switch jobs on. Run the test in `${CLAUDE_PLUGIN_ROOT}/reference/jtbd-patterns.md` first: cluster the existing material into candidate jobs *without* looking at its subject taxonomy, then compare. Clusters that reproduce the existing taxonomy mean the material is subject-shaped, and a jobs layer will duplicate structure that already works.

Say so if that is the finding, and say what to do instead — usually splitting the open-items layer by grammatical form (findings, errands, decisions) rather than adding a layer above it. Being wrong about this costs the person a migration and costs the model its credibility.

## Adding a job

**Do not accept the first phrasing.** People describe tasks and deliverables; a job is neither.

1. Get it into `When <situation>, I want to <motivation>, so I can <outcome>` form. Use the malformed-shape repairs in `jtbd-patterns.md` — artifact-as-motivation and missing-outcome are the two most common, and both produce a job that cannot be closed.
2. Ask for the definition of done. If they cannot name how they would know it went well, the job is not ready — say so and either park it as `readiness: low` or find the real job underneath.
3. Ask what they still need to know. Push for specifics: "whether the churn started before or after the price change," not "more on churn." This list is the intake priority signal, so vague entries buy nothing.

   Give every evidence item an **answer-status**, not just an open/closed state: `open` (nothing yet), `signal exists` (something points at an answer without establishing it), `partial` (answered in part — name what is missing), `in motion` (being answered by work already underway rather than by research), `answered` (with the claim ID that resolved it). Binary open/closed hides the most useful category: an item where signal exists needs a different next action than one with nothing on it, and collapsing them means the person re-discovers the difference every time they look.
4. Check for overlap with existing jobs before creating. Enriching an existing job usually beats a new one, and two jobs with overlapping evidence lists is the most common way this layer rots.
5. Assign the next `job-NNN` from `meta.json`, write the record, add the one-line `jobs/INDEX.md` entry, recount.

## Sharpening an existing job

Signals worth acting on, and what each means:

- **Evidence list over ten items** — it is a cluster, not a job. Split by the decision each item serves.
- **Evidence list empty while the job is active** — either it is actually done, or nobody has asked what it needs. Ask.
- **Everything on the list still `open` after weeks** — the job is not being served by any registered source. Check `connectors.md` for a blind spot, and say so plainly rather than leaving the list looking merely neglected.
- **Items sitting at `signal exists` indefinitely** — signal that never gets promoted is the most common place a job quietly stalls. Each one needs a named next step: who to ask, or what to pull.
- **Definition of done nobody could check** — rewrite it as an observable.
- **No `last_touched` change for a full horizon period** — surface for retirement review. Do not retire unprompted.
- **Same claims serving two jobs entirely** — they are one job with two names. Propose a merge.
- **Success signals that are aspirations** — replace with checkable observables, or move the aspiration to the outcome clause where it belongs.

## Splitting

Split when the evidence list serves two distinct decisions. Create the new job records, divide the evidence list, re-link claims to whichever job each actually serves (a claim may serve both), and leave a `History` note in each new record naming the parent. Update `jobs/INDEX.md` for all affected jobs in the same pass.

Never split by subject. Split by decision — subject splits recreate the topic-organized system that jobs exist to replace.

## Retiring

A job retires when its definition of done is met, its trigger stopped occurring, or it belongs to someone else now.

On retirement:

1. Set `status: retired` and log why in `History`. Never delete the record.
2. Find claims that served **only** this job. Propose retiring them too — this is the pruning rule that keeps the OS from growing forever, and it is the whole payoff of job-organization. Never delete them silently.
3. Note anything learned that outlives the job, and propose it as a durable claim with `Decay: none`.
4. Update `jobs/INDEX.md` and recount.

## The write gate

`jobs/` is derived-layer. Propose every job creation, edit, split, merge, and retirement, and wait for confirmation before writing — including changes that look purely mechanical.

`jobs/INDEX.md` and `meta.json` counts get updated in the same pass as any confirmed write. A job record that exists without its one-line index entry breaks the scan contract for every other skill.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-jobs --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

- Recounted `meta.json` (`jobs`, `next_job_id`) verified against an actual file count.
- One row appended to `usage/log.md`. Put the real friction in the friction field — "person could not state a definition of done for two of three jobs" is exactly the signal `corp-os-improve` needs.
- A concrete next action: what to capture for the job's top evidence item, and which source is most likely to have it.
