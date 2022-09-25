# SPDX-FileCopyrightText: 2022-present Jeroen van Zundert <mail@jeroenvanzundert.nl>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pipxl.data import Environment, ReqFileEntry
from pipxl.pip_cli import pip_cli


def pip_resolve(
    files_in: list[Path] | None = None, package_spec: list[str] | None = None, no_deps: bool = False
) -> tuple[list[ReqFileEntry], Environment]:
    target = _pip_install_target_arg(files_in, package_spec)
    json_report = _pip_install_fresh_dryrun(target, no_deps)
    return _parse_pip_install_json_report(json_report)


def _pip_install_target_arg(files_in: list[Path] | None = None, package_spec: list[str] | None = None) -> list[str]:
    if (files_in is None) and (package_spec is None):
        raise Exception("At least one files and/or package specification needs to be provided")

    file_arg = []
    if files_in is not None:
        for file in files_in:
            file_arg.extend(["-r", f"{str(file)}"])

    package_name_arg = [] if package_spec is None else package_spec

    arg = file_arg + package_name_arg
    return arg


def _pip_install_fresh_dryrun(target: list[str], no_deps: bool = False) -> dict[str, Any]:
    cmd = ["install", "--ignore-installed", "--dry-run", "--report", "-", "--quiet"]
    if no_deps:
        cmd += ["--no-deps"]

    output = pip_cli(cmd + target)
    if output.returncode != 0:
        raise Exception(output.stderr)
    js = json.loads(output.stdout)
    assert isinstance(js, dict)
    return js


def _parse_pip_install_json_report(js: dict[str, Any]) -> tuple[list[ReqFileEntry], Environment]:
    # first collect for each package all its dependencies
    deptree = dict()
    for package in js["install"]:
        # the raw version includes version and platform specifiers
        # example from httpx: 'certifi', 'sniffio', 'rfc3986[idna2008] (<2,>=1.3)', 'httpcore (<0.16.0,>=0.15.0)'
        # We store this as a dict, with the key being the name, for easy reference, and the value the full string
        meta = package["metadata"]
        if "requires_dist" in meta:
            deptree[meta["name"]] = {_package_name_from_requires_dist_string(s): s for s in meta["requires_dist"]}
        else:
            deptree[meta["name"]] = dict()

    # traverse through list of packages to get version and required_by
    out: list[ReqFileEntry] = []
    for package in js["install"]:
        meta = package["metadata"]

        if "requires_dist" in meta:
            requires = {_package_name_from_requires_dist_string(s): s for s in meta["requires_dist"]}
        else:
            requires = {}

        req_by = {
            potential_dep: reqs[meta["name"]] for potential_dep, reqs in deptree.items() if meta["name"] in reqs.keys()
        }
        archive_info = package["download_info"].get("archive_info")

        out.append(
            ReqFileEntry(
                name=meta["name"],
                version=meta["version"],
                requires=requires,
                required_by=req_by,
                url=package["download_info"]["url"],
                hash=archive_info["hash"] if archive_info is not None else None,
                requested=package["requested"],
                license=package["metadata"].get("license", None),
            )
        )

    # parse environment
    env_keys = [
        "platform_python_implementation",
        "implementation_version",
        "platform_system",
        "platform_release",
        "platform_machine",
    ]
    env = {k: v for k, v in js["environment"].items() if k in env_keys}
    env = {"pip_version": js["pip_version"]} | env
    return out, Environment(**env)


def _package_name_from_requires_dist_string(s: str) -> str:
    return s.split()[0].split("[")[0]
