from os.path import abspath, dirname, join

import fabric.main


def main():
    fabsetup_fabfile = join(
        dirname(dirname(abspath(__file__))), 'fabfile', '__init__.py')
    fabric.main.main(fabfile_locations=[fabsetup_fabfile])


if __name__ == '__main__':
    main()
