"""Yet another setup script for linux software, configurations and services.

* https://github.com/theno/fabsetup
* https://pypi.python.org/pypi/fabsetup
"""

import os
from setuptools import setup, find_packages
from codecs import open
from os import path

description = 'fabric setup scripts and fabric utils library'
long_description = ''
this_dir = path.abspath(path.dirname(__file__))
try:
    import pypandoc
    long_description = pypandoc.convert(path.join(this_dir, 'README.md'), 'rst')
except(IOError, ImportError):
    with open(path.join(this_dir, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

data_files = []
for directory, _, files in os.walk('fabfile_data'):
    files = [path.join(directory, file_) for file_ in files]
    if files:
        data_files.append((directory, files))

setup(
    name='fabsetup',
    version='0.4.3',
    description=description,
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
                                    'fabfile_data', 'fabsetup_custom']),
    data_files=data_files+[
        ('', ['README.md']),
    ],
)
