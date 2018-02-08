from fabric.api import env

from fabsetup.fabutils import exists, install_file_legacy, needs_packages, run, subtask
from fabsetup.fabutils import suggest_localhost, task
from fabsetup.utils import cyan, flo, uncomment_or_update_or_append_line


@task
@suggest_localhost
@needs_packages('git', 'build-essential', 'libssl-dev')
def nvm():
    '''Install latest or update to latest version of Node Version Manager (nvm).

    More infos:
      https://github.com/creationix/nvm/blob/master/README.markdown
    '''
    if not exists('~/.nvm/.git'):
        install_nvm()
        enable_nvm()
    else:
        upgrade_nvm()
    nvm_primer()


@subtask
def install_nvm():
    cmds = '''\
export NVM_DIR="$HOME/.nvm" && (
  git clone https://github.com/creationix/nvm.git "$NVM_DIR"
  cd "$NVM_DIR"
  git checkout `git describe --abbrev=0 --tags --match "v[0-9]*" origin`
) && . "$NVM_DIR/nvm.sh"'''
    run(cmds)


@subtask(doc1=True)
def enable_nvm():
    '''add to ~/.bashrc:  Export of $NVM env variable and load nvm command.'''
    bash_snippet = '~/.bashrc_nvm'
    install_file_legacy(path=bash_snippet)
    prefix = flo('if [ -f {bash_snippet} ]; ')
    enabler = flo('if [ -f {bash_snippet} ]; then source {bash_snippet}; fi')
    if env.host == 'localhost':
        uncomment_or_update_or_append_line(filename='~/.bashrc', prefix=prefix,
                                           new_line=enabler)
    else:
        print(cyan('\nappend to ~/.bashrc:\n\n    ') + enabler)


@subtask
def upgrade_nvm():
    cmds = '''\
(
  cd "$NVM_DIR"
  git fetch origin
  git checkout `git describe --abbrev=0 --tags --match "v[0-9]*" origin`
) && . "$NVM_DIR/nvm.sh"'''
    run(cmds)


@subtask(doc1=True)
def nvm_primer():
    '''Getting started with nvm (cf. https://github.com/creationix/nvm#usage).
    '''
    print('\nDownload, compile and install the latest release of node:\n\n' +
          cyan('    nvm install node'))
    print('\nAnd then in any new shell:\n\n' +
          cyan('    nvm use node') + '  #  use the installed version\n' +
          cyan('    nvm run node --version') + '  #  run it\n' +
          cyan('    nvm exec 4.2 node --version') + '  #  run any arbitrary '
          'command in a subshell with the desired version of node\n' +
          cyan('    nvm which 5.0') + '  # get the path to the executable to '
          'where it was installed')
    print('\nlist installed node versions:\n\n' +
          cyan('    nvm ls'))
    print('\nnvm usage:\n\n' +
          cyan('    nvm --help'))
    print('\n\n----\nBut at first, use a new shell or run `source ~/.bashrc`')
