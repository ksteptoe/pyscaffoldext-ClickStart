"""Place for fixtures and configuration that will be used in most of the tests.
A nice option is to put your ``autouse`` fixtures here.
Functions that can be imported and re-used are more suitable for the ``helpers`` file.
"""
import os
from pathlib import Path
from tempfile import mkdtemp

import pytest

from .helpers import rmpath


# @pytest.fixture
# def tmpfolder(tmp_path):
#     old_path = os.getcwd()
#     new_path = mkdtemp(dir=str(tmp_path))
#     os.chdir(new_path)
#     try:
#         yield Path(new_path)
#     finally:
#         os.chdir(old_path)
#         rmpath(new_path)

@pytest.fixture
def tmpfolder():
    """Fixture to use a known local directory instead of a temporary one."""
    old_path = Path.cwd()
    known_directory = Path(r"C:\Users\Kevin.Steptoe\tmp")

    # Ensure the directory exists ONLY IF it does not exist
    if not known_directory.exists():
        known_directory.mkdir(parents=True)

    # Check if "myproject" exists inside known_directory, and remove it if it does
    myproject_dir = known_directory / "my_project"
    if myproject_dir.exists() and myproject_dir.is_dir():
        rmpath(myproject_dir)

    # Change into the known directory
    os.chdir(known_directory)

    try:
        yield known_directory
    finally:
        # Change back to the original working directory
        os.chdir(old_path)
