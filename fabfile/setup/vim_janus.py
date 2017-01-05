from fabric.api import warn_only, execute

from fabfile.fabutils import custom_task as task  # here, every task is custom
from fabfile.fabutils import suggest_localhost, needs_packages, exists, subtask
from fabfile.fabutils import run, print_msg, subsubtask, install_file
from fabfile.fabutils import checkup_git_repos, needs_repo_fabsetup_custom
from fabfile.utils import flo, query_yes_no


REQUIRED_PACKAGES = ['vim', 'curl', 'tree', 'ruby-dev', 'rake',
                     'exuberant-ctags', 'ack-grep']


@task
@suggest_localhost
@needs_repo_fabsetup_custom
@needs_packages(*REQUIRED_PACKAGES)
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
            print_msg('not installed => install')
            install_janus()
        else:
            print_msg('already installed => update')
            update_janus()
        customize_janus()
        show_files_used_by_vim_and_janus()


@subtask
def install_janus():
    url = 'https://raw.githubusercontent.com/carlhuda/janus/master/bootstrap.sh'
    run(flo('curl {url} | bash'))


@subtask
def update_janus():
    run('cd ~/.vim  &&  rake')


def set_up_vim_addon_xmledit():
    print_msg('\nenable *.html files for vim addon xmledit:')
    ftplugin_dir = '~/.janus/xmledit/ftplugin'
    if exists(ftplugin_dir):
        # enable html file support (cf. http://stackoverflow.com/a/28603924):
        run(flo('cp -n {ftplugin_dir}/html.vim {ftplugin_dir}/html.vim.orig'))
        run(flo('ln -snf xml.vim {ftplugin_dir}/html.vim'))


def set_up_vim_addon_vim_instant_markdown():
    print_msg('\ninstall instant-markdown-d with npm (node.js) '
              'for vim addon vim-instant-markdown')
    install_cmd = 'npm install -g instant-markdown-d'
    with warn_only():
        res = run(install_cmd)
        if res.return_code != 0:
            print_msg('npm is not installed')
            query = "Run fabric task 'setup.nvm' in order to install npm?"
            if query_yes_no(query, default='yes'):
                from nvm import nvm
                execute(nvm)
                run('bash -c "source ~/.bashrc_nvm && nvm install node"',
                    msg='\ninstall latest version of npm')
                run(flo('bash -c "source ~/.bashrc_nvm && {install_cmd}"'),
                    msg="\nfabric task 'setup.nvm' finished\n\n"
                        '----\ninstall instant-markdown-d')


@subsubtask
def custom_vim_addons():
    from config import vim_janus_additional_addons
    checkup_git_repos(vim_janus_additional_addons, base_dir='~/.janus',
                      verbose=True, prefix='\n')
    set_up_vim_addon_xmledit()
    set_up_vim_addon_vim_instant_markdown()


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
def show_files_used_by_vim_and_janus():
    run('tree -L 1 ~/.vim', msg='.vim dir')
    run('tree -L 1 ~/.janus', msg='\n.janus dir')
    run('ls -hal ~/.gvimrc*', msg='\n.gvimrc files')
    run('ls -hal ~/.vimrc*', msg='\n.vimrc files')


@subtask
def uninstall_janus():
    '''Remove all janus files and dirs and (try to) restore previous vim config.
    '''
    if exists('~/.vim/janus'):
        run('rm -rf ~/.vim', msg='delete janus repo dir')
        with warn_only():
            run('rm -rf ~/.janus', msg='delete ~/.janus dir')
            run('bash -c "rm ~/.{,g}vimrc{,.before,.after}"',
                msg='delete ~/.vimrc, ~/.vimrc.before, ~/.vimrc.after, '
                    '~/.gvimrc, ~/.gvimrc.before and ~/.gvimrc.after')
            if exists('~/.vim.old'):
                run('mv ~/.vim.old  ~/.vim', msg='restore ~/.vim dir')
            for fname in ['~/.vimrc', '~/.gvimrc']:
                if exists(flo('{fname}.old')):
                    run(flo('mv {fname}.old  {fname}'),
                        msg=flo('restore {fname}'))
        run('ls -hal ~/.*vim*', msg='\nvim config restored:')
    else:
        print_msg('janus is not installed; nothing to do (abort)')
        exit(1)
