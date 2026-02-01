# Contributing to ClickStart

Thank you for considering contributing to ClickStart! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.12+
- Git
- Make (optional, but recommended)

### Setting Up Your Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ksteptoe/pyscaffoldext-ClickStart.git
   cd pyscaffoldext-ClickStart
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### Using the Makefile

If you have Make installed, you can use:

```bash
make bootstrap  # Create venv and install dependencies
make precommit  # Install pre-commit hooks
```

## Running Tests

### All Tests

```bash
pytest tests/ -v
```

### With Coverage

```bash
pytest tests/ --cov=pyscaffoldext.clickstart --cov-report=term-missing
```

### Specific Test Files

```bash
# Unit tests only
pytest tests/test_extension_unit.py -v

# Integration tests (generated content)
pytest tests/test_generated_content.py -v

# Template rendering tests
pytest tests/test_templates.py -v
```

### Using the Makefile

```bash
make test      # Run all tests
make test-all  # Run all tests without cache
```

## Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting.

### Checking Code Style

```bash
ruff check .
ruff format --check .
```

### Auto-fixing Issues

```bash
ruff check --fix .
ruff format .
```

### Using the Makefile

```bash
make lint    # Check code style
make format  # Auto-fix code style
```

### Style Guidelines

- Line length: 120 characters
- Target Python: 3.12+
- Follow PEP 8 conventions
- Use Google-style docstrings

## Project Structure

```
pyscaffoldext-ClickStart/
├── src/pyscaffoldext/clickstart/
│   ├── __init__.py           # Package initialization
│   ├── extension.py          # Main extension logic
│   └── templates/            # Template files
│       ├── Makefile.template
│       ├── pyproject.toml.template
│       ├── cli.template
│       ├── api.template
│       └── docs/             # Documentation templates
├── tests/
│   ├── conftest.py           # pytest fixtures
│   ├── test_custom_extension.py  # Integration tests
│   ├── test_extension_unit.py    # Unit tests
│   ├── test_generated_content.py # Content validation
│   └── test_templates.py         # Template rendering tests
└── docs/                     # Project documentation
```

## How to Modify Templates

Templates are located in `src/pyscaffoldext/clickstart/templates/`.

### Template Variables

Templates use two types of variable substitution:

1. **PyScaffold variables** (processed by PyScaffold):
   - `${name}` - Project name
   - `${package}` - Package name
   - `${author}` - Author name
   - `${license}` - License type
   - `${version}` - PyScaffold version

2. **Brace variables** (processed by ClickStart):
   - `{{ project_name }}` - Project name
   - `{{ package_name }}` - Package name

### Adding a New Template

1. Create the template file in `templates/` with `.template` extension
2. Use appropriate variable placeholders
3. Load and render the template in `extension.py`:
   ```python
   from pyscaffold.templates import get_template
   from . import templates as my_templates

   tpl = get_template("myfile", relative_to=my_templates)
   ```

### Modifying Existing Templates

1. Edit the template file
2. Run the tests to verify changes don't break generation
3. Add specific tests for new functionality if needed

## Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes:**
   - Write tests for new functionality
   - Update documentation if needed
   - Follow the code style guidelines

3. **Run tests and linting:**
   ```bash
   make lint
   make test
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add my feature"
   ```

5. **Push and create a pull request:**
   ```bash
   git push origin feature/my-feature
   ```
   Then open a PR on GitHub.

### PR Guidelines

- Keep PRs focused on a single change
- Include tests for new functionality
- Update documentation for user-facing changes
- Ensure all tests pass
- Ensure code passes linting

## Reporting Issues

When reporting issues, please include:

- Python version (`python --version`)
- PyScaffold version (`putup --version`)
- ClickStart version (`putup --clickstart-version`)
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Any error messages or stack traces

## Testing Generated Projects

After making changes, it's good practice to test the full workflow:

```bash
# Generate a test project
putup --clickstart test_project
cd test_project

# Verify it works
make bootstrap
make test
make lint
```

## Documentation

- Project documentation is in `docs/`
- Use MyST-Parser Markdown syntax
- Build locally with: `make docs`
- View at `docs/_build/html/index.html`

## Questions?

If you have questions about contributing, feel free to open an issue for discussion.
