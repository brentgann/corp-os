---
name: corp-os-recall
description: Answers questions from a Corp-OS knowledge base with citations, and enriches whatever the person is currently working on with the relevant claims, glossary terms, people history, and company context the OS already holds. Use when someone asks "what do we know about X", "what did they say about Y", "brief me before this meeting", "pull my context on this", "add what we know to this doc", or is drafting something and wants their own knowledge folded in. Not for capturing new material (use corp-os-intake or corp-os-pull) and not for the systematic staleness sweep (use corp-os-reality-check).
---

# Corp-OS recall

> **Mixed pass** — scanning the index and pulling matches is bookkeeping; deciding what the matches mean and what is not known is not. Worth the better model, and worth keeping the mechanical half in scripts so the model is paying for the judgment rather than the typing.

The skill the OS exists for. Everything else is upkeep; this is the payoff — and it is the skill that determines whether the person keeps using the system, so the quality bar is answering honestly rather than answering impressively.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — scan, in order, and stop early

0. `config.json` — which layers exist here, what they are called, what is excluded from the scan path
1. `INDEX.md`
2. `jobs/INDEX.md`
3. `claims/INDEX.md`
4. only then the specific claim, person, topic, company, or glossary files the question actually needs

Never load `raw/`. Open a raw file only to check a specific citation the person is questioning.

`sensitive.md` holds only `incidental` sensitive material and is outside the scan path — do not open it to answer a general question. Open it when the task specifically calls for it, and when an answer would be materially incomplete without it, say that sensitive context exists rather than either surfacing it unasked or silently omitting it.

**Sensitive entries marked `load_bearing` are in the scan path and belong in the answer.** This is one person's own knowledge base; withholding a fact from its owner does not protect anyone, and an answer computed around it is not cautious, it is wrong — and wrong in the worst way, because nothing in it signals that something was left out. Use them, and mark each one inline so the person knows what they are holding: `(CL-0061, sensitive — strip before this goes anywhere)`. That marking is what makes the export boundary visible at the moment they are most likely to paste the answer into a document.

Most questions resolve from the indexes alone. If they routinely do not, the indexes have drifted — note that as friction in the usage log, because it is a structural problem `corp-os-improve` should see.

**When step 4 would mean opening a whole file to find part of it, narrow first.**

```bash
python3 scripts/find.py --topic <term> --digest     # one line per match
python3 scripts/find.py --job job-004               # the matches, in full
python3 scripts/find.py --id CL-0042 --id CL-0044
```

A topic file holding forty entries costs all forty to answer a question about one, and the index grows with the corpus while the answer does not. `find.py` returns the matches instead of the files containing them, and `--digest` gives one line each — enough to decide which of them you actually need in full. It reads both entry encodings, refuses an unscoped search, and never returns from `proposals/`, so nothing unreviewed arrives wearing the same shape as something confirmed.

Selecting by id, job, topic, confidence or decay state is bookkeeping. What the matches mean is not, and that stays here.

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
- **Sensitive claims used, and marked inline every time.** Two halves, and both get dropped.

*Used*: a `load_bearing` sensitive claim is in the scan path deliberately, and leaving it out of the answer is the failure the two-axis model exists to prevent — the person gets a conclusion computed without the fact that changes it, with nothing signalling the omission. Measured, this gets skipped about a third of the time, usually out of a reflex that sensitive means withhold. It does not. There is one person in this OS and it is theirs.

*Marked*: `(CL-0061, sensitive — strip before this leaves)`, on the sentence carrying the fact. Not a footnote, not a closing caveat — the person is often mid-draft and will copy the paragraph, not the caveat. A claim is load-bearing precisely because it changes conclusions, which is the same reason someone outside would find it interesting.

*And not further*: this licenses using what is **in the scan path**, nothing more. `sensitive.md` holds `incidental` material and stays closed unless the task specifically calls for it. Reaching into it because sensitivity came up is the opposite error and just as wrong — measured, sharpening the first half of this rule pushed one run in three into exactly that over-correction. Two different rules: use what is in front of you; do not go looking behind the quarantine.
- **Unresolved identities named as unresolved.** If three people in the corpus share a first name and the question touches one of them, say so instead of picking the most likely. Confidently attributing something to the wrong person is worse than the ambiguity.

## Step 3 — say what is not known

The part that separates this from a search box, and the part most likely to get dropped under pressure to look useful.

- Name the gaps: what the question touches that the OS has nothing on.
- Name the **blind spots**: check `connectors.md` and say when the absence is structural. "Nothing from Alex's calls — meeting notes only cover calls you joined" is far more useful than silence, because it tells the person whether to go looking or to stop.
- Distinguish "we have nothing" from "we have nothing recent."

Never fill a gap with a plausible inference presented as knowledge. If an inference is worth making, mark it as yours: "nothing on this directly; based on CL-0031 and CL-0044 I'd guess X, but that's inference."

## Step 4 — enrich, when that is the actual ask

When the person is drafting, prepping, or building something rather than asking a question, the deliverable is their work with the OS folded in — not a report about the OS.

- **Meeting prep** — who they are meeting, what was last said and when, open asks in both directions, which job this advances, what to find out. Pull from `company/`, claims, and — where the OS declares a person layer — its records. Where it does not, the claims themselves carry the history; say what is known about the person from claims rather than reporting that a folder is missing.
- **A document or deck** — the relevant claims with citations, correct vocabulary from `glossary.md`, the numbers with their real definitions, and an explicit note on which supporting claims are past decay so nothing stale gets published under their name. If any of it is `sensitive`, say so at the top of what you hand back and offer `corp-os-redact` — this is the moment the export boundary is actually crossed, and a note buried at the bottom is a note that gets pasted over.
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

## When an answer is worth keeping

Sometimes the answer you just assembled is not a lookup — it is a **conclusion built across several entries**, with something to do about it and a moment after which doing it stops helping. No shipped layer holds that: an entry is one fact with one citation, a topic file asserts nothing on its own, and a decision is a fork with an owner and a date.

If this OS declares an arguments layer, offer to keep it, per `${CLAUDE_PLUGIN_ROOT}/reference/records.md`: the conclusion, the so-what, the timing, and `Rests on` naming the entries it depends on. **Inherit the weakest confidence** of what it rests on — an argument built on eleven `needs_review` entries is `needs_review` however convincing it reads.

Offer it rarely. In the OS this came from, 23 across six months and 220 sources — and 13 of those 23 were later marked `spent`, which is the reason the layer is worth having at all. A layer that accumulates and never retires is a layer nobody trusts.

If the OS has no arguments layer, do not create one here. That is `corp-os-configure`'s interrogation, and a layer improvised to hold one good answer is a layer declared without the checks that catch shape mistakes.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-recall --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

A `usage/log.md` row, with honest friction. The friction field here is the richest signal in the OS: "answered but 3 of 5 claims past decay," "had to open four detail files because the index one-liners were too thin," "no job matched the question." Those rows are what let `corp-os-improve` fix the structure rather than guess at it.
