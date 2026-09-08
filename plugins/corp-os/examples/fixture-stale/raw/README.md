# Raw

**Append-only.** Never edited, never summarized in place, never deleted. Existing here means *said*, not *true*.

One sanctioned exception: the `processed` flag in a file's frontmatter gets flipped to `true` once the derived layer has drawn from it. That is bookkeeping about the file, not part of what was said.

File shape: `YYYY-MM-DD--<source>--<slug>.md`, with frontmatter carrying `source`, `person`, `date`, `type`, `tags`, `external_id`, `processed`.
