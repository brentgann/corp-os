# Bundled fonts

Vendored so `render_docs.py` produces the same PDF on any machine, with no
network at build time. Google Fonts is unreachable from some build
environments, and a silently substituted font is a silently different
document.

| Family | Weights | Licence |
|---|---|---|
| Inter | 400, 500, 600, 700 | SIL Open Font License 1.1 |
| Space Grotesk | 600, 700 | SIL Open Font License 1.1 |
| IBM Plex Mono | 500, 600 | SIL Open Font License 1.1 |

All three are OFL and redistributable. Sourced from the `@fontsource`
packages of the same names; latin subsets only.
