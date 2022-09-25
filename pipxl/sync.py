# SPDX-FileCopyrightText: 2022-present Jeroen van Zundert <mail@jeroenvanzundert.nl>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import textwrap
from pathlib import Path

import typer

from pipxl.pip_cli import pip_cli
from pipxl.resolver import pip_resolve

pipxl_deps = ["typer", "click"]
PACKAGES_TO_IGNORE = ["pip", "pipxl", *pipxl_deps]


def sync(files_in: list[Path] | None = None, package_spec: list[str] | None = None, dry_run: bool = False) -> None:
    reqs, _ = pip_resolve(files_in, package_spec)
    target_install = [r.name + "==" + r.version for r in reqs]

    installed = get_installed_packages()

    to_install, to_uninstall = merge(target_install, installed)

    if dry_run:
        typer.echo("Would uninstall:")
        typer.echo(textwrap.indent("\n".join(to_uninstall), prefix="\t"))
        typer.echo("Would install")
        typer.echo(textwrap.indent("\n".join(to_install), prefix="\t"))
    else:
        uninstall_packages(to_uninstall)
        install_packages(to_install)


def get_installed_packages() -> list[str]:
    cmd = ["list", "--format=freeze"]
    output = pip_cli(cmd).stdout
    assert isinstance(output, str)
    return output.splitlines()


def install_packages(targets: list[str]) -> None:
    cmd = ["install"] + targets
    pip_cli(cmd)


def uninstall_packages(targets: list[str]) -> None:
    cmd = ["uninstall", "-y"] + targets
    pip_cli(cmd)


def merge(target_install: list[str], installed: list[str]) -> tuple[list[str], list[str]]:
    to_uninstall = set()
    to_install = set()

    for pkg in installed:
        if pkg in target_install:
            continue

        if "==" in pkg and pkg.split("==")[0] in PACKAGES_TO_IGNORE:
            continue

        to_uninstall.add(pkg)

    for pkg in target_install:
        if pkg not in installed:
            to_install.add(pkg)

    return (sorted(list(to_install)), sorted(list(to_uninstall)))
