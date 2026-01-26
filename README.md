# ClickStart

A PyScaffold extension to generate Click-based CLI projects.

## Usage

Install this package with `pip install pyscaffoldext-clickstart` and note that `putup -h` shows a new option `--clickstart`.

Use this flag to generate a modern Python CLI project with:

- **Click** for command-line interface
- **Modern pyproject.toml** configuration (no setup.cfg)
- **Ruff** for linting and formatting
- **pytest** with unit/integration test separation
- **Pre-commit** hooks configured
- **Makefile** for common development tasks

```bash
putup --clickstart my_project
cd my_project
make dev    # Install in development mode
make test   # Run tests
make lint   # Run linter
```

## Making Changes & Contributing

This project uses [pre-commit](https://pre-commit.com/). Please install it before making any changes:

```bash
pip install pre-commit
cd pyscaffoldext-ClickStart
pre-commit install
```

It is a good idea to update the hooks to the latest version:

```bash
pre-commit autoupdate
```

Don't forget to tell your contributors to also install and use pre-commit.

## Note

This project has been set up using PyScaffold 4.1.2. For details and usage information on PyScaffold see https://pyscaffold.org/.
