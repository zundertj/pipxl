# SPDX-FileCopyrightText: 2022-present Jeroen van Zundert <mail@jeroenvanzundert.nl>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

import pytest

from pipxl import compile


def test_pip_compile_no_input_provided_should_fail() -> None:
    with pytest.raises(Exception):
        compile(file_out=Path("."))
