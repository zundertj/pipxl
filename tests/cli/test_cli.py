# SPDX-FileCopyrightText: 2022-present Jeroen van Zundert <mail@jeroenvanzundert.nl>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

from typer.testing import CliRunner

from pipxl.__about__ import __version__
from pipxl.cli import app

runner = CliRunner()


def test_cli_version() -> None:
    result = runner.invoke(app, "--version")
    assert result.exit_code == 0
    assert result.output == __version__ + "\n"


def test_license() -> None:
    result = runner.invoke(app, "license httpx==0.23.0 requests==2.28.1")
    assert "BSD" in result.output
    assert "Apache" in result.output


def test_sync() -> None:
    result = runner.invoke(app, "sync pandas==1.4.3 --dry-run")
    assert "\tpandas==1.4.3" in result.output.splitlines()


def test_deptree() -> None:
    p = Path(__file__).parent.parent / "requirements.in"
    result = runner.invoke(app, f"deptree --r {p}")
    assert len(result.output.splitlines()) == 20


def test_deptreerev() -> None:
    p = Path(__file__).parent.parent / "requirements.in"
    result = runner.invoke(app, f"deptreerev --r {p}")
    assert len(result.output.splitlines()) == 40


def test_pip_compile() -> None:
    p = Path(__file__).parent.parent / "requirements.in"
    file_out = Path(__file__).parent.parent / "requirements.txt"
    result = runner.invoke(app, f"compile --r {p} --o {file_out}")
    assert result.exit_code == 0
