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

        actions = self.register(actions, add_clickstart_templates)

        actions = self.register(actions, reject_file)
        # ^ Activate a reject to prevent default 'skeleton.py' being generated.

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


def add_clickstart_templates(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    files = {
        "Makefile": (get_template("Makefile", relative_to=my_templates), NO_OVERWRITE),
        "pyproject.toml": (get_template("pyproject.toml", relative_to=my_templates), NO_OVERWRITE),
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
        .option("python_requires", ">=3.9,<3.10")
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
