# Quick start, and what to say to get what you want

Two halves. The first hour, and then a map from what you actually want to the skill that does it.

Every phrasing in the second half is taken from the routing eval — 77 queries against the full 23-skill roster, three repeats each. Overall accuracy is **100%**, which means these are not suggested magic words. They are ordinary sentences that were tested, and you do not have to match them.

---

## The first hour

### 1 · Install — two minutes

```
/plugin marketplace add brentgann/corp-os
/plugin install corp-os@brentgann
```

In the desktop app use the plugin browser rather than the slash command. Nothing exists yet; you have installed twenty-three skills that operate on a folder you do not have.

### 2 · Say what you want, not which skill — one minute

```
i installed this thing. what does it actually do and what should i do first
```

That routes to `corp-os-guide`, which finds out whether an OS exists, explains the model in a paragraph, and hands you to one named skill. It is the right first move and the right move any time you are unsure. It ends on a single next action rather than a menu.

### 3 · The interrogation — fifteen to twenty minutes

```
set up a work OS for me
```

`corp-os-setup` asks about nine areas before it writes anything. This is the part people want to skip and the part that decides whether the folder is still open in six months.

| Area | What it settles |
|---|---|
| 1 · Role and mandate | What you are accountable for, which is often not your title |
| 2 · Intent | What keeps going wrong — the thing that made you want this |
| 3 · Jobs to be done | Three to five outcomes you are working toward. Not fifteen |
| 4 · What earns its keep | What you actually go back and look for |
| 5 · Input paths | How information reaches you today |
| 6 · Tools and protocols | For each source: can it be fetched back verbatim, and at what cadence |
| 7 · Company and market | What your employer sells, and to whom |
| 8 · Output and design | Who else sees what this produces |
| 9 · Sensitivity | What must never leave, and what is merely private |

**A scaffold built without this produces a generic notebook that gets abandoned in a month.** Area 9 is the one people regret skipping: a quarantine file added later means retrofitting content out of files it has already been shared from.

You can say *"keep it short, make reasonable assumptions and tell me what you assumed"* and it will. That is a real answer, and the assumptions get written down.

### 4 · Put one real thing in — five minutes

Paste something. A transcript, a call note, a document.

```
here's the transcript from this morning's call with the Vertex folks, add it
```

`corp-os-intake` writes the source verbatim into `raw/`, proposes claims from it, and waits. The proposal is a file on disk, not a message in the chat — that is the review gate, and it is what you are confirming.

### 5 · Get one answer back — one minute

```
what do I actually have on the Northwind situation?
```

`corp-os-recall` answers from what the OS holds, with the citation attached, and tells you what it does not cover. An answer with no source behind it is the failure this whole design exists to prevent.

### 6 · Know what you have

Open `INDEX.md`. Every entry is one scannable line. If a question can be answered from that file alone, the system is working; if you keep having to open files, that is a finding worth telling `corp-os-improve` about later.

### What not to do first

- **Do not migrate before you set up.** Six months of Notion notes into an unshaped OS reproduces the mess with more steps. `corp-os-setup`, then `corp-os-migrate`.
- **Do not turn on every layer.** The jobs layer is a default, not a requirement — it pays for a decision-heavy role and costs more than it returns for reference accumulation. `corp-os-audit` runs an actual test rather than assuming.
- **Do not skip the friction field.** Every run ends with one line about where it hurt. "None" is a real answer; blank is not. That field is the only telemetry this system has.

---

## Say this, get that

### Getting material in

| You say | Skill | What happens |
|---|---|---|
| *here's the transcript from this morning, add it* | `intake` | Source into `raw/`, claims proposed, gate waits |
| *grab whatever's new from my meeting notes since last week* | `pull` | Fetches from a registered source, dedupes on id |
| *hook up my meeting notes tool* | `connect` | Registers the source, its cadence, and its blind spots |
| *I've got six months of notes in Notion and a wiki* | `migrate` | Cohort ceiling, spread decay, and a record of what was left behind |
| *catch me up, I've been out for a week* | `pull` | The backlog, not a summary of what you already had |

### Getting value out

| You say | Skill | What happens |
|---|---|---|
| *what do I actually have on X?* | `recall` | Answer with provenance, and an honest account of the gaps |
| *give me the monday morning rundown* | `brief` | What moved, what needs a decision, what went stale |
| *build me the job board* | `dashboard` | Runs a pattern's generator; the script is the artifact |
| *what do we sell, and to whom* | `company` | Company record from graded sources, never from recall |
| *I need to send this to someone outside* | `redact` | A cleaned copy **and** a private log of what was removed |

### Keeping it honest

| You say | Skill | What happens |
|---|---|---|
| *half of what's in here about Northwind is out of date* | `reality-check` | Sweeps decay, separates unrecoverable from merely stale |
| *what am I waiting on right now?* | `decide` | Open forks, led by whatever is past its date |
| *audit my knowledge base and tell me how it stacks up* | `audit` | Ten dimensions, plus what you have that the model lacks |
| *this is getting annoying to use* | `improve` | Reads the usage log, and refuses to propose from one occurrence |

### Changing its shape

| You say | Skill | What happens |
|---|---|---|
| *this is set up wrong for how I work — I have matters, not jobs* | `configure` | Renames the vocabulary, declares layers, enumerates the blast radius |
| *the topic files have gotten out of hand, redo the derived layer* | `rebuild` | Re-derives everything from `raw/`, which is why `raw/` is sacred |
| *I need a people layer with a proper schema* | `configure` | A layer is not created without a field schema and an index line |
| *I just updated the plugin — does my OS need anything?* | `upgrade` | Yes. Refreshes the OS's own script copies and names what it will not migrate |

### Working with other people

| You say | Skill | What happens |
|---|---|---|
| *this dashboard came out well, I want the team to build the same one* | `pattern` | Authors it as a portable pack, addressed by role not by name |
| *someone sent me our team's pack, how do I take it* | `pattern` | Binds against your vocabulary, or says which layer is missing |
| *write this up as a diff I can apply to the corp-os repo* | `contribute` | Real diffs against real files. Applies nothing |

---

## The six pairs people actually get wrong

These are the collisions the routing eval was built to probe. Each is a real distinction, not a naming quirk.

### "audit this" — `reality-check` or `audit`

**Is the content wrong, or is the system wrong?** `reality-check` goes through your entries and finds what has decayed. `audit` assesses the shape of a knowledge system, including one that is not a corp-os at all — a colleague's Obsidian vault scores fine here.

### "this is a mess" — `configure` or `rebuild`

**Rebuilding faithfully reproduces a shape that was wrong.** If the taxonomy drifted, `rebuild`. If the shape never fit how you work, `configure`. Rebuilding a bad shape gets you a tidy version of the same problem.

### "add this" — `intake`, `jobs`, or `glossary`

**Read what is being handed over.** Content to file is `intake`. Something you are trying to accomplish is `jobs`. A term two teams define differently is `glossary`, and that one is worth knowing about — a glossary that flattens a real disagreement into one authoritative entry is worse than no entry.

### anything with "decide" in it — `decide`, `claims`, or `jobs`

**Read the tense.** A choice still open is a decision record. A choice already made is a claim. An outcome you are working toward — *"decide how to handle renewals"* — is a job. Get this wrong and forks sit open for months, because filed as a job, nothing ever forces the date.

### "update my OS" — `pull` or `improve`

**Is material waiting, or is the system annoying you?** New material is `pull`. Recurring friction is `improve`. If you are hand-writing the same three fields every time, that is the second one.

### "something looks wrong since I updated" — `upgrade`, always first

Your OS carries **its own copies** of the shipped scripts, so it keeps working when the plugin is not loaded. A plugin update reaches none of them. A count that changed or a warning that appeared right after an update is almost always that gap rather than your content.

---

## Three sessions, end to end

**After a call — four minutes.** Paste the transcript, say *add it*. Read the proposal file, confirm what belongs and decline what does not. The declines are the half that matters: they are the only record of what you chose not to know.

**Monday morning — three minutes.** *"Give me the rundown."* What moved, what needs a decision, what went stale. Then *"what am I waiting on?"* for the forks past their date.

**Once a quarter — twenty minutes.** *"Audit my knowledge base."* Then `reality-check` on whatever it flagged, and `improve` on the usage log. The third one only proposes what the log can support: fewer real friction rows than the bar, and it writes nothing and says so.

---

## What is measured, so you know what to trust

- **Conformance: 203 of 208 checks**, 28 cases, 23 of 23 skills, Opus 5. Each case runs the real skill against a throwaway copy and scores what it did to the filesystem, not what it said about it.
- **Routing: 100%**, 77 queries × 3 repeats. Including the confusable pairs above.
- **Four checks are open and named** — `corp-os-guide` opens a decision itself instead of handing off, and `corp-os-recall` dropped a load-bearing sensitive fact in one run. Both are in `BACKLOG.md` with what is known.
- **What the harness measures has been wrong three times**, and each is recorded next to what it cost.

Trust the parts that are measured, at the rate they were measured. That is the whole posture, and it applies to this document too.
