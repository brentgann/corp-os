# Build brief: Corp-OS on brentgann.io

For the agent working on the site. Everything below is either an instruction to you or finished copy to place. Copy blocks are fenced with four backticks; the fence is not part of the content.

Two deliverables plus some small site-level edits:

1. **A dedicated page** at `/corp-os/`, the permanent reference. §4.
2. **A blog post** that tells the story and links to the page. §5.
3. **Site-level changes** so people can find both. §2.

The site is Hugo. Match the existing content structure rather than inventing one: look at a current page and a current post, copy their front matter shape, and only then use the front matter I have sketched below as a starting point for the fields it does not cover.

---

## 1. Ground rules — read before writing anything

**Every number and claim in the copy is real and checkable.** They come from an actual build with an actual eval suite. Do not round them, do not make them nicer, and do not add any that are not in this brief. If a sentence needs a number I have not given you, write the sentence without one.

**The figures from "a real corpus" are anonymized.** 836 claims, 599 of them, 215 sources over four months: these come from an audit of a real knowledge system, reported without identifying it. Never attach a company name, a person, or an employer to any of them. Never imply they came from a named client.

**Do not link the Claude artifacts.** They are private URLs and would 404 for a visitor. Use the exported images in §3 instead.

**Do not write marketing superlatives.** No "revolutionary", no "game-changing", no "powerful". The copy below works because it names specific failures and what they cost. Adding adjectives to that makes it weaker, not stronger.

**House style, which differs from the repo's own prose:**

- No em dashes. Use a colon, a comma, parentheses, or a full stop. The GitHub repo is full of em dashes; the site is not.
- No filler openers. Not "In today's world", not "We all know that".
- Conversational directness. Short sentences are fine. First person, because it is his site and he built it.
- No emoji.

**Version numbers go in exactly one place.** The page states v0.14.1 and a set of counts. Put those in a single clearly-commented block near the bottom (§4, "The facts block") so there is one thing to update, not eight sentences to hunt through. This is a lesson from the project itself: a fact retyped in a second place goes stale, and it has already happened five times in this repo.

---

## 2. Site-level changes

**Nav.** Add `Corp-OS` to the primary navigation, after Portfolio and before About. If the nav is already crowded, put it under Portfolio instead and skip the top-level entry.

**Portfolio card.** Add an entry to the portfolio grid linking to `/corp-os/`, not to GitHub. Card copy:

````
**Corp-OS**

A portable personal work OS, shipped as a Claude plugin: 23 skills that operate on a folder of markdown files. Built across a long series of releases with an eval suite that kept finding things reading never would, including one release where the tests found a missing review gate that had been absent since the first version.
````

**Homepage.** If there is a "what I'm working on" or recent-work area, one line:

````
Currently building [Corp-OS](/corp-os/), a personal work OS as a Claude plugin, and writing down what the evals keep finding.
````

**Tags.** Use the site's existing tag vocabulary. If new tags are warranted, keep them to the ones the site would plausibly reuse: `AI`, `Product`, `Tooling`, `Knowledge Management`. Do not create a one-off tag that will only ever hold this page.

---

## 3. Assets

The images are on the machine at `~/Development/corp-os/docs/img/`. **They are gitignored, so a fresh clone of that repo will not have them.** Copy them from that folder directly.

Put them in the site under `static/img/corp-os/` (or wherever the site's convention puts images) and reference them at the matching URL.

| File | Use | Alt text |
|---|---|---|
| `01-marketecture-wide.png` | The main diagram on the page. Place after the invariants section. | `Corp-OS architecture: material enters from registered sources into an append-only raw layer, passes a review gate, becomes a derived layer of claims and jobs, is reached through a scannable index, and leaves through a redaction boundary.` |
| `02-using-it-wide.png` | The flow diagram. Place in "A day with it". | `The Corp-OS operator loop: capture what was said, turn it into claims behind a review gate, ask questions or run a brief, then sweep for what has gone stale.` |
| `06-the-five-invariants.png` | Optional, in the invariants section if the prose feels thin without it. | `The five properties of Corp-OS that are not configurable: an append-only source layer, provenance, a review gate, a scannable index, and something that removes things.` |
| `00-full-page.png` | Do not use. It is 14,000px tall and exists as a reference copy. | |

Both diagrams are wide. Give them full content width, and let them open to full size on click if the theme supports it. On mobile they will be unreadable inline no matter what you do, so make sure tapping opens the full image.

Two PDFs also exist at `~/Development/corp-os/docs/` (`architecture-diagram.pdf` and `skill-map.pdf`) if a download link is wanted. Optional, and only if the theme has a clean way to present one.

---

## 4. The page: `/corp-os/`

Front matter starting point. Replace with the site's actual fields where they differ:

````
---
title: "Corp-OS"
description: "A portable personal work OS, built as a Claude plugin, and what its eval suite kept finding."
date: 2026-09-09
draft: false
type: "page"
---
````

Page body follows. This is finished copy. Edit for the site's heading conventions and for anything that reads wrong in its actual template, but do not rewrite the substance or soften the specifics.

````
I built a personal work OS, then spent a long run of releases trying to break it. The breaking is the interesting part.

## What it is

Corp-OS is a Claude plugin. It is 23 skills that operate on a folder of markdown files on your own disk. The folder is the knowledge base. The skills are what put things into it, turn them into statements you can cite, get them back out with their provenance attached, and take things out again when they stop being true.

There is no database, no server, and no account. If every part of this disappeared tomorrow you would still have a folder of markdown you could read with `cat` in ten years, which is the only durability guarantee that has ever actually held.

## The problem it is built around

Most personal knowledge systems are organized by subject: a folder per topic, a note per person. They only ever grow. Nothing in them ever expires. After a few months nobody trusts them enough to look, and the reason that happens is worth being precise about.

It is not that the notes are wrong. It is that you cannot tell which ones are. Every individual entry still looks reasonable. A pricing note from March reads exactly like a pricing note from last week, and the system has no opinion about which one you should believe. So you stop believing any of it, and the thing you built to save time becomes a place you visit to confirm what you already remembered.

The fix is not better note-taking. It is a system that knows when it is out of date and says so.

## Five things that are not configurable

Almost everything about Corp-OS is declared rather than assumed. Layer names, label vocabularies, how long things stay fresh, how strict the review step is, even the organizing idea itself: all of it lives in a config file that every skill reads before it does anything, and all of it is meant to be changed.

Five properties are not, because everything else rests on them.

1. **An append-only source layer.** Raw material is written once and never edited. Existing there means something was *said*, not that it is true.
2. **Provenance on anything derived from it.** Source, date, a verbatim quote, and a confidence level. A paraphrase in the citation field defeats the purpose, because the next reader cannot tell how much of the claim is the source and how much is the summarizer.
3. **A review gate in front of anything treated as knowledge.** Nothing is promoted without a person confirming it, and the proposal is written to disk before it is shown to you rather than living in a chat window that closes.
4. **An index that can be scanned** instead of a corpus that has to be loaded. One line per entry, always a descriptor, never a bare link.
5. **Something that removes things.** Every entry carries a window after which it needs re-checking, and there is a skill whose whole job is working that queue.

The fifth is the one most systems lack, and it is the one that decides whether yours is still worth opening in two years.

<!-- image: 01-marketecture-wide.png -->

## A day with it

Something gets said in a meeting. It goes into the raw layer, either pulled from a registered source or handed over directly, and it goes in as it was said rather than as a summary. Later you work the queue: each candidate becomes a proposal with its kind, its confidence, and a verbatim citation attached, and you confirm, decline, defer, or modify. Declines are kept, because the record of what you deliberately chose not to know is frequently the most useful thing in the file.

Then you get value back out. A question gets an answer with citations. A recurring brief says what moved, what needs a decision, and what went stale. A dashboard is a page you return to, built by a script that recounts what is actually on disk rather than by a model writing numbers into markup.

Once a month or so, you sweep. Claims past their window, claims never verified, contradictions, and assumptions that have quietly been promoted to facts.

<!-- image: 02-using-it-wide.png -->

## What building it actually taught me

This is the part I would want to read.

### Past a certain point, more instruction stops buying reliability

The redaction skill is supposed to write two files: the cleaned copy and a private log of exactly what was removed. Across five test runs it produced that log under four different names, and once not at all. The instruction to write it was present, concrete, explained, and had already been strengthened twice.

The retention-delete sequence was the same story. It held at 67% after two instruction passes, the second of which said *never edit the original into a tombstone* in as many words, and one run in three still did exactly that.

So the step stopped being something to remember. A script now writes both files together and refuses to write one without the other; another performs the delete sequence in the right order. With the script, that 67% became 8 out of 8.

The rule that came out of it, which I now apply everywhere: **a step that has to happen every time, that nothing else will catch if it is skipped, belongs in code rather than in an instruction.** Eleven scripts exist for that reason. None of them exercises judgment. That stays with the person.

### A model that only ever confirms itself is not measuring anything

Corp-OS organizes work around jobs to be done, which is its best idea and is wrong for some people. It pays off when the same questions get re-asked and the same evidence re-gathered. It costs more than it returns when the work is mostly reference accumulation.

So the audit skill runs an actual test before recommending it: cluster the existing material into candidate jobs without looking at the subject taxonomy, then compare. If the clusters just reproduce the taxonomy that already exists, the material is subject-shaped, and the audit says to leave the jobs layer off. A model that cannot argue against its own best idea is not giving you information.

### The tests found things that reading never would

There are three harnesses at three different costs, because a loop you can run in a minute is a loop you stay inside and a thirty-minute one is a loop you leave.

The first real conformance run found the intake skill doing four of its five required outputs, four runs out of four, with the fifth missing every time. It found a four-release-old contradiction where the spec said raw files are never edited while three skills instructed editing them, which nobody had noticed because it gets read in whichever direction you arrive from.

Then it found something worse about itself. Every conformance figure before v0.11.0 was void: the harness auto-approved file edits and nothing else, so not one shipped script had ever actually executed inside a test run. The file-level results were real, but what produced them was never measured, because a model told to run a script and blocked from doing so writes the result by hand. That cost six runs and three instruction passes chasing a failure that was the instrument the whole time.

The best one came last. A test written to check something else entirely found that the skill whose whole job is removing stale knowledge had never had a review gate, in any release, going back to the first. Three of four runs rewrote the derived layer with no proposal behind it, one of them across fourteen files. Nobody reading it had caught that, in any release. One run of a test did.

### Publish what still fails

One hand-off in the suite lands 2 times in 5. It is on the record at that number, in the docs, rather than reworded a fourth time until it sounds fixed. A wording pass meant to improve it measured 0 out of 2 and got reverted, because prose that does not move the number is churn.

A test that has never been wrong about what it measures has not been looked at hard enough, so when an assertion turned out to be wrong about the skill rather than the other way around, it got corrected on the record with the evidence attached. That happened eight times.

### One field carrying three questions makes a specific thing invisible

Confidence started as a single value, and it was quietly answering three unrelated questions at once: how faithful is the recording, how many independent sources exist, and is this contested.

Measured in a real corpus: 599 of 836 entries sat one rung below the top because they were single-source summaries. Their full transcripts were still fetchable through the same connector that produced the summaries. One call. Zero had taken it, because a ceiling that is elective looked exactly like a ceiling that is permanent, so it got treated as permanent.

Splitting the medium out into its own field turned that into a sortable list of entries that are one call away from being stronger. Not a list of what is weak. A list of what is cheap to fix.

### Sensitivity is two questions, and treating it as one made the system wrong

There is what must not leave, and there is whether the system can reason correctly without it. Those are different, and collapsing them into a single flag meant quarantining everything sensitive, which sounds safe and is not. When sensitive material is load-bearing, removing it from the working set does not produce a gap. It produces a confidently wrong answer with nothing in it to signal the omission.

Load-bearing sensitive material now stays where the system can see it, marked, and gets stripped at the boundary where things actually leave. That boundary is also the only place confidentiality was ever really enforced.

### Anything stating a fact that is already true somewhere else will go stale

This project has caught that same defect five times: a file saying "both shipped scripts" three releases after there were four, a hard-coded version string that went stale within one release, a version recorded in six files with six different values, a layer counted wrong for five releases, and two README files stating a skill count that was four short.

So the reference page listing every skill is generated from the plugin at build time, and the build fails if it has drifted. The stated counts in the prose are checked against the directories on disk. The only thing declared by hand is the judgment a machine cannot derive, and the generator refuses to run until a person has supplied it.

## Who it is wrong for

If your work is mostly reference accumulation, or is organized around long-lived subject areas that genuinely do not change, this will cost more than it returns and the audit will tell you so.

It assumes one operator. Sharing is an export event, not a mode: there is a step that produces a cleaned copy along with a private log of exactly what came out. That is deliberate, but it means this is not a team wiki and does not want to become one.

And the setup interrogation takes fifteen to twenty minutes. That is the deliverable as much as the folder is. A scaffold built without it produces a generic notebook that gets abandoned in a month, which is the thing this exists to avoid.

## Try it

Install it as a Claude plugin:

```
/plugin marketplace add brentgann/corp-os
/plugin install corp-os@brentgann
```

Then ask for Corp-OS setup, or run `/corp-os`.

Updating has two halves, and doing the first does nothing to the second. `/plugin marketplace update brentgann` replaces the skills. Asking for `corp-os-upgrade` brings your own folder in line with them, because every Corp-OS carries its own copies of the shipped scripts so that it keeps working when the plugin is not loaded.

The source, the architecture record with every decision and its reasoning, and the eval results are all on [GitHub](https://github.com/brentgann/corp-os). MIT licensed.

<!-- FACTS BLOCK. One place to update. Current as of v0.14.1, September 2026. -->

*Corp-OS v0.14.1: 23 skills, 8 slash commands, 11 scripts, 10 reference specs, 5 invariants. Routing accuracy 100% across 77 queries at 3 repeats. Conformance 114 of 122 checks across 19 cases and 15 skills, at one repeat, so a baseline rather than a rate. 8 skills still have no conformance case.*
````

---

## 5. The blog post

Shorter, story-shaped, and it points at the page rather than repeating it. Front matter starting point:

````
---
title: "The test found a missing gate that every release of reading had missed"
description: "What building a personal work OS taught me about the difference between writing an instruction and enforcing one."
date: 2026-09-09
draft: false
tags: ["AI", "Product", "Tooling"]
---
````

Post body:

````
I spent a few months building a personal work OS as a Claude plugin, and the most useful thing that came out of it was not the OS.

The thing I keep coming back to is this. Months in, I wrote a test for a feature I had just added. The test was checking whether a promotion backlog got reported the right way. It failed, but not on the thing I was checking. It failed because the skill under test, whose entire job is finding and removing stale knowledge, had been rewriting the knowledge base with no review step at all. Not in that release. In every release, going back to the first one.

Three of four runs did it. One of them rewrote fourteen files. I had read that skill dozens of times. I had reviewed it, edited it, and shipped it in every release since the first one. A single test run found in ten minutes what reading had missed for months.

That is the whole argument for measuring, and I would not have believed it as strongly if it had happened to somebody else's code.

There is a related lesson that took longer to accept. Early on, a skill that was supposed to write two files kept writing one. I made the instruction more explicit. It still failed. I made it more explicit again and explained why it mattered, in the imperative, at the top of the step. Across five runs it produced the missing file under four different names, and once not at all.

Another skill was supposed to never do a specific destructive thing, and the instruction literally said never do this specific destructive thing. One run in three did it anyway.

So I stopped writing instructions and wrote a script. The script writes both files or neither. The 67% became 8 out of 8. The rule I took from it is one I now use everywhere: **a step that has to happen every time, that nothing else will catch if it is skipped, belongs in code rather than in a prompt.** Judgment stays with the model and with the person. Bookkeeping does not.

I also learned to publish the numbers that are still bad. One hand-off in the suite works 2 times in 5. It is documented at 2 out of 5 rather than reworded a fourth time until it sounds solved. I tried the rewording. It measured 0 out of 2 and I reverted it, because prose that does not move the number is churn dressed up as progress.

If any of that is interesting, the full thing is written up at [Corp-OS](/corp-os/): what it is, how it is put together, and the rest of what the evals found. The code and the architecture record are on [GitHub](https://github.com/brentgann/corp-os).
````

---

## 6. If you need to trim

The page is long on purpose, but if the template cannot carry it:

- **Keep** the five invariants, the marketecture image, and "Past a certain point, more instruction stops buying reliability". Those three do the work.
- **Cut first** the "one field carrying three questions" and "sensitivity is two questions" subsections. They are the most specialized.
- **Never cut** "Who it is wrong for". A page that only says what something is good at reads as a pitch, and the honesty is the point of publishing this at all.

## 7. Keeping it current

The version and the counts will move. When they do, the only things that need editing are the facts block at the bottom of the page and the count in the portfolio card. Everything else in the copy is written to stay true across releases, which is deliberate: the numbers that change are quarantined in one place on purpose.

The install commands are stable. The marketplace name (`brentgann`) and plugin name (`corp-os`) come from manifests in the repo and will not change.
