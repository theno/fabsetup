from os.path import abspath, dirname, join

import fabric.main

from fabsetup._version import __version__


def main():
    fabfile = join(
        dirname(dirname(abspath(__file__))), 'fabfile', '__init__.py')
    fabric.main.main(fabfile_locations=[fabfile])


if __name__ == '__main__':
    main()
