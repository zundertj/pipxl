# SPDX-FileCopyrightText: 2022-present Jeroen van Zundert <mail@jeroenvanzundert.nl>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import textwrap
from pathlib import Path

from pipxl.data import ReqFileEntry
from pipxl.resolver import pip_resolve


def deptree(files_in: list[Path] | None = None, package_spec: list[str] | None = None) -> str:
    reqs, _ = pip_resolve(files_in, package_spec)

    top_level = [req for req in reqs if req.requested]

    output = ""
    for req in top_level:
        output += f"{req.name}=={req.version}\n"
        output += textwrap.indent(_deps_to_string(req.requires, reqs), prefix="\t")

    return output


def deptreerev(files_in: list[Path] | None = None, package_spec: list[str] | None = None) -> str:
    reqs, _ = pip_resolve(files_in, package_spec)

    output = ""
    for req in reqs:
        output += f"{req.name}=={req.version}\n"
        output += textwrap.indent(_reverse_deps_to_string(req.required_by, reqs), prefix="\t")
    return output


def _deps_to_string(deps: dict[str, str], reqs: list[ReqFileEntry]) -> str:
    output = ""
    for dep_name, dep_spec in deps.items():
        try:
            info = next(t for t in reqs if t.name == dep_name)
            output += f"{dep_name}=={info.version} [{dep_spec}]\n"
            output += textwrap.indent(_deps_to_string(info.requires, reqs), prefix="\t")
        except StopIteration:
            # StopIteration is raised if the dependency is not found in reqs.
            # If a package is not in reqs, it means that it would not be installed by pip.
            # This is usually the case for dependencies that are only required on other Python versions
            # or platforms, but not on the specific combination this function is run.
            continue

    return output


def _reverse_deps_to_string(rev_deps: dict[str, str], reqs: list[ReqFileEntry]) -> str:
    output = ""
    for dep_name, dep_spec in rev_deps.items():
        info = next(t for t in reqs if t.name == dep_name)
        output += f"{dep_name}=={info.version} [{dep_spec}]\n"
        output += textwrap.indent(_reverse_deps_to_string(info.required_by, reqs), prefix="\t")
    return output
