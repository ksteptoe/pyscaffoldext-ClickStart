# tests/conftest.py
from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture
def tmpfolder(tmp_path: Path):
    """Use a writable temp directory; allow override via CLICKSTART_TMP."""
    old_path = Path.cwd()

    # Optional override if you really want a stable path:
    override = os.environ.get("CLICKSTART_TMP")
    workdir = Path(override) if override else tmp_path

    workdir.mkdir(parents=True, exist_ok=True)
    os.chdir(workdir)
    try:
        yield workdir
    finally:
       os.chdir(old_path)

