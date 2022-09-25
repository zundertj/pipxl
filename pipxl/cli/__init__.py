# SPDX-FileCopyrightText: 2022-present Jeroen van Zundert <mail@jeroenvanzundert.nl>
#
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import Any, Optional

import typer

from pipxl import compile as pipxl_compile
from pipxl import deptree as pipxl_deptree
from pipxl import deptreerev as pipxl_deptreerev
from pipxl import license as pipxl_license
from pipxl import sync as pipxl_sync
from pipxl.__about__ import __version__

PACKAGE_SPEC_HELP = "Package specification as accepted by pip, for instance `pandas==1.4.3 httpx=0.23.1`."
R_HELP = "Requirements file. Can specify this argument multiple times to take the union of the requirements files."

app = typer.Typer()


@app.command()
def compile(
    package_spec: Optional[list[str]] = typer.Argument(None, help=PACKAGE_SPEC_HELP),
    r: list[Path] = typer.Option(None, help=R_HELP),
    o: Path = typer.Option(Path("requirements_lock.txt")),
) -> None:
    """
    Create pip-compliant requirements file with dependencies and dependencies-of-dependencies pinned.

    Use `pipxl sync` for updating your Python (virtual) environment with this requirements file.
    """
    pipxl_compile(r, package_spec, o)


@app.command()
def sync(
    package_spec: Optional[list[str]] = typer.Argument(None, help=PACKAGE_SPEC_HELP),
    r: Optional[list[Path]] = typer.Option(None, help=R_HELP),
    dry_run: bool = typer.Option(False),
) -> None:
    """
    Bring the active (virtual) environment in sync with the definition.

    Installs package versions not currently in the environment, and uninstalls what is not needed.
    """
    pipxl_sync(r, package_spec, dry_run=dry_run)


@app.command()
def deptree(
    package_spec: Optional[list[str]] = typer.Argument(None, help=PACKAGE_SPEC_HELP),
    r: Optional[list[Path]] = typer.Option(None, help=R_HELP),
) -> None:
    """
    Show dependency tree.

    In square brackets, the definition of the dependency, such as version and platform specifiers, is shown.
    """
    typer.echo(pipxl_deptree(r, package_spec))


@app.command()
def deptreerev(
    package_spec: Optional[list[str]] = typer.Argument(None, help=PACKAGE_SPEC_HELP),
    r: Optional[list[Path]] = typer.Option(None, help=R_HELP),
) -> None:
    """
    Show  dependency tree in reverse, listing for each package the packages that depend on it.

    In square brackets, the definition of the dependency, such as version and platform specifiers, is shown.
    """
    typer.echo(pipxl_deptreerev(r, package_spec))


@app.command()
def license(
    package_spec: Optional[list[str]] = typer.Argument(None, help=PACKAGE_SPEC_HELP),
    r: Optional[list[Path]] = typer.Option(None, help=R_HELP),
) -> None:
    """
    Show licenses of packages, including all dependencies and dependencies of dependencies.

    Information is pulled from PyPi's metadata. Some packages may not have a license uploaded,
    those will be flagged with `*UNKNOWN*`.
    """
    by_lic = pipxl_license(r, package_spec)
    for lic, packages in by_lic.items():
        if lic is None:
            lic = "*UNKNOWN*"
        typer.echo(f"{lic:<20}: {', '.join(packages)}")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def version(
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="List the pipxl package version"
    ),
) -> Any:
    # Do other global stuff, handle other global options here
    return


def main() -> Any:
    return app()
