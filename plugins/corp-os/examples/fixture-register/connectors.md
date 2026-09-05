# Connectors

What feeds this OS, by what protocol, and — the field that matters — what each source structurally cannot see.

## email · connected

- **Category**: email
- **Protocol**: MCP connector
- **Auth**: OAuth via the installed connector
- **Feeds**: `source: email`, `type: thread`
- **Serves**: oi-001, oi-002
- **Cadence**: daily
- **Last pull**: 2026-08-22
- **Status**: connected
- **Blind spots**: only threads this account is on. Anything decided in a call, or in a thread where someone was dropped from the chain, never appears here at all.

## meeting-notes · broken

- **Category**: meeting notes
- **Protocol**: MCP connector
- **Auth**: OAuth via the installed connector
- **Feeds**: `source: meeting-notes`, `type: meeting`
- **Serves**: oi-001
- **Cadence**: daily
- **Last pull**: 2026-07-30
- **Status**: broken — the connector stopped returning results after the vendor's July auth change. Not reconnected.
- **Blind spots**: only calls this account joined.

## crm · not-connected

- **Category**: CRM
- **Status**: not-connected
- **Reason**: considered and declined. It reflects what reps typed, not what the counterparty said, and nothing in this OS turns on pipeline stage. Recorded so the question stops being reopened.
