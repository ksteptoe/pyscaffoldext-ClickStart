# Release Note — Documentation system: single source of truth for doc deps

This release reworks how `pyscaffoldext-clickstart` scaffolds a project's
documentation toolchain, and hardens the test suite so the Windows CI leg
passes. Projects generated with this extension now build their Sphinx + MyST
docs from a single, consolidated dependency source, and unambiguous autodoc
cross-references out of the box.

## Highlights

- **One source of truth for documentation dependencies.** Generated projects no
  longer get a `docs/requirements.txt`. The Sphinx/MyST toolchain now lives in a
  `docs` optional-dependencies extra in `pyproject.toml`, which is folded into
  the `dev` extra. Because `make docs` installs `.[dev]`, the docs build is now
  self-sufficient — no more `No module named sphinx` when building locally.
- **Read the Docs installs the package, not a requirements file.** The generated
  `.readthedocs.yml` installs the package with `extras: [docs]` instead of
  pointing at `docs/requirements.txt`.
- **Unambiguous autodoc cross-references.** The generated `docs/conf.py` now sets
  `autodoc_default_options = {"ignore-module-all": True}`. When a package
  `__init__` re-exports its public API via `__all__`, autodoc would otherwise
  document each name twice (e.g. `pkg.Thing` *and* `pkg.module.Thing`), making
  `` :class:`Thing` `` cross-references ambiguous. Ignoring `__all__` at the
  package level keeps one canonical target per object. Harmless when no `__all__`
  is present.
- **Windows CI is green.** The extension's own test suite read generated files
  with the platform default codec, which raised `UnicodeDecodeError` on Windows
  (cp1252) for files containing UTF-8 emoji. All `read_text()` calls now pass
  `encoding="utf-8"`, so the `windows-latest` matrix leg passes. The CI matrix
  already covers Ubuntu, macOS, and Windows on Python 3.12 (plus 3.13 on Linux).

## What changed in this extension

| File | Change |
|------|--------|
| `templates/pyproject.toml.template` | New `docs` extra (`sphinx>=7`, `myst-parser>=2`); folded into `dev` via `{{ project_name }}[docs]` |
| `templates/.readthedocs.yml.template` | Install package with `extras: [docs]` instead of `requirements: docs/requirements.txt` |
| `templates/docs/conf.py.template` | Add `autodoc_default_options = {"ignore-module-all": True}` |
| `templates/docs/requirements.txt.template` | **Removed** (consolidated into `pyproject.toml`) |
| `extension.py` | Stop emitting `docs/requirements.txt` and `reject` PyScaffold's default so it is not re-added |
| `tests/` | New regression tests for the conventions above; `encoding="utf-8"` on all `read_text()` calls |

## Upgrade notes for existing generated projects

These conventions apply to *newly generated* projects. To adopt them in a
project already scaffolded with an older ClickStart:

1. Move your doc dependencies into a `docs` extra in `pyproject.toml` and add
   that extra to `dev` (e.g. `"<project>[docs]"`).
2. Point `.readthedocs.yml` at `extras: [docs]` and delete `docs/requirements.txt`.
3. If your package `__init__` re-exports via `__all__`, add
   `autodoc_default_options = {"ignore-module-all": True}` to `docs/conf.py`.

## Authoring conventions (not auto-generated, but recommended)

These came out of the same work and are worth following by hand in your project:

- **Narrative doc pages should not duplicate `sphinx-apidoc` output.** Because
  `conf.py` regenerates `api/*.rst` with `.. automodule::` on every build, a
  hand-written MyST page should *link* to the generated API
  (`` {doc}`Module Reference <api/modules>` ``) rather than embed its own
  `automodule` block — otherwise you get ~duplicate-object warnings. If a page
  genuinely needs an inline autodoc block, add `:no-index:`.
- **Wrap docstring code examples in a literal block.** Use
  `.. code-block:: python` (or a `::` literal block) for examples in NumPy/Google
  docstring sections. A bare indented example containing `"key": value` lines is
  parsed by docutils as a definition list and emits block-quote/definition-list
  warnings.
- **Build through `make`, not ad-hoc Sphinx.** `make docs` keeps the
  env-install + apidoc + build chain consistent; a clean check is
  `rm -rf docs/_build && make docs`, expecting `build succeeded.` with zero
  warnings.
