---
description: Make something safe to send — a cleaned copy, plus a private record of what came out
---

Invoke the `corp-os-redact` skill.

What is leaving, and to whom: `$ARGUMENTS`

If the audience is not stated, ask — it sets the whole threshold. If the person will not say, use the external threshold and tell them that is what you did.

Two outputs, always, written together by `scripts/write_export.py`: the cleaned copy, and a private log of every removal with its reason. The log stays local and never travels with the copy.

Then stop. This makes something shareable; the person decides whether to share it. A redaction step that also sends is a redaction step that can send a mistake.
