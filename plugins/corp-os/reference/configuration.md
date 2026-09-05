# Configuration

The shipped Corp-OS model is a **default profile, not a schema.** Everything it assumes — layer names, label vocabularies, decay behavior, how long raw material is kept, how strict the review gate is — is declared in `config.json` at the OS root, and every skill in this suite reads that file before falling back to any shipped default.

This exists because the parts of the model that are genuinely universal are few: an append-only source layer, provenance on derived entries, a review gate, an index that can be scanned, and something that removes things. Everything else is a reasonable guess about a stranger's work. A controller, a litigator, a field researcher, and a product manager need the same five properties and almost none of the same structure.

## Precedence

1. `config.json` in the OS root — the authority.
2. The OS's own `README.md` — for anything config does not cover, and for the human-readable explanation of why the config is shaped the way it is.
3. The shipped defaults in `data-model.md` — the fallback when no config exists, which is also what `corp-os-setup` writes as a starting point.

A config that contradicts the README is a bug to surface, not to resolve silently: one of the two is stale, and only the person knows which.

## The file

```json
{
  "corpos_version": "0.3.0",
  "profile": "default",

  "vocabulary": {
    "job": "job",
    "claim": "claim",
    "confidence": ["confirmed", "needs_review", "reconstructed", "disputed", "retired"],
    "sensitivity": ["public", "internal", "sensitive"],
    "bearing": ["incidental", "load_bearing"],
    "kinds": ["fact", "decision", "theme", "assumption", "constraint", "metric", "preference", "identity"],
    "answer_status": ["open", "signal exists", "partial", "in motion", "answered"],
    "tags": [],
    "tiers": []
  },

  "layers": {
    "raw":       { "enabled": true, "role": "source" },
    "jobs":      { "enabled": true, "role": "derived", "gated": true },
    "//jobs":    "optional — see 'Turning jobs off' below",
    "claims":    { "enabled": true, "role": "derived", "gated": true, "grouping": "topic" },
    "people":    { "enabled": true, "role": "derived", "gated": true,
                   "fields": ["role", "tier", "status", "aliases"] },
    "topics":    { "enabled": false },
    "glossary":  { "enabled": false },
    "company":   { "enabled": false },
    "proposals": { "enabled": true, "role": "record" },
    "sensitive": { "enabled": false, "role": "derived", "in_scan_path": false }
  },

  "decay": {
    "enabled": true,
    "applies_to": "sourced",
    "default": "90d",
    "by_kind": { "decision": "none", "constraint": "none", "identity": "none", "metric": "30d" },
    "by_tag": {},
    "sweep_cadence": "monthly"
  },

  "retention": {
    "raw": {
      "policy": "keep",
      "ttl": null,
      "archive_to": "raw/_archive/",
      "measure_from": "frontmatter_date",
      "exceptions": [],
      "reason": null
    },
    "proposals": { "policy": "archive", "ttl": "180d" },
    "sensitive": { "policy": "keep", "ttl": null }
  },

  "gate": {
    "mode": "propose",
    "persist_proposals": true,
    "trusted_sources": [],
    "batch_threshold": 12
  },

  "confidence_ceilings": [],

  "scan": {
    "index_first": true,
    "excluded_from_scan": ["sensitive.md", "raw/_archive/"]
  },

  "design":     { "system": null, "skill": null },
  "dashboards": { "default_target": "artifact" },
  "brief":      { "cadence": "weekly", "channel": "chat" }
}
```

## Vocabulary

Renaming a label changes what the person reads, never what a skill means by it. A `claim` renamed `finding` is still a claim: it still needs a source, a confidence, and a decay window. Skills resolve through the config and speak the person's word back to them.

This matters more than it sounds. "Claim" is wrong in several fields — a litigator hears something specific and different, a scientist hears something weaker than intended. Being unable to rename it is a real reason someone abandons a system, and the cost of allowing it is one indirection.

Two rules:

- **Renaming is free; removing a semantic is not.** Dropping `assumption` from `kinds` does not simplify the model, it removes the ability to distinguish what was observed from what is believed — which is the distinction that keeps the OS from lying to its owner. If someone wants it gone, say what it costs, then respect the answer.
- **`sensitivity` and `bearing` are two axes and both are renameable, but neither collapses into the other.** `sensitivity` is the export class; `bearing` decides whether an entry stays in the scan path. Someone who wants a single flag is asking for the model that shipped before 0.9.0, and it fails in a specific way worth naming: quarantining load-bearing material does not produce a gap, it produces a confidently wrong answer with nothing to signal the omission. Rename both freely; do not merge them.
- **A controlled `tags` list beats a free one past about fifty entries.** Empty means free-form. Populate it once the vocabulary stabilizes, and populate it from what is already in use rather than from an idea about what should be.

## Layers

Every layer declares a **role**, and this is the field most worth getting right:

- **`source`** — its own truth. Never regenerated, never overwritten. `raw` is the shipped example.
- **`derived`** — regenerable from source layers. `corp-os-rebuild` will overwrite it, by design.
- **`record`** — an audit trail of things that happened. Neither regenerable nor a source of truth; appended to and eventually archived. `proposals` is the shipped example.

Getting a role wrong is the one configuration error that destroys data. A `source` layer mislabeled `derived` gets overwritten by the next rebuild, and there is nothing to restore it from. **`corp-os-rebuild` refuses to touch any layer whose role is not `derived`,** and any new layer defaults to `source` until someone explicitly says otherwise — the safe direction to fail.

### No layer is enabled without a schema

**A layer may only be enabled if it declares an `entry_schema` and an `index_line`.** This applies to shipped layers and custom ones alike, and it is why `people` and `topics` are no longer scaffolded by default: both were being created, indexed, and read while no spec said what a person record or a topic record contains and no skill owned writing one. A layer in that state fills with whatever shape the session that happened to write it chose, which is precisely the drift the review gate and the scan contract exist to prevent.

The rule has a useful side effect: it forces the question "what is one entry, and what does one line of it look like in `INDEX.md`" to be answered before the folder exists, rather than discovered at forty entries.

### Custom layers

A layer Corp-OS never imagined is declared the same way as a shipped one:

```json
"experiments": {
  "enabled": true,
  "role": "derived",
  "gated": true,
  "path": "experiments/",
  "entry_schema": {
    "id":         { "type": "string",  "required": true },
    "hypothesis": { "type": "string",  "required": true },
    "status":     { "type": "enum",    "values": ["designing", "running", "read-out", "abandoned"] },
    "serves_jobs":{ "type": "list" },
    "readout":    { "type": "string" }
  },
  "index_line": "{id} — {hypothesis} ({status})",
  "promotion_bar": null,
  "decay": "none"
}
```

The two fields that carry the weight:

**`index_line`** is what keeps the scan contract intact. Without a one-line-per-entry template, a custom layer becomes a folder that has to be opened to be understood, and the whole scan-from-INDEX discipline degrades one layer at a time. `build_index.py` renders it; a layer with no `index_line` gets listed as a bare link and flagged as incomplete.

**`promotion_bar`** is for a layer that is a *tier* rather than a category — an `insights/` folder, a `decisions of record`, a `confirmed findings`. A tier without a stated bar fills with everything adjacent and stops being read. If a layer is a tier, write its bar as prose in this field and let skills enforce it verbatim.

Custom layers get provenance like anything else. A layer that opts out of source and confidence is a notes folder with extra steps, and the OS cannot reality-check it.

## Decay

`enabled: false` turns decay off entirely. Say plainly what that costs — nothing will ever flag a stale entry, so correctness becomes wholly dependent on someone noticing — and then respect it. A short-lived OS built for one project genuinely does not need decay.

`by_kind` is the setting that does the most work. Decisions and constraints are usually `none`: a decision that was made stays made, and what changes is whether it still applies, which is a new claim rather than a stale one. Metrics rot fastest. When everything ends up at the default, nobody set these thoughtfully and the monthly sweep will surface noise instead of signal — `corp-os-improve` checks for exactly that pattern.

`by_tag` overrides `by_kind`. A `pricing` tag at 30 days will do more for accuracy than any amount of care per claim.

### `applies_to` — the setting that decides whether decay is usable at all

`sourced` (the default) applies decay only to entries with a retrievable citation. `all` applies it to everything.

This distinction is not a refinement; it determines whether the sweep is worth running. **Decay assumes re-verification is possible.** An entry whose citation is `no source` can be flagged stale but can never be re-confirmed, because the thing that would confirm it does not exist. Set `applies_to: "all"` on a corpus with a large unsourced share and every sweep surfaces the same permanently unresolvable backlog — which is precisely how someone learns to skip the sweep, taking the resolvable items down with it.

Corpora migrated from a previous system are the common case here: it is entirely normal for a third or more of such a corpus to have no retrievable source. Those entries need a **one-time disposition pass** — keep as an `assumption`, retire, or backfill a real source — and then to stop being carried as decay candidates. `corp-os-reality-check` handles that as its own bucket rather than mixing it into the overdue list.

Use `all` only when nearly everything is sourced, or when the point of the sweep is specifically to force the unsourced material to a decision.

## Retention — including raw TTL

Four policies, and the differences between them are consequential:

| Policy | What happens | Rebuild fidelity | When it is right |
|---|---|---|---|
| `keep` | nothing expires | full, permanently | the default; almost always correct |
| `archive` | moved to `archive_to`, dropped from the scan path, still on disk | full | raw/ has grown and is slowing scans |
| `summarize_then_archive` | a summary is written, the original archived | reduced | a long corpus where old detail is genuinely dead |
| `delete` | permanently removed | broken for anything sourced there | a legal, contractual, or regulatory obligation |

**`archive` is what most people asking for a raw TTL actually want.** The complaint is usually that raw/ has grown unwieldy, and the fix is removing it from the scan path — not removing it from disk. Archiving costs nothing and is reversible. Offer it first.

### If the policy is `delete`

Deletion of source material is not a cleanup operation. It is a **claim-integrity event**, and treating it as file management is how an OS quietly fills with claims that cite files which no longer exist — which is worse than `no source`, because it still *looks* sourced and nothing downstream can tell the difference.

Before deleting anything:

1. **Find every claim citing the file.** All of them, across every layer.
2. **Re-cite each to `no source`** and **lower its confidence** — `confirmed` becomes `reconstructed` at best, because the thing that made it confirmable is gone. Add the reason and the date.
3. **Record a cohort ceiling** for the affected claims, so no later pass promotes them back.
4. **Log it** in `meta.json` history: what was deleted, under what obligation, how many claims were affected.
5. Only then remove the files.

`reason` is required when the policy is `delete`, and it should name the actual obligation — a retention schedule, an NDA clause, a customer's deletion right. "Housekeeping" is not a reason to destroy source material; that is what `archive` is for.

Exceptions match on tag, source, or path, and always win over the policy:

```json
"exceptions": [
  { "match": "tag:contract",   "policy": "keep" },
  { "match": "kind:decision",  "policy": "keep" },
  { "match": "source:legal",   "policy": "keep" }
]
```

`measure_from` should stay `frontmatter_date`. Filesystem mtime changes when a file is copied, synced, or restored from backup, which would silently reset or trip every TTL in the corpus at once.

## Gate

`mode` sets how much the review gate asks of the person:

- **`propose`** — everything is proposed individually. Strictest, correct default.
- **`propose_batched`** — proposals grouped into one confirmation once a run exceeds `batch_threshold`. The pragmatic setting for someone processing dozens of items, and the one that keeps the gate from becoming a rubber stamp through sheer volume.
- **`trusted_sources`** — claims sourced from a named allowlist are written directly. Genuinely useful for a mechanical, high-precision source: a filing, a query result, an audit export. Genuinely dangerous for anything conversational or model-generated.

If someone asks for `trusted_sources`, say what it costs before setting it: every claim from that source enters the derived layer unreviewed, and the review gate is the reason the derived layer counts as knowledge rather than a second copy of raw/. Nothing conversational, summarized, or model-generated belongs on that list.

`corp-os-improve` watches for the gate becoming theater — proposals confirmed unread. The fix for that is fewer, better proposals or `propose_batched`, never turning the gate off.

## Starter profiles

Structural shapes only. No profile ships domain vocabulary, categories, or content — that comes from the person.

- **`minimal`** — `raw`, `jobs`, `claims`, `proposals`. Decay on. The honest starting point for most people, and easy to grow.
- **`default`** — `minimal` plus `glossary`. What `corp-os-setup` writes unless the interrogation says otherwise. Note what it does *not* add: a person or topic layer, because neither earns a place until the interrogation says the work needs one.
- **`relationship`** — declares a `people` layer, tiered and load-bearing, with aliases on and short decay on role and status claims. For work that is mostly about knowing the state of a set of counterparties. The declaration it writes:

  ```json
  "people": {
    "enabled": true, "role": "derived", "gated": true, "path": "people/",
    "entry_schema": {
      "name":    { "type": "string", "required": true },
      "role":    { "type": "string", "required": true },
      "org":     { "type": "string" },
      "tier":    { "type": "enum",   "values": ["core", "regular", "peripheral"] },
      "status":  { "type": "enum",   "values": ["active", "dormant", "departed"] },
      "aliases": { "type": "list" }
    },
    "index_line": "{name} — {role} · {tier}",
    "decay": "365d"
  }
  ```

  Person records are a **readable view**; correctness still lives in claims, the same way a company record does. Anything asserted on a person record exists as a claim with its own citation, or it is invisible to `corp-os-reality-check` and will rot unnoticed.
- **`research`** — `glossary` on, `claims` grouped by topic, longer decay, and a `sources` layer for external material distinct from first-hand capture. A separate `topics` layer is available as a custom declaration, but grouping claims by topic already does most of that work, and running both is the most common way the same fact ends up in two places with different wording.
- **`archive`** — `raw` plus an index, no derived layer, decay off. A searchable record with no curation. Legitimate, and worth naming what it gives up: no summary layer, nothing queryable without reading the material.
- **`decision`** — declares a `decisions` layer alongside jobs and claims. For work where the recurring unit is a fork someone has to pick between rather than a fact to accumulate. The declaration it writes:

  ```json
  "decisions": {
    "enabled": true, "role": "derived", "gated": true, "path": "decisions/",
    "entry_schema": {
      "id":            { "type": "string", "required": true },
      "statement":     { "type": "string", "required": true },
      "owner":         { "type": "string", "required": true },
      "status":        { "type": "enum",   "values": ["open", "blocked", "decided", "lapsed", "moot"] },
      "decide_by":     { "type": "date",   "required": true },
      "reversibility": { "type": "enum",   "values": ["reversible", "costly", "one-way"] },
      "blocks":        { "type": "list" }
    },
    "index_line": "{id} — {statement} · {owner} · by {decide_by}",
    "decay": "none"
  }
  ```

  `owner` and `decide_by` are required on purpose. Both are the fields people skip, and a decision missing either is the one still open next quarter — see `corp-os-decide`.
- **`register`** — `jobs` off; an open-items layer tiered by urgency carries the priority signal instead, with decay providing the removal rule. The right shape when the work is reference accumulation rather than a handful of recurring decisions. See "Turning jobs off" below before choosing it.

### Turning jobs off

`layers.jobs.enabled: false` is supported and sometimes correct. Read the "When a jobs layer is the wrong answer" section of `data-model.md` first — it contains the empirical test, which is worth running rather than guessing at.

When jobs are off, something else must carry the two functions they provide:

- **An intake priority signal.** Usually urgency tiering on the open-items layer.
- **A rule that removes things.** Usually decay, sometimes a resolved/retired tier that is actually pruned.

If neither substitute is in place, the OS has no stopping rule and will grow without bound. That is the one configuration worth arguing against, and it is worth saying plainly rather than letting someone discover it at four hundred entries.

A profile is a starting point that gets edited, not a mode the OS stays in. `corp-os-configure` changes any of it later.

## Changing config on a live OS

Some changes are safe and some are migrations. Skills treat them differently:

**Safe** — renaming vocabulary, adding a layer, adding a field, loosening decay, changing dashboard target or brief cadence.

**Migrations** — need a plan and a confirmation before anything is written:

- **Disabling a layer** — its content has to go somewhere. Propose a destination; never orphan a folder.
- **Removing a value from a vocabulary** — every entry using it needs remapping. Enumerate them first and show the count.
- **Tightening decay** — will immediately mark a large share of the corpus overdue. Say how many before applying, or the next sweep looks like a catastrophe rather than a backlog.
- **Any retention change toward `delete`** — the claim-integrity sequence above, in full.
- **Changing a layer's role** — `derived` to `source` is safe; `source` to `derived` means the next rebuild will overwrite it. Confirm explicitly, and say so in those words.

Every config change gets a dated entry in `meta.json` history with what changed and why. A config whose current state cannot be explained is a config nobody will dare edit.
