# Connectors

What is registered, what it feeds, and what it cannot see.

### Granola
- **Category**: meeting notes
- **Protocol**: MCP connector
- **Access**: list+fetch
- **Auth**: OAuth via connector, no local credentials
- **Credential**: managed by the connector — never a value in this file
- **Scope**: read-only
- **Feeds**: raw/ as `source: meeting-notes`, `type: meeting`
- **Selector**: n/a — already personal, only calls I joined
- **Serves jobs**: job-001
- **Cadence**: daily
- **Limits**: 60 calls/min published, 1 concurrent
- **Ceiling**: 25 calls per run
- **Medium**: summary
- **List call**: `list_meetings(since, limit)` — id, title, date, participants. No bodies.
- **Fetch call**: `get_transcript(id)` — the body, verbatim
- **Verbatim fetch**: yes
- **Status**: healthy
- **Yield**: 1 file → 1 cited (100%) — 2026-09-10, from `source_yield.py`
- **Blind spots**: attachments are not indexed, so a decision living in a PDF on a thread is invisible to this OS.

### Hallway
- **Category**: notes
- **Protocol**: manual paste
- **Access**: manual
- **Auth**: n/a
- **Credential**: n/a
- **Scope**: n/a — nothing is connected
- **Feeds**: raw/ as `source: manual`, `type: note`
- **Serves jobs**: job-002
- **Cadence**: on demand
- **Medium**: reconstructed
- **Verbatim fetch**: no
- **Status**: manual-only
- **Blind spots**: everything not written down within the hour is gone. These are the entries that can never be re-confirmed.
