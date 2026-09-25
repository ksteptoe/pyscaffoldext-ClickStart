# HANDOFF — pyscaffoldext-ClickStart

State-of-play for whoever picks this up next (human or agent). Update after every
completed task or release: current state, HEAD, latest tag, task list.

## Current state (2026-09-25)

| Item | Value |
|---|---|
| Branch | `main` |
| HEAD | `4b98f1d` — Add pipx-install target; make release installs the tagged checkout via pipx |
| Latest tag | `v2.3.0` on `b3ec7bb` (published to PyPI via Upload Python Package run 36100410698, 2026-09-25) |
| Unreleased commits | 0 |
| CI | Green as of run 36100215577 (2026-09-25) |
| Working tree | Clean, pushed to origin/main |

### Released in v2.3.0 (previously unreleased since v2.2.5)

- `12cb280` Stop commit messages being executed during a release
- `127aee9` Makefile template: stamp targets always run so the signature cache
  actually works; per-tier coverage files (`.stamps/coverage.unit`,
  `.stamps/coverage.integration`) combined before the aggregated report
- `9a7842f` Reformat fenced Python blocks in `README.md` and `docs/usage.md`
  (CI fix only, no behaviour change)
- `a35e67d` Add HANDOFF.md
- `4b98f1d` pipx-install target; `make release` ends with a local pipx install

`CHANGELOG.md` already carries the two Makefile-template entries under
**Unreleased**. The release fix and the docs reformat are not listed there.

## What happened this session (2026-09-24)

Added a `pipx-install` Makefile target to both this repo's `Makefile` and the
scaffold's `Makefile.template`. It runs `pipx install --force $(PIPX_INSTALL_ARGS)
"$(CURDIR)"` and fails clearly if `pipx` is not on PATH. `make release` now calls
it as its final step, after the tag is pushed, so the pipx-installed version matches
the new tag. This repo sets `PIPX_INSTALL_ARGS ?= --include-deps` because it has no
console script of its own and `putup` comes from the pyscaffold dependency; the
template leaves it empty. Two tests added in `tests/test_templates.py`
(`TestMakefilePipxInstall`); README, `docs/usage.md` and `CHANGELOG.md` updated.
Verified: `make -n pipx-install` here and in a freshly scaffolded project; Makefile
tests pass; `make lint` green. Committed as `4b98f1d` and pushed on 2026-09-25.
Released the same day as `v2.3.0` via `make release KIND=minor`; the new pipx step
ran successfully and the local pipx venv now holds 2.3.0 (was 2.2.1).

Follow-up (2026-09-25): this repo's own `Makefile` still used the pre-`12cb280`
changelog handling, so a commit subject with backticks or `$(...)` was executed by
`make changelog`, `changelog-md` and `release-*`. Ported the template's
`git_changelog` define and temp-file `git tag -F` approach. Verified in throwaway
repos with a bare remote: old Makefile executed the injected commands, new one
tags the subject verbatim. Not shipped in the package, so no release needed.

## What happened previously (2026-09-13)

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

1. ~~Pin Ruff in CI~~ Done 2026-09-25: `ruff==0.16.7` pinned in the `dev` extra;
   the CI lint job reads that pin from `pyproject.toml` and installs it; the
   pre-commit ruff rev matches. **To upgrade Ruff, bump all three together.**
2. ~~CHANGELOG tidy~~ Done 2026-09-25: 2.3.0 entries moved under their own
   heading, with entries added for `12cb280` and `9a7842f`.
3. ~~Pre-commit config is stale~~ Done 2026-09-25: replaced with Ruff-only
   (`ruff-check`, `ruff-format`) plus pre-commit-hooks v6.0.0. Its
   end-of-file-fixer normalised trailing newlines in four templates and
   `pyproject.toml`. Full suite: 104 passed.
5. ~~Template pre-commit Ruff rev is old~~ Done 2026-09-25: template pre-commit
   now ruff-pre-commit v0.16.7 with `ruff-check`; template dev extra `ruff>=0.16.7`.
   Unreleased; recorded in CHANGELOG under Unreleased.
6. **Generated projects fail their own Ruff checks (pre-existing).** A fresh
   `putup demo --clickstart` fails `pre-commit run --all-files`: `ruff check`
   finds 4 fixable errors (import sorting) and `ruff format` would reformat
   `docs/conf.py`, `src/<pkg>/__main__.py`, `api.py`, `cli.py`, and
   `tests/integration/test_layout.py` changes too. Identical under Ruff 0.6.9 and
   0.16.7, so not caused by the bump. Fix the templates (`docs/conf.py.template`,
   `runner.template`, `api.template`, `cli.template`, tests templates) so generated
   output is Ruff-clean, and add a test that runs Ruff on a generated project.
   **Do this before the next release.**
4. ~~Stray files in the repo root~~ Done 2026-09-25: deleted the two scratch notes
   `pyscaffoldDoc.md` and `pyscaffoldDoc2.md` (recoverable from git history before
   the deleting commit). `build/`, `dist/` and `coverage.xml` do not show in git status.

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
