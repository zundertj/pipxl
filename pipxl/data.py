# SPDX-FileCopyrightText: 2022-present Jeroen van Zundert <mail@jeroenvanzundert.nl>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReqFileEntry:
    name: str
    version: str
    requires: dict[str, str]
    required_by: dict[str, str]
    url: str
    hash: str | None  # not available for local packages
    requested: bool
    license: str | None  # only available if uploaded to PyPi

    def to_string(self, add_hash: bool = True) -> str:
        out = f"{self.name}=={self.version}"

        # NOTE: use four spaces, not tabs, to indent, otherwise pip install breaks
        if add_hash and self.hash is not None:
            out += f" \\\n    --hash={self.hash.replace('=',':')}"

        for req_by, specifier in self.required_by.items():
            out += f"\n    # via {req_by}"
            if specifier:
                out += f" [{specifier}]"

        return out


@dataclass
class Environment:
    pip_version: str
    platform_python_implementation: str
    implementation_version: str
    platform_system: str
    platform_release: str
    platform_machine: str
