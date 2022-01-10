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

REQUIREMENT_DEPENDENCIES = ('importlib-metadata; python_version>"3.9"', "click>=8.0")


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

        return actions


def add_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Adds the click_skeleton template. See :obj:`pyscaffold.actions.Action`"""

    template = get_template("click_skeleton", relative_to=my_templates)

    files: Structure = {
        "src": {opts["package"]: {"skeleton.py": (template, NO_OVERWRITE)}},
        "setup.cfg": modify_setupcfg(struct["setup.cfg"], opts),
    }

    return merge(struct, files), opts


def reject_file(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Rejects the default skeleton template. See :obj:`pyscaffold.actions.Action`"""

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

    modifiers = (add_requirements,)
    new_setupcfg = reduce(lambda acc, fn: fn(acc, opts), modifiers, setupcfg)

    return str(new_setupcfg), original_op


def add_requirements(setupcfg: ConfigUpdater, _opts) -> ConfigUpdater:
    """Add [options.install_requires] requirements"""

    requires = setupcfg["options"]
    requires["install_requires"].set_values(REQUIREMENT_DEPENDENCIES)
    return setupcfg
