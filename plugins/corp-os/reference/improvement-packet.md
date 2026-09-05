# Improvement packet

The interchange format for improving the Corp-OS model itself. Produced by `improve-corp-os` (from one person's own usage) and by `corp-os-audit` (from studying someone else's system). Consumed by whoever maintains this plugin.

The point of a shared format is that improvements can travel without the OS contents traveling with them. A packet describes *structure and friction*, never the person's actual claims, people, or company data.

## File

Write to `usage/improvement-packet-<YYYY-MM-DD>.md` in the OS folder, or to the session's output folder when auditing a system that is not the operator's own.

```markdown
# corp-os improvement packet — <YYYY-MM-DD>

## Origin
- **Produced by**: improve-corp-os | corp-os-audit
- **Operator role shape**: decision-heavy | relationship-heavy | build-heavy | operate-heavy | orientation
  (role *shape*, not job title — this is what makes the packet generalizable)
- **OS age**: 4 months
- **Scale**: 212 raw files, 38 jobs (6 active), 407 claims, 9 connectors
- **Anonymized**: yes — no claim bodies, person names, company names, or citations included

## Friction observed
One entry per recurring friction. Evidence is a count and a quoted usage-log
friction field, never a claim body.

### F1 — Evidence lists go stale silently
- **Frequency**: 14 of 61 recall runs
- **Evidence**: "answered but 2 of 3 claims past decay" appears in usage log 14 times
- **Diagnosis**: decay is enforced at reality-check time but never surfaced at recall time
- **Proposed change**: recall should mark past-decay claims inline in its answer
- **Affects skill**: corp-os-recall
- **Confidence this generalizes**: high — nothing about it is role-specific

## Structures this operator invented
The most valuable section. Things the person built that the shipped model does
not have, described as shape only.

### S1 — Per-job "who to ask" field
- **What it is**: each job record grew a list of people who reliably know the answer, distinct from stakeholders
- **Why it emerged**: stakeholders are who cares; this is who knows — the operator kept conflating them
- **How often used**: referenced in roughly a third of recall runs
- **Generalizes to**: any relationship-heavy or orientation role
- **Recommendation**: add as an optional job field, not mandatory

## Structures shipped but unused
Equally valuable, and the section people skip. Unused structure is a cost, not
a neutral.

### U1 — topics/
- **Created**: at setup
- **Times written to since**: 2
- **Why unused**: claims are grouped by topic already; topics/ duplicated it
- **Recommendation**: stop scaffolding by default; offer only when claims exceed ~200

## Model deltas
Concrete proposed edits to reference/data-model.md, one per line, each traceable
to an F, S, or U entry above.

- Add optional `who_to_ask` to the job record. (S1)
- Surface decay state in recall output. (F1)
- Remove topics/ from default scaffold. (U1)

## Not recommended
Things considered and rejected, with the reason. This section stops the same
idea being re-proposed by the next packet.

- Auto-promoting claims past a corroboration threshold — removes the review gate,
  which is the load-bearing part of the two-layer split.
```

## The config test — apply it before writing anything

**If a finding could be a `config.json` setting, it is not a model change and does not belong in a packet.** The model is a default profile: layer names, vocabulary, decay windows, retention policy, gate strictness, and entirely new layers with their own schemas are all configurable.

So a person who wanted a field the model lacks produced a *config* finding — hand it to `corp-os-configure`. A person who needed a **concept** the model lacks, something no field, layer, or vocabulary could express, produced a model finding. Only the second kind travels.

This test is what keeps packets small and worth reading. Without it, every packet is mostly a list of preferences that the receiving maintainer can do nothing useful with, and the genuine findings get buried.

## Rules

- **Anonymize by construction, not by review.** Build the packet from counts, structure, and usage-log friction fields. Never open a claim body, a person file, or a company record to write one. If a friction entry cannot be described without quoting private content, describe it abstractly or leave it out.
- **Evidence or nothing.** Every friction entry carries a count. "This feels clunky" without a frequency is a hunch, and hunches are what made the last personal-OS attempt fail.
- **Say when something does not generalize.** A change that only helps one role is still worth shipping, as an optional field. Mislabeling it as universal is what bloats a model.
- **Never edit the plugin from a packet automatically.** A packet is a proposal. Applying it is a separate, deliberate act by whoever maintains the plugin.
