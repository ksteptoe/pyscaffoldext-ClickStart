"""Unit tests for pyscaffoldext.clickstart.extension core functions.

Tests individual functions in isolation without generating full scaffolds.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from pyscaffoldext.clickstart.extension import (
    _clickstart_version,
    _integration_test_layout,
    _substitute_brace_vars,
    _tests_readme,
    _unit_test_import,
    modify_gitignore,
)


class TestSubstituteBraceVars:
    """Tests for _substitute_brace_vars template variable substitution."""

    def test_project_name_double_spaced(self):
        """Test {{ project_name }} replacement."""
        opts = {"project": "my-project", "package": "my_package"}
        text = "Project: {{ project_name }}"
        result = _substitute_brace_vars(text, opts)
        assert result == "Project: my-project"

    def test_project_name_no_space(self):
        """Test {{project_name}} replacement without spaces."""
        opts = {"project": "my-project", "package": "my_package"}
        text = "Project: {{project_name}}"
        result = _substitute_brace_vars(text, opts)
        assert result == "Project: my-project"

    def test_package_name_double_spaced(self):
        """Test {{ package_name }} replacement."""
        opts = {"project": "my-project", "package": "my_package"}
        text = "Package: {{ package_name }}"
        result = _substitute_brace_vars(text, opts)
        assert result == "Package: my_package"

    def test_package_name_no_space(self):
        """Test {{package_name}} replacement without spaces."""
        opts = {"project": "my-project", "package": "my_package"}
        text = "Package: {{package_name}}"
        result = _substitute_brace_vars(text, opts)
        assert result == "Package: my_package"

    def test_pascal_case_project_name(self):
        """Test {{ ProjectName }} and {{ProjectName}} replacement."""
        opts = {"project": "my-project", "package": "my_package"}
        text = "{{ ProjectName }} {{ProjectName}}"
        result = _substitute_brace_vars(text, opts)
        assert result == "my-project my-project"

    def test_pascal_case_package_name(self):
        """Test {{ PackageName }} and {{PackageName}} replacement."""
        opts = {"project": "my-project", "package": "my_package"}
        text = "{{ PackageName }} {{PackageName}}"
        result = _substitute_brace_vars(text, opts)
        assert result == "my_package my_package"

    def test_short_package_placeholder(self):
        """Test {{package}} replacement."""
        opts = {"project": "my-project", "package": "my_package"}
        text = "import {{package}}"
        result = _substitute_brace_vars(text, opts)
        assert result == "import my_package"

    def test_multiple_replacements(self):
        """Test multiple placeholders in same text."""
        opts = {"project": "my-project", "package": "my_package"}
        text = "{{ project_name }} uses {{ package_name }}"
        result = _substitute_brace_vars(text, opts)
        assert result == "my-project uses my_package"

    def test_special_characters_in_project_name(self):
        """Test project name with various special characters."""
        opts = {"project": "my_project-123", "package": "my_package_123"}
        text = "{{ project_name }}"
        result = _substitute_brace_vars(text, opts)
        assert result == "my_project-123"

    def test_fallback_to_project_name_key(self):
        """Test fallback when using 'project_name' key instead of 'project'."""
        opts = {"project_name": "alt-project", "package": "alt_package"}
        text = "{{ project_name }}"
        result = _substitute_brace_vars(text, opts)
        assert result == "alt-project"

    def test_fallback_to_name_key(self):
        """Test fallback when using 'name' key."""
        opts = {"name": "named-project"}
        text = "{{ project_name }}"
        result = _substitute_brace_vars(text, opts)
        assert result == "named-project"

    def test_package_fallback_to_package_name_key(self):
        """Test package fallback when using 'package_name' key."""
        opts = {"project": "my-project", "package_name": "alt_pkg"}
        text = "{{ package_name }}"
        result = _substitute_brace_vars(text, opts)
        assert result == "alt_pkg"

    def test_package_derived_from_project(self):
        """Test package name derived from project when not specified."""
        opts = {"project": "my-project"}
        text = "{{ package_name }}"
        result = _substitute_brace_vars(text, opts)
        assert result == "my_project"

    def test_empty_opts_uses_defaults(self):
        """Test with empty opts uses default 'project'."""
        opts = {}
        text = "{{ project_name }} {{ package_name }}"
        result = _substitute_brace_vars(text, opts)
        assert result == "project project"

    def test_no_placeholders_unchanged(self):
        """Test text without placeholders is unchanged."""
        opts = {"project": "my-project", "package": "my_package"}
        text = "No placeholders here"
        result = _substitute_brace_vars(text, opts)
        assert result == "No placeholders here"


class TestModifyGitignore:
    """Tests for modify_gitignore function."""

    def test_adds_version_file_to_existing_gitignore(self):
        """Test adding version file line to existing .gitignore."""
        definition = ("*.pyc\n__pycache__/\n", None)
        opts = {"project": "my-project", "package": "my_package"}

        result, _op = modify_gitignore(definition, opts)

        assert "src/my_package/_version.py" in result
        assert "# Generated by setuptools_scm" in result
        assert "*.pyc" in result

    def test_creates_gitignore_from_scratch(self):
        """Test creating .gitignore content when definition is empty."""
        definition = (None, None)
        opts = {"project": "my-project", "package": "my_package"}

        result, _op = modify_gitignore(definition, opts)

        assert "src/my_package/_version.py" in result
        assert "# Generated by setuptools_scm" in result

    def test_idempotent_does_not_duplicate(self):
        """Test that running twice doesn't duplicate the version line."""
        definition = (
            "*.pyc\n# Generated by setuptools_scm\nsrc/my_package/_version.py\n",
            None,
        )
        opts = {"project": "my-project", "package": "my_package"}

        result, _op = modify_gitignore(definition, opts)

        # Count occurrences - should be exactly one
        assert result.count("src/my_package/_version.py") == 1

    def test_adds_newline_if_missing(self):
        """Test that newline is added if content doesn't end with one."""
        definition = ("*.pyc", None)  # No trailing newline
        opts = {"project": "my-project", "package": "my_package"}

        result, _op = modify_gitignore(definition, opts)

        # Should have proper newline separation
        assert "*.pyc\n# Generated" in result

    def test_preserves_original_operation(self):
        """Test that the original operation is preserved."""
        mock_op = MagicMock()
        definition = ("*.pyc\n", mock_op)
        opts = {"project": "my-project", "package": "my_package"}

        _result, op = modify_gitignore(definition, opts)

        assert op is mock_op

    def test_package_derived_from_project(self):
        """Test package name derived from project with hyphen conversion."""
        definition = ("", None)
        opts = {"project": "my-cool-project"}

        result, _op = modify_gitignore(definition, opts)

        assert "src/my_cool_project/_version.py" in result


class TestTestsReadme:
    """Tests for _tests_readme function."""

    def test_contains_readme_header(self):
        """Test that output contains # Tests header."""
        opts = {"project": "test-project", "package": "test_package"}
        result = _tests_readme(opts)
        assert "# Tests" in result

    def test_contains_unit_tests_section(self):
        """Test that output describes unit tests."""
        opts = {}
        result = _tests_readme(opts)
        assert "tests/unit/" in result
        assert "fast" in result.lower()

    def test_contains_integration_tests_section(self):
        """Test that output describes integration tests."""
        opts = {}
        result = _tests_readme(opts)
        assert "tests/integration/" in result

    def test_contains_run_commands(self):
        """Test that output contains pytest run commands."""
        opts = {}
        result = _tests_readme(opts)
        assert "pytest" in result
        assert 'pytest -m "not integration"' in result
        assert "pytest -m integration" in result


class TestUnitTestImport:
    """Tests for _unit_test_import function."""

    def test_contains_package_import(self):
        """Test that output imports the correct package."""
        opts = {"package": "my_package"}
        result = _unit_test_import(opts)
        assert 'import_module("my_package")' in result

    def test_is_valid_python(self):
        """Test that output is valid Python syntax."""
        opts = {"package": "test_pkg"}
        result = _unit_test_import(opts)
        # Should compile without SyntaxError
        compile(result, "<test>", "exec")

    def test_contains_test_function(self):
        """Test that output contains a test function."""
        opts = {"package": "my_package"}
        result = _unit_test_import(opts)
        assert "def test_package_importable" in result

    def test_uses_importlib(self):
        """Test that output uses importlib module."""
        opts = {"package": "my_package"}
        result = _unit_test_import(opts)
        assert "import importlib" in result


class TestIntegrationTestLayout:
    """Tests for _integration_test_layout function."""

    def test_contains_package_path_check(self):
        """Test that output checks for package path."""
        opts = {"package": "my_package"}
        result = _integration_test_layout(opts)
        assert '"my_package"' in result or "'my_package'" in result

    def test_is_valid_python(self):
        """Test that output is valid Python syntax."""
        opts = {"package": "test_pkg"}
        result = _integration_test_layout(opts)
        # Should compile without SyntaxError
        compile(result, "<test>", "exec")

    def test_contains_integration_marker(self):
        """Test that output uses pytest.mark.integration."""
        opts = {"package": "my_package"}
        result = _integration_test_layout(opts)
        assert "@pytest.mark.integration" in result

    def test_contains_pyproject_check(self):
        """Test that output checks for pyproject.toml."""
        opts = {"package": "my_package"}
        result = _integration_test_layout(opts)
        assert "pyproject.toml" in result

    def test_contains_test_function(self):
        """Test that output contains a test function."""
        opts = {"package": "my_package"}
        result = _integration_test_layout(opts)
        assert "def test_project_layout_exists" in result


class TestClickstartVersion:
    """Tests for _clickstart_version function."""

    def test_returns_string(self):
        """Test that function returns a string."""
        result = _clickstart_version()
        assert isinstance(result, str)

    def test_returns_non_empty(self):
        """Test that function returns non-empty string."""
        result = _clickstart_version()
        assert len(result) > 0

    @patch("pyscaffoldext.clickstart.extension.packages_distributions")
    @patch("pyscaffoldext.clickstart.extension.dist_version")
    def test_uses_installed_version(self, mock_dist_version, mock_packages_dist):
        """Test that function tries to get installed distribution version."""
        mock_packages_dist.return_value = {"pyscaffoldext": ["pyscaffoldext-clickstart"]}
        mock_dist_version.return_value = "1.2.3"

        result = _clickstart_version()

        assert result == "1.2.3"
        mock_dist_version.assert_called_once_with("pyscaffoldext-clickstart")

    @patch("pyscaffoldext.clickstart.extension.packages_distributions")
    def test_fallback_on_missing_distribution(self, mock_packages_dist):
        """Test fallback when distribution is not found."""
        mock_packages_dist.return_value = {}

        result = _clickstart_version()

        # Should return something (either from _version.py or "unknown")
        assert isinstance(result, str)

    @patch("pyscaffoldext.clickstart.extension.packages_distributions")
    @patch("pyscaffoldext.clickstart.extension.dist_version")
    def test_fallback_on_version_error(self, mock_dist_version, mock_packages_dist):
        """Test fallback when version lookup raises exception."""
        mock_packages_dist.return_value = {"pyscaffoldext": ["pyscaffoldext-clickstart"]}
        mock_dist_version.side_effect = Exception("Version not found")

        result = _clickstart_version()

        # Should not raise, returns fallback
        assert isinstance(result, str)
