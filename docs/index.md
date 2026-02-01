# ClickStart

A PyScaffold extension to generate modern Click-based CLI projects with batteries included.

ClickStart generates a complete, production-ready Python CLI project structure with:

- **Click-based CLI** - Modern command-line interface framework
- **Modern packaging** - pyproject.toml only (no setup.py/setup.cfg)
- **Ruff** - Fast linting and formatting
- **pytest** - Testing with unit/integration separation
- **Sphinx + MyST** - Markdown documentation
- **Makefile** - Development task automation
- **Pre-commit** - Git hooks configured

## Quick Start

```bash
pip install pyscaffoldext-clickstart
putup --clickstart my_project
cd my_project
make bootstrap
make test
```

## Contents

```{toctree}
:maxdepth: 2

Overview <readme>
User Guide <usage>
API Reference <api>
Contributions & Help <contributing>
License <license>
Authors <authors>
Changelog <changelog>
Module Reference <api/modules>
```

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
