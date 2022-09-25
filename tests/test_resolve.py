# SPDX-FileCopyrightText: 2022-present Jeroen van Zundert <mail@jeroenvanzundert.nl>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

from pipxl.resolver import pip_resolve


def test_resolve() -> None:
    p = Path(__file__).parent / "requirements.in"
    result, _ = pip_resolve([p])
    assert len(result) == 11
    assert result[0].name == "httpx"
    assert result[0].version == "0.23.0"
    assert result[0].required_by == {}
    output = result[2].to_string(add_hash=False).splitlines()
    assert output[0].startswith("certifi==")
    assert output[1] == "\t# via httpx [certifi]"
    assert output[2] == "\t# via requests [certifi (>=2017.4.17)]"
    assert output[3] == "\t# via httpcore [certifi]"
    assert output[4] == "\t# via urllib3 [certifi ; extra == 'secure']"
