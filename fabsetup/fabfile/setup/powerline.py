import os.path

from fabric.api import env

from fabsetup.fabutils import checkup_git_repo, needs_packages
from fabsetup.fabutils import needs_repo_fabsetup_custom, suggest_localhost
from fabsetup.fabutils import install_file, run, subtask, subsubtask, task
from fabsetup.utils import flo, update_or_append_line, comment_out_line
from fabsetup.utils import uncomment_or_update_or_append_line, query_yes_no


@task
@needs_repo_fabsetup_custom
@suggest_localhost
@needs_packages('python-pip')
def powerline():
    '''Install and set up powerline for vim, bash, tmux, and i3.

    It uses pip (python2) and the most up to date powerline version (trunk) from
    the github repository.

    More infos:
      https://github.com/powerline/powerline
      https://powerline.readthedocs.io/en/latest/installation.html
      https://github.com/powerline/fonts
      https://youtu.be/_D6RkmgShvU
      http://www.tecmint.com/powerline-adds-powerful-statuslines-and-prompts-to-vim-and-bash/
    '''
    bindings_dir, scripts_dir = install_upgrade_powerline()
    set_up_powerline_fonts()
    set_up_powerline_daemon(scripts_dir)
    powerline_for_vim(bindings_dir)
    powerline_for_bash_or_powerline_shell(bindings_dir)
    powerline_for_tmux(bindings_dir)
    powerline_for_i3(bindings_dir)
    print('\nYou may have to reboot for make changes take effect')


@subsubtask
def install_special_glyphs():
    '''
    More infos:
      https://powerline.readthedocs.io/en/latest/installation/linux.html#fonts-installation
      https://wiki.archlinux.org/index.php/Font_configuration
      $XDG_CONFIG_HOME: http://superuser.com/a/365918
    '''
    from_dir = '~/repos/powerline/font'

    run('mkdir -p ~/.local/share/fonts')
    run(flo('cp {from_dir}/PowerlineSymbols.otf  ~/.local/share/fonts'))

    to_dir = '~/.config/fontconfig/conf.d/'
    run(flo('mkdir -p {to_dir}'))
    run(flo('cp {from_dir}/10-powerline-symbols.conf  {to_dir}'))


@subtask
def install_upgrade_powerline():
    '''
    More infos:
      https://powerline.readthedocs.io/en/latest/installation.html#pip-installation
    '''
    checkup_git_repo('https://github.com/powerline/powerline.git')
    path_to_powerline = os.path.expanduser('~/repos/powerline')
    run(flo('pip install --user --editable={path_to_powerline}'))
    run('pip show powerline-status')  # only for information
    install_special_glyphs()
    bindings_dir = '~/repos/powerline/powerline/bindings'
    scripts_dir = '~/repos/powerline/scripts'
    return bindings_dir, scripts_dir


@subtask
def set_up_powerline_fonts():
    checkup_git_repo('https://github.com/powerline/fonts.git',
                     name='powerline-fonts')
    # install fonts into ~/.local/share/fonts
    run('cd ~/repos/powerline-fonts && ./install.sh')
    prefix = 'URxvt*font: '
    from config import fontlist
    line = prefix + fontlist
    update_or_append_line(filename='~/.Xresources', prefix=prefix,
                          new_line=line)
    if env.host_string == 'localhost':
        run('xrdb  ~/.Xresources')


@subtask
def set_up_powerline_daemon(scripts_dir):
    bash_snippet = '~/.bashrc_powerline_daemon'
    install_file(path=bash_snippet, scripts_dir=scripts_dir)
    prefix = flo('if [ -f {bash_snippet} ]; ')
    enabler = flo('if [ -f {bash_snippet} ]; then source {bash_snippet}; fi')
    update_or_append_line(filename='~/.bashrc', prefix=prefix, new_line=enabler)


@subtask
def powerline_for_vim(bindings_dir):
    pass  # TODO


def powerline_for_bash_or_powerline_shell(bindings_dir):
    '''Set up the bash extension of powerline or powerline_shell (another task).
    '''
    question = '\nSet up powerline-shell instead of powerline bash extension?'
    if query_yes_no(question, default='yes'):
        from setup import powerline_shell
        powerline_shell()
        # disable powerline bash extension if it has been set up
        powerline_bash_enabler = 'if [ -f ~/.bashrc_powerline_bash ]; then ' \
                                 'source ~/.bashrc_powerline_bash; fi'
        comment_out_line(filename='~/.bashrc', line=powerline_bash_enabler)
    else:
        powerline_for_bash(bindings_dir)
        # disable powerline_shell if it has been set up
        powerline_shell_enabler = 'if [ -f ~/.bashrc_powerline_shell ]; then ' \
                                  'source ~/.bashrc_powerline_shell; fi'
        comment_out_line(filename='~/.bashrc', line=powerline_shell_enabler)


@subtask
def powerline_for_bash(bindings_dir):
    bash_snippet = '~/.bashrc_powerline_bash'
    install_file(path=bash_snippet, bindings_dir=bindings_dir)
    prefix = flo('if [ -f {bash_snippet} ]; ')
    enabler = flo('if [ -f {bash_snippet} ]; then source {bash_snippet}; fi')
    uncomment_or_update_or_append_line(filename='~/.bashrc', prefix=prefix,
                                       new_line=enabler, comment='#')


@subtask
def powerline_for_tmux(bindings_dir):
    pass  # TODO


@subtask
def powerline_for_i3(bindings_dir):
    pass  # TODO
