from functools import reduce
from pathlib import Path
from typing import List

from pyscaffold.actions import Action, ActionParams, ScaffoldOpts, Structure
from pyscaffold.extensions import Extension
from pyscaffold.operations import no_overwrite
from pyscaffold.structure import (
    Leaf,
    ResolvedLeaf,
    merge,
    reify_content,
    reject,
    resolve_leaf,
)
from pyscaffold.templates import get_template
from pyscaffold.update import ConfigUpdater

from . import templates as my_templates

NO_OVERWRITE = no_overwrite()

REQUIREMENT_DEPENDENCIES = ('importlib-metadata; python_version>"3.9"',
                            "click>=8.0",
                            'pytest',
                            'pytest-cov',
                            )
PYTHON_REQUIRES = "python_requires = >=3.9"


class Clickstart(Extension):
    """
    This creates an extension that uses click as the CLI
    """

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activates See :obj:`pyscaffold.extension.Extension.activate`."""

        actions = self.register(actions, add_files)
        # ^ First an add extension and add template.

        actions = self.register(actions, reject_file)
        # ^ Activate a reject to prevent default 'skeleton.py' being generated.

        actions = self.register(actions, modify_pyproject_toml)
        # ^ Adds Black settings

        actions = self.register(actions, modify_gitignore)
        # ^ Adds _version.py to .gitignore

        # actions = self.register(actions, modify_setup_py)
        # ^ Updates use_scm_version in setup.py

        actions = self.register(actions, remove_setup_py)
        # ^ Prevents setup.py from being created

        return actions


def add_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Adds the click_skeleton template in cli
       Adds api_skeleton
       __main__.py as a runner
    See :obj:`pyscaffold.actions.Action`"""

    cli_template = get_template("cli", relative_to=my_templates)
    api_template = get_template("api", relative_to=my_templates)
    runner_template = get_template('runner', relative_to=my_templates)
    conftest_template = get_template('conftest', relative_to=my_templates)
    files: Structure = {
        "src": {opts["package"]: {'cli.py': (cli_template, NO_OVERWRITE),
                                  'api.py': (api_template, NO_OVERWRITE)}},
        "__main__.py": (runner_template, NO_OVERWRITE),
        "setup.cfg": modify_setupcfg(struct["setup.cfg"], opts),
        "tests": {'conftest.py': (conftest_template, NO_OVERWRITE)}
    }

    return merge(struct, files), opts


def reject_file(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Rejects the default skeleton template.
    See :obj:`pyscaffold.actions.Action`"""

    file = Path("src", opts["package"], "skeleton.py")

    return reject(struct, file), opts


def modify_setupcfg(definition: Leaf, opts: ScaffoldOpts) -> ResolvedLeaf:
    """Modify setup.cfg to add install_requires and pytest settings before it is
    written.
    See :obj:`pyscaffold.operations`.
    """
    contents, original_op = resolve_leaf(definition)

    if contents is None:
        raise ValueError("File contents for setup.cfg should not be None")

    setupcfg = ConfigUpdater()
    setupcfg.read_string(reify_content(contents, opts))

    modifiers = (add_install_requires, py_requires, add_entry_point)
    new_setupcfg = reduce(lambda acc, fn: fn(acc, opts), modifiers, setupcfg)

    return str(new_setupcfg), original_op


def add_install_requires(setupcfg: ConfigUpdater, _opts) -> ConfigUpdater:
    """Add [options.install_requires] requirements"""
    requires = setupcfg["options"]
    requires["install_requires"].set_values(REQUIREMENT_DEPENDENCIES)
    return setupcfg


def py_requires(setupcfg: ConfigUpdater, _opts) -> ConfigUpdater:
    """Replace
    # python_requires = >=3.8
        with
    python_requires = >=3.9"""
    (
        setupcfg["options"]["install_requires"]
        .add_before.comment("# Minimum Python Version 3.9 required")
        .option("python_requires", ">=3.9,<3.13")
    )

    return setupcfg


def add_entry_point(setupcfg: ConfigUpdater, opts: ScaffoldOpts) -> ConfigUpdater:
    """Adds the extension's entry_point to setup.cfg"""
    entry_points_key = "options.entry_points"

    if not setupcfg.has_section(entry_points_key):
        setupcfg["options"].add_after.section(entry_points_key)

    entry_points = setupcfg[entry_points_key]
    entry_points.insert_at(0).option("console_scripts")
    template = "{package} = {package}.cli:cli"
    value = template.format(file_name="py", **opts)
    entry_points["console_scripts"].set_values([value])

    return setupcfg

def modify_pyproject_toml(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Modify pyproject.toml to add Black, setuptools_scm, and pytest configuration with extra spacing."""

    toml_path = "pyproject.toml"

    # Check if pyproject.toml is in struct
    if toml_path not in struct:
        return struct, opts  # Skip modification if missing

    # Resolve the leaf to get actual contents
    contents, original_op = resolve_leaf(struct[toml_path])

    # Ensure contents are resolved correctly using `reify_content`
    contents = reify_content(contents, opts)

    # Ensure we have a valid string
    if not isinstance(contents, str):
        raise TypeError(f"Expected string for {toml_path}, got {type(contents).__name__}")

    # Parse the existing pyproject.toml
    pyproject = ConfigUpdater()
    pyproject.read_string(contents)

    # Get the package name dynamically from opts
    package_name = opts["package"]
    write_to_path = f'src/{package_name}/_version.py'  # Correct path

    # --- Add setuptools_scm settings ---
    if not pyproject.has_section("tool.setuptools_scm"):
        pyproject.add_section("tool.setuptools_scm")

    pyproject["tool.setuptools_scm"].set("version_scheme", '"guess-next-dev"')
    pyproject["tool.setuptools_scm"].set("local_scheme", '"node-and-date"')
    pyproject["tool.setuptools_scm"].set("write_to", f'"{write_to_path}"')

    # Force a blank line after [tool.setuptools_scm]
    pyproject["tool.setuptools_scm"].add_after.space(1)

    # --- Add Black settings ---
    if not pyproject.has_section("tool.black"):
        pyproject.add_section("tool.black")

    pyproject["tool.black"].set("line-length", "120")
    pyproject["tool.black"].set("target-version", '["py312"]')
    pyproject["tool.black"].set("skip-string-normalization", "true")

    # Force a blank line after [tool.black]
    pyproject["tool.black"].add_after.space(1)

    # --- Add Pytest settings ---
    if not pyproject.has_section("tool.pytest.ini_options"):
        pyproject.add_section("tool.pytest.ini_options")

    pyproject["tool.pytest.ini_options"].set("log_cli", "true")
    pyproject["tool.pytest.ini_options"].set("log_cli_level", '"INFO"')
    pyproject["tool.pytest.ini_options"].set("log_cli_format", '"%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"')
    pyproject["tool.pytest.ini_options"].set("log_cli_date_format", '"%d/%m/%Y %H:%M:%S"')

    # Modify struct to apply changes before writing
    struct[toml_path] = (str(pyproject), original_op)

    return struct, opts

from pyscaffold.structure import resolve_leaf, reify_content

def modify_setup_py(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Modify setup.py to update use_scm_version setting."""

    setup_path = "setup.py"

    # Check if setup.py exists in struct
    if setup_path not in struct:
        return struct, opts  # Skip modification if setup.py is missing

    # Resolve the leaf to get actual contents
    contents, original_op = resolve_leaf(struct[setup_path])

    # Ensure contents are resolved correctly using `reify_content`
    contents = reify_content(contents, opts)

    # Ensure we have a valid string
    if not isinstance(contents, str):
        raise TypeError(f"Expected string for {setup_path}, got {type(contents).__name__}")

    # Replace the specific line
    updated_contents = contents.replace(
        'setup(use_scm_version={"version_scheme": "no-guess-dev"})',
        'setup(use_scm_version=True)  # Removed explicit "no-guess-dev"'
    )

    # Modify struct to apply changes before writing
    struct[setup_path] = (updated_contents, original_op)

    return struct, opts


def remove_setup_py(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Prevent setup.py from being generated."""
    setup_path = Path("setup.py")

    return reject(struct, setup_path), opts

def modify_gitignore(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Modify .gitignore to include src/{package}/_version.py"""

    gitignore_path = ".gitignore"

    # Check if .gitignore exists in struct
    if gitignore_path not in struct:
        return struct, opts  # Skip modification if missing

    # Resolve the leaf to get actual contents
    contents, original_op = resolve_leaf(struct[gitignore_path])

    # Ensure contents are resolved correctly using `reify_content`
    contents = reify_content(contents, opts)

    # Ensure we have a valid string
    if not isinstance(contents, str):
        raise TypeError(f"Expected string for {gitignore_path}, got {type(contents).__name__}")

    # Get the package name dynamically
    package_name = opts["package"]
    version_file = f"src/{package_name}/_version.py"

    # Check if _version.py is already ignored
    if version_file in contents:
        return struct, opts  # Skip modification if already present

    # Append the ignore rule at the end of the file
    updated_contents = contents.strip() + f"\n{version_file}\n"

    # Modify struct to apply changes before writing
    struct[gitignore_path] = (updated_contents, original_op)

    return struct, opts


