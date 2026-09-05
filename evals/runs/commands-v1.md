# Commands

Model `claude-opus-5` · 23 cases × 3 · 8 commands

**100% reached the intended skill**

## Roster

- /corp-os-brief: Run the recurring Corp-OS brief — what moved, what needs a decision, what went stale
- /corp-os-capture: File something into your Corp-OS — a transcript, a thread, a document, or a note
- /corp-os-catchup: Pull what is new from your connected sources and see what moved
- /corp-os-check: Sweep your OS for what has gone stale, contradicted itself, or was never verified
- /corp-os-open: See the decisions you have open — what is past its date, and what is blocked on whom
- /corp-os-recall: Ask your Corp-OS a question, or fold what it knows into what you are working on
- /corp-os-share: Make something safe to send — a cleaned copy, plus a private record of what came out
- /corp-os: Open Corp-OS — explains the system, finds your OS, and routes to the right operation

## First action, as reported

The line worth reading. A command can reach the right skill and still open on the wrong move.

- **guide-noargs** — Locate their Corp-OS on disk and read its index/state.
- **guide-args** — Sweep the OS for stale, unverified, and contradicted claims, oldest first.
- **capture-args** — Append Wren's verbatim note to the raw layer, timestamped and tagged decision/ownership.
- **capture-noargs** — Ask what they're filing — paste the transcript, thread, doc, or note.
- **recall-args** — Scan the OS for Northwind — contract, decisions, threads — then answer with provenance.
- **recall-noargs** — Ask what they want recalled — no arguments given, so scan nothing yet.
- **brief-noargs** — Read meta.json for the last brief timestamp; if none, ask for a window.
- **brief-args** — Read meta.json, then scan sources dated 2026-08-22 onward for movement.
- **catchup-noargs** — Read each connected source's recorded cutoff, then pull everything since.
- **catchup-args** — Pull only meeting-notes sources, window scoped to Monday forward.
- **open-noargs** — Load the open decision forks and sort by past-due date first.
- **open-args** — Open the mid-market pricing fork's record; read owner, decide_by, and reversibility window.
- **check-noargs** — Load the OS index and pull claims with the highest cost-of-being-wrong.
- **check-args** — Pull every pricing claim from the OS, ordered by cost of being wrong.
- **share-args** — Set external threshold — board advisor is outside the company.
- **share-noargs** — Ask who the audience is, since that sets the redaction threshold.
- **picker-catchup** — Find the connected meeting-notes source and pull everything new since last sync.
- **picker-brief** — Locate their Corp-OS root and read the last brief's timestamp as the delta boundary.
- **picker-open** — Pull open decisions, sort by age past date and who they're blocked on.
- **picker-check** — Scan the OS for claims past their verify-by date or unverified.
- **picker-share** — Ask which document, then locate it and scan for comp-related content to redact.
- **picker-recall** — Search the OS for every Northwind renewal claim, with dates and sources.
- **picker-capture** — Read the transcript, identify the source and date, then file it.
