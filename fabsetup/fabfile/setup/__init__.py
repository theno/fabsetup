# -*- coding: utf-8 -*-

import os.path

from fabric.api import env, local, sudo, warn_only
from fabric.contrib.files import append

from fabsetup.fabutils import exists, install_packages, install_package
from fabsetup.fabutils import install_file, install_user_command, needs_packages
from fabsetup.fabutils import needs_repo_fabsetup_custom, run, suggest_localhost
from fabsetup.fabutils import checkup_git_repo, checkup_git_repos, task
from fabsetup.fabutils import print_msg
from fabsetup.utils import flo, query_yes_no
from fabsetup.utils import magenta, cyan
from fabsetup.utils import update_or_append_line
from fabsetup.utils import uncomment_or_update_or_append_line


# "activate" tasks
import ct
import service
from calibre import calibre
from dumpasn1 import dumpasn1
from nvm import nvm
from openssl import openssl
from powerline import powerline
from revealjs import decktape, revealjs, revealjs_template
from tmux import tmux
from vim_janus import vim_janus


@task
@suggest_localhost
def ripping_of_cds():
    '''Install the tools ripit and burnit in order to rip and burn audio cds.

    More info: http://forums.debian.net/viewtopic.php?f=16&t=36826
    '''
    # install and configure ripit
    install_package('ripit')
    install_file(path='~/.ripit/config', username=env.user)
    # install burnit
    run('mkdir -p  ~/bin')
    install_file('~/bin/burnit')
    run('chmod 755 ~/bin/burnit')


@task
@suggest_localhost
def regex_repl():
    '''Install RegexREPL, a helper tool for building regular expressions.

    More infos:
     * https://github.com/theno/RegexREPL
     * REPL: https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop

    Files created by this task:

        > tree ~
        ├── bin
        │   ├── find_regex_repl.pl -> ~/repos/RegexREPL/find_regex_repl.pl
        │   └── match_regex_repl.pl -> ~/repos/RegexREPL/match_regex_repl.pl
        └── repos
            └── RegexREPL
                ├── find_regex_repl.pl
                ├── match_regex_repl.pl
                └── README.md
    '''
    install_package('libterm-readline-gnu-perl')
    checkup_git_repo(url='https://github.com/theno/RegexREPL.git')
    for cmd in ['find_regex_repl.pl', 'match_regex_repl.pl']:
        run(flo('ln -snf  ~/repos/RegexREPL/{cmd} ~/bin/{cmd}'))


@task
@suggest_localhost
@needs_packages('pkg-config')
def i3():
    '''Install and customize the tiling window manager i3.'''
    install_package('i3')
    install_file(path='~/.i3/config', username=env.user, repos_dir='repos')

    # setup: hide the mouse if not in use
    # in ~/.i3/config: 'exec /home/<USERNAME>/repos/hhpc/hhpc -i 10 &'
    install_packages(['make', 'pkg-config', 'gcc', 'libc6-dev', 'libx11-dev'])
    checkup_git_repo(url='https://github.com/aktau/hhpc.git')
    run('cd ~/repos/hhpc  &&  make')


@task
@suggest_localhost
def solarized():
    '''Set solarized colors in urxvt, tmux, and vim.

    More Infos:
    * Getting solarized colors right with urxvt, st, tmux and vim:
      https://bbs.archlinux.org/viewtopic.php?id=164108

    * Creating ~/.Xresources:
      https://wiki.archlinux.org/index.php/Rxvt-unicode#Creating_.7E.2F.Xresources

    * Select a good font on Ubuntu:
      https://michaelheap.com/getting-solarized-working-on-ubuntu/

    * tmux and 256 colors:
      http://unix.stackexchange.com/a/118903
    '''
    install_packages(['rxvt-unicode', 'tmux', 'vim'])
    install_file('~/.Xresources')
    if env.host_string == 'localhost':
        run('xrdb  ~/.Xresources')

    # install and call term_colors
    run('mkdir -p  ~/bin')
    install_file('~/bin/term_colors')
    run('chmod 755 ~/bin/term_colors')
    run('~/bin/term_colors')


@task
@suggest_localhost
def vim():
    '''Customize vim, install package manager pathogen and some vim-packages.

    pathogen will be installed as a git repo at ~/repos/vim-pathogen and
    activated in vim by a symbolic link at ~/.vim/autoload/pathogen.vim

    A ~/.vimrc will be installed which loads the package manager within of vim.

    The vim packages vim-colors-solarized, nerdtree, and tagbar are installed
    as git repos placed at dir ~/.vim/bundle/

    If you want to install more vim packages also place them at this dir, cf.
    https://logicalfriday.com/2011/07/18/using-vim-with-pathogen/
    '''
    install_package('vim')

    print_msg('## install ~/.vimrc\n')
    install_file('~/.vimrc')

    print_msg('\n## set up pathogen\n')
    run('mkdir -p  ~/.vim/autoload  ~/.vim/bundle')
    checkup_git_repo(url='https://github.com/tpope/vim-pathogen.git')
    run('ln -snf  ~/repos/vim-pathogen/autoload/pathogen.vim  '
        '~/.vim/autoload/pathogen.vim')

    print_msg('\n## install vim packages\n')
    install_package('ctags')  # required by package tagbar
    repos = [
        {
            'name': 'vim-colors-solarized',
            'url': 'git://github.com/altercation/vim-colors-solarized.git',
        },
        {
            'name': 'nerdtree',
            'url': 'https://github.com/scrooloose/nerdtree.git',
        },
        {
            'name': 'vim-nerdtree-tabs',
            'url': 'https://github.com/jistr/vim-nerdtree-tabs.git',
        },
        {
            'name': 'tagbar',
            'url': 'https://github.com/majutsushi/tagbar.git',
        },
    ]
    checkup_git_repos(repos, base_dir='~/.vim/bundle')


@task
@needs_packages('git')
def pyenv():
    '''Install or update the pyenv python environment.

    Checkout or update the pyenv repo at ~/.pyenv and enable the pyenv.
    Pyenv wird also als Github-Repo "installiert" unter ~/.pyenv

    More info:
     * https://github.com/yyuu/pyenv
     * https://github.com/yyuu/pyenv/wiki/Common-build-problems#requirements
    Tutorial:
     * http://amaral-lab.org/resources/guides/pyenv-tutorial
    '''
    install_packages([
        'make',
        'build-essential',
        'libssl-dev',
        'zlib1g-dev',
        'libbz2-dev',
        'libreadline-dev',
        'libsqlite3-dev',
        'wget',
        'curl',
        'llvm',
        'libncurses5-dev',
        'libncursesw5-dev',
    ])
    if exists('~/.pyenv'):
        run('cd ~/.pyenv  &&  git pull')
        run('~/.pyenv/bin/pyenv update')
    else:
        run('curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/'
            'master/bin/pyenv-installer | bash')

    # add pyenv to $PATH and set up pyenv init
    bash_snippet = '~/.bashrc_pyenv'
    install_file(path=bash_snippet)
    prefix = flo('if [ -f {bash_snippet} ]; ')
    enabler = flo('if [ -f {bash_snippet} ]; then source {bash_snippet}; fi')
    if env.host == 'localhost':
        # FIXME: next function currently only works for localhost
        uncomment_or_update_or_append_line(filename='~/.bashrc', prefix=prefix,
                                           new_line=enabler)
    else:
        print(cyan('\nappend to ~/.bashrc:\n\n    ') + enabler)


@task
@suggest_localhost
def virtualbox_host():
    '''Install a VirtualBox host system.

    More Infos:
     * overview:     https://wiki.ubuntuusers.de/VirtualBox/
     * installation: https://wiki.ubuntuusers.de/VirtualBox/Installation/
    '''
    if query_yes_no(question='Uninstall virtualbox-dkms?', default='yes'):
        run('sudo apt-get remove virtualbox-dkms')
    install_packages([
        'virtualbox',
        'virtualbox-qt',
        'virtualbox-dkms',
        'virtualbox-guest-dkms',
        'virtualbox-guest-additions-iso',
    ])
    users = [env.user]
    for username in users:
        run(flo('sudo  adduser {username} vboxusers'))
    #run('newgrp - vboxusers')


@task
def server_customizations():
    '''Customize the server (user, authorized_keys, ...).'''

    username = env.user
    env.user = 'root'

    # create user
    all_users = run('cut -d: -f1 /etc/passwd').split()
    if username not in all_users:

        host = env.host

        run(flo('adduser {username}'))

        # add user to the sudo group, cf. http://askubuntu.com/a/7484
        #run('sudo adduser {username} sudo'.format(**locals()))
        # http://jeromejaglale.com/doc/unix/ubuntu_sudo_without_password
        append('/etc/sudoers', flo('{username} ALL=(ALL) NOPASSWD: ALL'),
               use_sudo=True)

        # set up password-less login
        local(flo('ssh-copy-id -i ~/.ssh/id_rsa.pub  {username}@{host}'))

        env.user = username

        # Disable service apache2 httpd, cf. http://askubuntu.com/a/355102
        sudo('update-rc.d apache2 disable')
    else:
        print(magenta(flo(' nothing to do, user {username} already exists')))
        env.user = username


@task
@suggest_localhost
def pencil2():
    '''Install or update latest Pencil version 2, a GUI prototyping tool.

    Tip: For svg exports displayed proper in other programs (eg. inkscape,
    okular, reveal.js presentations) only use the 'Common Shapes' and
    'Desktop - Sketchy GUI' elements.

    More info:
        github repo (forked version 2): https://github.com/prikhi/pencil
    '''
    repo_name = 'pencil2'
    repo_dir = flo('~/repos/{repo_name}')

    print_msg('## fetch latest pencil\n')
    checkup_git_repo(url='https://github.com/prikhi/pencil.git',
                     name=repo_name)

    print_msg('\n## build properties\n')
    update_or_append_line(flo('{repo_dir}/build/properties.sh'),
                          prefix='export MAX_VERSION=',
                          new_line="export MAX_VERSION='100.*'")
    run(flo('cat {repo_dir}/build/properties.sh'))

    run(flo('cd {repo_dir}/build && ./build.sh  linux'),
        msg='\n## build pencil\n')
    install_user_command('pencil2', pencil2_repodir=repo_dir)
    print_msg('\nNow You can start pencil version 2 with this command:\n\n'
              '    pencil2')


@task
@suggest_localhost
def pencil3():
    '''Install or update latest Pencil version 3, a GUI prototyping tool.

    While it is the newer one and the GUI is more fancy, it is the "more beta"
    version of pencil.  For exmaple, to display a svg export may fail from
    within a reveal.js presentation.

    More info:
        Homepage: http://pencil.evolus.vn/Next.html
        github repo: https://github.com/evolus/pencil
    '''
    repo_name = 'pencil3'
    repo_dir = flo('~/repos/{repo_name}')
    print_msg('## fetch latest pencil\n')
    checkup_git_repo(url='https://github.com/evolus/pencil.git', name=repo_name)
    run(flo('cd {repo_dir} && npm install'), msg='\n## install npms\n')
    install_user_command('pencil3', pencil3_repodir=repo_dir)
    print_msg('\nNow You can start pencil version 3 with this command:\n\n'
              '    pencil3')


@task
def server_prepare_root_bin_dir():
    '''Install custom commands for user root at '/root/bin/'.'''
    commands = ['run_backup']
    for command in commands:
        install_file(flo('/root/bin/{command}'), sudo=True)
        sudo(flo('chmod 755 /root/bin/{command}'))
        if command == 'run_backup':
            sudo('ln -snf /root/bin/run_backup /etc/cron.daily/run_backup')


@task
@suggest_localhost
def latex():
    '''Install a lot of packages to compile latex documents.

    A latex installation may be "completed" by the execution of the task
    'setup.users_bin_dir'.
    '''
    install_packages([
        'texlive',
#        'texlive-doc-de', # Gibt es nur auf ubuntu 14.04?
        'texlive-fonts-extra',
        'texlive-generic-extra',
        'texlive-lang-german',
        'texlive-latex-extra',
        'pandoc',
    ])


@task
@needs_repo_fabsetup_custom
def irssi():
    '''Set up irc client irssi.

    More infos:
     * https://wiki.archlinux.org/index.php/Irssi
    '''
    install_packages(['irssi'])
    install_file('~/.irssi/config')
    run(os.path.expanduser('chmod 600 ~/.irssi/config'))
    # TODO autostart irssi within of a tmux session "as a service"


@task
@needs_repo_fabsetup_custom # for import of domain_groups from config.py
@needs_packages('git', 'nginx', 'tree')
def server_letsencrypt():
    '''Create tls-webserver certificates which are trusted by the web pki.

    More info:
     * www.letsencrypt.org
     * https://letsencrypt.readthedocs.org/en/latest/
     * https://tty1.net/blog/2015/using-letsencrypt-in-manual-mode_en.html
    '''
    checkup_git_repo(url='https://github.com/letsencrypt/letsencrypt.git')
    sudo('service nginx stop')
    options = ' '.join([
        '--standalone',
        '--rsa-key-size 4096',
        # obtain a new certificate that duplicates an existing certificate
#        '--duplicate',
    ])
    from config import domain_groups
    for domains in domain_groups:
        domain_opts = ' '.join([flo(' -d {domain}') for domain in domains])
        # command 'letsencrypt-auto' requests for root by itself via 'sudo'
        run(flo('~/repos/letsencrypt/letsencrypt-auto  certonly  {options} {domain_opts}'))
        # FIXME 'letsencrypt-auto reenwal' of already existing certificates
    sudo('service nginx start')
    sudo('tree /etc/letsencrypt')


@task
@needs_repo_fabsetup_custom # for import of domain_groups from config.py
@suggest_localhost
def powerline_shell():
    '''Install and set up powerline-shell prompt.

    More infos:
     * https://github.com/banga/powerline-shell
     * https://github.com/ohnonot/powerline-shell
     * https://askubuntu.com/questions/283908/how-can-i-install-and-use-powerline-plugin
    '''
    assert env.host == 'localhost', 'This task cannot run on a remote host'

    # set up fonts for powerline

    checkup_git_repo('https://github.com/powerline/fonts.git',
            name='powerline-fonts')
    run('cd ~/repos/powerline-fonts && ./install.sh')
#    run('fc-cache -vf ~/.local/share/fonts')
    prefix = 'URxvt*font: '
    from config import fontlist
    line = prefix + fontlist
    update_or_append_line(filename='~/.Xresources', prefix=prefix,
            new_line=line)
    if env.host_string == 'localhost':
        run('xrdb  ~/.Xresources')

    # set up powerline-shell

    checkup_git_repo('https://github.com/banga/powerline-shell.git')
#    checkup_git_repo('https://github.com/ohnonot/powerline-shell.git')
    install_file(path='~/repos/powerline-shell/config.py')
    run('cd ~/repos/powerline-shell && ./install.py')

    question = 'Use normal question mark (u003F) for untracked files instead '\
        'of fancy "black question mark ornament" (u2753, which may not work)?'
    if query_yes_no(question, default='yes'):
        filename = '~/repos/powerline-shell/powerline-shell.py'
        update_or_append_line(filename, keep_backup=False,
                              prefix="        'untracked': u'\u2753',",
                              new_line="        'untracked': u'\u003F',")
        run(flo('chmod u+x  {filename}'))

    bash_snippet = '~/.bashrc_powerline_shell'
    install_file(path=bash_snippet)
    prefix = flo('if [ -f {bash_snippet} ]; ')
    enabler = flo('if [ -f {bash_snippet} ]; then source {bash_snippet}; fi')
    uncomment_or_update_or_append_line(filename='~/.bashrc', prefix=prefix,
                                       new_line=enabler)


@task
@suggest_localhost
def telegram():
    '''Install Telegram desktop client for linux (x64).

    More infos:
      https://telegram.org
      https://desktop.telegram.org/
    '''
    if not exists('~/bin/Telegram', msg='Download and install Telegram:'):
        run('mkdir -p /tmp/telegram')
        run('cd /tmp/telegram  &&  wget https://telegram.org/dl/desktop/linux')
        run('cd /tmp/telegram  &&  tar xf linux')
        with warn_only():
            run('mv /tmp/telegram/Telegram  ~/bin')
        run('rm -rf /tmp/telegram')
    else:
        print('skip download, dir ~/bin/Telegram already exists')
    run('ln -snf ~/bin/Telegram/Telegram  ~/bin/telegram',
            msg="\nCreate executable 'telegram':")
