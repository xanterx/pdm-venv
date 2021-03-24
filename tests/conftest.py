"""Configuration for the pytest test suite."""
import functools
import os

import pytest
from click.testing import CliRunner
from pdm.core import Core
from pdm.utils import cd

from pdm_venv.plugin import Project

DUMMY_PYPROJECT = """[project]
requires-python = ">=3.6"
dependencies = []
"""


@pytest.fixture
def isolated(tmp_path, mocker):
    tmp_path.joinpath("pyproject.toml").write_text(DUMMY_PYPROJECT)
    mocker.patch("pathlib.Path.home", return_value=tmp_path)
    os.environ.pop("VIRTUAL_ENV", None)
    return tmp_path


@pytest.fixture
def project(isolated):
    core = Core()
    core.init_parser()
    core.load_plugins()
    p = Project(isolated)
    p.core = core
    p.global_config["venv.location"] = str(isolated / "venvs")
    p.global_config["venv.backend"] = os.getenv("VENV_BACKEND", "virtualenv")
    return p


@pytest.fixture
def invoke(isolated):
    runner = CliRunner(mix_stderr=False)
    core = Core()
    with cd(isolated):
        (isolated / ".pdm.toml").unlink(True)
        yield functools.partial(runner.invoke, core, prog_name="pdm")
