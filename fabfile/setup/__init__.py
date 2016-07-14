import os.path
import tempfile

from fabric.api import cd, env, sudo
from fabric.contrib.files import append

from ..fabutils import exists, install_packages, install_package
from ..fabutils import install_file, install_user_command, needs_packages
from ..fabutils import needs_repo_fabsetup_custom, put, run
from ..fabutils import checkup_git_repo, checkup_git_repos, task
from ..utils import doc1, print_doc1, flo, print_full_name, query_yes_no
from ..utils import black, red, green, yellow, blue, magenta, cyan, white
from ..utils import filled_out_template

import service


@task
def ripping_of_cds():
    '''Install the tools ripit and burnit in order to rip and burn audio cds.

    More info: http://forums.debian.net/viewtopic.php?f=16&t=36826
    '''
    # install and configure ripit
    install_packages([
        'ripit',
    ])
    install_file(path='~/.ripit/config', username=env.user)
    # install burnit
    run('mkdir -p  ~/bin')
    put('fabfile_data/files/home/USERNAME/bin/burnit', '~/bin/burnit')
    run('chmod 755 ~/bin/burnit')


@task
def regex_repl():
    '''Install RegexREPL, a helper tool for building regular expressions.

    More infos:
     * https://github.com/theno/RegexREPL
     * REPL: https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop
    '''
    install_package('libterm-readline-gnu-perl')
    checkup_git_repo(url='https://github.com/theno/RegexREPL.git')
    for cmd in ['find_regex_repl.pl', 'match_regex_repl.pl']:
        run(flo('ln -snf  ~/repos/RegexREPL/{cmd} ~/bin/{cmd}'))


@task
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
    put('fabfile_data/files/home/USERNAME/.Xresources', '~/.Xresources')
    if env.host_string == 'localhost':
        run('xrdb  ~/.Xresources')

    # install and call term_colors
    run('mkdir -p  ~/bin')
    put('fabfile_data/files/home/USERNAME/bin/term_colors', '~/bin/term_colors')
    run('chmod 755 ~/bin/term_colors')
    run('~/bin/term_colors')


@task
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
    # custom ~/.vimrc
    put('fabfile_data/files/home/USERNAME/.vimrc', '~/.vimrc')

    # first, install pathogen
    run('mkdir -p  ~/.vim/autoload  ~/.vim/bundle')
    checkup_git_repo(url='https://github.com/tpope/vim-pathogen.git')
    run('ln -snf  ~/repos/vim-pathogen/autoload/pathogen.vim  ~/.vim/autoload/pathogen.vim')
    # then, install vim packages
    install_package('ctags') # required by package tagbar
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
def tmux():
    '''Customize tmux for solarized colors and other things.

    Tweaks for:
     * enable 256 colors
     * correct highlighting within man pages,
       cf. http://stackoverflow.com/a/10563271
    '''
    put('fabfile_data/files/home/USERNAME/.tmux.conf', '~/.tmux.conf')

    # create a terminfo file with modified sgr, smso, rmso, sitm and ritm
    # entries
    # Infos:
    # * http://stackoverflow.com/a/10563271
    # * http://tmux.svn.sourceforge.net/viewvc/tmux/trunk/FAQ
    cmds = r'''
mkdir -p  $HOME/.terminfo/
screen_terminfo="screen"
infocmp "$screen_terminfo" | sed \
  -e 's/^screen[^|]*|[^,]*,/screen-it|screen with italics support,/' \
  -e 's/%?%p1%t;3%/%?%p1%t;7%/' \
  -e 's/smso=[^,]*,/smso=\\E[7m,/' \
  -e 's/rmso=[^,]*,/rmso=\\E[27m,/' \
  -e '$s/$/ sitm=\\E[3m, ritm=\\E[23m,/' > /tmp/screen.terminfo
tic /tmp/screen.terminfo'''
    run(cmds)


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
    else:
        run('curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash')


@task
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
def pencil():
    '''Install or update Pencil, a GUI prototyping tool.'''
    checkup_git_repo(url='https://github.com/prikhi/pencil.git')
    run('cd ~/repos/pencil/build && ./build.sh  linux')
    install_user_command('pencil')


@task
def server_prepare_root_bin_dir():
    '''Install custom commands for user root at '/root/bin/'.'''
    commands = ['run_backup']
    for command in commands:
        put(flo('fabfile_data/files/root/bin/{command}'), '/tmp')
        sudo('mkdir -p /root/bin')
        sudo(flo('mv /tmp/{command} /root/bin/{command}'))
        sudo(flo('chmod 755 /root/bin/{command}'))
        if command == 'run_backup':
            sudo('ln -snf /root/bin/run_backup /etc/cron.daily/run_backup')


@task
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
    put('fabsetup_custom/files/home/USERNAME/.irssi/config',
        os.path.expanduser('~/.irssi/config'))
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
