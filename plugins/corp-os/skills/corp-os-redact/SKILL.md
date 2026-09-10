---
name: corp-os-redact
description: Produces a shareable version of anything leaving a Corp-OS knowledge base — a brief, a claim set, a dashboard, a company record, a raw transcript — with personal, personnel, compensation, credential, and confidential material removed, plus a private local log of exactly what was pulled and why. Use when someone says "clean this up before I share it", "scrub this", "make this safe to send", "redact this transcript", "can I share this with my team", or is about to publish or forward OS content. Nothing is silently deleted. Not for deciding what is worth sharing on relevance grounds — that judgment stays with the person.
---

# Corp-OS redact

> **Judgment pass** — the reasoning is the product here. Run it on your best model, and do not economise by skipping the questions it asks.

Produces two outputs, always: a cleaned copy safe to share, and a private log of every removal with its reason. The log is what makes this reviewable rather than a black box, and it is the difference between redaction and quiet deletion.

Never modify the original in place. `raw/` in particular is append-only and must survive this untouched.

## Pre-flight

Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 0 — establish what is leaving, and to whom

The audience determines the threshold. Ask if it is not stated:

- **The person's own team** — personnel and comp still go; product and process detail generally stays.
- **Elsewhere in the company** — add: individual performance detail, internal conflict, unannounced plans.
- **Outside the company** — add: anything under NDA, customer-identifying detail, internal metrics, roadmap, pricing not already public.
- **Published to a URL** — treat as fully external regardless of intent, because a link travels.

If the person will not say the audience, use the external threshold and say that is what you did.

## Step 1 — keep the removal list as you go

Keep a running list of removals as you sweep — category, location, action, original, replacement, reason — one entry per decision, written down while you are already thinking about it.

You will not hand-write either output file. `scripts/write_export.py` in the OS writes both, and **it refuses to write the cleaned copy without the log.** That refusal is the point. Measured across five runs, the log was the thing that went missing or came out under four different names, while the instruction to write it was present, concrete, and explained the whole time. Past a certain point more instruction stops buying reliability, and the answer is to take the step out of the model's hands — the same move `build_index.py` makes for the index.

`usage/` is outside the scan path, so neither file loads on every scan or needs declaring as a layer.

This ordering is the whole point. Written up at the end, the log is the thing that gets dropped — measured against a fixture it went missing in every run, because by then the judgment is done and it feels like paperwork. Written as you go, there is nothing left to remember: the log accumulates while you are already thinking about each decision, which is also when the reasoning is sharpest and cheapest to record.

The log holds the sensitive material by design. It stays local, never travels with the cleaned copy, and never gets published.

## Step 2 — sweep for the categories

Work all of these, not just the obvious ones:

- **Credentials** — tokens, keys, passwords, connection strings, internal URLs with embedded auth. Always removed regardless of audience, and worth flagging as something to rotate if it appears in a captured transcript at all.
- **Compensation** — salary, equity, bonus, band, offer detail, anything comp-adjacent.
- **Personnel** — performance assessments, promotion and termination discussion, hiring deliberations about named people, health, family, personal circumstances.
- **Interpersonal** — conflict between named people, candid assessments of individuals, "between us" asides. The category most often missed, because it rarely uses obvious keywords.
- **Third-party confidential** — customer names where the relationship is not public, anything under NDA, another company's internals shared in confidence.
- **Regulated personal data** — contact details, identifiers, addresses, anything a data-protection regime would recognize.
- **Internal-only business detail** — unannounced pricing, roadmap, financials, legal exposure, security findings.

Then check the OS's own `sensitivity` flags and `sensitive.md`. Anything marked `sensitive` gets pulled by default, but do not rely on the flags alone — the sweep must run on content, because flags are applied by fallible judgment at capture time.

**`bearing` changes nothing here.** A `load_bearing` entry sits in the scan path precisely so the person can reason with it; that is an argument about their own OS and none at all about what may leave it. If anything, load-bearing sensitive material is the most dangerous kind at an export boundary — it is load-bearing because it changes conclusions, which is exactly why someone outside would find it interesting. Redaction is the only place confidentiality is enforced, so a sensitive entry that reached the scan path legitimately must still be generalized or removed on the way out.

## Step 3 — prefer generalizing to deleting

A hole in a document destroys its usefulness; a generalization usually preserves the point.

- "Priya said Marcus isn't ready for the promotion" → "there was a discussion about readiness for an internal promotion"
- "Acme's CFO said the seat math kills it above $180k" → "the customer's finance leader flagged per-seat cost as the renewal obstacle"
- "the token is sk-abc123" → `[credential removed]`

Credentials are the exception: remove, never generalize.

When generalizing would make a claim meaningless, remove it and say in the log that removal was necessary rather than pretending the cleaned version is complete.

## Step 4 — quarantine at the source, not just at the exit

Redacting on the way out is necessary and not sufficient. A `sensitive` entry sitting inline in a topic file still loads on every scan, still gets read over a shoulder, and still travels the next time that file is shared by someone who did not run this skill.

When the sweep finds sensitive content living inline in the derived layer, ask first whether it is `incidental` or `load_bearing` — see the two-axis model in `${CLAUDE_PLUGIN_ROOT}/reference/claim-record.md`. Only `incidental` material gets quarantined. Moving a `load_bearing` entry out of the scan path does not protect anything (redaction already does that) and it makes every later answer wrong in a way nobody can see, which is the failure this model exists to prevent.

For `incidental` material, propose moving it to `sensitive.md` — the quarantine file deliberately outside the scan path — leaving a one-line pointer behind so continuity is not lost:

> Personnel context on this exists — see `sensitive.md`.

Captured, never suppressed. The aim is that content nobody needs for the daily job stops sitting in the daily path.

Quarantine migrations are derived-layer writes: propose, confirm, then move. And treat a deferred migration as debt with a date, not a standing note — "migrate the next time this file is touched" is a TODO with no forcing function, and it will still be pending three months later.

## Step 5 — log reclassifications as decisions, not edits

Sensitivity judgments get revised, in both directions. An over-cautious `sensitive` flag turns out to be ordinary business signal; something filed as `internal` turns out to touch a person.

Record the change and its reasoning as an entry, never as a silent edit. The next reader — including a future rebuild — needs to see that a flag was *reviewed and downgraded against the schema's actual definition*, not that it was never applied. This is provenance for the classification, distinct from provenance for the content, and systems that skip it develop a slow invisible drift in what their own labels mean.

## Step 6 — check what remains for re-identification

The step that is almost always skipped. Individually clean details can identify someone in combination: a role plus a team plus a date plus a decision often names exactly one person. Read the cleaned copy as an outsider with organizational context would, and generalize further where the combination gives it away.

## Step 7 — write both outputs

Call the script with a spec — `slug`, `audience`, `cleaned`, and `removals`:

```bash
python3 scripts/write_export.py spec.json --os-root .
```

It writes `usage/exports/<date>--<slug>--<audience>.md` with a header saying it is redacted and where the log lives, and `usage/exports/<date>--<slug>--redaction-log.md` beside it. Pass `removals: []` when the sweep genuinely found nothing — an empty log and an absent log mean different things, and the script will not accept the field missing. Copy the cleaned file wherever the person is sending it from; the OS keeps its own record either way.

**The cleaned copy**

**The log** — written by the same call, never separately. Its shape, for reference when reading one back:

```markdown
## Removal 3
- **Category**: personnel
- **Location**: "What moved" section, second bullet
- **Action**: generalized
- **Original**: <the actual text>
- **Replacement**: "a discussion about internal promotion readiness"
- **Reason**: names an individual in a promotion context; audience is company-wide
```

The log contains the sensitive material by design. State plainly that it stays local.

## Step 8 — report and hand the decision back

Say what was removed by category and count, name anything that was a genuine judgment call, and state what could not be cleaned without losing the point.

Then stop. **Do not publish, send, or forward the cleaned copy.** This skill makes something shareable; the person decides whether to share it. That boundary is the point — a redaction skill that also distributes is a redaction skill that can distribute a mistake.

If asked to redact something so that a third party will take it as complete or authentic when it is not, decline.

## Before anything leaves — check the citation clusters

```bash
 python3 scripts/check_citations.py <the OS> --strict
```

Sensitivity is set per entry. The thing being protected is the **source text**. The model mints entries per topic, so one quote routinely yields several entries written by several passes, and nothing reconciles their classifications.

Measured: per-entry redaction was mechanically correct on all 836 entries of a real corpus and the boundary still leaked — the sensitive member was correctly withheld as a stub, and the byte-identical quote was emitted in full twice as the two members a different pass had classified as ordinary. Every per-entry check passes on that corpus, because every entry is individually right.

`--strict` exits non-zero on a split cluster. Resolve it to one class before continuing; do not redact around it. Withholding one copy of a quote that goes out in full elsewhere is not redaction, it is the appearance of it.

## Every run ends with

Close the run with `scripts/log_run.py` in the OS rather than editing the files by hand — it writes the `usage/log.md` row and the dated `meta.json` history entry in one call, and refuses a blank friction field:

```bash
python3 scripts/log_run.py --skill corp-os-redact --scope "<what this run covered>" \
    --friction "<where it hurt, or 'none'>" \
    --event "<what changed>" \
    --gate-note "redaction pass — removing material, not proposing it"
```

These are the two writes measurement says get dropped, because they sit after the interesting work is done. A step that has to happen every time and that nothing else will catch belongs in code, not in a reminder.

It also refuses to close a run that put something in a derived layer with no proposal file behind it, and names the files and the `propose.py` call that repairs the record. The gate is checked here because this is the step that never gets skipped — three attempts at stating it nearer the write got it to one run in three.

- **Both files on disk**, as the script reports them. If it errored, nothing was written — fix the spec and call it again rather than writing either file by hand.
- A `usage/log.md` row noting a redaction ran and for what audience — never the removed content itself.
