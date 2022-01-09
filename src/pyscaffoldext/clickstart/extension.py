from typing import List
from pathlib import Path

from pyscaffold.actions import Action, ActionParams, ScaffoldOpts, Structure
from pyscaffold.extensions import Extension

from pyscaffold.operations import no_overwrite
from pyscaffold.structure import create, merge, reject
from pyscaffold.templates import get_template
from . import templates as my_templates


class Clickstart(Extension):
    """
        This class inherits Extension and creates an extension that uses click as the CLI
        """

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activates See :obj:`pyscaffold.extension.Extension.activate`."""

        actions = self.register(actions, add_file)
        # ^ First an add extension.

        actions = self.register(actions, reject_file)
        # ^ Activate a reject to prevent default skeleton being generated.

        return actions


def add_file(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Adds the click_skeleton template. See :obj:`pyscaffold.actions.Action`"""

    template = get_template("click_skeleton", relative_to=my_templates)

    files: Structure = {
        "src": {opts["package"]: {"click_skeleton.py": (template, no_overwrite(create))}}
    }

    return merge(struct, files), opts


def reject_file(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Rejects the default skeleton template. See :obj:`pyscaffold.actions.Action`"""

    file = Path("src", opts["package"], "skeleton.py")

    return reject(struct, file), opts
