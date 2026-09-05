# Fixture OS

A synthetic Corp-OS, committed so `validate.py` can execute `build_index.py` against a real tree and assert what it renders. Not an example to copy — `config-worked-example.json` is that. This one exists to be *run*.

It deliberately exercises the cases that broke the script before:

- a **custom layer** (`decisions/`) the shipped model does not scaffold, with its own `index_line`
- a **disabled layer** (`glossary`) that must be omitted from the render rather than counted as empty
- a **single-file layer** shape, and list-style entries, which used to count as zero
- a layer with **`jobs` enabled** so the jobs path is covered, alongside a config that renames vocabulary
- an **excluded** directory (`usage/`) that must stay out of the scan path
- a copy of **`scripts/build_index.py`**, because `corp-os-setup` puts one in every OS it scaffolds and several skills tell the model to run it. The first version of this fixture omitted it, and `corp-os-intake` then wrote a raw file without an index entry on three runs out of four — the skill was reaching for a script that was not there. A fixture that is missing what a real OS has does not test the skill; it tests the fixture.

Every name in it is invented. Nothing here is anyone's real work, which is what makes it safe to commit.
