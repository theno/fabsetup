"""fabric setup scripts and fabric utils library

* https://github.com/theno/fabsetup
* https://pypi.python.org/pypi/fabsetup
"""

import os
import shutil
from setuptools import setup, find_packages
from codecs import open
from os import path


def create_readme_with_long_description():
    this_dir = os.path.abspath(os.path.dirname(__file__))
    readme_md = os.path.join(this_dir, 'README.md')
    readme = os.path.join(this_dir, 'README')
    if os.path.isfile(readme_md):
        if os.path.islink(readme):
            os.remove(readme)
        shutil.copy(readme_md, readme)
    try:
        import pypandoc
        long_description = pypandoc.convert(readme_md, 'rst', format='md')
        if os.path.islink(readme):
            os.remove(readme)
        with open(readme, 'w') as out:
            out.write(long_description)
    except(IOError, ImportError, RuntimeError):
        if os.path.isfile(readme_md):
            os.remove(readme)
            os.symlink(readme_md, readme)
        with open(readme, encoding='utf-8') as in_:
            long_description = in_.read()
    return long_description


this_dir = os.path.abspath(os.path.dirname(__file__))
filename = os.path.join(this_dir, 'fabsetup', '_version.py')
with open(filename, 'rt') as fh:
    version = fh.read().split('"')[1]

description = __doc__.split('\n')[0]
long_description = create_readme_with_long_description()

data_files = []
for directory, _, files in os.walk('fabfile_data'):
    files = [path.join(directory, file_) for file_ in files]
    if files:
        data_files.append((directory, files))

setup(
    name='fabsetup',
    version=version,
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
)
