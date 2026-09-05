# Evals

Three harnesses, three different questions, three very different costs.

| | Question | Cost | Command |
|---|---|---|---|
| `run_commands.py` | Does a person reach the right thing? | **~1 min** | `python3 evals/run_commands.py` |
| `run_routing.py` | Can nineteen similar descriptions be told apart? | ~15 min | `python3 evals/run_routing.py --repeats 3` |
| `run_conformance.py` | Do the skills do what they say, to a real folder? | ~30 min | `python3 evals/run_conformance.py --repeats 3` |

Conformance is the one that finds real defects. Commands is the one you can actually iterate against — and the cost column is why it exists as a separate thing rather than more conformance cases. A minute is a loop you stay inside; thirty is a loop you leave and come back to, which is a different way of working and a worse one for wording.

---

## Routing

Nineteen skills that all operate on the same object, in the same vocabulary, for the same person. That is what makes their descriptions collide — and collision is invisible from reading them, because each looks perfectly clear on its own. The only way to find out is to put the whole roster in front of a model, hand it something a real person would type, and see which one it picks.

`routing-set.json` holds 58 queries, each with the one skill that should win (or `none`), tagged by what it probes. Results land in `runs/` as JSON and a markdown report: accuracy per probe, every miss as expected → chosen, and the unstable queries that split across repeats.

**Repeats matter.** Routing is stochastic. A query that routes correctly two times in three is one a real person hits wrong a third of the time, and a single run cannot tell that apart from a clean pass.

### What it found

**Iteration 1 — 93%.** Every collision pair the 0.6.0 audit predicted scored 100%: reality-check vs audit, configure vs rebuild, "add this" across intake/jobs/glossary, pull vs improve. The descriptions discriminate, which is the opposite of what the audit expected.

The one real failure was the newest skill. `corp-os-decide`'s description listed "we went with X" and "why did we decide that" as trigger phrases, and it duly absorbed queries belonging to `corp-os-claims` and `corp-os-recall`. Its *body* had the boundary right; the description advertised the opposite. **The body is not what routes.**

**Iteration 2 — 100%,** after rewriting that description to lead with the tense test and move the counterexamples into explicit not-for position.

**Iteration 3 — 100% over a deliberately harder set.** Fourteen queries added across the four categories a 100% score is supposed to make you suspicious of: the person's own renamed vocabulary ("we call them findings here", "matters", "engagements"), phrasings carrying no Corp-OS words at all ("my second brain", "that thing you set up for me"), mid-conversation fragments where context carries the intent ("ok but who actually owns that one"), and queries that legitimately touch two skills, where `expect` is whichever must go *first*. All four categories: 100%.

### The honest conclusion

Three iterations, 58 queries, four hard categories, no misses. At some point the responsible read stops being "make the set harder again" and becomes **routing is not this suite's risk.** Further eval effort belongs in conformance, which found three real defects on its first run.

One query was relabelled between iterations rather than counted as a miss, and the reason is written into the query itself. `neg-8` was written as a negative and routed to `corp-os-recall` every time; on review the model was right and the label was wrong. Silently flipping a label to make a number go up is how an eval stops meaning anything.

---

## Commands

A slash command is a thin prompt file whose whole job is to reach the right skill and hand it the right scope. That is a narrow question, and a narrow question can be asked with one short call instead of a whole session — the sweep runs in about a minute, which is the difference between iterating on wording and waiting on it.

Each case shows the roster and one thing a person typed, and asks two lines back: which skill fires, and what it would do first. That second line is the one worth reading. A command can reach the right skill and still open on the wrong move, and "Ask them to paste the material" versus "Locate the OS and scan it" is the difference between a command that respects an empty invocation and one that wastes it.

Cases come in pairs — with arguments and without — because the no-args path is where a command either does something sensible or asks a question nobody wanted. And seven `picker` cases carry no command at all: plain English, roster only. Those are the real risk of having eight commands, since a person scanning the list has nothing but eight one-liners about the same knowledge base to tell them apart.

**Current: 100% over 23 cases × 3 repeats.** Including every picker case, which settles the question of whether eight commands is too many — they are distinguishable, so the roster earns its place.

### What building it turned up

Almost all of it was the harness, which is what a fast loop is for — you find these in a minute rather than in half an hour.

- **The first run scored 74% because the model kept answering "that skill isn't installed here."** It was being literal about availability when the question was about routing. One line in the frame fixed it.
- **The picker cases scored 0% while picking correctly every time** — they answered with the command name (`/corp-os-catchup`) and the scorer wanted the skill (`corp-os-pull`). A right answer in the wrong currency. The scorer now resolves either.
- **Three cases were removed rather than fixed.** They checked that `configure`, `rebuild` and `audit` are reachable *without* a command, and the model kept answering `none` — correctly, because this harness's question is about commands and theirs is about skills. `run_routing.py` already answers it at 100%. Contorting a harness to ask a question another one asks better makes both worse.
- **A skill from a different plugin turned up in an answer.** `rebuild-corpus`, installed in the same session, competing with `corp-os-rebuild`. A useful reminder that these commands do not live alone on anyone's machine.

### The static half

`validate.py` checks what does not need a model at all, and it catches more than expected: frontmatter present, description under 90 characters (they sit one line each in a picker), no two descriptions opening the same way, every command naming a real skill, `$ARGUMENTS` handled, and the no-args path stated rather than left to chance. That last check found two commands that never said what an empty invocation does — the path most people take first.

---

## Conformance

Everything else in this repo checks that a skill *says* the right thing. `validate.py` greps for the pre-flight block. The routing eval measures which skill a query reaches. Neither had ever watched a skill run.

`run_conformance.py` does. Each case gets a throwaway copy of `examples/fixture-os`, one skill, and a prompt — then the runner reads the filesystem and asks what the cross-cutting rules actually claim:

- **`raw/` stays append-only**, with the `processed` flag as the one sanctioned edit.
- **A `usage/log.md` row was appended.** Open since 0.2.0 with no way to answer it, and the improvement flywheel depends on it entirely.
- **Derived-layer writes have a proposal file behind them.** Stated this way rather than "must not write", because these runs are told the person confirms — so a write is legitimate and a write with no proposal is not.
- **Unprocessed raw files are reachable from `INDEX.md`.**
- Per-case expectations in `conformance-cases.json`, each carrying a `why` that says what breaks if it fails.

```bash
python3 evals/run_conformance.py                 # all cases, once each
python3 evals/run_conformance.py --repeats 3     # rates, not pass/fail
python3 evals/run_conformance.py --case intake   # one
python3 evals/run_conformance.py --keep          # leave the trees for inspection
```

**Use `--repeats` for anything you are about to act on.** A single run cannot tell a defect from variance, and the close-out steps — the log row, the history entry, the redaction log — turn out to be exactly where these skills are least deterministic. With repeats, a check reports the share of runs it passed, and a step that lands three times in five reads as what it is rather than as a coin-flip pass.

Two fixtures ship, and cases name which they want:

- **`examples/fixture-os`** — the shipped default. Jobs on, claims on, one custom layer, a load-bearing sensitive claim in the scan path and an incidental one quarantined.
- **`examples/fixture-register`** — a legitimately-configured OS that shares almost none of that. Jobs off with an urgency-tiered `open-items/` layer carrying the priority signal, vocabulary renamed to `entries`, a cohort ceiling over a half-unsourced corpus, and `playbooks/` — a hand-maintained layer marked `role: source`, planted as a trap. It looks derived. A rebuild that overwrites it destroys work with nothing to restore from, which is the one failure mode in this system that loses data rather than degrading quality.

Runs against a disposable copy of a synthetic fixture, each in its own temp dir. Never point `--fixture` at a real OS.

### What it found, in order

**A contradiction in the model.** `corp-os-claims` edited a raw file — exactly as its own instructions say, flipping `processed: true`. But `data-model.md` said raw is "never edited". Both had been true in the repo for four releases and could not both be right. Resolved by naming `processed` as the one sanctioned exception and saying why: it is bookkeeping *about* the file, not part of what was said, and it has to live on the file so a rebuild reading `raw/` wholesale can tell what was already worked.

**A reproducible defect in the most-used skill.** `corp-os-intake` wrote the raw file, recounted `meta.json`, filed the proposal, appended the log row — and left the index entry out, four runs out of four. Nothing about reading the skill reveals this; by the time the interesting work is done, the bookkeeping feels finished. Step 4 now says to run `build_index.py` and then *re-read `INDEX.md` and confirm the file is in it*, and that confirmation is in the run's close-out list.

**A fixture that was not representative.** The first fixture had no `scripts/build_index.py`, while every OS `corp-os-setup` scaffolds has one and several skills tell the model to run it. A fixture missing what a real OS has tests the fixture, not the skill. `validate.py` now asserts the fixture carries it.

**`corp-os-brief` skipping its one write.** The dated `meta.json` history entry is the only thing a brief changes, and without it the next brief has no window and covers the whole corpus. The instruction now says that explicitly rather than listing it as a bullet.

### Two mistakes the harness made, kept on the record

Both were the harness being wrong about the skills, and both would have led to "fixing" something that was already right.

**Two skills correctly refused to run without a person.** In the first full run, `corp-os-intake` and `corp-os-brief` wrote nothing at all. Not a failure: intake asks when a type is ambiguous, and brief asks for a window when `meta.json` records no prior brief. Both were following their own instructions exactly. The frame now answers a clarifying question and continues rather than stopping at it.

**An assertion that encoded a wrong mental model.** "Every new raw file must appear in `INDEX.md`" failed a run that had done everything right — because the index lists the *unprocessed queue*, and a file the same run went on to process correctly drops off it. The check is now scoped to files still carrying `processed: false`.

An eval that has never been wrong about the thing it measures has not been looked at hard enough.

### What the irreversible-path cases found

Adding `rebuild`, `configure`'s delete sequence, and `redact` was where the fixture's trap earned its place — **the rebuild left `playbooks/` alone**, every run. The role model holds under a skill that has license to regenerate everything.

Two other things came out of it, both of which changed the spec rather than the run:

**A retention deletion invented the tombstone.** Asked to destroy raw material under a stated obligation, a run wrote a `.deleted.md` in its place carrying the original frontmatter, the date, and the obligation — and that is better than what the spec had. Without it a deletion leaves a hole, and a later rebuild reading `raw/` cannot tell "never captured" from "destroyed under obligation", which call for opposite responses. Adopted.

**Redaction pairs its log with its export.** The skill said `usage/redaction-log-<date>.md`; runs kept pairing the log with the specific export instead, which is better when someone produces three exports in a day. Also adopted.

### The finding that drove three scripts: close-out steps are not deterministic

Across five full runs, the steps that fail are always the last ones. `corp-os-brief` writes its `meta.json` history entry most runs, not all. `corp-os-recall` proposes before writing to a job's evidence list most runs, not all. `corp-os-redact` produced its private log under four different names across five runs — `redaction-log`, `redaction-record`, `.redaction-log`, `.LEDGER` — and once not at all.

Run with `--repeats 3`, the rates were unambiguous:

| check | rate |
|---|---|
| `corp-os-brief` writes its `meta.json` history entry | **33%** |
| `corp-os-redact` produces both outputs (`redact-external`) | **67%** |
| `corp-os-redact` produces both outputs (`redact-strips-load-bearing`) | **0%** |
| `corp-os-recall` surfaces the load-bearing sensitive claim | **67%** |
| everything else — 68 of 75 checks | 100% |

The pattern is the point: **the failures are all the last step of a run, never the judgment before it.** The instruction to write the log was present, concrete, explained, and strengthened twice — including a rewrite that moved it from the end of the skill to the beginning so it would accumulate during the sweep. Variance persisted.

So past a certain point more instruction stops buying reliability, and the answer is to take the step out of the model's hands. Two scripts came out of this measurement:

- **`write_export.py`** — writes redaction's cleaned copy and its private log, and refuses to write one without the other.
- **`log_run.py`** — writes the `usage/log.md` row and the dated `meta.json` history entry together, and refuses a blank friction field. Sixteen skills call it.

Neither exercises judgment; they write what they are handed, including the friction, which is the one field a script could never invent. That is the same line `build_index.py` has always sat on.

**One of the five could not be fixed this way.** `corp-os-recall` withholding a load-bearing sensitive claim a third of the time is judgment — a reflex that sensitive means hide — so there was nothing to hand to code. It got a sharper instruction naming the reflex and why it is wrong here, and whether that worked shows up as a rate rather than an opinion. That is the whole argument for keeping rates instead of pass/fail.

The redaction assertion now counts outputs instead of matching a name, because chasing the name was testing a convention rather than the behavior that matters: two files, one of them private.

### The one that has not been made to pass

`setup-from-empty` is the only case that starts from an empty directory, and the only one still failing. Asked to set up an OS for a contracts manager, `corp-os-setup` produces a contracts filing system — `agreements/`, `renewals.md`, `vendors/`, a template, a clause checklist. Sensible for that person. None of the five invariants: no `INDEX.md`, no `meta.json`, no `config.json`, no `raw/`. Nothing else in the suite can operate on it.

**Six runs, three configurations, no movement.** The scaffolder unmentioned; the scaffolder called in Step 3; the scaffolder as Step 0, before a single question, with the reasoning written out. 2/9 to 3/10 every time.

That is a negative result worth the space, because the obvious next move — write the instruction more forcefully — has now been tried twice and is what this repo already learned does not work.

Two readings, and separating them is the actual next step:

- **It may be the skill.** With no existing OS to anchor to and a request dense with the person's own domain vocabulary, the structure loses to the vocabulary. Both pressures are legitimate: adapting to how someone describes their work is something `corp-os-setup` should do, and "I'd rather see something than answer twenty questions" is a reasonable thing to say.
- **It may be this harness.** The frame says *the skill is at this path, read it and follow it* — which a model may reasonably treat as reference material rather than as a procedure to execute. Fifteen of sixteen cases follow their skill closely, which argues against this. But all fifteen start from an existing OS, so none of them tests what this one tests.

The way to tell: install the plugin and run `/corp-os` in a real session against an empty folder. If it scaffolds correctly there, the harness is the problem and this case needs a different shape. If it does not, the fix is structural — the command runs `scaffold.py` itself before handing off, so the invariants land before the domain can push them off the disk.

Recorded as unresolved rather than patched a third time.

### Where to take it next

Twelve cases across nine skills. The ten skills with no case are the remaining gap, and none of them now has an irreversible path — those were the priority and they are covered. What is left is mostly the input side (`pull`, `connect`, `company`, `glossary`) plus the meta skills (`improve`, `audit`, `guide`, `setup`).

`corp-os-setup` is the interesting one and the hardest: it starts from nothing, so it needs a case that begins with an empty directory rather than a fixture, and the only assertion worth making is that what comes out is a valid OS — every file the spec calls for, counts that match a real count, a `config.json` that describes the shape actually on disk. That is weaker than the question anyone cares about (does the nine-area interrogation land on a real person?) but it is not nothing, and it is the only part of that question a machine can answer.
