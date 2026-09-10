---
name: corp-os-decide
description: Tracks the forks a person has NOT decided yet in a Corp-OS knowledge base — each open choice with its named options, an owner, a decide_by date past which it gets made by default, what it is blocking, and what evidence would settle it — then records the outcome and hands it to corp-os-claims once the call is made. The test is tense: this is only for a choice still open. Use when someone says "we're stuck between two options", "what's still open", "what am I waiting on", "log this open decision", "this keeps coming back up and never gets settled", or names a live fork with a deadline or an owner. Not for a decision already made — "we went with X", "why did we decide that" — which is a decision claim via corp-os-claims. Not for an outcome someone is working toward, like "decide how to handle renewals", which is a job (use corp-os-jobs).
---

# Corp-OS decide

> **Judgment pass** — the reasoning is the product here. Run it on your best model, and do not economise by skipping the questions it asks.

A claim of kind `decision` records a call that was already made. This skill carries the ones that have not been made yet, which is a different object with different fields and a different failure mode: a claim rots by going stale, and an open decision rots by going quiet.

The distinction is the whole reason this layer exists. **A decision nobody is tracking does not feel like a problem — it feels like flexibility**, right up until the option that mattered has expired and the choice was made by default. That is the specific thing this skill is here to prevent, and it is why every open decision carries a date.

Read the decision record section of `${CLAUDE_PLUGIN_ROOT}/reference/records.md`.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

If `layers.decisions` is not declared, this OS has no decision layer. Offer to add one via `corp-os-configure` and say what it buys — a place where a live fork is visible between the moment it appears and the moment it closes. Do not create it silently, and do not fake it by writing `decision` claims for choices nobody has made.

## Step 0 — scan

Read `INDEX.md`, `jobs/INDEX.md`, the decision layer's index, and `claims/INDEX.md` for prior decisions that bear on this one. Never load `raw/`.

## Step 1 — tell a decision from the three things it gets confused with

Most of what people call a decision is one of these, and filing it wrong means it never closes:

- **A job.** "Decide how to handle renewals" is an outcome someone is working toward, not a fork. Hand to `corp-os-jobs`.
- **A task.** "Decide who to email" completes once and leaves nothing worth keeping. It belongs in a task tracker.
- **A finished decision.** "We went with Postgres" is a `decision` claim: made, citable, decayable. Hand to `corp-os-claims`, and note the direction of travel — this skill produces those claims as its output, so a finished call that was never tracked here still files as a claim rather than as a closed record nobody opened.

What is left is the real thing: **a choice between named options that is currently open, that someone is or should be responsible for, and that something else is waiting on.** If nothing is waiting on it, it is a preference, not a decision — record it as a `preference` claim and move on.

## Step 2 — get the fields, and push on the three that get skipped

- **Statement** — the fork as a question with its options visible. "Per-seat or usage pricing for the mid-market tier," not "pricing."
- **Options** — two or more, each named, each with what it costs and what it buys. A single option is not a decision; it is an announcement waiting for approval.
- **Owner** — a person, not a team. **Push here.** A decision owned by "us" is owned by nobody, and it is the most reliable predictor that a fork will still be open in three months. If the honest answer is that the owner is someone else entirely, that is worth recording too: the decision is then *blocked on a person*, which is a different problem with a different fix.
- **`decide_by`** — the date after which the choice is made by default or the good option expires. **Push here too.** "No deadline" is almost never true; there is usually a contract date, a release, a budget cycle, or a point past which the reversible option stops being reversible. Write that date and what happens at it. A decision with no date is the one that goes quiet.
- **Blocks** — the jobs, deliverables, or other decisions waiting on this. This is what orders the list; a decision blocking an active job outranks an interesting one blocking nothing.
- **What would settle it** — the specific evidence that would make the answer obvious. Write this as an evidence item on the owning job, so intake and recall start working on it. A fork whose settling evidence is never named is one that gets re-argued from the same position every time it comes up.
- **Reversibility** — `reversible`, `costly`, or `one-way`. This is what sets how much evidence is worth gathering before deciding: a reversible call made quickly and corrected beats a one-way call made slowly on the same information, and treating both the same way is how a team spends a month on something they could have tried in an afternoon.
- **Status** — `open`, `blocked`, `decided`, `lapsed`, `moot`.

## Step 2.5 — write the proposal before the record

1. **Write the proposal to disk before anything is written to `decisions/`.** Not a proposal made in the conversation — a file, because the conversation ends and the file is what the gate leaves behind:

```bash
python3 scripts/propose.py --root <the OS> --layer decisions --slug <batch> \
  --headline "<the one thing here that matters>" \
  --item "<create|enrich|flag|decline> · <id> · <what>" \
  --not-proposing "<what is being held back, and why>"
```

Present it, wait, then record the answer per item — the declines are the half that matters:

```bash
python3 scripts/propose.py --root <the OS> --record <the file it wrote> \
  --outcome "<item>: confirmed" --outcome "<item>: declined"
```

2. Only then write the decision record itself.

## Step 3 — check it against what is already there

- **A prior decision this would reverse.** Surface it with its date and reasoning. Reversing an earlier call is legitimate and common; doing it without seeing the original reasoning is how the same ground gets re-litigated every eight months. Link them.
- **An assumption it rests on.** If a `fact` or `assumption` claim is load-bearing on one of the options, link it. An untested assumption under a one-way decision is the highest-value thing this skill can surface, and it is the specific handoff to `corp-os-reality-check`.
- **A duplicate.** Two decisions with the same blocks list are usually one decision phrased twice. Propose a merge.

## Step 4 — the standing review

When asked "what's open" or "what am I waiting on," do not just list the layer. Order by consequence and say what each is costing:

- **Past `decide_by`** — the choice is being made by default right now. Lead with these, always, and say which option is winning by inaction.
- **Blocking an active job** — name the job.
- **Open with no owner, or no `decide_by`** — these are the ones that will still be here next quarter. Fixing the field is usually a one-question conversation, so ask it.
- **Quiet** — no movement for a full horizon period. Ask whether it is still live. `moot` is a perfectly good outcome and closing one is as useful as making one.

## Step 5 — closing it

On a decision being made:

1. Set `status: decided` with the date, the option chosen, and **the reasoning at the time** — not the reasoning that looks best afterward. The value of a decision log is almost entirely in being able to tell later whether a call was wrong or merely unlucky, and that distinction is unrecoverable if the record was written to look good.
2. Write it as a `decision` claim via `corp-os-claims`, with the decision record as its source. The claim is what recall surfaces and what decays; the record is what shows how the call got made.
3. Note what would make it worth revisiting, and set that as the claim's decay. Decisions do not become false the way facts do — they become obsolete when their inputs change, so the re-check condition is more useful than an interval.
4. Strike the settled evidence item from the owning job.

A decision that **lapsed** gets the same treatment with `status: lapsed` and an honest line about what the default outcome turned out to be. Those records are the most useful ones in the file after a year, and they are the ones a person is most tempted not to write.

## The write gate

The decision layer is derived. Propose every creation, edit, and closure, and wait for confirmation — including a closure the person just described in conversation, because the reasoning is what gets lost and it is worth reading back before it is written.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-decide --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

It also refuses to close a run that put something in a derived layer with no proposal file behind it, and names the files and the `propose.py` call that repairs the record. The gate is checked here because this is the step that never gets skipped — three attempts at stating it nearer the write got it to one run in three.

- Recounted index and `meta.json`, verified against an actual file count.
- A `usage/log.md` row. Real friction: "three of five open decisions had no owner" is exactly the signal `corp-os-improve` needs — it points at a review cadence problem, not a schema problem.
- One concrete next action: the decision closest to its date, and the one question that would settle it.
