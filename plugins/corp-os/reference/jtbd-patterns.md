# Job statement patterns

Reference for `corp-os-jobs` and `corp-os-setup`. Use it to recognize and repair job statements — never to hand someone a pre-filled job.

## Before anything: does this person need a jobs layer?

Answer this before helping someone write job statements, because the enthusiastic default is to fit jobs onto work that is not shaped that way.

Run the test in `data-model.md`: cluster the existing material into three to seven candidate jobs **without looking at the existing subject taxonomy**, then compare. If the clusters reproduce that taxonomy, the material is subject-shaped and a jobs layer duplicates something that already works. High cross-assignment (a quarter or more of entries fitting two clusters equally) and clusters named after domains rather than decisions are the two other tells.

There is a second, faster diagnostic worth applying to any existing open-items layer: **sort its entries by grammatical form rather than by subject.**

- **Findings** — a fact plus an implied concern, with no question and no decision attached ("throughput is down 30%", "the vendor bill is higher than expected").
- **Errands** — imperatives ("book time with X", "get access to Y", "read Z").
- **Decisions** — a live fork the person actually picks between.

A layer that is mostly findings is a **status register**, not a question queue, and JTBD is a lens for organizing questions someone keeps re-asking. If only a small share is decision-shaped, that share needs a decision log with owners and dates — not a taxonomy layer above it. Errands belong in a task tracker; findings usually belong in whatever subject file already covers them.

Say this plainly when it is true. Recommending a jobs layer to someone whose material will not support one is how a model loses the credibility it needs for the parts that do matter.

## The canonical form

> When `<situation>`, I want to `<motivation>`, so I can `<outcome>`.

Each clause does work:

- **Situation** is the trigger. It tells the OS *when* this job becomes live, which is what lets a brief say "this job is relevant this week."
- **Motivation** is the capability sought, stated as knowing or being able to do something — not as an artifact produced.
- **Outcome** is what the capability is *for*. This is the clause that determines whether a claim is relevant, so a vague outcome makes recall vague.

## Malformed shapes, and the repair

**A task wearing a job's clothes.**
"I want to finish the Q4 deck." — Completes once, then the record is dead weight. Ask what the deck is for and what makes it hard, and the real job usually surfaces: "When I present quarterly to the exec team, I want to know which numbers will get challenged, so I can walk in with the answer rather than a follow-up."

**An artifact as the motivation.**
"...I want a competitive one-pager..." — Encodes today's format into the job, so the OS starts serving the document instead of the need. Repair: "I want to know where we actually win and lose against each competitor."

**Outcome missing.**
"When I'm in a customer call, I want to have their history handy." — For what? Without the outcome clause there is no relevance test, so everything about the customer looks equally important. Ask "and that lets you do what?"

**Situation that's always true.**
"When I'm doing my job, I want..." — Not a trigger, so the job is permanently live and never prioritizable. Push for the specific moment.

**Two jobs in one sentence.**
Look for "and" joining unrelated outcomes. Split them; a job with two definitions of done cannot be closed.

**A job that's really a metric.**
"I want to get NPS above 40." — That's a success signal, not a job. The job is whatever work moves it. File the number under success signals of the real job.

## How jobs differ by role shape

Do not use these as templates. Use them to recognize which *kind* of job you are hearing, because the kind determines what evidence the job needs.

- **Decision-heavy roles** (managers, buyers, investors, clinicians, editors) — jobs cluster around recurring decisions made under incomplete information. Evidence needs are specific and perishable; decay windows are short.
- **Relationship-heavy roles** (sales, recruiting, partnerships, account management, fundraising) — jobs cluster around knowing the state of a set of counterparties. A declared person layer is load-bearing here — the `relationship` profile in `configuration.md` carries the declaration — and the evidence is mostly what someone said and when.
- **Build-heavy roles** (engineering, design, writing, analysis) — jobs cluster around reducing rework and remembering rationale. Decisions and constraints dominate over facts; `glossary.md` and decision-kind claims are load-bearing.
- **Operate-heavy roles** (ops, support, finance, program management) — jobs cluster around keeping a process healthy and explaining variance. Metric-kind claims and dashboards dominate; decay is continuous.
- **Orientation jobs** (anyone new in seat, or entering a new domain) — a distinct kind with a real end state. Statement form: "When I'm asked about X, I want to answer without checking, so I can be trusted with X." These *should* retire, and a job of this kind still open after two quarters is a signal worth surfacing.

Most people have jobs of two or three kinds at once. A job's kind is a hint about what to collect, not a category to file it under.

## Sizing

A well-sized job:

- recurs, or has a real end state — not both vague and endless
- has a definition of done someone else could check
- has an evidence list between two and about eight items (one item means it's a task; twenty means it's a role)
- would be recognized as one thing by a colleague

If a job's evidence list keeps growing past ten items, it is a cluster. Split by the decision each item serves.

## Retiring

A job retires when its definition of done is met, its trigger stopped occurring, or it turned out to belong to someone else. Retire, do not delete: a retired job is the only record of why a pile of claims was ever collected, and it is the pruning rule for claims that served nothing else.

Surface a job for retirement review when it has been `active` with no `last_touched` change for a full horizon period. Do not retire it unprompted.
