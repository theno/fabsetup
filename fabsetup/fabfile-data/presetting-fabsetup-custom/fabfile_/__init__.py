import sys
from os.path import dirname, join

from fabric.api import execute

custom_path = join(dirname(dirname(__file__)), 'fabfile')
sys.path = [custom_path] + sys.path

from fabsetup.fabfile import setup
from fabsetup.fabutils import checkup_git_repo, install_packages, run
from fabsetup.fabutils import suggest_localhost
from fabsetup.fabutils import custom_task as task # here every task is custom

import custom # enable task custom.latex


# usefull packages for both, dektop and webserver
usefull = [
    'aptitude',
    'mosh',
    'ntp',
    'rxvt-unicode',
    'tmux',
    'tree',
    'vim',
]

packages_webserver = usefull + [
    'python3',
    'python3-pip',
    'xauth', # cf. http://unix.stackexchange.com/a/212952, redhat: xorg-x11-xauth
]

packages_desktop = usefull + [
    'arandr',
    'baobab',
    'chromium-browser',
    'gitk',
    'gthumb',
    'k3b',
    'mplayer',
    'okular',
    'openssh-server',
    'sshfs',
    'vlc',
    'youtube-dl',
]


@task
@suggest_localhost
def setup_desktop():
    '''Run setup tasks to set up a nicely configured desktop pc.

    This is highly biased on my personal preference.

    The task is defined in file fabsetup_custom/fabfile_addtitions/__init__.py
    and could be customized by Your own needs.  More info: README.md
    '''
    run('sudo apt-get update')
    install_packages(packages_desktop)
    execute(custom.latex)
    execute(setup.ripping_of_cds)
    execute(setup.regex_repl)
    execute(setup.i3)
    execute(setup.solarized)
    execute(setup.vim)
    execute(setup.tmux)
    execute(setup.pyenv)
    # circumvent circular import, cf. http://stackoverflow.com/a/18486863
    from fabfile import dfh, check_reboot
    dfh()
    check_reboot()


@task
def setup_webserver():
    '''Run setup tasks to set up a nicely configured webserver.

    Features:
     * owncloud service
     * fdroid repository
     * certificates via letsencrypt
     * and more

    The task is defined in file fabsetup_custom/fabfile_addtitions/__init__.py
    and could be customized by Your own needs.  More info: README.md
    '''
    run('sudo apt-get update')
    install_packages(packages_webserver)
    execute(custom.latex)
    execute(setup.solarized)
    execute(setup.vim)
    execute(setup.tmux)
    checkup_git_repo(url='git@github.com:letsencrypt/letsencrypt.git')
    execute(setup.service.fdroid)
    execute(setup.service.owncloud)
    # circumvent circular import, cf. http://stackoverflow.com/a/18486863
    from fabfile import dfh, check_reboot
    dfh()
    check_reboot()
