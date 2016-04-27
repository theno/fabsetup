from fabfile.fabutils import checkup_git_repo, checkup_git_repos, flo
from fabfile.fabutils import install_package, install_packages
from fabfile.fabutils import install_user_command, run
from fabfile.fabutils import custom_task as task # here, every task is custom

import config


def users_bin_dir():
    '''Put custom commands at '~/bin/'
    
    For the conversion of diagrams into the pdf format:
    * dia2pdf, ep2svg, svg2pdf
    * alldia2pdf, allep2svg, alldia2pdf
    '''
    # circumvent circular import, cf. http://stackoverflow.com/a/18486863
    from fabfile.setup import pencil
    pencil() # used by ~/bin/ep2svg
    install_packages([
        'dia',
        'inkscape', # used by ~/bin/svg2pdf
        'xsltproc', # used by ~/bin/ep2svg
    ])
    commands = [
        'alldia2pdf',
        'allep2svg',
        'allsvg2pdf',
        'dia2pdf',
        'ep2svg',
        'svg2pdf'
    ]
    for command in commands:
        install_user_command(command)


@task
def latex():
    '''Install all packages and tools required to compile my latex documents.
    
    * Install or update a lot of latex packages.
    * Install or update pencil, dia, inkscape, xsltproc for diagrams and
      images.
    * Install or update util commands for conversion of dia, ep, svg into pdf
      files.
    * Checkout or update a haw-thesis template git repository which uses all of
      the upper mentioned tools.
    '''
    users_bin_dir()
    # circumvent circular import, cf. http://stackoverflow.com/a/18486863
    from fabfile.setup import latex
    latex()
    checkup_git_repo('https://github.com/theno/haw-inf-thesis-template.git')


@task
def github():
    '''Checkout or update github repositories.

    The git repos are defined in github_repos in config.py.
    '''
    checkup_git_repos(config.github_repos)


@task
def vim():
    '''Set up my vim environment.'''
    from fabfile.setup import vim
    vim()
    checkup_git_repos(config.vim_package_repos, base_dir='~/.vim/bundle')
