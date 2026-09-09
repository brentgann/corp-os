---
name: corp-os-contribute
description: Turns friction already surfaced in a Corp-OS operator's usage — by corp-os-improve, corp-os-audit, or raised directly in conversation — into apply-ready diffs against the corp-os plugin's own source. Reads the plugin's actual SKILL.md files, reference docs, and scripts; never the operator's claim bodies or person records. Use when someone says "write this up for the plugin repo", "give me a diff I can apply upstream", "how would I fix corp-os itself", "turn this into something my other environment can use", or is the person who maintains the corp-os plugin and wants a concrete proposal rather than an anonymized note. Not for changing this OS's own config (use corp-os-configure) and not for the routine, evidence-gated local-improvement pass (use corp-os-improve) — this skill assumes that work, or its equivalent, already happened.
---

# Corp-OS contribute

> **Judgment pass** — the reasoning is the product here. Run it on your best model, and do not economise by skipping the questions it asks.

`corp-os-improve` keeps a packet thin and anonymized because it assumes a stranger maintains the plugin. This skill assumes the opposite: the person running it either maintains corp-os directly or is handing this straight to someone who does. That changes what's worth writing — not a cautious note, an apply-ready diff.

Read `${CLAUDE_PLUGIN_ROOT}/reference/improvement-packet.md` for the config test this skill also uses (Step 1), and for the fallback packet shape in Step 4.

## Pre-flight

Confirm the plugin's own source is actually reachable right now — its `skills/`, `reference/`, and `scripts/` directories, not a memory of what they probably contain. If this environment doesn't have that path, ask for it rather than guessing at file contents; a diff against remembered text is worse than no diff, because it looks authoritative and isn't.

Confirm who this is for. If the person doesn't maintain the plugin and isn't handing this to someone who does, this is the wrong skill — point at `corp-os-improve` instead, whose packet output is built for exactly that case.

## Step 0 — start from something already diagnosed

This skill does not mine `usage/log.md` itself — that's `corp-os-improve`'s job, and re-doing it here duplicates work and drops the run-count discipline that keeps that skill from over-reacting to thin evidence.

Valid starting points:

- A `corp-os-improve` run's `usage/proposals.md` entries or `usage/improvement-packet-*.md`.
- A `corp-os-audit` export.
- Something raised directly in conversation — a bug just hit, a pattern just needed that the shipped model doesn't have.

If none of these exist yet, say so and offer to run `corp-os-improve` or `corp-os-audit` first. Starting from nothing produces guesses, not diffs.

## Step 1 — apply the contribution bar, not the restructuring bar

`corp-os-improve` gates on volume because restructuring someone's live OS on a hunch is the failure mode it guards against. Nothing here touches a live OS, so that bar doesn't transfer. The bar here is **diagnosis, not frequency**: a single occurrence is enough evidence *if* the mechanism is fully traced — exact file, exact lines, a clear reason the same thing would happen to any OS that followed the shipped model as documented, not just this one.

Run the same test `corp-os-improve` already uses (`improvement-packet.md`'s config test), aimed at the plugin instead of the OS: **if this could have been fixed by a setting in this OS's own `config.json`, it isn't a plugin finding.** A config-shape mistake specific to one person's OS (they mis-declared a layer) stays local. A shipped default, script, or reference doc that would produce the same problem for any OS following it as written is what belongs here.

## Step 2 — read the real files, write real diffs

Open the actual current content of every file a proposal touches. Never paraphrase a change or describe it in prose only — write literal before/after blocks against what the file says right now, the same way a pull request would. The plugin evolves independently of any one OS; a diff against a remembered version of a file is exactly the failure mode `raw/`'s append-only discipline exists to prevent, aimed at the wrong corpus.

## Step 3 — one proposal, four parts

For each change:

- **Problem and evidence** — what happened, traced to its mechanism, not just its symptom.
- **The diff** — exact before/after, against the file's real current text.
- **Migration note** — what an OS already running the old shape needs to do.
- **What this doesn't fix** — say plainly if the diff only covers part of the mechanism, or if a cheaper alternative was considered and rejected. A proposal that overstates what it fixes is worse than a narrower one that's honest about its edges.

Rank proposals by how well-diagnosed they are, not by how appealing they sound — the same discipline `corp-os-improve` uses for local fixes, aimed at a different bar (Step 1).

## Step 4 — anonymize only when the audience requires it

When the person maintains the plugin themselves, skip the anonymization ceremony entirely — there's no one to anonymize from, and stripping detail only makes the diff harder to verify. When this skill is invoked on someone else's behalf — surfacing a finding for a *third-party* maintainer neither the operator nor this session has a relationship with — fall back to `improvement-packet.md`'s packet discipline instead: counts and structure, never a claim body, a person record, or a company file's content.

## Step 5 — write it as a standalone file, apply nothing

The deliverable is a portable document meant to leave this OS — not a write to `usage/`, not an edit to `config.json`. Never modify the plugin's own files directly from this skill, even when they're technically reachable. Applying a diff is a separate, deliberate act in whatever environment actually holds the plugin source; this skill's job ends at hand-off.

## Every run ends with

Still close in the OS, briefly — not because the plugin's repo needs it, but because a future session reading `usage/log.md` should be able to tell that this happened and what it produced:

```bash
python3 scripts/log_run.py --skill corp-os-contribute --scope "<what was proposed>" \
    --friction "<where it hurt, or 'none'>" \
    --event "wrote <path to the proposals file>, N proposals"
```

- The proposals file itself, handed to the person.
- A one-line statement of which proposals are ready to apply as-is and which need the maintainer's own judgment first.
