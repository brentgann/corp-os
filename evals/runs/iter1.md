# Routing eval

Model `claude-opus-5` · 44 queries × 3 repeats · 19 skills on the roster

**Overall routing accuracy: 93%**

## By collision pair

The pairs the audit named as likely to collide, plus the coverage set.

| probe | queries | accuracy |
|---|---|---|
| new:decide | 5 | 60% |
| negative | 8 | 88% |
| pair:reality-check-vs-audit | 4 | 100% |
| pair:configure-vs-rebuild | 4 | 100% |
| pair:add-this | 5 | 100% |
| pair:update-vs-improve | 4 | 100% |
| coverage | 14 | 100% |

## Where it went instead

Every miss, as expected → chosen. A pair appearing repeatedly is a real description collision; a one-off is usually an ambiguous query.

| expected | chosen instead | times |
|---|---|---|
| `corp-os-claims` | `corp-os-decide` | 3 |
| `corp-os-jobs` | `corp-os-decide` | 3 |
| `none` | `corp-os-recall` | 3 |

## Queries that never routed correctly

- **decide-3** — expected `corp-os-claims`, always got `corp-os-decide`
  > we went with postgres in the end, mostly because the team already knew it. get that recorded so nobody re-opens it in six months
- **decide-4** — expected `corp-os-jobs`, always got `corp-os-decide`
  > i need to decide how we're going to handle renewals going forward — that's basically my whole quarter
- **neg-8** — expected `none`, always got `corp-os-recall`
  > draft the agenda for my 1:1 with Priya tomorrow
