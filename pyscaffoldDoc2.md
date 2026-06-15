# pdest — PDF Documentation Output (for the PyScaffold agent)

Context: companion to `pyscaffoldDoc.md`. `pdest` is a PyScaffold-generated
project using the **PyScaffold Clickstart** extension (src-layout, Sphinx + MyST
docs, Read the Docs, `setuptools_scm`, a top-level `Makefile` with `make docs`,
Ruff-only, pyproject-only). This note records the changes made to add **single-
file PDF output** for the documentation, and distills the reusable parts so they
can be backfilled into the **pyscaffold-clickstart extension**.

The clickstart template already ships an HTML docs target
(`make docs -> sphinx -b html`) but no PDF path. PyScaffold's stock `conf.py`
already defines a `latex_documents` entry, and the Sphinx-generated
`docs/Makefile` has a catch-all `latexpdf` mode — but neither is wired into the
top-level Makefile, and the default (pdflatex + xindy) fails on two common
fronts: arbitrary Unicode in the docs, and a missing `xindy` binary. This note
fixes both and adds a convenient, self-checking target.

Outcome: `make docs-pdf` builds `docs/_build/latex/<dist>.pdf` from the same
sources as the HTML docs, exits non-zero with a helpful message if no LaTeX
toolchain is present, and tolerates Windows/OneDrive directory locks.

```{note}
Template variables: the clickstart Makefile already defines `PKG`/`DIST`
(e.g. `pdest`). Everywhere this note hardcodes `pdest`, the template should
substitute the project/dist name — `$(PKG)` in the Makefile, and the
PyScaffold-templated project name in `conf.py`'s `latex_documents`.
```

---

## 1. New top-level `make docs-pdf` target

Add a PDF target next to the existing `docs` target in the top-level Makefile.
Build the LaTeX sources with the Sphinx **latex builder**, then compile with
`latexmk` directly:

```make
# -----------------------------------------------------------------------------#
# Docs
docs: $(ENV_STAMP)
	"$(PY)" -m sphinx -b html docs docs/_build/html

# Build a single PDF of the whole documentation set via the Sphinx LaTeX
# builder + latexmk. Requires a LaTeX toolchain (xelatex + latexmk) on PATH;
# install TeX Live or MiKTeX if `make docs-pdf` reports them missing.
# Output: docs/_build/latex/$(PKG).pdf
docs-pdf: $(ENV_STAMP)
	@command -v latexmk >/dev/null 2>&1 || { \
	  echo "latexmk not found. Install a LaTeX toolchain (TeX Live or MiKTeX) to build the PDF."; exit 1; }
	rm -rf docs/_build/latex 2>/dev/null || true   # best-effort clean; tolerate Windows/OneDrive locks
	"$(PY)" -m sphinx -b latex docs docs/_build/latex
	cd docs/_build/latex && latexmk -pdfxe -interaction=nonstopmode -halt-on-error $(PKG).tex
	@echo "PDF written to docs/_build/latex/$(PKG).pdf"
```

Also register it in `.PHONY` and `help`:

```make
.PHONY: help venv bootstrap precommit docs docs-pdf lint format \
        ...

help:
	...
	@echo "  make docs                - build Sphinx/MyST docs to docs/_build/html"
	@echo "  make docs-pdf            - build a single PDF to docs/_build/latex/$(PKG).pdf (needs LaTeX)"
```

**Why not `sphinx -M latexpdf` (the one-liner)?** Sphinx's make-mode
`latexpdf` target shells out to `make`/`make.bat` inside the generated `latex/`
directory to run the PDF compile. On Windows (Git Bash + MiKTeX) that step fails
with `Error: Failed to run: make.bat`. Driving `latexmk` ourselves is
cross-platform and avoids the nested-make dependency.

**Why `-pdfxe`?** It selects the XeLaTeX engine in `latexmk`, matching
`latex_engine = "xelatex"` from §2. (Sphinx also writes a `latexmkrc` that sets
the engine, so a bare `latexmk` would usually work too, but the explicit flag is
unambiguous and independent of the generated rc.)

**Scaffold takeaway:** add a `docs-pdf` Make target that runs `sphinx -b latex`
then `latexmk -pdfxe <PKG>.tex`, guarded by a `command -v latexmk` check so it
fails fast and friendly on machines without a TeX toolchain. Use the `$(PKG)`
variable for the `.tex`/`.pdf` filename.

---

## 2. `conf.py` — use the XeLaTeX engine for Unicode robustness

The default engine (`pdflatex`) **fatally aborts** on Unicode characters that are
routine in modern MyST docs. Two real failures seen here, each halting the build:

- `! LaTeX Error: Unicode character ⚠ (U+26A0)` — an emoji in a heading.
- `! LaTeX Error: Unicode character ≤ (U+2264)` — inside an inline code span
  (`low ≤ likely ≤ high`). Sphinx pre-declares many symbols (`→ × … ≤`) for
  pdflatex in *prose*, but those substitutions do **not** apply inside
  `\sphinxcode`/verbatim, so any non-ASCII in backticked code is fatal.

Switching to XeLaTeX makes Unicode work natively; a glyph the font lacks degrades
to a *warning* (missing character) instead of failing the build:

```python
# -- Options for LaTeX output ------------------------------------------------

# Use XeLaTeX so arbitrary Unicode in the docs (≤, →, ×, … — including inside
# code spans, where pdflatex's character substitutions don't apply) renders
# without per-character LaTeX declarations. Any glyph the font lacks degrades
# to a warning rather than failing the build.
latex_engine = "xelatex"
```

**Scaffold takeaway:** default `latex_engine = "xelatex"` in the clickstart
`conf.py`. It removes a whole class of "PDF build dies on an em-dash/arrow/emoji"
failures that pdflatex projects hit the first time a non-ASCII char lands in a
code span. (LuaLaTeX would also work; XeLaTeX is the lighter default.)

---

## 3. `conf.py` — pin the index to makeindex (the one caveated change)

This is the half-generic, half-environment change; **do not propagate it
silently.** When `latex_engine` is `xelatex` (or `lualatex`), Sphinx flips its
default indexer to **xindy** (Unicode-aware, the technically *better* tool) and
writes a `latexmkrc` whose `$makeindex` calls `xindy`. If `xindy` is not
installed, the PDF compile fails:

```
Run number 1 of rule 'makeindex pdest.idx'
  makeindex pdest.idx: Command for 'makeindex pdest.idx' gave return code 32512
```

`32512` is `0x7F00` → shell exit `127` → *command not found*: MiKTeX here ships
`makeindex` but not `xindy`. `makeindex` handles the ASCII autodoc index fine
(verified: 134 entries, 0 rejected), so pin the indexer back to it:

```python
# With xelatex, Sphinx defaults to xindy for the index; some TeX installs
# (e.g. this MiKTeX) ship makeindex but not xindy. makeindex handles the
# ASCII autodoc index fine, so pin to it to keep `make docs-pdf` self-contained.
latex_use_xindy = False
```

**Trade-off to document, not hide:** `xindy` produces better indexes for
non-ASCII / multilingual content and is what Read the Docs uses (RTD has it
installed, so on RTD this setting is suboptimal-but-harmless). Projects that need
a high-quality index and can install `xindy` may remove this line.

**Scaffold takeaway:** when defaulting to `xelatex`, also set
`latex_use_xindy = False` so PDF builds work on the common case (TeX dist with
`makeindex` but no `xindy`) — and leave the comment explaining the trade-off so
users know to flip it back if they install `xindy`.

---

## 4. Windows / OneDrive lock tolerance

Two Windows-specific gotchas surfaced (this repo lives under OneDrive):

1. **`conf.py` already deletes `docs/api/` on every build** (PyScaffold's apidoc
   step does `shutil.rmtree(output_dir)`). On OneDrive this intermittently raises
   `PermissionError: [WinError 5] Access is denied: '...\\docs\\api'` and kills the
   whole build. (Out of scope for this note, but the same fragility motivates the
   tolerant clean below; consider `shutil.rmtree(output_dir, ignore_errors=True)`
   upstream.)

2. **The `rm -rf docs/_build/latex` clean step** can fail with
   `Device or resource busy` when either OneDrive is syncing the freshly written
   files **or** a shell's current directory is *inside* `docs/_build/latex`
   (Windows refuses to remove a directory that is any process's cwd — a real trap
   when iterating: don't leave a terminal `cd`'d into the build dir).

The target above makes the clean **best-effort and non-fatal**
(`rm -rf … 2>/dev/null || true`): if the directory can't be removed, the build
proceeds anyway — `sphinx -b latex` overwrites the `.tex` sources and `latexmk`
rebuilds incrementally.

**Scaffold takeaway:** in clickstart Make recipes that pre-clean a build dir on
Windows-friendly projects, make the `rm` non-fatal so an OneDrive/cwd lock
doesn't abort the whole target.

---

## 5. Read the Docs — native PDF (the cloud counterpart)

`make docs-pdf` is the *local* path. Read the Docs can build and host the PDF with
no local TeX toolchain at all — its build image already has TeX Live **and**
`xindy`. `pyscaffoldDoc.md` §3 already switched RTD to install the `docs` extra;
add a `formats` block to emit PDF (and optionally ePub):

```yaml
# .readthedocs.yml
version: 2

formats:
  - pdf            # also builds/hosts the PDF on Read the Docs

python:
  install:
    - method: pip
      path: .
      extras:
        - docs
```

Because RTD has `xindy`, the `latex_use_xindy = False` from §3 is mildly
suboptimal there but causes no failure — the index just uses makeindex.

**Scaffold takeaway:** pair the local `make docs-pdf` with `formats: [pdf]` in the
clickstart `.readthedocs.yml`, so projects get a published PDF for free in
addition to the local build.

---

## What NOT to backfill (project-specific)

- **`latex_documents` filename.** This project renamed the LaTeX target from the
  PyScaffold default to `pdest.tex` (so the artifact is `pdest.pdf`). The template
  already templates this name from the project name — keep using the templated
  name; just ensure the Makefile target (`$(PKG).tex`) and `conf.py` agree.
- **Content fixes.** Removing an emoji from a doc heading, etc., are content-level
  and not template concerns. (XeLaTeX from §2 means emoji no longer *break* the
  build; they just warn if the font lacks the glyph.)

---

## Prerequisites (document in the extension's docs)

PDF generation needs a system LaTeX toolchain — it is **not** pip-installable and
not added to the `docs` extra:

- `xelatex` and `latexmk` on `PATH` (TeX Live, or MiKTeX on Windows).
- `makeindex` (ships with both; used because `latex_use_xindy = False`).
- The `command -v latexmk` guard in the target gives a clear message when these
  are absent, so the target is safe to ship even though the toolchain is optional.

---

## Files touched (PDF output)

| File | Change |
|------|--------|
| `Makefile` | new `docs-pdf` target; `.PHONY` + `help` entries; non-fatal clean |
| `docs/conf.py` | `latex_engine = "xelatex"`; `latex_use_xindy = False`; `latex_documents` -> `<PKG>.tex` |
| `.readthedocs.yml` | add `formats: [pdf]` (cloud PDF) |
| `docs/user_guide.md` | content only (dropped an emoji from a heading) — not scaffold-relevant |

---

## Checklist for the PyScaffold agent

- [ ] Top-level Makefile has a `docs-pdf` target: `sphinx -b latex` + `latexmk -pdfxe $(PKG).tex`, guarded by `command -v latexmk`.
- [ ] `docs-pdf` is in `.PHONY` and listed in `make help`.
- [ ] The clean step is non-fatal (`rm -rf docs/_build/latex 2>/dev/null || true`).
- [ ] `conf.py` sets `latex_engine = "xelatex"`.
- [ ] `conf.py` sets `latex_use_xindy = False` **with** the trade-off comment.
- [ ] `latex_documents` uses the templated project name and matches `$(PKG).tex` in the Makefile.
- [ ] `.readthedocs.yml` has `formats: [pdf]` (and installs `extras: [docs]` per `pyscaffoldDoc.md` §3).
- [ ] Extension docs note the LaTeX toolchain prerequisite (xelatex + latexmk + makeindex) and that it is optional.
- [ ] Verify: `make docs-pdf` -> exit 0 and `docs/_build/latex/<PKG>.pdf` exists; on a machine without LaTeX, the target exits with the friendly "latexmk not found" message.
```
