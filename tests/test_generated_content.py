"""Integration tests validating generated file content and structure.

These tests generate actual scaffolds and verify the resulting files are valid.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
import tomllib
import yaml
from pyscaffold import cli

from pyscaffoldext.clickstart.extension import Clickstart

EXT_FLAGS = [Clickstart().flag]


@pytest.fixture
def generated_project(tmpfolder):
    """Generate a project and return its path."""
    args = ["test_project", "--no-config", "-p", "test_package", *EXT_FLAGS]
    cli.main(args)
    project_path = Path("test_project")
    assert project_path.exists(), "Project should be generated"
    return project_path


class TestGeneratedPythonFiles:
    """Tests validating generated Python files have valid syntax."""

    def test_generated_cli_is_valid_python(self, generated_project):
        """Verify cli.py has valid Python syntax."""
        cli_path = generated_project / "src" / "test_package" / "cli.py"
        assert cli_path.exists(), "cli.py should be generated"

        content = cli_path.read_text(encoding="utf-8")
        # Should compile without SyntaxError
        ast.parse(content)

    def test_generated_api_is_valid_python(self, generated_project):
        """Verify api.py has valid Python syntax."""
        api_path = generated_project / "src" / "test_package" / "api.py"
        assert api_path.exists(), "api.py should be generated"

        content = api_path.read_text(encoding="utf-8")
        ast.parse(content)

    def test_generated_runner_is_valid_python(self, generated_project):
        """Verify __main__.py has valid Python syntax."""
        runner_path = generated_project / "src" / "test_package" / "__main__.py"
        assert runner_path.exists(), "__main__.py should be generated"

        content = runner_path.read_text(encoding="utf-8")
        ast.parse(content)

    def test_generated_init_is_valid_python(self, generated_project):
        """Verify __init__.py has valid Python syntax."""
        init_path = generated_project / "src" / "test_package" / "__init__.py"
        assert init_path.exists(), "__init__.py should be generated"

        content = init_path.read_text(encoding="utf-8")
        ast.parse(content)

    def test_unit_test_is_valid_python(self, generated_project):
        """Verify generated unit test has valid Python syntax."""
        test_path = generated_project / "tests" / "unit" / "test_import.py"
        assert test_path.exists(), "test_import.py should be generated"

        content = test_path.read_text(encoding="utf-8")
        ast.parse(content)

    def test_integration_test_is_valid_python(self, generated_project):
        """Verify generated integration test has valid Python syntax."""
        test_path = generated_project / "tests" / "integration" / "test_layout.py"
        assert test_path.exists(), "test_layout.py should be generated"

        content = test_path.read_text(encoding="utf-8")
        ast.parse(content)


class TestGeneratedConfigFiles:
    """Tests validating generated configuration files are well-formed."""

    def test_generated_pyproject_is_valid_toml(self, generated_project):
        """Verify pyproject.toml is valid TOML."""
        pyproject_path = generated_project / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml should be generated"

        content = pyproject_path.read_text(encoding="utf-8")
        # tomllib.loads will raise on invalid TOML
        data = tomllib.loads(content)

        # Basic structure checks
        assert "build-system" in data
        assert "project" in data
        assert data["project"]["name"] == "test_project"

    def test_pyproject_has_docs_extra_folded_into_dev(self, generated_project):
        """Doc deps live in a `docs` extra that is folded into `dev`."""
        content = (generated_project / "pyproject.toml").read_text(encoding="utf-8")
        data = tomllib.loads(content)
        extras = data["project"]["optional-dependencies"]

        # The `docs` extra is the single source of truth for the doc toolchain.
        assert "docs" in extras, "pyproject.toml should define a `docs` extra"
        docs_deps = " ".join(extras["docs"])
        assert "sphinx" in docs_deps
        assert "myst-parser" in docs_deps

        # `dev` pulls in the docs extra so `make docs` (installs .[dev]) works.
        assert any("[docs]" in dep for dep in extras["dev"]), "`dev` extra should include the project's `[docs]` extra"

    def test_generated_precommit_is_valid_yaml(self, generated_project):
        """Verify .pre-commit-config.yaml is valid YAML."""
        precommit_path = generated_project / ".pre-commit-config.yaml"
        assert precommit_path.exists(), ".pre-commit-config.yaml should be generated"

        content = precommit_path.read_text(encoding="utf-8")
        # yaml.safe_load will raise on invalid YAML
        data = yaml.safe_load(content)

        assert "repos" in data
        assert isinstance(data["repos"], list)

    def test_generated_readthedocs_is_valid_yaml(self, generated_project):
        """Verify .readthedocs.yml is valid YAML."""
        rtd_path = generated_project / ".readthedocs.yml"
        assert rtd_path.exists(), ".readthedocs.yml should be generated"

        content = rtd_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)

        assert data is not None

    def test_readthedocs_installs_docs_extra(self, generated_project):
        """RTD installs the package with its `docs` extra, not requirements.txt."""
        content = (generated_project / ".readthedocs.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(content)

        installs = data["python"]["install"]
        # No reference to the (now removed) docs/requirements.txt.
        assert not any("requirements" in step for step in installs), (
            ".readthedocs.yml should not reference docs/requirements.txt"
        )
        # Installs the package with the `docs` extra.
        extras = [e for step in installs for e in step.get("extras", [])]
        assert "docs" in extras, ".readthedocs.yml should install extras: [docs]"


class TestGeneratedProjectStructure:
    """Tests validating the generated project structure."""

    def test_generated_tests_structure(self, generated_project):
        """Verify tests/unit and tests/integration directories exist."""
        tests_dir = generated_project / "tests"
        assert tests_dir.exists(), "tests/ should exist"

        unit_dir = tests_dir / "unit"
        assert unit_dir.exists(), "tests/unit/ should exist"

        integration_dir = tests_dir / "integration"
        assert integration_dir.exists(), "tests/integration/ should exist"

        # Should have README explaining test structure
        readme = tests_dir / "README.md"
        assert readme.exists(), "tests/README.md should exist"

    def test_generated_docs_structure(self, generated_project):
        """Verify docs/ has all expected files."""
        docs_dir = generated_project / "docs"
        assert docs_dir.exists(), "docs/ should exist"

        expected_files = [
            "index.md",
            "readme.md",
            "authors.md",
            "changelog.md",
            "contributing.md",
            "license.md",
            "conf.py",
        ]

        for filename in expected_files:
            filepath = docs_dir / filename
            assert filepath.exists(), f"docs/{filename} should exist"

    def test_no_docs_requirements_txt(self, generated_project):
        """Doc deps live only in pyproject.toml; no docs/requirements.txt."""
        req = generated_project / "docs" / "requirements.txt"
        assert not req.exists(), "docs/requirements.txt should NOT be generated"

    def test_generated_src_structure(self, generated_project):
        """Verify src/<package>/ has all expected files."""
        src_dir = generated_project / "src" / "test_package"
        assert src_dir.exists(), "src/test_package/ should exist"

        expected_files = [
            "__init__.py",
            "cli.py",
            "api.py",
            "__main__.py",
        ]

        for filename in expected_files:
            filepath = src_dir / filename
            assert filepath.exists(), f"src/test_package/{filename} should exist"


class TestGitignore:
    """Tests for .gitignore content."""

    def test_gitignore_includes_version_file(self, generated_project):
        """Verify .gitignore has _version.py entry."""
        gitignore_path = generated_project / ".gitignore"
        assert gitignore_path.exists(), ".gitignore should be generated"

        content = gitignore_path.read_text(encoding="utf-8")
        assert "src/test_package/_version.py" in content

    def test_gitignore_has_setuptools_scm_comment(self, generated_project):
        """Verify .gitignore has explanatory comment."""
        gitignore_path = generated_project / ".gitignore"
        content = gitignore_path.read_text(encoding="utf-8")
        assert "setuptools_scm" in content.lower() or "setuptools-scm" in content.lower()


class TestRejectedFiles:
    """Tests verifying certain files are NOT generated."""

    def test_no_rst_files_generated(self, generated_project):
        """Verify RST files are rejected/not present."""
        # Root level RST files should not exist
        rst_files = [
            "README.rst",
            "AUTHORS.rst",
            "CHANGELOG.rst",
            "CONTRIBUTING.rst",
        ]
        for filename in rst_files:
            filepath = generated_project / filename
            assert not filepath.exists(), f"{filename} should NOT be generated"

        # docs/ RST files should not exist
        docs_rst_files = [
            "index.rst",
            "readme.rst",
            "authors.rst",
            "changelog.rst",
            "contributing.rst",
            "license.rst",
        ]
        docs_dir = generated_project / "docs"
        for filename in docs_rst_files:
            filepath = docs_dir / filename
            assert not filepath.exists(), f"docs/{filename} should NOT be generated"

    def test_no_setup_py_generated(self, generated_project):
        """Verify setup.py is rejected/not present."""
        setup_py = generated_project / "setup.py"
        assert not setup_py.exists(), "setup.py should NOT be generated"

    def test_no_setup_cfg_generated(self, generated_project):
        """Verify setup.cfg is rejected/not present."""
        setup_cfg = generated_project / "setup.cfg"
        assert not setup_cfg.exists(), "setup.cfg should NOT be generated"

    def test_no_skeleton_py_generated(self, generated_project):
        """Verify skeleton.py is rejected/not present."""
        skeleton = generated_project / "src" / "test_package" / "skeleton.py"
        assert not skeleton.exists(), "skeleton.py should NOT be generated"

    def test_no_default_conftest(self, generated_project):
        """Verify PyScaffold's default tests/conftest.py is rejected."""
        conftest = generated_project / "tests" / "conftest.py"
        # May or may not exist, but if it does, it shouldn't be PyScaffold's default
        if conftest.exists():
            content = conftest.read_text(encoding="utf-8")
            # PyScaffold's default conftest typically has specific content
            # Our extension removes it, so it shouldn't have the default fixture
            assert "capsys" not in content or "custom" in content.lower()

    def test_no_default_test_skeleton(self, generated_project):
        """Verify PyScaffold's default test_skeleton.py is rejected."""
        test_skeleton = generated_project / "tests" / "test_skeleton.py"
        assert not test_skeleton.exists(), "test_skeleton.py should NOT be generated"


class TestMakefile:
    """Tests for generated Makefile."""

    def test_makefile_exists(self, generated_project):
        """Verify Makefile is generated."""
        makefile = generated_project / "Makefile"
        assert makefile.exists(), "Makefile should be generated"

    def test_makefile_has_help_target(self, generated_project):
        """Verify Makefile has help target."""
        makefile = generated_project / "Makefile"
        content = makefile.read_text(encoding="utf-8")
        assert "help:" in content

    def test_makefile_has_test_targets(self, generated_project):
        """Verify Makefile has test-related targets."""
        makefile = generated_project / "Makefile"
        content = makefile.read_text(encoding="utf-8")

        assert "test:" in content
        assert "test-all:" in content

    def test_makefile_has_lint_targets(self, generated_project):
        """Verify Makefile has lint/format targets."""
        makefile = generated_project / "Makefile"
        content = makefile.read_text(encoding="utf-8")

        assert "lint:" in content
        assert "format:" in content

    def test_makefile_stamp_targets_always_run(self, generated_project):
        """Stamp targets carry a FORCE prerequisite so the signature check runs every time.

        Without it an existing stamp file is up to date forever and NO_CACHE=1 or
        edits under src/ and tests/ never trigger a re-run.
        """
        makefile = generated_project / "Makefile"
        content = makefile.read_text(encoding="utf-8")

        assert "FORCE:" in content
        assert "$(UNIT_STAMP): FORCE |" in content
        assert "$(INTEG_STAMP): FORCE |" in content

    def test_makefile_per_tier_coverage_files(self, generated_project):
        """Each tier writes its own coverage file and `test` combines them.

        A shared .coverage wiped by the unit recipe under-reported the aggregated
        coverage whenever only the unit tier re-ran.
        """
        makefile = generated_project / "Makefile"
        content = makefile.read_text(encoding="utf-8")

        assert "rm -f .coverage;" not in content
        assert "COVERAGE_FILE=$(UNIT_COV)" in content
        assert "COVERAGE_FILE=$(INTEG_COV)" in content
        assert "coverage combine --keep $(UNIT_COV) $(INTEG_COV)" in content


class TestDocumentation:
    """Tests for generated documentation files."""

    def test_readme_md_exists(self, generated_project):
        """Verify README.md is generated at root."""
        readme = generated_project / "README.md"
        assert readme.exists(), "README.md should be generated"

    def test_readme_contains_project_name(self, generated_project):
        """Verify README.md contains project name."""
        readme = generated_project / "README.md"
        content = readme.read_text(encoding="utf-8")
        assert "test_project" in content

    def test_docs_conf_is_valid_python(self, generated_project):
        """Verify docs/conf.py is valid Python."""
        conf_path = generated_project / "docs" / "conf.py"
        assert conf_path.exists(), "docs/conf.py should be generated"

        content = conf_path.read_text(encoding="utf-8")
        ast.parse(content)

    def test_docs_conf_has_myst_parser(self, generated_project):
        """Verify docs/conf.py configures MyST-Parser."""
        conf_path = generated_project / "docs" / "conf.py"
        content = conf_path.read_text(encoding="utf-8")
        assert "myst_parser" in content

    def test_docs_conf_ignores_module_all(self, generated_project):
        """conf.py disambiguates __all__ re-exports via ignore-module-all.

        Keeps one canonical autodoc target per object so ``:class:`Thing```
        cross-references resolve when the package __init__ re-exports its API.
        """
        conf_path = generated_project / "docs" / "conf.py"
        content = conf_path.read_text(encoding="utf-8")
        assert "autodoc_default_options" in content
        assert "ignore-module-all" in content
