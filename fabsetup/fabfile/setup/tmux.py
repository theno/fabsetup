from fabsetup.fabutils import install_file_legacy, run, suggest_localhost, subtask
from fabsetup.fabutils import task
from fabsetup.fabutils import checkup_git_repo


@task
@suggest_localhost
def tmux():
    '''Customize tmux for solarized colors and other things.

    Tweaks for:
     * enable 256 colors
     * correct highlighting within man pages,
       cf. http://stackoverflow.com/a/10563271
    '''
    install_file_legacy('~/.tmux.conf')
    set_up_terminfo()
    tmux_plugin_manager()


@subtask
def set_up_terminfo():
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


@subtask
def tmux_plugin_manager():
    checkup_git_repo(url='https://github.com/tmux-plugins/tpm',
                     name='tpm', base_dir='~/.tmux/plugins')
