# HANDOFF — pyscaffoldext-ClickStart

State-of-play for whoever picks this up next (human or agent). Update after every
completed task or release: current state, HEAD, latest tag, task list.

## Current state (2026-09-13)

| Item | Value |
|---|---|
| Branch | `main` |
| HEAD | `9a7842f` — Format Python code blocks in Markdown docs so Ruff 0.16 format check passes |
| Latest tag | `v2.2.5` (published to PyPI, 2026-06-15) |
| Unreleased commits | 3 (see below) |
| CI | Green on all six jobs (lint, build, 4× test matrix) as of run 34737250170 |
| Working tree | Clean after commit |

### Unreleased since v2.2.5

- `12cb280` Stop commit messages being executed during a release
- `127aee9` Makefile template: stamp targets always run so the signature cache
  actually works; per-tier coverage files (`.stamps/coverage.unit`,
  `.stamps/coverage.integration`) combined before the aggregated report
- `9a7842f` Reformat fenced Python blocks in `README.md` and `docs/usage.md`
  (CI fix only, no behaviour change)

`CHANGELOG.md` already carries the two Makefile-template entries under
**Unreleased**. The release fix and the docs reformat are not listed there.

## What happened this session

CI had failed on the last two pushes (2026-08-31 and 2026-09-13). Both failures
were the **lint** job only. The workflow installs unpinned Ruff, which reached
0.16.7 and now formats fenced Python code blocks inside Markdown files. The local
venv had Ruff 0.14.9, which ignores Markdown, so `make lint` passed locally and
hid the drift.

Fix applied and pushed as `9a7842f`:

- Ran Ruff 0.16.7 `format` and applied its output to `README.md` and
  `docs/usage.md` (quote style and blank lines in example code only).
- Upgraded Ruff in `.venv` to 0.16.7 so local lint matches CI.
- Confirmed the scaffold templates under `src/pyscaffoldext/clickstart/templates/`
  contain no Markdown with Python fences, so generated projects are unaffected.

## Open tasks

1. **Decide whether to pin Ruff in CI.** `.github/workflows/ci.yml` runs
   `pip install ruff` unpinned, so a future Ruff release can break lint with no
   code change. Options: pin to the version in the `dev` extra, or install
   `.[dev]` in the lint job. Policy call, not yet made.
2. **Release.** Three commits are sitting unreleased on top of `v2.2.5`. The
   Makefile-template stamp fix is a real bug fix for generated projects, so a
   `make release KIND=patch` (→ `v2.2.6`) is warranted. Before releasing, add
   `CHANGELOG.md` entries for `12cb280` and `9a7842f` if you want them recorded.
   Releasing is always the main session's job, always confirmed with Kevin first.
3. **Pre-commit config is stale.** `.pre-commit-config.yaml` still references
   isort and black (2021 revs) and a `git://` URL for pre-commit-hooks, none of
   which match the Ruff-only tooling the project actually uses. Low priority.
4. **Stray files in the repo root.** `pyscaffoldDoc.md` and `pyscaffoldDoc2.md`
   look like scratch notes; `build/`, `dist/` and `coverage.xml` are build
   outputs. Check whether they are gitignored and tidy if not.

## How to work here

- `make bootstrap` creates `.venv` and installs `.[dev]`. Use `.venv`, not conda.
- `make lint` / `make format` / `make test` / `make test-all` / `make docs`.
- The test suite scaffolds real projects via the CLI and takes ~5 minutes.
  It needs a git identity (`user.name` / `user.email`) or PyScaffold raises
  `GitNotConfigured`; CI sets one explicitly.
- Doc dependencies live only in the `docs` extra of `pyproject.toml`.
- Versions come from git tags via setuptools_scm. Tag push publishes to PyPI
  through Trusted Publishing (OIDC) in the "Upload Python Package" workflow.

## Layout

```
src/pyscaffoldext/clickstart/
  extension.py        # the PyScaffold extension (putup <name> --clickstart)
  tests_structure.py  # generated tests/ layout
  templates/          # *.template files rendered into new projects
tests/                # pytest suite; scaffolds real projects, ~5 min
docs/                 # Sphinx (MyST)
.github/workflows/    # ci.yml (lint/test/build), publish workflow on tag push
```
