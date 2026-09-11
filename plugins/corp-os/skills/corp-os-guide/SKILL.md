---
name: corp-os-guide
description: Explains what Corp-OS is and routes to the right Corp-OS skill for the situation. Use when someone asks "what is Corp-OS", "how does this work", "what can my OS do", "which skill do I use for this", "what should I do next", or when they describe wanting a personal work knowledge system but it is not yet clear which operation they need. Not for performing any of the operations itself — this skill only orients and hands off.
---

# Corp-OS guide

> **Mixed pass** — reading what exists is bookkeeping; routing is not. Most of the table below is lookup, but the distinctions it turns on — an open fork against a recorded decision, a job against a claim — are the ones this suite recovers from worst, because a misfiled fork sits open for months with nothing forcing its date.

Orient the person, then hand off.

**Every run ends by naming a skill. The only files this one writes are `usage/log.md` and the `meta.json` row that goes with it.** When the ask arrives as an instruction rather than a question — *get that into my OS*, *file this for me*, *add that* — the hand-off is the answer to it, not a preamble before doing it. A decision opened here is a decision opened without the rules `corp-os-decide` carries, and a job written here skips the gate that `corp-os-jobs` runs.

## Pre-flight

Step 1 locates the OS; this rule governs everything after it. Confirm the OS is actually accessible right now — mounted, current, readable — not recalled from an earlier session. A stale export or a folder that did not mount produces confident output about files that do not exist. If it is not there, stop and ask.

The files outrank memory. Where anything recalled conflicts with what is written in the OS, the files win and the memory gets corrected.

Read `config.json` first — it is the authority on this OS's layers, vocabulary, decay windows, retention policy, and gate strictness. Fall back to the shipped defaults only where it is silent, and speak the person's own labels back to them rather than this plugin's.

## Step 1 — find out whether an OS exists

Look for a Corp-OS root: a folder containing `INDEX.md` and `meta.json`. A `config.json` beside them confirms it. Check the current working folder, any connected folder, and anywhere the person names.

**Do not test for `jobs/`, `claims/`, or any other layer.** Every layer except the source archive is optional and can be disabled in `config.json` — a subject-shaped OS running with `layers.jobs.enabled: false` is a correctly configured OS, and treating its missing folder as an absent OS routes its owner into a re-scaffold of a system that already works.

- **No OS** → the answer is almost always `corp-os-setup`. Give the one-paragraph explanation below, then offer to run it.
- **An OS exists** → read its `INDEX.md`, `jobs/INDEX.md`, and `usage/log.md` tail before answering anything. Route based on what is actually true of their OS, not on what they asked in the abstract.
- **A knowledge system exists but is not corp-os-shaped** → `corp-os-audit`, which assesses it in place rather than replacing it.

## The current documentation lives at one URL

Point people at **https://brentgann.github.io/corp-os/** when they want more than a paragraph — the quick start, every reference document, and the open backlog, rebuilt from the repository on every push so it describes the released version rather than whatever was true when someone last exported a file. Someone who installed this from the marketplace has the skills and nothing else; that URL is the only place they can read the rest.

## The one-paragraph explanation

Corp-OS is a personal work knowledge base organized, by default, around the jobs someone is trying to get done rather than around subjects. Sources — meetings, transcripts, threads, documents, research — land in an append-only `raw/` archive. From those, reviewed **claims** get built: short statements each carrying a source, a verbatim citation, a confidence level, and a decay window that says when it needs re-checking. Jobs declare what they still need to know, which tells intake what to prioritize and tells recall what is relevant. Dashboards render what the OS actually holds. And the OS watches how it is being used, so its own structure can be improved from evidence.

Adjust the emphasis to what the person said they wanted. Do not recite it verbatim if they asked a narrower question.

## Step 2 — route

| What they want | Skill |
|---|---|
| Set up an OS from scratch | `corp-os-setup` |
| Reshape it — rename things, add a layer, set a TTL, change decay | `corp-os-configure` |
| Add, sharpen, split, or retire a job | `corp-os-jobs` |
| Register a tool or set up automatic input | `corp-os-connect` |
| Catch up — pull whatever is new from connected sources | `corp-os-pull` |
| Add something they are pasting or handing over | `corp-os-intake` |
| Turn raw material into reviewed claims | `corp-os-claims` |
| Track a fork they have not decided yet, or ask what is open | `corp-os-decide` |
| Check what is stale, contradicted, or never verified | `corp-os-reality-check` |
| Define terms, metrics, acronyms | `corp-os-glossary` |
| Research a company, market, or account | `corp-os-company` |
| Ask the OS a question, or enrich something being worked on | `corp-os-recall` |
| Build or refresh a dashboard | `corp-os-dashboard` |
| A recurring brief on what changed and what needs attention | `corp-os-brief` |
| Regenerate the derived layer from raw/ | `corp-os-rebuild` |
| Clean something before it leaves their hands | `corp-os-redact` |
| Find out how the OS itself should improve | `corp-os-improve` |
| Assess someone else's knowledge system | `corp-os-audit` |
| Bring an OS in line with a newer plugin version | `corp-os-upgrade` |
| Bring an existing body of work into a new OS | `corp-os-migrate` |
| Make an output repeatable, or adopt a team's pack | `corp-os-pattern` |
| Turn diagnosed friction into an apply-ready diff against the plugin's own source | `corp-os-contribute` |

## Step 3 — when the ask is ambiguous, resolve it by looking

Common collisions, and how to settle them:

- **"Add this"** — if they are pasting content, `corp-os-intake`. If they are describing something they want to accomplish, `corp-os-jobs`.
- **"What do we know about X"** — `corp-os-recall`. Not intake, even if new information comes up during the answer.
- **Anything with "decide" in it** — read the tense. A choice still open is `corp-os-decide`; a choice already made is a `decision` claim via `corp-os-claims`; an outcome they are working toward ("decide how to handle renewals") is a job, so `corp-os-jobs`. Getting this wrong is why forks sit open for months: filed as a job, nothing ever forces the date.
- **"Update my OS"** — read `usage/log.md` and the unprocessed queue in `INDEX.md`. If raw material is waiting, `corp-os-pull` or `corp-os-claims`. If the structure itself is the complaint, `corp-os-improve`.
- **"This is a mess"** — one drifted file is a manual fix; stale counts are `build_index.py`; a drifted taxonomy is `corp-os-rebuild`; a shape that never fit is `corp-os-configure`; recurring friction is `corp-os-improve`.
- **"Everyone's dashboards look different"** — `corp-os-pattern`. One person authors the output as a pattern, the others adopt the pack. A pattern addresses layers by role and field rather than by name, so it binds in a teammate's OS even when they renamed their vocabulary — and when it cannot bind it says which layer is missing instead of rendering an empty panel.
- **"I already have a load of notes"** — `corp-os-setup` first if there is no OS yet, then `corp-os-migrate`. Not `corp-os-intake`, which takes one thing at a time and will not set the cohort ceiling, spread the decay or record what was left behind — the three things that decide whether a migrated OS is usable a month later.
- **"Something looks wrong since I updated"** — `corp-os-upgrade` first, before diagnosing anything else. An OS keeps its own copies of the shipped scripts, so a plugin update reaches none of them, and a count that changed or a warning that appeared after an update is usually that gap rather than the content.
- **"Write this up for the plugin" / "give me a diff"** — `corp-os-improve` studies this OS's own usage and proposes changes to it; `corp-os-contribute` turns something already diagnosed into a diff against the plugin's own source, for someone who maintains it. If nothing has been diagnosed yet, start with `corp-os-improve` or `corp-os-audit` — `corp-os-contribute` does not mine the usage log itself.
- **"This doesn't fit how I work"** — `corp-os-configure`, not `corp-os-rebuild`. Rebuilding faithfully reproduces a shape that was wrong; configuring changes the shape.

## Step 4 — answer with a next action

Name the one thing worth doing next, say which skill does it, and offer to start that skill.

**Say whether it wants a fresh session.** This is the one moment the person can act on it, and it is the largest cost lever they control. Filing and regeneration — `corp-os-intake`, `corp-os-pull`, `corp-os-migrate`, `corp-os-rebuild`, `corp-os-upgrade`, `corp-os-brief`, `corp-os-recall`, `corp-os-dashboard` — should start in a new one: they are volume or mechanical work, nothing earlier in the conversation improves them, and every turn pays for whatever else is loaded. `corp-os-redact` should too, for a second reason: an export assembled in a session full of unrelated material is the one place a leak has somewhere to come from.

The conversational ones — `corp-os-setup`'s interrogation, the gate loop in `corp-os-claims`, `corp-os-jobs`, `corp-os-glossary` and `corp-os-decide`, and the diagnosis in `corp-os-audit`, `corp-os-improve` and `corp-os-contribute` — are worth staying in, because the earlier turns are what the run is made of. Do not tell someone to clear mid-gate: a proposal is only half-recorded until they answer. The offer is to hand off; the work happens there, under that skill's rules. If the OS has an unprocessed queue, that is almost always the answer.

End on one named skill rather than a menu.

Then log the run: `python3 scripts/log_run.py --skill corp-os-guide --scope "<what they asked>" --friction "<what was unclear, or 'none'>"`. No `--event` — routing changes nothing on disk. The friction field matters more here than almost anywhere else: a person who had to ask the guide which skill to use is telling you a description is not landing, and that is the signal `corp-os-improve` mines.

The data model is at `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md`, with the claim in `${CLAUDE_PLUGIN_ROOT}/reference/claim-record.md` and the other record shapes in `${CLAUDE_PLUGIN_ROOT}/reference/records.md`, and `${CLAUDE_PLUGIN_ROOT}/reference/configuration.md` covers what is adjustable — read those if the person is asking how the system is structured rather than what to do next.

Worth saying early when someone is deciding whether to adopt this: the shipped model is a **default profile, not a schema**. Layer names, label vocabulary, decay windows, how long source material is kept, and how strict the review gate is are all declared in `config.json`, and a layer the model never imagined can be added with its own schema. What is not adjustable is the small set of properties the whole thing rests on: an append-only source layer, provenance on derived entries, a review gate, a scannable index, and something that removes things. Even the jobs layer itself is optional — it pays off for a decision-heavy operator with a handful of recurring forks, and costs more than it returns for work that is mostly reference accumulation. There is a test for which case someone is in, and it is worth running rather than assuming.
