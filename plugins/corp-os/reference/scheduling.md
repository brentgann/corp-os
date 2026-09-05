# Scheduling

Reference for every skill that offers to set up a recurring run — `corp-os-brief`, `corp-os-connect`, `corp-os-dashboard`, `corp-os-reality-check`, and `corp-os-decide`.

## Why this file exists

Several skills offer to schedule something and none of them used to say by what mechanism. That is a worse gap than it looks, because **the common failure is silent**: a schedule created with an in-process scheduler lives inside the session that created it and dies with it. Nothing errors. The person is told their brief will arrive on Monday, and it never does, and they find out weeks later when they notice they have not been reading it.

A recurring brief plus a recurring pull is the minimum viable operating rhythm for a low-upkeep OS, and it is the specific fix for the person whose last knowledge system died of neglect. Getting it silently wrong is worse than not offering it.

## The rule

**Use the host's durable scheduler — the one whose schedules survive the session that created them — and confirm which one that is before promising a cadence.**

The mechanism differs by environment and changes over time, so this file does not name a tool. What it names is the test:

1. **Enumerate what this environment actually offers.** The same rule as `corp-os-connect` Step 0: the environment knows its own inventory better than the person does, and better than any list written months ago.
2. **Ask of each candidate: does a schedule made here survive this session ending?** If the answer is no, or unclear, it is not the one. Scheduling tools that run inside the current process are for work within a single run, not for a weekly brief.
3. **Prefer the mechanism whose runs are visible to the person** — something they can list, edit, and cancel without asking an agent. A schedule only an agent can see is one nobody audits.
4. **If nothing durable is available, say so plainly** and offer the honest alternative: a calendar reminder that prompts them to run the skill. That is a worse mechanism and a real one, which beats a better mechanism that does not fire.

## What a scheduled run needs to carry

A scheduled run starts with no memory of the conversation that created it, so the instruction it fires has to stand alone:

- **Where the OS is.** An absolute path, not "the usual folder."
- **What to do**, named as the skill plus its scope: "run the weekly brief over everything since the last one."
- **What to do when the OS is not reachable.** Pre-flight applies to scheduled runs exactly as it does to interactive ones, and it matters more: nobody is watching. Say plainly that it should report the failure rather than work from memory of what the OS probably contains.

## Cadence

Match the person's honest upkeep budget from setup, not their aspirational one. Two schedules is usually the whole rhythm:

- A **pull** at the cadence of the fastest-moving connected source.
- A **brief** weekly, or on the weekday morning they actually read things.

A staleness sweep is better offered as a small recurring pass over the past-decay bucket than as a quarterly event. One that resolves ten items monthly keeps an OS honest; one that surfaces two hundred once a year is an event nobody repeats.

**Ask before scheduling anything.** A recurring job someone did not agree to is a notification they will learn to ignore, which costs more than it gave.
