from __future__ import annotations

from pyscaffold import structure
from pyscaffold.operations import no_overwrite, skip_on_update

NO_OVERWRITE = no_overwrite()
SKIP_ON_UPDATE = skip_on_update()


def _unit_test(opts) -> str:
    pkg = opts["package"]
    return f'''"""Unit smoke tests (fast)."""

import importlib


def test_package_importable():
    importlib.import_module("{pkg}")
'''


def _integration_test(opts) -> str:
    pkg = opts["package"]
    return f'''"""Integration-ish smoke tests (filesystem/layout)."""

from pathlib import Path
import pytest


@pytest.mark.integration
def test_src_layout_exists():
    root = Path(__file__).resolve().parents[2]
    assert (root / "pyproject.toml").exists()
    assert (root / "src" / "{pkg}").exists()
'''


def _tests_readme(_opts) -> str:
    return """# Tests

- `unit/`: fast import/smoke tests
- `integration/`: tests that touch the filesystem or run external tools

Run:
- `pytest` (all)
- `pytest -m "not integration"` (unit only)
- `pytest -m integration` (integration only)
"""


def amend_tests(struct: structure.Structure, opts):
    # Remove PyScaffold defaults
    struct = structure.reject(struct, "tests/conftest.py")
    struct = structure.reject(struct, "tests/test_skeleton.py")

    # Add Clickstart defaults
    struct = structure.merge(
        struct,
        {
            "tests": {
                "README.md": (_tests_readme, NO_OVERWRITE),
                "unit": {
                    "test_import.py": (_unit_test, SKIP_ON_UPDATE),
                },
                "integration": {
                    "test_layout.py": (_integration_test, SKIP_ON_UPDATE),
                },
            }
        },
    )

    return struct, opts
