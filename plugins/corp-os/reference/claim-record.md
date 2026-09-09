# The claim record

The unit of knowledge in a Corp-OS. Read this when you are minting, editing, sweeping or exporting claims; the layer rules and the scan contract are in `reference/data-model.md`, and the other record shapes are in `reference/records.md`.

## Claim record

Claims live grouped by topic in `claims/<topic-slug>.md`, one block each:

```markdown
### CL-0042 — Acme flagged pricing as their top renewal concern
- **Statement**: Acme's economic buyer named per-seat pricing as the primary obstacle to renewing at current volume.
- **Kind**: fact          # fact | decision | theme | assumption | constraint | metric | preference
- **Jobs**: job-004
- **Confidence**: confirmed   # confirmed | needs_review | reconstructed | disputed | retired
- **Source fidelity**: verbatim   # verbatim | summary | reconstructed | absent
- **Sensitivity**: internal   # public | internal | sensitive
- **Source**: raw/2026-09-02--granola--acme-qbr.md — Dana Chen (Acme), 2026-09-02
- **Citation**: "Honestly the seat math is the only thing my CFO is going to push back on."
- **Verified**: 2026-09-02 — heard first-hand on the call
- **Decay**: 90d              # re-verify after this long, or `none` for durable facts
- **Relations**: supersedes CL-0031
```

Field notes that matter:

- **Kind** separates what is observed from what is chosen from what is guessed. Conflating a `fact` with an `assumption` is the single most common way one of these systems starts lying to its owner.
- **Confidence** is about evidentiary standing, not importance. `confirmed` means verbatim or corroborated. `needs_review` means inferred, single-mention, or ambiguous. `reconstructed` means backfilled from a summary rather than a real source. `disputed` means live evidence points both ways — keep both sides visible rather than picking a winner. `retired` means no longer true; kept, not deleted, so the record of having believed it survives.
- **Source fidelity** is a property of the claim's relationship to its source, and it is not confidence. One enum was carrying three independent questions: how faithful is the *medium* (was this a quote, a paraphrase, a reconstruction, or is the original gone), how many independent sources exist, and is the claim contested. Two of those are about evidence and one is about the recording, and collapsing them makes a specific thing invisible.

  Measured, in a real corpus: **599 of 836 claims** were single-source summaries parked one step below the top confidence value, and the config documented two routes upward — a second independent recording, or pulling the verbatim transcript through the same connector that produced the summary. The second is one API call. **Zero claims had taken it.** Meanwhile 60 claims sat lower still because their source genuinely no longer exists, and nothing in the record distinguished the two populations. A ceiling that is *elective* looked exactly like a ceiling that is *permanent*, so it got treated as permanent.

  Separating the medium out fixes that: `summary` plus a source whose connector exposes a verbatim fetch is a **visible, sortable backlog of claims one call from promotion**. `absent` is a claim nothing can ever re-confirm, which belongs in a one-time disposition pass rather than a decay window.

- **Retrievable** is derived, never written. A claim is retrievable when its source's record in `connectors.md` says that connector exposes a verbatim fetch. Deriving it means it cannot go stale the way a hand-set flag would, and it means disconnecting a source correctly changes the promotion backlog rather than leaving a field lying.

- **Confidence reason** and **Sensitivity reason** are optional free-text siblings, never suffixes on the value. `needs_review` covers three situations — the source is thin, two readings genuinely compete, and a paraphrase cannot satisfy a verbatim requirement — and a sweep cannot triage them apart. Writing the reason *inside* the value (`needs_review — explicitly an open unknown`) was proposed and rejected: everything that reads confidence equality-tests that string, including `build_index.py`, the export emitter, every ceiling rule and every eval assertion. A sibling field carries the same information at no migration cost.

- **Decay** is what makes "refine data that has drifted from reality" mechanical instead of a vibe. A pricing claim rots in a quarter; a claim about a person's job title rots in a year; "our fiscal year starts in February" is `none`. `corp-os-reality-check` works this field.
- **Citation** is a verbatim excerpt, always. A paraphrase in the citation field defeats the purpose, because the next reader cannot tell how much of the claim is the source and how much is the summarizer.

Claim IDs are globally sequential (`CL-0001` up), never reused, tracked in `meta.json`. A rebuild never renumbers them — external references (dashboards, sent documents, prior briefs) depend on them holding still.

### When a citation does not exist

`no source` is a **sanctioned literal value** for the citation field. Use it when a claim traces to a summary, a migration, or someone's recollection with no retrievable original.

This exists because the alternative is worse in both directions: omitting the field makes an unsourced claim indistinguishable from a sourced one, and inventing a plausible-looking citation is the single most corrosive thing that can happen to a claims layer. A claim reading `Citation: no source` is honest and correctable. Nothing should ever be repaired by manufacturing a citation for it.

### Update blocks

A claim that develops does not always need to be superseded. When new evidence extends or qualifies a claim without contradicting it, append a dated update block inside the claim, carrying its own confidence and citation:

```markdown
- **Update (2026-08-25)**: the mitigation shipped and has early numbers —
  roughly two thirds of new arrivals now land in the cheaper tier. The
  underlying problem is not resolved; this is the response, not the fix.
  _(confirmed · raw/2026-08-25--monthly-review.md)_
```

Use an update block when the claim is still true and now known in more detail. Mint a new claim and retire the old one when the claim is no longer true. The distinction matters: a reader following a claim's update blocks can see how understanding developed, which a chain of superseded atomic claims makes almost unreadable.

### Conflicts get a diagnosis, not just a flag

Marking two claims `disputed` records that they disagree. It does not record *why*, and the why is usually what resolves it. Write the diagnosis into the conflict:

> Either two distinct initiatives share a name, or one source is stale. Not resolved here.

> Could be two different offers — a basic partnership versus a full connector-exchange tier — rather than a genuine contradiction. Needs a direct check rather than a guess.

A named hypothesis about the *shape* of a conflict is what lets someone resolve it in one question instead of re-deriving the confusion from scratch. A bare `disputed` pair gets skipped every time it is read.

### Identity claims

Any corpus with people in it accumulates identity ambiguity: two spellings of one name, one first name shared by four people, someone referred to by a role rather than a name, a person who "left" a project but not the company.

These get tracked as claims of kind `identity` and resolved deliberately, never merged on resemblance. Two rules:

- **Do not merge on similarity.** A fourth person appearing under a shared first name, now with a surname attached, is a new candidate — not confirmation that they are one of the three already on file. Record it as a candidate and say so. The pull toward tidying an ambiguity into a single entry is strong and almost always wrong.
- **When resolved, record the resolution and every place it propagated.** Not just "these two names are one person," but which files were corrected and whether the resolution changed anything else — an alias that turns out to describe someone leaving a *role* rather than the organization may also mean an entry was over-flagged as sensitive.

Where the OS declares a `people` layer, its records carry an `aliases` list for this. An unresolved identity question is a normal state and belongs on a job's evidence list.

### `Rests on` is not the arguments layer's field

It is introduced there because that is where it was first needed, but it belongs to any entry, in any layer, that is **built from a bounded set of other entries** — an argument, a registered dashboard, an authored spec or brief in a layer someone declared. The field is the same, the parser is the same, and the two views that read it (`N entries / M sources`, and the stale-grounding join below) apply wherever it appears.

```markdown
- **Rests on**: CL-0031, CL-0044, CL-0052
```

**Bounded is the word that matters.** An output built from a whole layer — a job board reading every job — has nothing to list and should not pretend otherwise; it records `Source files` and there is nothing to check. `Rests on` is for the case where a specific, nameable set of entries is what the thing stands on. Listing a folder there is worse than listing nothing, because it renders as breadth that was never measured.

**What it buys, and why it is worth the field.** Decay is carried by the entry and swept by `corp-os-reality-check`. It is not carried by the things built from entries, and nothing joined the two — so a dashboard registered in March off four claims, two of which went past their window in June, reads exactly like one refreshed yesterday. `build_index.py` performs that join and renders **Resting on evidence that has gone stale**, per entry, as *n of m past its window*. The ratio is the finding: one of one and two of nine are different objects.

An entry that declares no decay window is not the same as one whose window is `none`, and neither is reported as stale. A cited entry that was never verified at all is reported separately in the same line, because an output resting on something nobody ever confirmed is a different weakness from one resting on something that has aged.

### The source record, and what a connector can give back

`connectors.md` carries one block per registered source. Two fields on it decide what the claims drawn from that source can ever become:

```markdown
### Granola
- **Protocol**: MCP connector
- **Medium**: summary          # verbatim | summary | mixed
- **Verbatim fetch**: yes      # can the original text be pulled back on demand
- **Feeds**: raw/, meeting notes
- **Blind spots**: attachments are not indexed, so a decision living in a PDF is invisible
```

**Medium** is what the connector produces by default. **Verbatim fetch** is whether the original can be retrieved later. They are different questions and the second is the one that matters: a notetaker that writes summaries but keeps transcripts is a source whose claims are one call from promotion, and a notetaker that discards them is not. Without the distinction, both look identical in the record and neither gets acted on.

`corp-os-connect` asks both when a source is registered. `corp-os-claims` reads them to set `source_fidelity` without asking, because the answer is a property of the source rather than a judgment about the claim.

### Alias provenance

A person record's `aliases` decide whether two renderings are one entity, and that field is what deduplication reads. An **assumed** merge must not be able to look identical to a **confirmed** one.

```yaml
aliases:
  - alias: Rosh
    resolved_by: Dana Okafor
    resolved_on: 2026-08-14
  - alias: Arosh              # a bare string still parses: unresolved, and says so
```

Both shapes are read. A bare string is an alias nobody has confirmed, which is a legitimate state and should render as one — not silently as a confirmation. Requiring the object form would break every existing person record, and the point is to make the distinction visible rather than to force a migration.

The measured cost of not having this: in one corpus, three claims minted from a single quote reached three different conclusions about one name resolution — one asserting it settled, one stating it was never confirmed, one saying "likely" — none cross-referencing the others, while the person record carried **both renderings in `aliases`**. The unconfirmed resolution had been promoted into the exact field that decides whether two entities are one. That is how a corpus quietly merges two people or splits one.

### Corpus-level confidence ceilings

Per-claim confidence is not sufficient on its own. When a batch of material enters the OS from a source that is structurally weaker than verbatim — a migration from a previous system, a bulk import of AI-generated meeting summaries, a backfill from someone's memory — that whole cohort gets a **ceiling**, recorded once in `meta.json` and in the OS's README:

```json
"confidence_ceilings": [
  { "cohort": "2026-07-08 migration from prior system",
    "ceiling": "reconstructed",
    "raw_marker": "reconstructed: true in frontmatter",
    "count": 32,
    "note": "summaries, not verbatim source; cannot reach confirmed without new material" }
]
```

Without a ceiling, one careless pass promotes a whole cohort of summaries to `confirmed` and there is no way afterward to tell which claims were ever really sourced. Mark the cohort in the raw frontmatter too, so a rebuild rediscovers the ceiling rather than depending on the README being read.

### Sensitivity has two axes, and conflating them makes the OS wrong

A Corp-OS has one operator. Sensitivity exists so that material does not cross an **export boundary** into a multi-person system, not so that the person is kept from their own knowledge. Those are different jobs, and a single flag cannot do both — which is what an earlier version of this spec tried, and it failed in a way that is hard to see.

Every derived entry carries two independent fields:

**`sensitivity`** — the **export class**. What must not leave, and to whom. `internal` / `sensitive` / `restricted` by default, renameable like any vocabulary. This is `corp-os-redact`'s axis, and redaction is the only place it is enforced.

**`bearing`** — whether the OS can **reason correctly without it**. Two values:

- **`incidental`** — the content is sensitive and the analysis does not depend on it. Someone's compensation band, a personal circumstance mentioned in passing. Removing it makes an answer thinner, not wrong.
- **`load_bearing`** — the analysis is wrong without it. A departure that invalidates three plans. A constraint nobody outside the room knows about. A number that changes a conclusion.

#### `placement:` — an operator instruction that outranks the schema

Placement is normally decided by schema, and that is what makes regeneration safe. But an operator sometimes gives an instruction the schema disagrees with: *"this stays out of her person record"*, *"file it, leave no pointer."* Under a purely schema-driven model that instruction is unrepresentable, so it gets written into a derived file or into nothing, and a rebuild honours the schema and violates the instruction.

So it lives in the **raw** file's frontmatter, with the source it governs:

```yaml
placement: sensitive_only    # a declared layer name, or `none` to derive nothing
```

`corp-os-intake` writes it at the moment the instruction is given. `corp-os-rebuild` reads every one before deriving anything and refuses to guess when the named layer is not declared.

This is the only failure mode in the model that destroys a commitment rather than degrading an answer, and it surfaces the first time someone runs the operation this suite recommends when a derived layer tangles.

#### Where an entry lives follows from `bearing`, not from `sensitivity`

| `sensitivity` | `bearing` | Where it lives |
|---|---|---|
| not sensitive | — | its normal layer, in the scan path |
| sensitive | `incidental` | `sensitive.md`, outside the scan path, one-line pointer left behind |
| sensitive | `load_bearing` | **its normal layer, in the scan path**, marked |

**This is the correction, and it is worth being explicit about what was wrong.** Quarantining everything sensitive assumed that sensitive material is never needed for the daily job. When that assumption is false, the quarantine does not produce a gap — it produces a **confidently wrong answer**. The person does not hear "I don't know about that"; they hear a conclusion computed without the fact that would have changed it, with no signal that anything is missing. A gap someone can see is recoverable. An answer that is wrong for an invisible reason is not, and it is worse than never having captured the fact at all.

So load-bearing sensitive material stays where the scan can reach it. The confidentiality is enforced at the export boundary, by `corp-os-redact`, which is the only place it was ever really enforced anyway — a quarantine file protects nothing the moment someone shares the folder.

#### The test, and which way to fail

Ask: **would an answer computed without this be *wrong*, or just thinner?** If removing it changes a conclusion, a priority, a number, or who is responsible, it is `load_bearing`. If it only removes colour, it is `incidental`.

**Required on `sensitive` entries; optional everywhere else, defaulting to `load_bearing`.** The axis only has a behavioural consequence on sensitive entries and at the export boundary, and asking for it everywhere costs a judgment per entry that routes nothing. Measured in a real corpus: 727 of 836 entries carried `load_bearing` — 87%, including 100% of sensitive entries and 70–100% within every kind — and the field routed **zero** entries anywhere. An axis that is right to default is an axis that mostly reports its default, and collecting it 767 more times does not make it more informative.

**Default to `load_bearing` when it is genuinely unclear.** The two errors are not symmetric. Wrongly marking something `incidental` quarantines a fact the person needed and produces silent wrong answers. Wrongly marking something `load_bearing` means it sits in the scan path and `corp-os-redact` has one more thing to strip on the way out — visible, recoverable, and caught by a skill built for exactly that. Fail toward the recoverable direction, the same way a new layer defaults to `role: source`.

### Deletion leaves a tombstone

When raw material is destroyed under a retention obligation, write a tombstone in its place — same path, `.deleted.md` suffix — recording what was deleted, its original frontmatter, the date, the obligation, and how many derived entries were re-cited as a result.

**This came out of running the thing.** Asked to carry out a retention deletion against a fixture, a run invented the tombstone unprompted, and it is better than what the spec had. A deletion without one leaves a hole: a later rebuild reading `raw/` sees material that does not exist and cannot tell the difference between "never captured" and "destroyed under obligation" — and those call for completely different responses. The tombstone also means the `no source` entries left behind can be traced to a reason rather than looking like sloppiness.

The tombstone carries no content from the deleted file. That would defeat the obligation.

#### `sensitive.md`

Still the quarantine for `incidental` material, still outside the scan path, still with a one-line pointer left behind so continuity is not lost:

> Personnel context on this exists — see `sensitive.md`.

Captured, never suppressed. What changed is that it is no longer where *all* sensitive material goes — only the part whose absence costs nothing but detail.

### Reclassification is logged, never silent

When something's confidence, sensitivity, **bearing**, or kind is changed on review, record the change and its reasoning as an entry — not as an edit.

A `bearing` change is the one most worth logging, because it moves the entry: promoting `incidental` to `load_bearing` pulls it back into the scan path, and demoting does the reverse. Someone reading later needs to know that the placement was decided rather than defaulted.

An over-cautious `sensitive` flag downgraded to `internal` because the content turned out to be business signal rather than personnel signal is a **decision about the schema's application**, and the next person to look (including a future rebuild) needs to see that it was reviewed rather than assume it was never flagged. The same applies in reverse.

This is provenance for the classification, distinct from provenance for the content. Systems that skip it develop a slow, invisible drift in what their own labels mean.
