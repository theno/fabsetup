from fabric.api import warn_only

from fabfile.fabutils import custom_task as task  # here, every task is custom
from fabfile.fabutils import suggest_localhost, needs_packages, exists, subtask
from fabfile.fabutils import run, print_msg, subsubtask, install_file
from fabfile.fabutils import checkup_git_repos, needs_repo_fabsetup_custom
from fabfile.utils import flo


@task
@suggest_localhost
@needs_repo_fabsetup_custom
@needs_packages('ruby-dev', 'rake', 'exuberant-ctags', 'ack-grep')
def vim_janus(uninstall=None):
    '''Install or update Janus, a distribution of addons and mappings for vim.

    More info:
      https://github.com/carlhuda/janus
      Customization: https://github.com/carlhuda/janus/wiki/Customization

    Args:
        uninstall: If not None, Uninstall janus and restore old vim config
    '''
    if uninstall is not None:
        uninstall_janus()
    else:
        if not exists('~/.vim/janus'):
            install_janus()
        else:
            update_janus()
        customize_janus()
    show_files_used_by_vim()


@subtask
def install_janus():
    url = 'https://raw.githubusercontent.com/carlhuda/janus/master/bootstrap.sh'
    run(flo('curl {url} | bash'))


@subtask
def update_janus():
    run('cd ~/.vim  &&  rake')


@subsubtask
def custom_vim_addons():
    from config import vim_janus_additional_addons
    checkup_git_repos(vim_janus_additional_addons, base_dir='~/.janus',
                      verbose=True, prefix='\n')


@subsubtask
def vimrc_customizations():
    install_file('~/.vimrc.before')
    install_file('~/.vimrc.after')
    install_file('~/.gvimrc.before')
    install_file('~/.gvimrc.after')


@subtask
def customize_janus():
    custom_vim_addons()
    vimrc_customizations()


@subtask
def show_files_used_by_vim():
    run('tree -L 1 ~/.vim ~/.janus', msg='.vim dir')
    run('ls -hal ~/.vimrc*', msg='\n.vimrc files')


@subtask
def uninstall_janus():
    '''Remove all janus files and dirs and (try to) restore previous vim config.
    '''
    if exists('~/.vim/janus'):
        run('rm -rf ~/.vim', msg='delete janus repo dir')
        with warn_only():
            run('rm -rf ~/.janus', msg='delete ~/.janus dir')
            run('rm ~/.{,g}vimrc.{before,after}',
                msg='delete ~/.vimrc.before, ~/.vimrc.after, '
                    '~/.gvimrc.before and ~/.gvimrc.after')
            run('mv ~/.vim.old  ~/.vim', msg='restore ~/.vim dir')
            run('mv ~/.vimrc.old  ~/.vimrc', msg='restore ~/.vimrc')
    else:
        print_msg('janus is not installed; nothing to do (abort)')
        exit(1)
