---
name: corp-os-redact
description: Produces a shareable version of anything leaving a Corp-OS knowledge base — a brief, a claim set, a dashboard, a company record, a raw transcript — with personal, personnel, compensation, credential, and confidential material removed, plus a private local log of exactly what was pulled and why. Use when someone says "clean this up before I share it", "scrub this", "make this safe to send", "redact this transcript", "can I share this with my team", or is about to publish or forward OS content. Nothing is silently deleted. Not for deciding what is worth sharing on relevance grounds — that judgment stays with the person.
---

# Corp-OS redact

Produces two outputs, always: a cleaned copy safe to share, and a private log of every removal with its reason. The log is what makes this reviewable rather than a black box, and it is the difference between redaction and quiet deletion.

Never modify the original in place. `raw/` in particular is append-only and must survive this untouched.

## Step 0 — establish what is leaving, and to whom

The audience determines the threshold. Ask if it is not stated:

- **The person's own team** — personnel and comp still go; product and process detail generally stays.
- **Elsewhere in the company** — add: individual performance detail, internal conflict, unannounced plans.
- **Outside the company** — add: anything under NDA, customer-identifying detail, internal metrics, roadmap, pricing not already public.
- **Published to a URL** — treat as fully external regardless of intent, because a link travels.

If the person will not say the audience, use the external threshold and say that is what you did.

## Step 1 — sweep for the categories

Work all of these, not just the obvious ones:

- **Credentials** — tokens, keys, passwords, connection strings, internal URLs with embedded auth. Always removed regardless of audience, and worth flagging as something to rotate if it appears in a captured transcript at all.
- **Compensation** — salary, equity, bonus, band, offer detail, anything comp-adjacent.
- **Personnel** — performance assessments, promotion and termination discussion, hiring deliberations about named people, health, family, personal circumstances.
- **Interpersonal** — conflict between named people, candid assessments of individuals, "between us" asides. The category most often missed, because it rarely uses obvious keywords.
- **Third-party confidential** — customer names where the relationship is not public, anything under NDA, another company's internals shared in confidence.
- **Regulated personal data** — contact details, identifiers, addresses, anything a data-protection regime would recognize.
- **Internal-only business detail** — unannounced pricing, roadmap, financials, legal exposure, security findings.

Then check the OS's own `sensitivity` flags and `sensitive.md`. Anything marked `sensitive` gets pulled by default, but do not rely on the flags alone — the sweep must run on content, because flags are applied by fallible judgment at capture time.

## Step 2 — prefer generalizing to deleting

A hole in a document destroys its usefulness; a generalization usually preserves the point.

- "Priya said Marcus isn't ready for the promotion" → "there was a discussion about readiness for an internal promotion"
- "Acme's CFO said the seat math kills it above $180k" → "the customer's finance leader flagged per-seat cost as the renewal obstacle"
- "the token is sk-abc123" → `[credential removed]`

Credentials are the exception: remove, never generalize.

When generalizing would make a claim meaningless, remove it and say in the log that removal was necessary rather than pretending the cleaned version is complete.

## Step 3 — quarantine at the source, not just at the exit

Redacting on the way out is necessary and not sufficient. A `sensitive` entry sitting inline in a topic file still loads on every scan, still gets read over a shoulder, and still travels the next time that file is shared by someone who did not run this skill.

When the sweep finds sensitive content living inline in the derived layer, propose moving it to `sensitive.md` — the quarantine file deliberately outside the scan path — leaving a one-line pointer behind so continuity is not lost:

> Personnel context on this exists — see `sensitive.md`.

Captured, never suppressed. The aim is that content nobody needs for the daily job stops sitting in the daily path.

Quarantine migrations are derived-layer writes: propose, confirm, then move. And treat a deferred migration as debt with a date, not a standing note — "migrate the next time this file is touched" is a TODO with no forcing function, and it will still be pending three months later.

## Step 4 — log reclassifications as decisions, not edits

Sensitivity judgments get revised, in both directions. An over-cautious `sensitive` flag turns out to be ordinary business signal; something filed as `internal` turns out to touch a person.

Record the change and its reasoning as an entry, never as a silent edit. The next reader — including a future rebuild — needs to see that a flag was *reviewed and downgraded against the schema's actual definition*, not that it was never applied. This is provenance for the classification, distinct from provenance for the content, and systems that skip it develop a slow invisible drift in what their own labels mean.

## Step 5 — check what remains for re-identification

The step that is almost always skipped. Individually clean details can identify someone in combination: a role plus a team plus a date plus a decision often names exactly one person. Read the cleaned copy as an outsider with organizational context would, and generalize further where the combination gives it away.

## Step 6 — write both outputs

**The cleaned copy** — to the session output folder or wherever the person is sending it from, clearly named as the cleaned version. Add a one-line header noting it has been redacted and pointing at the log, so nobody downstream mistakes it for complete.

**The log** — private and local, in the OS folder (`usage/redaction-log-<date>.md`), never published, never shared alongside the cleaned copy:

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

## Step 7 — report and hand the decision back

Say what was removed by category and count, name anything that was a genuine judgment call, and state what could not be cleaned without losing the point.

Then stop. **Do not publish, send, or forward the cleaned copy.** This skill makes something shareable; the person decides whether to share it. That boundary is the point — a redaction skill that also distributes is a redaction skill that can distribute a mistake.

If asked to redact something so that a third party will take it as complete or authentic when it is not, decline.

## Every run ends with

A `usage/log.md` row noting a redaction ran and for what audience — never the removed content itself.
