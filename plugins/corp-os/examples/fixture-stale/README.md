# fixture-stale

An OS two releases behind the installed plugin. It exists so `corp-os-upgrade`
can be tested against the situation it is for, rather than against a healthy OS
where there is nothing to find.

Deliberately wrong, and none of it should be repaired:

- `config.json` records `corpos_version: 0.9.0`.
- `scripts/build_index.py` is an older copy — it predates the fix that counts a
  single-file layer by its entry headers.
- `scripts/delete_source.py` is absent. This OS predates it, so the retention
  path in `corp-os-configure` fails against it today.
- `dashboards/registry.md` is the pre-0.10.1 layout: a directory-shaped path
  over one file holding three entries, which the index counts as one.

That last one is a **migration**, not a script refresh. `upgrade_os.py` reports
it and refuses to perform it; `corp-os-configure` is what moves someone's
files, after enumerating and asking. A run against this fixture that quietly
moves the registry has done the thing the split exists to prevent.

The two healthy fixtures are `fixture-os` (the shipped default shape) and
`fixture-register` (a legitimately different configuration).
