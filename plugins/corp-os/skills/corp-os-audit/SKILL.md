---
name: corp-os-audit
description: Audits any existing personal or team knowledge system — one built from Corp-OS, from a different model, or grown by accident — across ten dimensions, then reports the gaps worth closing, the new skills and workflow changes worth building, and the structures that system has which the Corp-OS model lacks, exporting the generalizable ones as an improvement packet. Use when someone says "review my second brain", "audit my knowledge base", "compare my setup to yours", "what am I missing in my notes system", "what should I build next", "is my OS any good", or hands over a folder, wiki, or notebook they built themselves. Two-way by design — never converts their system to Corp-OS unasked.
---

# Corp-OS audit

> **Judgment pass** — the reasoning is the product here. Run it on your best model, and do not economise by skipping the questions it asks.

Assesses a knowledge system in place and learns from it. **Two-way by design**, and the second direction matters more: anyone running a real system for months has solved problems the shipped model has not. An audit that only grades is half a skill.

Say that out loud at the start. It changes how the person engages — from defending their system to comparing notes.

Read `${CLAUDE_PLUGIN_ROOT}/reference/os-audit-rubric.md` and `${CLAUDE_PLUGIN_ROOT}/reference/improvement-packet.md`.

## Pre-flight

Confirm their system is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory, and here that matters twice over: an audit scored from what someone remembers about their own system is worth nothing. Where anything recalled conflicts with what is written, the files win.

If what they hand over is a Corp-OS, read its `config.json` first and assess it against its own declared shape rather than the shipped defaults. A layer they disabled deliberately is not a missing layer.

## Step 0 — read their system on its own terms first

Before applying any rubric, understand what they built and why. Read their own README, index, or entry point if one exists. Sample actual entries — a handful across different areas and dates, not just the newest. Note the vocabulary and conventions they use.

Do not translate their terms into Corp-OS terms while reading. A system that calls them "notes" instead of "claims" is not thereby deficient, and reading through the model's vocabulary is how an auditor misses what is actually there.

Ask three questions before assessing:

- What made you build this, and what was going wrong before?
- What do you actually use it for, day to day?
- What annoys you about it?

That third answer usually predicts the audit's top finding, and getting it first means the report confirms something they already sensed rather than arriving as a verdict.

## Step 1 — score the ten dimensions

Per the rubric: source of truth, review gate, provenance, queryability, decay, outcome-orientation, registered inputs, output, self-improvement, adjustability.

Score each `absent`, `informal`, `partial`, or `solid`. No numeric composite — a number invites arguing with the number instead of fixing the gap.

`informal` deserves its own level and gets used often: the discipline exists in the person's head but not in the system. That is one write-down from `solid` and needs no new structure, which is a very different recommendation from `absent`.

Score from evidence in the files, not from what the person says they do. If they describe a review process, look for whether entries actually show it.

## Step 2 — the two findings that recur, and how to deliver them

**No source of truth.** Everything edited in place, no way to trace a conclusion back to what was said. The highest-consequence finding, because every other dimension is downstream: a system without a raw layer cannot be corrected, only argued with. Deliver it as a forward-looking fix — start an append-only archive now, backfill nothing. Telling someone to reconstruct eight months of sources is a recommendation nobody follows.

**Nothing decays.** Almost universal. Deliver it by asking them to name three things in their system they no longer believe. They always can, usually instantly, and that lands better than any explanation of decay windows.

## Step 3 — resist finding what the model predicts

The failure mode of an audit carried out by someone holding a model is confirming the model. Two places this bites hardest, both worth handling explicitly:

**Outcome-orientation.** Do not score this from the absence of a jobs layer. Run the test: cluster their open items into three to seven candidate outcomes *without looking at their subject taxonomy first*, then compare. If the clusters reproduce the taxonomy they already have, their material is subject-shaped and an outcome layer would duplicate working structure. Say that plainly — it is a more useful finding than the one the model wanted, and score the dimension on whether *something* provides a priority signal and a removal rule instead.

**Decay.** Before recommending decay, check whether re-verification is even possible. Count how many entries have a retrievable source. On a corpus migrated from a previous tool it is normal for a third or more to have none, and decay on those can only ever ratchet downward — producing a backlog nobody can clear, which teaches people to skip the sweep entirely. The right recommendation there is decay scoped to the sourced subset plus a one-time disposition pass on the rest.

If the evidence contradicts a recommendation you already made, say so in the report and show the counts. An audit that revises itself is worth more than one that does not.

## Step 4 — report the gaps, smallest change first

Order by what unblocks the most, and for each name **the smallest change that moves it**. Not a rebuild. Nobody rebuilds a working system on an audit's advice, so a rebuild recommendation is a wasted recommendation.

- No provenance → add a source line to new entries only. Do not backfill.
- Not queryable → add one-line descriptors to the index they already have.
- No decay → add a review date to the twenty entries that matter, not all of them.
- No outcome orientation → name three things they are trying to accomplish and tag existing entries against them.

State the trade honestly where the Corp-OS model is genuinely one option among others. Subject organization is simpler than job organization and a small system may not need jobs at all. Say so rather than presenting the model as the answer.

If they want to move to the Corp-OS model, offer `corp-os-setup` alongside a plan for migrating their existing material into `raw/`. Do not start converting anything unasked — an auditor who reorganizes someone's system is not welcome twice.

**Before recommending they change anything about their shape, check whether `config.json` can already express it.** The model is a default profile, not a schema: their layer names, label vocabulary, decay windows, retention policy, and gate strictness are all configurable, and a layer Corp-OS never imagined can be declared with its own schema and index line. Most of what looks like a mismatch between their system and this model is a config, and saying so is far more useful than telling someone their working system is shaped wrong. What genuinely cannot be configured away is the short list the whole thing rests on — an append-only source layer, provenance, a review gate, a scannable index, and something that removes things.

## Step 5 — find what they have that the model lacks

The half that must not be skipped, and it needs real effort rather than a courtesy paragraph. Look specifically for:

- **Fields or sections** on their entries with no Corp-OS equivalent.
- **Conventions** for handling a recurring case — how they mark uncertainty, how they handle a source they cannot cite, how they deal with something half-known.
- **Rituals** — a weekly pass, a rule about what never gets captured, a threshold for when something graduates.
- **Structures for things the model does not represent at all** — time, sequence, geography, obligations, recurring cycles, relationships between entries.
- **Deliberate omissions.** Something the model insists on that they consciously chose not to do, and it worked out. This is the most valuable and least obvious category, because it identifies where the model is over-built.

For each: what it is, why it emerged, how often it is used, and whether it generalizes beyond their role. Then say which ones you would adopt.

## Step 6 — propose what to build next

Part of why someone commissions an audit is to find out what to *build*, and none of this shows up as a dimension score. Look for it specifically:

- **A step done by hand every run.** Anything repeated manually across more than a few sessions is a skill waiting to be written.
- **A question asked repeatedly the system cannot answer from its structure.** A missing view or a missing field.
- **A recurring moment with no support** — a weekly review, pre-meeting prep, a handoff, a monthly report assembled from scratch each time.
- **A layer written to but never read.** It needs an output that surfaces it, or it should not exist.
- **Debt tracked by a trigger rather than a date.** "Next time this file is touched" never fires.

Write each as a concrete proposal — what it does, what triggers it, what it saves — not as an observation that something is absent. Two or three real ones beat a list of ten.

## Step 7 — write the packet

Anything generalizable goes into an improvement packet per the reference format, written to the session output folder — not into their system.

Anonymize by construction: structure, counts, and shape only. Never copy their entry content, names, companies, or citations into a packet. If a structure cannot be described without their content, describe it abstractly.

Confirm with the person before producing a packet from their system at all. It is their work, and the packet exists to travel.

## Step 8 — report

Four sections, in this order:

1. **What they built that works**, and specifically what the Corp-OS model should take from it. Leading here is not politeness — it is accurate, and it establishes that the audit was a comparison rather than an examination.
2. **Anything you got wrong**, with the counts. If a recommendation did not survive contact with their corpus, that belongs high in the report, not buried.
3. **The dimension scores, and the three smallest changes worth making**, in order.
4. **What to build next** — the skills and workflow changes from Step 6.

Then one action, offered. Usually the smallest fix from section 3.

## What this never does

- Never converts, reorganizes, or writes into their system unasked.
- Never scores from claimed process rather than file evidence.
- Never produces a gaps-only report.
- Never scores outcome-orientation from the absence of a jobs layer without running the clustering test.
- Never recommends decay without first checking whether their entries can actually be re-verified.
- Never recommends a rebuild.
- Never puts their content into a packet.
