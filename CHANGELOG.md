# Changelog

## Unreleased

## Version 2.3.0 (2026-09-25)

- Makefile template (and this repo's Makefile): new `pipx-install` target that runs
  `pipx install --force` on the checkout. `make release` now calls it after tagging,
  so the released CLI is installed locally via pipx. Configurable with `PIPX` and
  `PIPX_INSTALL_ARGS`.
- Makefile template: the unit and integration stamp targets now carry a FORCE
  prerequisite, so the recipe (and its sha1 signature check over tests/, src/ and
  pyproject.toml) runs on every invocation. Previously an existing stamp file was
  treated as up to date forever, so make test was a false green from the second
  run on and NO_CACHE=1 was ignored.
- Makefile template: each test tier writes its own coverage data file
  (.stamps/coverage.unit, .stamps/coverage.integration) and make test runs
  coverage combine --keep before the aggregated report, so a unit-only re-run no
  longer wipes the integration coverage and under-reports.
- Makefile template: the release targets no longer pass the changelog through the
  shell. Commit subjects were previously interpolated into a double-quoted string,
  so backticks in a subject were executed during `make release`. The tag message
  is now written to a temporary file straight from `git log` and passed with `-F`.
- Docs: reformatted fenced Python examples in README.md and docs/usage.md so the
  Ruff 0.16 Markdown format check passes in CI. No behaviour change.

## Version 0.1

- Initial release
