---
name: corp-os-brief
description: Produces the recurring operating brief for a Corp-OS knowledge base — what came in, which jobs moved, what needs review, what went stale, what is blocked, and the single most useful thing to do next — and can set itself up as a scheduled daily or weekly run. Use when someone says "brief me", "what's the state of my OS", "my weekly review", "what needs my attention", "set up a daily brief", or wants a recurring digest of their own knowledge base. Not for answering a specific question (use corp-os-recall) and not for a visual dashboard (use corp-os-dashboard).
---

# Corp-OS brief

The operating rhythm. The specific fix for the person whose last knowledge system died of neglect: a recurring moment where the OS is read rather than only written to.

A brief is short. If it runs past a screen, it has become a report and will stop being read.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — scan

Read `config.json` (for cadence, layers, and vocabulary), then `INDEX.md`, `jobs/INDEX.md`, `claims/INDEX.md`, `connectors.md`, `meta.json` (for the last brief's date in `history`), and the tail of `usage/log.md`.

Brief on the layers this OS actually has, in its own words. A section about a layer that is disabled is noise.

Never load `raw/`. The unprocessed queue in `INDEX.md` tells you what came in without reading it.

## Step 1 — establish the window

Since the last brief, per `meta.json` history. If there is no prior brief, ask for a window rather than briefing on the whole corpus — a first brief covering four months is a report, not a brief.

## Step 2 — assemble, in this order

Order matters. Lead with what changed, not with housekeeping.

**What moved.** Jobs whose status, readiness, or evidence list changed. Name the job and the change in one line each. This is the section the person actually wants.

**What came in.** Counts by source, plus the two or three items that mattered. Do not list twelve meetings; say "twelve meetings pulled, two bear on job-004." The unprocessed count belongs here.

**What needs a decision.** Claims proposed and awaiting confirmation, `disputed` pairs unresolved, jobs with no definition of done. Each is something only the person can settle, so keep this list short and specific or it gets ignored wholesale.

**What went stale.** Count past decay, plus the ones bearing on active jobs called out individually. A count alone gets skimmed past; "CL-0042, which job-004 depends on, is 30 days past re-check" does not.

**What is blocked.** Jobs with blockers, and connectors `stale` or `broken`. Name who owns each blocker.

**Quiet things.** Jobs untouched for a full horizon period, connectors that returned nothing, evidence items open longest. This section catches the failure the other sections cannot: a job that is not failing, just forgotten.

## Step 3 — end with exactly one action

Not a list. The single highest-value thing to do next, chosen by consequence: an active job blocked on one piece of information beats forty stale claims in a retired area.

Then offer to do it. A brief whose next action requires the person to start a new conversation loses most of its value.

## Step 4 — tone

Write it flat. No enthusiasm about the OS, no congratulation for having captured things, no framing of maintenance as achievement. The person is reading this at the start of a workday and wants to know what changed and what to do.

Say "nothing moved this week" when nothing moved. A brief that manufactures activity to seem useful trains the person to stop reading it.

## Step 5 — scheduling

If asked to set up a recurring brief, or if the person's setup answers indicated they wanted one, schedule it — weekday mornings or weekly, matching their honest upkeep budget rather than their aspirational one. Ask before scheduling.

A scheduled brief plus recurring `corp-os-pull` is the minimum viable operating rhythm for a low-upkeep OS. Say so once when setting it up, then stop mentioning it.

Use the mechanism `${CLAUDE_PLUGIN_ROOT}/reference/scheduling.md` describes, and read it before promising a cadence — a schedule made with a session-scoped scheduler dies with the session, silently, and the person finds out weeks later when they notice the brief never came.

## Format

Chat by default — a brief is meant to be read in place. Render it as a page only when the person asks, or when it is going to someone else, in which case follow `design.md` and run it past `corp-os-redact` first if it contains anything sensitive.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-brief --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

- A dated `history` entry in `meta.json` marking the brief and its window. Write it even though nothing else about a brief changes the OS — **this is the one write a brief makes, and skipping it is silent**: the next brief has no prior date, so it either asks for a window again or covers the whole corpus, and a brief covering four months is a report nobody reads. A run that produced a good brief and no history entry has not finished.
- A `usage/log.md` row.
