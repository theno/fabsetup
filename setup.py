"""Summary: fabric-2 setup scripts and fabric utils library

* https://github.com/theno/fabsetup
* https://pypi.python.org/pypi/fabsetup
"""

import codecs
import os
import re
from setuptools import setup, find_packages

thisdir = os.path.abspath(os.path.dirname(__file__))
package = "fabsetup"
module = package.replace("-", "_")

with open(os.path.join(thisdir, "README.md"), encoding="utf-8") as fh_in:
    long_description = fh_in.read()


def read(*parts):
    with codecs.open(os.path.join(thisdir, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name=package,
    version=find_version(module, "_version.py"),
    description=__doc__.split("\n")[0],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/theno/fabsetup",
    author="Theodor Nolte",
    author_email="fabsetup@theno.eu",
    license="MIT",
    entry_points={
        "console_scripts": [
            "fabsetup = fabsetup.__main__:main",
            "fabs = fabsetup.__main__:main",
            "fap = fabsetup.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="python development utilities library",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    include_package_data=True,
    install_requires=[
        "fabric>=2.0.0",
    ],
    extras_require={
        "devel": [
            "black",
            "mutmut",
            "pytest",
            "recommonmark",
            "sphinx",
            "tox",
        ]
    },
)
