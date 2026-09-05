# The setup interrogation

The question bank for `corp-os-setup`. Not a form to read out. Nine areas, asked conversationally, in this order, with the answers to each shaping the questions in the next.

**Rules for running it:**

- Ask in small batches (two to four questions), never all nine areas at once.
- Reflect back what was heard before moving on. A wrong reading caught in area 2 is cheap; caught in area 9 it has already shaped the whole scaffold.
- Skip anything already answered. If someone opens with "I'm a recruiter drowning in candidate call notes," areas 1 and 4 are largely done — confirm rather than re-ask.
- Push once when an answer is abstract, then accept it. "Get better at my job" is not a job statement; ask what this week would look like if it were going well. If the second answer is still abstract, write it down as-is and mark the job `readiness: low` — an honest vague job beats a fabricated crisp one.
- Never supply domain content. Supply shapes. "A job needs a definition of done — what's yours?" not "your job is probably pipeline coverage."

---

## Area 1 — Role and mandate

- What's your role, and what are you actually accountable for? (These differ more often than not — ask for both if the first answer is just a title.)
- Who do you answer to, and what do they judge you on?
- Who depends on your output?
- How long have you been in this seat? (A new-in-role operator needs the OS pointed at orientation; a five-year veteran needs it pointed at leverage.)

## Area 2 — Intent for the OS

- What made you want to build this? What's the thing that keeps going wrong?
- Six months from now, what would make you say this was worth it?
- What have you tried before — a notes app, a wiki, a spreadsheet — and specifically why did it fall over?

That last question is the highest-yield one in the whole interrogation. The failure mode of the last system predicts the failure mode of this one. Someone whose Notion died of neglect needs low-friction intake and a scheduled brief; someone whose wiki died of sprawl needs aggressive pruning and decay windows.

## Area 3 — Jobs to be done

The core of the setup. Aim to leave with three to five jobs, not fifteen.

- Walk me through a normal week. What do you actually spend it doing?
- What decisions do you get asked to make, and which ones do you make with less information than you'd like?
- What do you have to re-figure-out every time, that you wish you just knew?
- What's the recurring thing you dread because you're never quite prepared for it?

For each candidate job, get it into the form `When <situation>, I want to <motivation>, so I can <outcome>` — then ask the two questions that make it real:

- How would you know this was handled well? (definition of done)
- What don't you know today that you'd need to know? (the evidence list, which becomes the intake priority)

See `jtbd-patterns.md` for how job statements tend to look across roles, and for the common malformed shapes to correct.

## Area 4 — What data actually earns its keep

- Of everything crossing your desk, what do you go back and look for again?
- What do you keep having to ask someone else for?
- What gets captured religiously and never once re-read? (Name it, then agree not to ingest it. Declining a source at setup is a real decision, not a gap.)
- Is there something you'd love to have but currently have no way to see?

## Area 5 — Input paths

- How does information reach you today — meetings, chat, email, docs, dashboards, hallway?
- Which of those do you want flowing in automatically, and which would you rather hand over deliberately?
- Where do you write things down right now, and should the OS read from there or replace it?
- How much per-week upkeep are you honestly willing to spend? (Under 15 minutes means recurring pulls plus a scheduled brief and almost no manual curation; an hour-plus supports a real review cadence. Design to the honest answer, not the aspirational one.)

## Area 6 — Tools and protocols

For each source named in area 5, establish:

- What's the tool?
- How does it connect — an installed MCP connector, a direct API with a token, a browser session, an export file, or copy-paste?
- Is it already connected in this environment? (Check. Don't ask the person to guess at what tools are available — enumerate what's actually there and confirm against it.)
- What is this source blind to? (Goes straight into the connector registry's blind-spots field.)
- If it isn't connected and could be: is it worth connecting now, or is manual fine for a month?

Record answers even for tools that are not connected — a `not-connected` entry with a note on why is a more useful artifact than an absent one, because it stops the same question being re-litigated every month.

## Area 7 — Company and market context

- Where do you work, and what does the company actually sell?
- Who are the users, and are they the same people as the buyers?
- What's the current company situation — growing, flat, raising, post-raise, being acquired, turning around?
- Who do you lose to?
- What company facts do you find yourself explaining or looking up repeatedly?

Do not research yet. Collect the anchor facts and the name, then hand off to `corp-os-company` after setup finishes, so the web research is grounded in what the person already knows rather than displacing it.

## Area 8 — Output and design

- When this thing produces something — a brief, a dashboard, a summary — who else sees it?
- Do you have a design system, brand guide, or a design skill that outputs should follow? (If a design skill is installed in this environment, name it and ask whether to bind it.)
- Dashboards: private to you, or shared with a team?
- Do you want a recurring brief, and at what cadence?

## Area 9 — Sensitivity and boundaries

- Will anything in here be personnel-adjacent, comp-related, or otherwise sensitive?
- Does any of it belong to a customer or under an NDA?
- Is there any chance parts of this get shared into a team wiki later?

If the answer to the third question is anything but a firm no, turn on the sensitivity tag from day one. Retrofitting sensitivity across 200 claims is miserable; carrying an unused field is free.

---

## What setup must not do

- Do not scaffold categories nobody asked for. `glossary.md` and `company/` are optional and get created on request; a person or topic layer is a declared layer with its own schema, created only when the answers here call for one.
- Do not create more than five jobs. A person who names twelve is describing tasks; help them cluster.
- Do not pull any data during setup. Setup builds the container and the first job records. Intake is a separate, deliberate first run.
- Do not skip writing the OS's own `README.md`. A scaffold whose conventions live only in this plugin breaks the moment someone opens the folder without the plugin loaded.
