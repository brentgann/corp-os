---
name: doc-initiative-evidence
kind: doc
pack: corp-os-shipped@0.15.0
requires:
  - role: derived
    fields: [citation, confidence]
  - role: derived
    label: decisions
    fields: [owner, decide_by]
    optional: true
produces: one markdown brief, scoped to a job or an initiative
target: local
shield: n/a
generator: scripts/build_initiative_evidence.py
---

## What it answers

Before anyone writes a spec, a memo, or a proposal: **what do we already know
about this, how good is it, and what is still open.**

The failure it prevents is a document that re-derives what was settled months
ago, or worse, asserts something the corpus already contradicts. Re-deriving is
what wastes the session; contradicting is what makes the document wrong in a way
that reads perfectly coherent.

## Composition

- **What is known.** Every entry on the topic, with its confidence and its
  citation. Grouped by confidence so the weight is visible without reading.
- **What is contested.** Entries whose confidence is `disputed`, or pairs that
  disagree, with both sides quoted. Never resolved here — a brief that quietly
  picks a winner has destroyed the disagreement it was built to surface.
- **What is still open.** Open decisions touching this topic, worst date first,
  and the job's unanswered evidence items. Cited from the root index, which
  already computes both. Do not recompute.
- **What is cheap to strengthen.** Entries at a confidence ceiling whose source
  still exposes a verbatim fetch. One call each, and a document that cites the
  summary when the transcript was available is weaker for no reason.
- **What it rests on.** The entry ids, emitted as a `Rests on` line the author
  pastes into whatever they write, so the resulting document joins the
  stale-grounding view instead of standing outside it.

## Refuses

- Rendering an entry from `proposals/` as though it were confirmed. Unreviewed
  material may be named, labelled, and never counted in a confidence total.
- Emitting a confidence figure without the citation behind it.
- Collapsing a contradiction to one side.
- Filling a gap with anything not on disk. A short brief plus an honest gap is
  worth more than a complete-looking one, because the reader cannot tell which
  half to trust otherwise.
- Rendering an empty section where a layer did not bind. Say it was dropped.

## Verification

The five checks in `reference/patterns.md`. No shield checks: this pattern
declares `shield: n/a` because its output is markdown a person pastes into a
document, and a shield protects a screen. Anything leaving the OS goes through
`corp-os-redact`, which is the boundary — and a brief that quotes claim
citations verbatim is exactly the case `check_citations.py` exists for.
