# SPDX-FileCopyrightText: 2022-present Jeroen van Zundert <mail@jeroenvanzundert.nl>
#
# SPDX-License-Identifier: MIT

import subprocess
import sys


def pip_cli(cmd: list[str], py_executable: str = sys.executable) -> subprocess.CompletedProcess[str]:
    # https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program
    return subprocess.run([py_executable, "-m", "pip"] + cmd, capture_output=True, timeout=60, text=True)
