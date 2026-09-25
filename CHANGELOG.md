# Changelog

## Unreleased

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

## Version 0.1

- Initial release
