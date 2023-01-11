# Development

Commands for the development of fabsetup.

## Setup

Clone this repository an `cd` into it:

```sh
git clone https://github.com/theno/fabsetup.git
cd fabsetup
```

Fabsetup supports several Python versions, Python 3.5, Python 3.6,
Python 3.7, Python 3.8, and Python 3.9.  In order to run the following
commands and set up an environment with all of this Pythons, an
[installation of pyenv](https://github.com/pyenv/pyenv#installation) is
required.

Install and set up latest python versions with
[pyenv](https://github.com/pyenv/pyenv#simple-python-version-management-pyenv):

```sh
# learn for the latest pythons
pyenv update

# install them
pys=()  # python versions
for minor in {5..9}; do
  latest=$(pyenv install --list | \
           grep -oP "(?<=^  )3\.$minor\.\d+$" | tail -1)
  pys=("${pys[@]}" $latest)
  pyenv install --skip-existing  $latest
done

# create virtualenv for build tasks
py39=${pys[-1]}
pyenv virtualenv ${py39} fabsetup_py39

# activate pythons
#   vanilla Python-3.5, -3.6, -3.7, -3.8
#   and Python-3.9 virtualenv fabsetup_py39
pyenv local ${pys[@]::${#pys[@]}-1} fabsetup_py39

# install build dependencies (pytest, tox, sphinx)
# in virtualenv fabsetup_py39
pip3.9 install --upgrade -e .[devel]
```

Show and check environment. On success, the return code of the following
commands is `0`:

```sh
# active pythons
pyenv version |& \
        grep -zE '3\.5.*3\.6.*3\.7.*3\.8.*fabsetup_py39.*python-version'

# virtualenv fabsetup_py39
pyenv which python3.9 |& grep fabsetup_py39

# correct pytest version is active
pyenv which pytest    |& grep fabsetup_py39

# correct tox version is active
tox --version         |& grep fabsetup_py39

# correct pip version is active
pip3.9 --version      |& grep fabsetup_py39

# required packages are installed
pip3.9 freeze         |& grep -zE 'fabsetup.*pytest.*Sphinx.*tox'
```

## Tests

Run [pytest](https://docs.pytest.org/). Executes unit tests against
Python 3.9:

```sh
pytest tests -s

# long-winded way
PYTHONPATH=  python3.9 -m pytest tests/ -s
```

Run [doctest](https://docs.python.org/3/library/doctest.html). Executes
and tests code examples in docstrings:

```sh
pytest fabsetup --doctest-modules

# long-winded way
PYTHONPATH=  python3.9 -m pytest fabsetup/ --doctest-modules
```

Run [tox](https://tox.readthedocs.io/). Against Python 3.5, Python 3.6,
Python 3.7, Python 3.8, and Python 3.9 it executes
[check-manifest](https://github.com/mgedmin/check-manifest#check-manifest),
[setup.py check](https://stackoverflow.com/a/30332432), unit tests,
doctests, [flake8](https://flake8.pycqa.org/), and [coverage
check](https://pytest-cov.readthedocs.io/):

```sh
tox

# long-winded way
PYTHONPATH=  python3.9 -m tox
```

## Mutation Tests

Run [mutmut](https://mutmut.readthedocs.io/) which executes [mutation
tests](https://hackernoon.com/mutmut-a-python-mutation-testing-system-9b9639356c78)
in order to test the unit tests:

```sh
mutmut run

# show results
mutmut results
mutmut show

# show mutation diff
mutmut show MUTATION_ID

# clean-up
rm -f .mutmut-cache
```

## Run fabsetup

Run `fabsetup` devel command:

```sh
fabsetup

# long-winded ways
~/.pyenv/versions/fabsetup_py39/bin/fabsetup
~/.pyenv/versions/fabsetup_py39/bin/python  -m fabsetup
python3.9 -m fabsetup
python3.9  fabsetup/__main__.py
```

Run with [debug output
](https://docs.pyinvoke.org/en/stable/concepts/configuration.html#default-configuration-values):

```sh
INVOKE_DEBUG=1 fabsetup

fabsetup --debug
```

## Documentation

Create [Sphinx](https://www.sphinx-doc.org/) HTML documentation:

```sh
ln -s ../README.md  docs/
cd docs && make clean html; cd ..
```

Update API docs structure, run command
[sphinx-apidoc](https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html)
that generates Sphinx sources which includes the docstrings with
[autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html):

```sh
rm -rf docs/api && sphinx-apidoc -o docs/api --module-first fabsetup

# apply tweaks
sed -i '/Submodules/{ N; s/.*----------//; }' docs/api/fabsetup{,.{fab,}utils}.rst
sed -i 's/fabsetup package/fabsetup API/' docs/api/fabsetup.rst
sed -i 's/Subpackages/Submodules/' docs/api/fabsetup.rst
sed -i 's/ package$//' docs/api/fabsetup.{fab,}utils.rst
sed -i 's/ module$//g' docs/api/fabsetup{,.{fab,}utils}.rst
rm docs/api/modules.rst

cd docs && make clean html; cd ..
```

This commands are executed to create the readthedocs documentation:
<https://github.com/theno/fabsetup/blob/main/.readthedocs.yaml>
