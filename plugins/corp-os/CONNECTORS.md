# Connectors

## How tool references work

Corp-OS skills refer to data sources by **category**, not by product. A `~~meeting notes` reference means whatever meeting-notes tool the person actually uses.

This is deliberate and load-bearing. An OS built around "Granola" breaks when someone switches tools or hands the system to a colleague on a different stack. One built around "meeting notes" does not. The connector registry in every Corp-OS records both — the category, which is durable, and the product, which is not.

## Categories Corp-OS knows how to use

| Category | Placeholder | Common options | Feeds raw/ as |
|---|---|---|---|
| Meeting notes | `~~meeting notes` | Granola, Otter, Fathom, Gong, Fireflies | `type: meeting` |
| Chat | `~~chat` | Slack, Microsoft Teams, Discord | `type: thread` |
| Email | `~~email` | Gmail, Outlook | `type: thread` |
| Documents | `~~documents` | Google Drive, Notion, Confluence, Box, SharePoint | `type: document` |
| Issue tracker | `~~tracker` | Jira, Linear, Asana, GitHub Issues | `type: document` |
| CRM | `~~crm` | Salesforce, HubSpot, Attio | `type: document` |
| Warehouse | `~~warehouse` | Redshift, Snowflake, BigQuery, Postgres | `type: research` |
| Calendar | `~~calendar` | Google Calendar, Outlook Calendar | `type: meeting` |
| Web | `~~web` | web search and fetch | `type: web` |
| Design system | `~~design` | a design-system skill, a brand guide, Figma tokens | bound via `design.md` |

## No connectors required

Corp-OS works with zero connectors. `corp-os-intake` handles pasted transcripts, uploaded documents, forwarded email, and typed notes, and a manual-only OS is a legitimate configuration — `corp-os-connect` records those sources with `protocol: manual`.

Connectors reduce upkeep. They are not the system.

## Registering a source

`corp-os-connect` writes each source into the OS's own `connectors.md` with category, protocol, auth mechanism, what it feeds, jobs served, cadence, status, and blind spots.

The **blind spots** field is the one that is easy to skip and should not be. A registry listing only what each source provides quietly implies full coverage, which is never true. Meeting notes only capture calls the person joined; chat search only reaches channels they are in; a CRM reflects what reps typed, not what customers said. Writing those limits down is what stops the OS from mistaking silence for absence.

## Credentials

Never written into the OS folder. The registry records the mechanism — "OAuth via installed connector," "token in environment" — never the secret itself. If a credential turns up inside captured material, `corp-os-redact` removes it and flags it for rotation.
