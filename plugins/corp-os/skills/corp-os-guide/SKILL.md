---
name: corp-os-guide
description: Explains what Corp-OS is and routes to the right Corp-OS skill for the situation. Use when someone asks "what is Corp-OS", "how does this work", "what can my OS do", "which skill do I use for this", "what should I do next", or when they describe wanting a personal work knowledge system but it is not yet clear which operation they need. Not for performing any of the operations itself — this skill only orients and hands off.
---

# Corp-OS guide

Orient the person, then hand off. This skill never does the work itself.

## Step 1 — find out whether an OS exists

Confirm it is actually accessible right now, not recalled from an earlier session. And note for every skill that follows: the OS's files outrank memory of past sessions.

Look for a Corp-OS root: a folder containing `INDEX.md`, `meta.json`, and `jobs/`. Check the current working folder, any connected folder, and anywhere the person names.

- **No OS** → the answer is almost always `corp-os-setup`. Give the one-paragraph explanation below, then offer to run it.
- **An OS exists** → read its `INDEX.md`, `jobs/INDEX.md`, and `usage/log.md` tail before answering anything. Route based on what is actually true of their OS, not on what they asked in the abstract.
- **A knowledge system exists but is not corp-os-shaped** → `corp-os-audit`, which assesses it in place rather than replacing it.

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
| Check what is stale, contradicted, or never verified | `corp-os-reality-check` |
| Define terms, metrics, acronyms | `corp-os-glossary` |
| Research a company, market, or account | `corp-os-company` |
| Ask the OS a question, or enrich something being worked on | `corp-os-recall` |
| Build or refresh a dashboard | `corp-os-dashboard` |
| A recurring brief on what changed and what needs attention | `corp-os-brief` |
| Regenerate the derived layer from raw/ | `corp-os-rebuild` |
| Clean something before it leaves their hands | `corp-os-redact` |
| Find out how the OS itself should improve | `improve-corp-os` |
| Assess someone else's knowledge system | `corp-os-audit` |

## Step 3 — when the ask is ambiguous, resolve it by looking

Common collisions, and how to settle them:

- **"Add this"** — if they are pasting content, `corp-os-intake`. If they are describing something they want to accomplish, `corp-os-jobs`.
- **"What do we know about X"** — `corp-os-recall`. Not intake, even if new information comes up during the answer.
- **"Update my OS"** — read `usage/log.md` and the unprocessed queue in `INDEX.md`. If raw material is waiting, `corp-os-pull` or `corp-os-claims`. If the structure itself is the complaint, `improve-corp-os`.
- **"This is a mess"** — one drifted file is a manual fix; stale counts are `build_index.py`; a drifted taxonomy is `corp-os-rebuild`; a shape that never fit is `corp-os-configure`; recurring friction is `improve-corp-os`.
- **"This doesn't fit how I work"** — `corp-os-configure`, not `corp-os-rebuild`. Rebuilding faithfully reproduces a shape that was wrong; configuring changes the shape.

## Step 4 — answer with a next action

Never end on a menu. Name the one thing worth doing next and offer to do it. If the OS has an unprocessed queue, that is almost always the answer.

The full data model is at `${CLAUDE_PLUGIN_ROOT}/reference/data-model.md`, and `${CLAUDE_PLUGIN_ROOT}/reference/configuration.md` covers what is adjustable — read those if the person is asking how the system is structured rather than what to do next.

Worth saying early when someone is deciding whether to adopt this: the shipped model is a **default profile, not a schema**. Layer names, label vocabulary, decay windows, how long source material is kept, and how strict the review gate is are all declared in `config.json`, and a layer the model never imagined can be added with its own schema. What is not adjustable is the small set of properties the whole thing rests on: an append-only source layer, provenance on derived entries, a review gate, a scannable index, and something that removes things. Even the jobs layer itself is optional — it pays off for a decision-heavy operator with a handful of recurring forks, and costs more than it returns for work that is mostly reference accumulation. There is a test for which case someone is in, and it is worth running rather than assuming.
