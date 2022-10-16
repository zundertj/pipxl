# SPDX-FileCopyrightText: 2022-present Jeroen van Zundert <mail@jeroenvanzundert.nl>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from pathlib import Path

from pipxl.resolver import pip_resolve


def license(files_in: list[Path] | None = None, package_spec: list[str] | None = None) -> dict[str | None, list[str]]:
    reqs, _ = pip_resolve(files_in, package_spec)

    by_license = {}
    for r in reqs:
        lic = _parse_license(r.license)
        if lic not in by_license:
            by_license[lic] = [r.name]
        else:
            by_license[lic] += [r.name]

    # return sorted by license
    by_license = dict(sorted(by_license.items(), key=lambda item: item[0] if item[0] is not None else "*"))

    return by_license


def _parse_license(lic: str | None) -> str | None:
    return lic if (lic is not None and len(lic) < 50) else None
