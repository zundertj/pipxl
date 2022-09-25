# pipxl

[![PyPI - Version](https://img.shields.io/pypi/v/pipxl.svg)](https://pypi.org/project/pipxl)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pipxl.svg)](https://pypi.org/project/pipxl)

-----

**Table of Contents**

- [Installation](#installation)
- [Features](#features)
- [Why pipxl?](#why-pipxl)
- [Non-goals](#non-goals)
- [Alternatives](#alternatives)
- [License](#license)

## Installation

```console
pip install pipxl
```

## Features
`pipxl` is a wrapper around `pip`, the default Python package manager. 

`pipxl` adds the following to `pip`:
* `pipxl compile`: from a list of top-level dependencies, generate a pip-compliant requirements file with all dependencies and dependencies-of-dependencies pinned
* `pipxl sync`: sync current environment with the requirements file
* `pipxl deptree`: show for a set of packages the dependencies and dependencies-of-dependencies including all version specifiers
* `pipxl deptreerev`: show for a set of packages the dependency tree in reverse
* `pipxl license`: list the licensing of the dependencies, including sub-dependencies, in an easy format

### compile
Compile can take in a `pyproject.toml` file, one or more requirements file and direct package specifications, including combinations of those:

```console
# pyproject.toml
$ pipxl compile .

# pyproject.toml, with custom output_file. Defaults to requirements_lock.txt
$ pipxl compile . --o my_requirements_lock.txt 

# pyproject.toml, including optional dependencies defined under `all`
$ pipxl compile .[all]

# single requirements file
$ pipxl compile --r requirements.in

# multiple requirements files
$ pipxl compile --r requirements.in --r requirements-dev.in

# direct package specifications
$ pipxl compile pandas==1.4.3
```

The generated file includes all packages, with version, the correct hash, and detailed version information for why the dependency was included:
```
pandas==1.4.3 \
    --hash=sha256:6f803320c9da732cc79210d7e8cc5c8019aad512589c910c66529eb1b1818230
numpy==1.23.3 \
    --hash=sha256:004f0efcb2fe1c0bd6ae1fcfc69cc8b6bf2407e0f18be308612007a0762b4089
    # via pandas [numpy (>=1.21.0) ; python_version >= "3.10"]
python-dateutil==2.8.2 \
    --hash=sha256:961d03dc3453ebbc59dbdea9e4e11c5651520a876d0f4db161e8674aae935da9
    # via pandas [python-dateutil (>=2.8.1)]
pytz==2022.2.1 \
    --hash=sha256:220f481bdafa09c3955dfbdddb7b57780e9a94f5127e35456a48589b9e0c0197
    # via pandas [pytz (>=2020.1)]
six==1.16.0 \
    --hash=sha256:8abb2f1d86890a2dfb989f9a77cfcfd3e47c2a354b01111771326f8aa26e0254
    # via python-dateutil [six (>=1.5)]
```

### sync
Sync updates the active (virtual) environment:
```console
$ pipxl sync --r requirements_lock.txt
```

### deptree

The `deptree` command shows the dependency tree, listing for each requested package all dependencies, dependencies-of-dependencies, and so on.

```console
# pyproject.toml
$ pipxl deptree .
...

# direct package specification
$ pipxl deptree pandas==1.4.3
pandas==1.4.3
        python-dateutil==2.8.2 [python-dateutil (>=2.8.1)]
                six==1.16.0 [six (>=1.5)]
        pytz==2022.2.1 [pytz (>=2020.1)]
        numpy==1.23.3 [numpy (>=1.21.0) ; python_version >= "3.10"]
```

### deptreerev
The output of `deptree` works top-down: for every requested package, the dependencies are listed.
`deptreerev` works the opposite way: for each package, it lists the packages that depend on it.
This is useful to figure out why a particular dependency has been installed. 

```console
$ pipxl deptreerev pandas==1.4.3 numpy==1.21.1
pandas==1.4.3
numpy==1.21.1
        pandas==1.4.3 [numpy (>=1.21.0) ; python_version >= "3.10"]
python-dateutil==2.8.2
        pandas==1.4.3 [python-dateutil (>=2.8.1)]
pytz==2022.2.1
        pandas==1.4.3 [pytz (>=2020.1)]
six==1.16.0
        python-dateutil==2.8.2 [six (>=1.5)]
                pandas==1.4.3 [python-dateutil (>=2.8.1)]
```
This shows that for instance `six` is a dependency of `python-dateutil`, which in turn is a dependency of `pandas`. In square brackets, you can see how the dependency has been defined. For example, `python-dateutil` requires `six >= 1.5`; the pip resolver has selected the most recent version `1.16.0`.

### license
Not all packages on PyPi are licensed for usage in all environments, particularly not in corporate environments.
It is thus useful to check under which license the package comes. 
The problem is complicated by dependencies of the dependencies; there are typically a large number of those and they may change over time.
The `license` commands collects all dependencies and dependencies-of-dependencies, and groups the output by license.
Do note that some packages may not have uploaded the license information (properly) to PyPi.
For those, `*UNKNOWN*` will be displayed. 
`pipxl` does not attempt to extract it from Github, the wheel, or other sources, as it may result in the wrong license being assigned.

```console
# pyproject.toml
$ pipxl license .
...

$ pipxl license pandas==1.4.3
BSD                 : numpy
BSD-3-Clause        : pandas
Dual License        : python-dateutil
MIT                 : pytz, six
```

## Why pipxl?
`pipxl` is a set of additional tools to `pip` that I wish would be part of `pip`, as they are useful in nearly every Python project I work on.

Initial inspiration for creating `pipxl` comes from the release of pip [22.2](https://pip.pypa.io/en/stable/news/#v22-2), which adds the following to `pip install`
* `--dry-run` flag to not actually install packages
* a reports flag providing detailed JSON output of the resolution process.

In combination, the two allow us to pass a set of requirements to pip, and get the results of the resolver without hooking into the pip api. Alternatives, most with a narrower scope, such as `pip-tools` do hook into the api, but it is [not official and not recommended](https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program), although for lack of alternatives (until pip 22.2!) various packages do use it. By using the CLI, the risk of breakage on pip version upgrades should be limited (although the JSON report may change).

What is still missing is being able to provide a list of packages to be considered installed, as to make use of the `--upgrade-strategy=only-if-needed` option. Right now, `pipxl` will eagerly upgrade all packages not requested (i.e. dependencies-of-dependencies), as it cannot simulate this behavior currently.
In theory, it could set up a temporary virtual environment, actually install current packages, dry-run pip install with the `only-if-needed` flag, and record the results.

## Non-goals
* Dependency resolution: `pipxl` uses the pip resolver, and does not, and will not, try to aid pip. `pipxl` is geared towards explaining what `pip`, and in particular the pip resolver, does, not replacing it.


## Alternatives

* [pip-tools](https://github.com/jazzband/pip-tools): offers `pip-compile` and `pip-sync`, similar to `pipxl lock` and `pipxl sync`. Relies on pip internals. See [this issue](https://github.com/jazzband/pip-tools/issues/1654) for using the pip CLI interface instead.
* [pipgrip](https://github.com/ddelange/pipgrip): pip dependency resolver using the PubGrub algorithm, useful for viewing dependency trees
* [pipdeptree](https://github.com/tox-dev/pipdeptree): offers functionality similar to `pipxl deptree` and `pipxl deptreerev`
* [poetry](https://github.com/python-poetry/poetry): alternative to pip
* [pdm](https://github.com/pdm-project/pdm): alternative to pip

## License

`pipxl` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
