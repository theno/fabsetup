"""Yet another setup script for linux software, configurations and services.

* https://github.com/theno/fabsetup
* https://pypi.python.org/pypi/fabsetup
"""

from setuptools import setup, find_packages
from codecs import open
from os import path


this_dir = path.abspath(path.dirname(__file__))

long_description = ''
with open(path.join(this_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fabsetup',
    version='0.4.1',
    description='fabric setup scripts and fabric utils library',
    long_description=long_description,
    url='https://github.com/theno/fabsetup',
    author='Theodor Nolte',
    author_email='fabsetup@theno.eu',
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='python development utilities library',
    packages=find_packages(exclude=['contrib', 'docs', 'tests',
                                    'fabsetup_custom']),
)
