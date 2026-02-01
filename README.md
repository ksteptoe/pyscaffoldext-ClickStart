# ClickStart

[![PyPI-Server](https://img.shields.io/pypi/v/pyscaffoldext-clickstart.svg)](https://pypi.org/project/pyscaffoldext-clickstart/)
[![Tests](https://github.com/ksteptoe/pyscaffoldext-ClickStart/actions/workflows/ci.yml/badge.svg)](https://github.com/ksteptoe/pyscaffoldext-ClickStart/actions)
[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

> A PyScaffold extension to generate modern Click-based CLI projects with batteries included.

ClickStart generates a complete, production-ready Python CLI project structure with sensible defaults and modern tooling. It eliminates the boilerplate of setting up a new CLI application so you can focus on writing your actual code.

## Installation

```bash
pip install pyscaffoldext-clickstart
```

This installs the extension alongside PyScaffold. You can verify installation with:

```bash
putup --help | grep clickstart
```

## Quick Start

Generate a new CLI project:

```bash
putup --clickstart my_project
cd my_project
make bootstrap    # Create venv and install dependencies
make test         # Run tests
my_project --help # Run your CLI
```

That's it! You have a working CLI application with tests, documentation, and all the tooling configured.

## What Gets Generated

```
my_project/
├── src/
│   └── my_project/
│       ├── __init__.py       # Package initialization
│       ├── __main__.py       # python -m support
│       ├── cli.py            # Click CLI entry point
│       └── api.py            # Core API logic
├── tests/
│   ├── README.md             # Testing guide
│   ├── unit/
│   │   └── test_import.py    # Package import smoke test
│   └── integration/
│       └── test_layout.py    # Project structure tests
├── docs/
│   ├── index.md              # Documentation home
│   ├── conf.py               # Sphinx configuration
│   └── ...                   # Other doc files
├── Makefile                  # Development task automation
├── pyproject.toml            # Project configuration (PEP 621)
├── .pre-commit-config.yaml   # Pre-commit hooks (Ruff)
├── .gitignore                # Git ignore patterns
├── README.md                 # Project readme
├── LICENSE.txt               # MIT license
├── AUTHORS.md                # Author credits
├── CHANGELOG.md              # Version history
└── CONTRIBUTING.md           # Contribution guide
```

## Makefile Targets

The generated Makefile provides common development tasks:

| Target | Description |
|--------|-------------|
| `make help` | Show all available targets |
| `make venv` | Create virtual environment |
| `make bootstrap` | Create venv and install `.[dev]` |
| `make precommit` | Install pre-commit hooks |
| `make test` | Run cached unit + integration tests |
| `make test-all` | Run all tests (no cache) |
| `make test-live` | Run `@live` marked tests |
| `make lint` | Run Ruff checks |
| `make format` | Auto-fix with Ruff |
| `make docs` | Build Sphinx documentation |
| `make build` | Build wheel and sdist |
| `make upload` | Upload to PyPI via Twine |
| `make version` | Show setuptools_scm version |
| `make changelog` | Show changes since last tag |
| `make release` | Run tests and create git tag |
| `make clean` | Remove build artifacts |
| `make run-cli` | Run CLI via `python -m` |

### Release Workflow

The Makefile includes Git-tag-based release automation:

```bash
make release KIND=patch  # v1.0.0 -> v1.0.1
make release KIND=minor  # v1.0.0 -> v1.1.0
make release KIND=major  # v1.0.0 -> v2.0.0
```

This runs tests, generates changelog, creates a signed git tag, and pushes to origin.

## Configuration Options

ClickStart works with all standard PyScaffold options:

```bash
# Basic usage
putup --clickstart my_project

# With package name different from project
putup --clickstart my-project -p my_package

# With namespace package
putup --clickstart my_project --namespace my.ns

# Skip creating git repo
putup --clickstart my_project --no-git

# Show what would be generated
putup --clickstart my_project --pretend
```

## Features

### Modern Python Packaging

- **pyproject.toml only** - No setup.py or setup.cfg
- **setuptools-scm** - Automatic version from git tags
- **PEP 621** compliant project metadata

### Testing Infrastructure

- **pytest** with sensible defaults
- **Unit/Integration separation** - Fast vs slow tests
- **Coverage** reporting configured
- **pytest-xdist** for parallel testing
- **pytest-timeout** for hanging test protection

### Code Quality

- **Ruff** for linting and formatting (replaces Black, isort, flake8)
- **Pre-commit** hooks configured
- Consistent code style enforced

### Documentation

- **Sphinx** with MyST-Parser for Markdown
- **ReadTheDocs** configuration included
- **API autodoc** generation

### CLI Framework

- **Click** for command-line interface
- Entry point configured in pyproject.toml
- `python -m` support via `__main__.py`
- Logging with `-v`/`-vv` verbosity flags

## Customization

### Modifying the CLI

Edit `src/<package>/cli.py` to add commands:

```python
@cli.command()
@click.argument('name')
def greet(name):
    """Greet someone by name."""
    click.echo(f'Hello, {name}!')
```

### Adding Dependencies

Edit `pyproject.toml`:

```toml
dependencies = [
    "click>=8.1",
    "requests>=2.31",  # Add your dependency
]
```

Then reinstall: `pip install -e ".[dev]"`

### Adding Tests

- Fast unit tests go in `tests/unit/`
- Slower integration tests go in `tests/integration/`

Mark integration tests:

```python
import pytest

@pytest.mark.integration
def test_something_slow():
    ...
```

### Environment Variables

The Makefile supports customization via environment variables:

```bash
# Use a different venv location
make bootstrap VENV=~/.venvs/my_project

# Force test re-run
make test NO_CACHE=1

# Pass arguments to CLI
make run-cli CLI_ARGS="--help"
```

## Requirements

- Python 3.12+
- PyScaffold 4.5+
- Git (for version detection)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE.txt](LICENSE.txt)

## Acknowledgments

This project extends [PyScaffold](https://pyscaffold.org/), the Python project generator. Thanks to the PyScaffold maintainers for the excellent foundation.
