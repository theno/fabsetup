from os.path import abspath, dirname, join

import fabric.main


def main():
    fabfile = join(dirname(abspath(__file__)), 'fabfile', '__init__.py')
    fabric.main.main(fabfile_locations=[fabfile])


if __name__ == '__main__':
    main()
