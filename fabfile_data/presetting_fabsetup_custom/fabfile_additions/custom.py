from fabfile.fabutils import checkup_git_repo, flo, install_package
from fabfile.fabutils import install_packages, install_user_command, run, task


def users_bin_dir():
    '''Put custom commands at '~/bin/'.'''
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
    
    A complete latex installation "requires" the execution of the task
    'setup.users_bin_dir', too.
    '''
    users_bin_dir()
    # circumvent circular import, cf. http://stackoverflow.com/a/18486863
    from fabfile.setup import latex
    latex()
    checkup_git_repo('https://github.com/theno/haw-inf-thesis-template.git')
