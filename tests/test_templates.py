"""Tests for template variable substitution and rendering.

Validates that template placeholders are correctly replaced with project values.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pyscaffold import cli

from pyscaffoldext.clickstart.extension import Clickstart

EXT_FLAGS = [Clickstart().flag]


@pytest.fixture
def generated_project(tmpfolder):
    """Generate a project and return its path."""
    args = ["my_cool_project", "--no-config", "-p", "my_cool_package", *EXT_FLAGS]
    cli.main(args)
    project_path = Path("my_cool_project")
    assert project_path.exists(), "Project should be generated"
    return project_path


@pytest.fixture
def hyphenated_project(tmpfolder):
    """Generate a project with hyphens to test name conversion."""
    args = ["my-hyphenated-project", "--no-config", *EXT_FLAGS]
    cli.main(args)
    project_path = Path("my-hyphenated-project")
    assert project_path.exists(), "Project should be generated"
    return project_path


class TestMakefileVariables:
    """Tests for Makefile variable substitution."""

    def test_makefile_dist_variable_substituted(self, generated_project):
        """Test that DIST variable has project name."""
        makefile = generated_project / "Makefile"
        content = makefile.read_text()

        # Should have DIST := my_cool_project
        assert "DIST := my_cool_project" in content

    def test_makefile_pkg_variable_substituted(self, generated_project):
        """Test that PKG variable has package name."""
        makefile = generated_project / "Makefile"
        content = makefile.read_text()

        # Should have PKG := my_cool_package
        assert "PKG  := my_cool_package" in content

    def test_makefile_no_brace_vars_remain(self, generated_project):
        """Test that no template placeholders remain in Makefile."""
        makefile = generated_project / "Makefile"
        content = makefile.read_text()

        # No {{ }} placeholders should remain
        assert "{{ " not in content
        assert "{{" not in content
        assert " }}" not in content

    def test_makefile_code_dirs_uses_pkg_variable(self, generated_project):
        """Test that CODE_DIRS uses the PKG Make variable."""
        makefile = generated_project / "Makefile"
        content = makefile.read_text()

        # CODE_DIRS uses the Make PKG variable, not the literal package name
        assert "CODE_DIRS  := src/$(PKG)" in content


class TestMakefileWithHyphenatedProject:
    """Test Makefile with hyphenated project name."""

    def test_hyphenated_project_dist_preserved(self, hyphenated_project):
        """Test that DIST keeps hyphens for project name."""
        makefile = hyphenated_project / "Makefile"
        content = makefile.read_text()

        # DIST should keep hyphens
        assert "DIST := my-hyphenated-project" in content

    def test_hyphenated_project_pkg_converted(self, hyphenated_project):
        """Test that PKG converts hyphens to underscores."""
        makefile = hyphenated_project / "Makefile"
        content = makefile.read_text()

        # PKG should convert hyphens to underscores
        assert "PKG  := my_hyphenated_project" in content


class TestPyprojectTomlVariables:
    """Tests for pyproject.toml variable substitution."""

    def test_pyproject_project_name_substituted(self, generated_project):
        """Test that project name is substituted in pyproject.toml."""
        pyproject = generated_project / "pyproject.toml"
        content = pyproject.read_text()

        assert 'name = "my_cool_project"' in content

    def test_pyproject_scripts_entry_substituted(self, generated_project):
        """Test that scripts entry point is substituted."""
        pyproject = generated_project / "pyproject.toml"
        content = pyproject.read_text()

        assert 'my_cool_project = "my_cool_package.cli:cli"' in content

    def test_pyproject_scm_write_to_substituted(self, generated_project):
        """Test that setuptools_scm write_to path is substituted."""
        pyproject = generated_project / "pyproject.toml"
        content = pyproject.read_text()

        assert 'write_to = "src/my_cool_package/_version.py"' in content

    def test_pyproject_coverage_source_substituted(self, generated_project):
        """Test that coverage source is substituted."""
        pyproject = generated_project / "pyproject.toml"
        content = pyproject.read_text()

        assert 'source = ["my_cool_package"]' in content

    def test_pyproject_no_brace_vars_remain(self, generated_project):
        """Test that no template placeholders remain."""
        pyproject = generated_project / "pyproject.toml"
        content = pyproject.read_text()

        assert "{{ " not in content
        assert "{{" not in content


class TestReadmeVariables:
    """Tests for README.md variable substitution."""

    def test_readme_project_name_in_title(self, generated_project):
        """Test that project name appears in README title."""
        readme = generated_project / "README.md"
        content = readme.read_text()

        # Title should be the project name
        assert "# my_cool_project" in content

    def test_readme_package_in_usage(self, generated_project):
        """Test that package name appears in usage section."""
        readme = generated_project / "README.md"
        content = readme.read_text()

        # Usage should reference the package
        assert "my_cool_package" in content

    def test_readme_no_dollar_vars_remain(self, generated_project):
        """Test that no ${var} placeholders remain."""
        readme = generated_project / "README.md"
        content = readme.read_text()

        # PyScaffold uses ${name}, ${package}, etc.
        # These should all be substituted
        assert "${name}" not in content
        assert "${package}" not in content


class TestCliTemplateVariables:
    """Tests for CLI template package name substitution."""

    def test_cli_imports_correct_package(self, generated_project):
        """Test that cli.py imports the correct package."""
        cli_path = generated_project / "src" / "my_cool_package" / "cli.py"
        content = cli_path.read_text()

        assert "from .api import my_cool_package_api" in content

    def test_cli_calls_api_function(self, generated_project):
        """Test that cli.py calls the correct API function."""
        cli_path = generated_project / "src" / "my_cool_package" / "cli.py"
        content = cli_path.read_text()

        assert "my_cool_package_api(" in content

    def test_cli_no_dollar_vars_remain(self, generated_project):
        """Test that no ${var} placeholders remain in cli.py."""
        cli_path = generated_project / "src" / "my_cool_package" / "cli.py"
        content = cli_path.read_text()

        assert "${package}" not in content
        assert "${qual_pkg}" not in content


class TestApiTemplateVariables:
    """Tests for API template package name substitution."""

    def test_api_function_name_substituted(self, generated_project):
        """Test that api.py has correctly named function."""
        api_path = generated_project / "src" / "my_cool_package" / "api.py"
        content = api_path.read_text()

        assert "def my_cool_package_api(" in content


class TestDocsConfVariables:
    """Tests for docs/conf.py variable substitution."""

    def test_docs_conf_project_name(self, generated_project):
        """Test that Sphinx config has correct project name."""
        conf_path = generated_project / "docs" / "conf.py"
        content = conf_path.read_text()

        assert 'project = "my_cool_project"' in content

    def test_docs_conf_module_dir(self, generated_project):
        """Test that Sphinx config has correct module directory."""
        conf_path = generated_project / "docs" / "conf.py"
        content = conf_path.read_text()

        assert '"../src/my_cool_package"' in content

    def test_docs_conf_htmlhelp_basename(self, generated_project):
        """Test that htmlhelp_basename is substituted."""
        conf_path = generated_project / "docs" / "conf.py"
        content = conf_path.read_text()

        assert 'htmlhelp_basename = "my_cool_project-doc"' in content

    def test_docs_conf_no_dollar_vars_remain(self, generated_project):
        """Test that no ${var} placeholders remain."""
        conf_path = generated_project / "docs" / "conf.py"
        content = conf_path.read_text()

        assert "${name}" not in content
        assert "${package}" not in content


class TestPreCommitVariables:
    """Tests for .pre-commit-config.yaml content."""

    def test_precommit_has_ruff_hook(self, generated_project):
        """Test that pre-commit config includes Ruff."""
        precommit = generated_project / ".pre-commit-config.yaml"
        content = precommit.read_text()

        assert "ruff" in content.lower()


class TestGitignoreVariables:
    """Tests for .gitignore variable substitution."""

    def test_gitignore_has_correct_package_path(self, generated_project):
        """Test that .gitignore references correct package."""
        gitignore = generated_project / ".gitignore"
        content = gitignore.read_text()

        assert "src/my_cool_package/_version.py" in content


class TestTestsReadmeContent:
    """Tests for tests/README.md content."""

    def test_tests_readme_structure(self, generated_project):
        """Test that tests README explains directory structure."""
        readme = generated_project / "tests" / "README.md"
        content = readme.read_text()

        assert "unit" in content
        assert "integration" in content


class TestUnitTestVariables:
    """Tests for generated unit test package name substitution."""

    def test_unit_test_imports_package(self, generated_project):
        """Test that unit test imports correct package."""
        test_path = generated_project / "tests" / "unit" / "test_import.py"
        content = test_path.read_text()

        assert '"my_cool_package"' in content


class TestIntegrationTestVariables:
    """Tests for generated integration test package name substitution."""

    def test_integration_test_checks_package(self, generated_project):
        """Test that integration test checks correct package path."""
        test_path = generated_project / "tests" / "integration" / "test_layout.py"
        content = test_path.read_text()

        assert '"my_cool_package"' in content
