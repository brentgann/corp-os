---
name: corp-os-recall
description: Answers questions from a Corp-OS knowledge base with citations, and enriches whatever the person is currently working on with the relevant claims, glossary terms, people history, and company context the OS already holds. Use when someone asks "what do we know about X", "what did they say about Y", "brief me before this meeting", "pull my context on this", "add what we know to this doc", or is drafting something and wants their own knowledge folded in. Not for capturing new material (use corp-os-intake or corp-os-pull) and not for the systematic staleness sweep (use corp-os-reality-check).
---

# Corp-OS recall

The skill the OS exists for. Everything else is upkeep; this is the payoff — and it is the skill that determines whether the person keeps using the system, so the quality bar is answering honestly rather than answering impressively.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

## Step 0 — scan, in order, and stop early

0. `config.json` — which layers exist here, what they are called, what is excluded from the scan path
1. `INDEX.md`
2. `jobs/INDEX.md`
3. `claims/INDEX.md`
4. only then the specific claim, person, topic, company, or glossary files the question actually needs

Never load `raw/`. Open a raw file only to check a specific citation the person is questioning.

`sensitive.md` is outside the scan path — do not open it to answer a general question. Open it only when the task specifically calls for it, and when an answer would be materially incomplete without it, say that sensitive context exists rather than either surfacing it unasked or silently omitting it.

Most questions resolve from the indexes alone. If they routinely do not, the indexes have drifted — note that as friction in the usage log, because it is a structural problem `improve-corp-os` should see.

## Step 1 — read the question for its job

Ask which job this serves, or infer it. This is the relevance filter that makes recall better than search: "what do we know about pricing" is unanswerable in the abstract, but "what do we know about pricing that bears on the Acme renewal" has a real answer.

When the question maps to no job, answer it anyway — but note it, because a recurring off-job question is usually an unnamed job, and that is worth surfacing at the end.

## Step 2 — answer, with the provenance visible

Structure:

- **The answer first.** Not a preamble about what was searched.
- **Each substantive point carries its claim ID, source, and date.** Inline, compactly: `(CL-0042, Dana Chen, 2026-09-02)`.
- **Confidence shown where it is not `confirmed`.** Say "one unconfirmed mention" or "this is an assumption, not something anyone told us." Do not launder a `needs_review` claim into a confident sentence — that is the single most damaging thing this skill can do, because it makes the OS worse than having no OS.
- **Past-decay claims marked inline.** "Their pricing was per-seat as of June — that's past its re-check window." A stale claim delivered without its age is a lie of omission.
- **`disputed` claims presented as disputed,** both sides plus the recorded diagnosis of why they might conflict — not resolved for tidiness.
- **Unresolved identities named as unresolved.** If three people in the corpus share a first name and the question touches one of them, say so instead of picking the most likely. Confidently attributing something to the wrong person is worse than the ambiguity.

## Step 3 — say what is not known

The part that separates this from a search box, and the part most likely to get dropped under pressure to look useful.

- Name the gaps: what the question touches that the OS has nothing on.
- Name the **blind spots**: check `connectors.md` and say when the absence is structural. "Nothing from Alex's calls — meeting notes only cover calls you joined" is far more useful than silence, because it tells the person whether to go looking or to stop.
- Distinguish "we have nothing" from "we have nothing recent."

Never fill a gap with a plausible inference presented as knowledge. If an inference is worth making, mark it as yours: "nothing on this directly; based on CL-0031 and CL-0044 I'd guess X, but that's inference."

## Step 4 — enrich, when that is the actual ask

When the person is drafting, prepping, or building something rather than asking a question, the deliverable is their work with the OS folded in — not a report about the OS.

- **Meeting prep** — who they are meeting, what was last said and when, open asks in both directions, which job this advances, what to find out. Pull from `people/`, `company/`, and claims.
- **A document or deck** — the relevant claims with citations, correct vocabulary from `glossary.md`, the numbers with their real definitions, and an explicit note on which supporting claims are past decay so nothing stale gets published under their name.
- **A decision** — the `decision` and `constraint` claims that bear on it, prior decisions this would supersede, and the assumptions it rests on. Surfacing the untested assumption is usually the highest-value move here.

Match the person's format and voice. If `design.md` binds a design system and the output is visual, follow it.

## Step 5 — capture what the answer surfaced

Recall reveals gaps, and gaps are intake priority. When an answer turns up something the OS should have known:

- Propose adding it to the relevant job's evidence list.
- If the person answers their own question from memory during the exchange, propose capturing it as a claim with them as the source — this is one of the highest-yield intake paths in the whole system and it is invisible unless recall watches for it.
- If a claim turned out to be wrong or stale, hand off to `corp-os-reality-check` rather than editing it here.

All proposals, not writes.

## Step 6 — offer the next thing, briefly

One line. The most useful next action given what the answer exposed — a specific source to pull, a person to ask, a claim to verify. Not a menu.

## Every run ends with

A `usage/log.md` row, with honest friction. The friction field here is the richest signal in the OS: "answered but 3 of 5 claims past decay," "had to open four detail files because the index one-liners were too thin," "no job matched the question." Those rows are what let `improve-corp-os` fix the structure rather than guess at it.
