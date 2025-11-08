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

# --------------------------------------------------------------------------- #
# Global constants
# --------------------------------------------------------------------------- #

NO_OVERWRITE = no_overwrite()

# For backward compatibility only — safe to remove once setup.cfg is deprecated
REQUIREMENT_DEPENDENCIES = (
    "click>=8.1",
    "pytest>=8",
    "pytest-cov>=5",
)

PYTHON_REQUIRES = "python_requires = >=3.12"

# --------------------------------------------------------------------------- #
# Template & scaffold injection
# --------------------------------------------------------------------------- #
def add_clickstart_templates(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Add rendered project templates like Makefile, pyproject.toml, and pre-commit config."""

    from pyscaffold.structure import reify_content

    # --- Load templates ---------------------------------------------------
    makefile_tmpl = get_template("Makefile", relative_to=my_templates)
    pyproject_tmpl = get_template("pyproject.toml", relative_to=my_templates)
    precommit_tmpl = get_template(".pre-commit-config.yaml", relative_to=my_templates)

    # --- Render templates with project variables -------------------------
    makefile = reify_content(makefile_tmpl, opts)
    pyproject = reify_content(pyproject_tmpl, opts)
    precommit = reify_content(precommit_tmpl, opts)

    # --- Register rendered files into structure --------------------------
    files = {
        "Makefile": (makefile, no_overwrite()),
        "pyproject.toml": (pyproject, no_overwrite()),
        ".pre-commit-config.yaml": (precommit, no_overwrite()),
    }

    # Remove legacy setup.cfg if PyScaffold created one
    struct.pop("setup.cfg", None)

    return merge(struct, files), opts





class Clickstart(Extension):
    """Main entry point for the Clickstart PyScaffold extension."""

    def activate(self, actions: List[Action]) -> List[Action]:
        """Register custom actions to extend PyScaffold’s default behaviour."""
        actions = self.register(actions, add_files)
        actions = self.register(actions, add_clickstart_templates)
        actions = self.register(actions, reject_file)
        return actions


def add_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Add CLI, API, runner, and test scaffold templates."""

    cli_template = get_template("cli", relative_to=my_templates)
    api_template = get_template("api", relative_to=my_templates)
    runner_template = get_template("runner", relative_to=my_templates)
    conftest_template = get_template("conftest", relative_to=my_templates)

    # Only include setup.cfg if it exists (for backward compatibility)
    setup_cfg_entry = {}
    if "setup.cfg" in struct:
        setup_cfg_entry = {"setup.cfg": modify_setupcfg(struct["setup.cfg"], opts)}

    files: Structure = {
        "src": {
            opts["package"]: {
                "cli.py": (cli_template, NO_OVERWRITE),
                "api.py": (api_template, NO_OVERWRITE),
            }
        },
        "__main__.py": (runner_template, NO_OVERWRITE),
        "tests": {"conftest.py": (conftest_template, NO_OVERWRITE)},
        **setup_cfg_entry,
    }

    return merge(struct, files), opts


def reject_file(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Reject the default skeleton file from PyScaffold."""
    file = Path("src", opts["package"], "skeleton.py")
    return reject(struct, file), opts


# --------------------------------------------------------------------------- #
# setup.cfg modification (legacy mode only)
# --------------------------------------------------------------------------- #
def modify_setupcfg(definition: Leaf, opts: ScaffoldOpts) -> ResolvedLeaf:
    """Modify setup.cfg to inject dependencies and entry points."""
    contents, original_op = resolve_leaf(definition)
    if contents is None:
        raise ValueError("File contents for setup.cfg should not be None")

    setupcfg = ConfigUpdater()
    setupcfg.read_string(reify_content(contents, opts))

    modifiers = (add_install_requires, py_requires, add_entry_point)
    new_setupcfg = reduce(lambda acc, fn: fn(acc, opts), modifiers, setupcfg)
    return str(new_setupcfg), original_op


def add_install_requires(setupcfg: ConfigUpdater, _opts) -> ConfigUpdater:
    """Add install_requires dependencies."""
    requires = setupcfg["options"]
    requires["install_requires"].set_values(REQUIREMENT_DEPENDENCIES)
    return setupcfg


def py_requires(setupcfg: ConfigUpdater, _opts) -> ConfigUpdater:
    """Ensure the correct Python version requirement."""
    (
        setupcfg["options"]["install_requires"]
        .add_before.comment("# Minimum Python Version 3.12 required")
        .option("python_requires", ">=3.12,<3.13")
    )
    return setupcfg


def add_entry_point(setupcfg: ConfigUpdater, opts: ScaffoldOpts) -> ConfigUpdater:
    """Adds the console entry point to setup.cfg."""
    entry_points_key = "options.entry_points"

    if not setupcfg.has_section(entry_points_key):
        setupcfg["options"].add_after.section(entry_points_key)

    entry_points = setupcfg[entry_points_key]
    entry_points.insert_at(0).option("console_scripts")
    template = "{package} = {package}.cli:cli"
    value = template.format(**opts)
    entry_points["console_scripts"].set_values([value])
    return setupcfg
