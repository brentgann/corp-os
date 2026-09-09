# The arguments layer

Optional, and offered rather than scaffolded. An argument is a conclusion built across entries rather than taken from one, which is why it is the one record whose confidence is inherited rather than assigned.

Read this only when an OS actually declares the layer. The `Rests on` field it turns on is specified in `${CLAUDE_PLUGIN_ROOT}/reference/claim-record.md`, which also states why that field is not this layer's private property.

## The record

A claim is one fact with one citation. A topic file is narrative that asserts nothing on its own. A decision is a fork with an owner and a date. None of them can hold: *here is a conclusion built across eleven entries, here is what to do about it, and here is when doing it stops being useful.*

```markdown
## AR-0007 — The middle of the funnel is where the drop-off actually is
- **So what**: Stop instrumenting the top. Move the next two weeks of work to the hand-off.
- **Timing**: useful until the Q1 plan locks; after that it is a retrospective
- **Status**: live            # live | spent | stale
- **Rests on**: CL-0142, CL-0155, CL-0201, CL-0233
- **Confidence**: needs_review   # inherit the weakest of what it rests on
```

**`rests_on` is rendered as two numbers, never one.** `4 entries / 3 sources`. The count of supporting entries reads as evidence breadth and does not measure it: entries are minted at whatever granularity a pass chose, so a source that yielded nine contributes nine and a source that yielded one contributes one. Measured, in a real corpus: one argument rested on **nine entries that all traced to a single meeting**. Nine entries from one conversation is one data point, and the number looked like breadth.

`corp-os-reality-check` flags any argument whose distinct-source count is 1. Not wrong, necessarily — an argument resting on one conversation is a different object from one resting on nine, and only the record can tell them apart.

**Inherit the weakest.** An argument's confidence is the lowest confidence among what it rests on. An argument built on eleven `needs_review` entries is `needs_review`, however convincing it reads.

**Why optional.** It is a decision-heavy and orientation-role structure. A build-heavy operator would write two a year and the layer would read as overhead, so `corp-os-setup` offers it rather than scaffolding it.

**Why it earns a place at all.** In the OS that invented it, 23 entries across six months and 220 sources — deliberately rare — and **13 of 23 marked `spent`, 2 `stale`.** The operator retired more than half his own arguments. That is the removal test this model applies to every layer, and this one passed it while the shipped claims layer had retired nothing at all.

One thing it must not have: a hand-set signal-strength rating. The prior system had one and it was dropped as decorative. Its actual function was counting independent witnesses, which `rests_on` derives for free and which cannot go stale.
