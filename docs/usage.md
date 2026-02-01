# User Guide

This guide covers everything you need to know to use ClickStart effectively.

## Installation

Install ClickStart from PyPI:

```bash
pip install pyscaffoldext-clickstart
```

This installs both PyScaffold and the ClickStart extension. Verify installation:

```bash
putup --help | grep clickstart
```

You should see `--clickstart` in the available options.

## Generating a Project

### Basic Usage

```bash
putup --clickstart my_project
```

This creates a new directory `my_project/` with a complete CLI application structure.

### Common Options

```bash
# Specify a different package name
putup --clickstart my-project -p my_package

# Use a namespace package
putup --clickstart my_project --namespace mycompany.tools

# Preview without creating files
putup --clickstart my_project --pretend

# Force overwrite existing project
putup --clickstart my_project --force

# Skip git initialization
putup --clickstart my_project --no-git
```

### All PyScaffold Options

ClickStart supports all standard PyScaffold options. See `putup --help` for the complete list.

## Understanding the Generated Structure

```
my_project/
├── src/my_project/           # Source code
│   ├── __init__.py           # Package marker
│   ├── __main__.py           # python -m support
│   ├── cli.py                # CLI entry point
│   └── api.py                # Core logic
├── tests/                    # Test files
│   ├── README.md             # Testing guide
│   ├── unit/                 # Fast tests
│   │   └── test_import.py
│   └── integration/          # Slower tests
│       └── test_layout.py
├── docs/                     # Documentation
│   ├── index.md
│   ├── conf.py               # Sphinx config
│   └── ...
├── Makefile                  # Task automation
├── pyproject.toml            # Project metadata
├── .pre-commit-config.yaml   # Git hooks
├── .gitignore
├── README.md
├── LICENSE.txt
├── AUTHORS.md
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## Developing Your CLI

### The CLI Module (`cli.py`)

The generated `cli.py` contains a basic Click application:

```python
import click
from .api import my_project_api

@click.command()
@click.version_option()
@click.option('-v', '--verbose', 'loglevel', flag_value=logging.INFO)
@click.option('-vv', '--very_verbose', 'loglevel', flag_value=logging.DEBUG)
def cli(loglevel):
    """Your CLI description here."""
    my_project_api(loglevel)
```

### Adding Commands

For a simple CLI with one command, modify the existing function:

```python
@click.command()
@click.argument('name')
@click.option('--greeting', default='Hello', help='Greeting to use')
def cli(name, greeting):
    """Greet someone."""
    click.echo(f'{greeting}, {name}!')
```

For multiple commands, convert to a command group:

```python
@click.group()
def cli():
    """My CLI application."""
    pass

@cli.command()
@click.argument('name')
def greet(name):
    """Greet someone."""
    click.echo(f'Hello, {name}!')

@cli.command()
def version():
    """Show version."""
    from . import __version__
    click.echo(f'Version: {__version__}')
```

### The API Module (`api.py`)

Keep your core business logic in `api.py`, separate from CLI concerns:

```python
def my_project_api(loglevel):
    """Main API function called by CLI."""
    setup_logging(loglevel)
    # Your logic here
```

This separation makes your code:
- Easier to test (import and call directly)
- Reusable as a library
- Cleaner and more maintainable

### Running Your CLI

```bash
# After installation
my_project --help

# During development (without installing)
python -m my_project --help

# Via Makefile
make run-cli CLI_ARGS="--help"
```

## Testing Your Project

### Test Structure

ClickStart separates tests into two categories:

**Unit tests** (`tests/unit/`):
- Fast, isolated tests
- No file system or network access
- Run frequently during development

**Integration tests** (`tests/integration/`):
- Slower, more comprehensive tests
- May use file system, spawn processes
- Marked with `@pytest.mark.integration`

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Exclude integration tests
pytest -m "not integration"

# With coverage
pytest --cov=my_project --cov-report=term-missing
```

### Using the Makefile

```bash
make test       # Cached unit + integration tests
make test-all   # All tests, no cache
make test-live  # @live marked tests only
```

### Writing Tests

Unit test example:

```python
# tests/unit/test_api.py
from my_project.api import process_data

def test_process_data():
    result = process_data("input")
    assert result == "expected"
```

Integration test example:

```python
# tests/integration/test_cli.py
import pytest
from click.testing import CliRunner
from my_project.cli import cli

@pytest.mark.integration
def test_cli_greet():
    runner = CliRunner()
    result = runner.invoke(cli, ['greet', 'World'])
    assert result.exit_code == 0
    assert 'Hello, World' in result.output
```

## Building and Releasing

### Version Management

ClickStart uses [setuptools-scm](https://github.com/pypa/setuptools-scm) for automatic versioning based on git tags:

```bash
# Check current version
make version

# Or directly
python -m setuptools_scm
```

### Building Packages

```bash
make build
```

This creates both wheel and source distribution in `dist/`.

### Releasing

The Makefile provides automated release workflows:

```bash
# Show current state
make release-show

# Patch release (v1.0.0 -> v1.0.1)
make release KIND=patch

# Minor release (v1.0.0 -> v1.1.0)
make release KIND=minor

# Major release (v1.0.0 -> v2.0.0)
make release KIND=major
```

The release process:
1. Runs full test suite
2. Shows changelog since last tag
3. Creates annotated git tag
4. Pushes tag to origin

### Uploading to PyPI

```bash
make upload
```

This uses Twine to upload to PyPI. Make sure you have credentials configured.

## Documentation

### Building Docs Locally

```bash
make docs
```

Open `docs/_build/html/index.html` in your browser.

### Documentation Structure

- `docs/index.md` - Main page
- `docs/readme.md` - Includes README.md
- `docs/api/` - Auto-generated API docs

### MyST-Parser Syntax

Documentation uses MyST-Parser for Markdown in Sphinx. Key features:

```markdown
# Heading

Regular **bold** and *italic* text.

Code blocks:
```python
def example():
    pass
```

Admonitions:
```{note}
This is a note.
```

```{warning}
This is a warning.
```

Cross-references:
{ref}`genindex`
```

## Pre-commit Hooks

### Setup

```bash
make precommit
# or
pre-commit install
```

### What's Included

The generated `.pre-commit-config.yaml` includes Ruff for:
- Code linting
- Import sorting
- Code formatting

### Running Manually

```bash
pre-commit run --all-files
```

### Updating Hooks

```bash
pre-commit autoupdate
```

## Environment Variables

### Makefile Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VENV` | `.venv` | Virtual environment path |
| `NO_CACHE` | `0` | Set to `1` to force test re-run |
| `KIND` | `patch` | Release type (patch/minor/major) |
| `CLI_ARGS` | | Arguments for `make run-cli` |

### Usage

```bash
# Use different venv location
make bootstrap VENV=~/.venvs/my_project

# Force tests to run
make test NO_CACHE=1

# Run CLI with arguments
make run-cli CLI_ARGS="greet World"
```

## Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -e ".[dev]"
```

**Pre-commit fails:**
```bash
make format  # Auto-fix issues
```

**Tests fail on clean checkout:**
```bash
pip install -e ".[dev]"  # Ensure dev deps installed
```

**Version shows as "0.0.0":**
```bash
git tag v0.1.0  # Create initial tag
```

### Getting Help

- Check the [README](https://github.com/ksteptoe/pyscaffoldext-ClickStart)
- Open an issue on GitHub
- See [PyScaffold documentation](https://pyscaffold.org/)
