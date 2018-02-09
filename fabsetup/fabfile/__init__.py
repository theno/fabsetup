# ~*~ coding: utf-8 ~*~
'''Set up and maintain a local or remote (Ubuntu) linux system.'''

import ConfigParser
import os.path
import StringIO
import sys

import fabric.main
import fabric.operations

from os.path import dirname, isdir, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from fabric.api import hosts

import fabsetup
from fabsetup.fabutils import task, needs_packages, needs_repo_fabsetup_custom
from fabsetup.fabutils import run, suggest_localhost, subtask
from fabsetup.fabutils import install_file_legacy, exists
from fabsetup.fabutils import FABSETUP_CUSTOM_DIR, import_fabsetup_custom
from fabsetup.fabutils import FABFILE_DATA_DIR
from fabsetup.utils import flo
from fabsetup.utils import cyan, blue, green, magenta, red
from fabsetup.utils import query_input, query_yes_no
from fabsetup.addons import load_pip_addons, load_repo_addons

import setup  # load tasks from module setup


if not isdir(FABSETUP_CUSTOM_DIR):

    from fabric.api import task

    @task(default=True)
    @needs_repo_fabsetup_custom
    def INIT():
        '''Init repo `~/.fabsetup-custom` with custom tasks and config.'''
        # decorator @needs_repo_fabsetup_custom makes the job
        print(green('Initialization finished\n'))
        fabsetup_custom_dir = FABSETUP_CUSTOM_DIR
        fabric.operations.local(flo('tree {fabsetup_custom_dir}'))
        print('\nList available tasks: ' + blue('fabsetup -l'))
        print('Show details of a task: `fabsetup -d <task>`, eg: ' +
              blue('fabsetup -d new_addon'))

    @task
    @needs_repo_fabsetup_custom
    def setup_desktop():
        '''Run setup tasks to set up a nicely configured desktop pc.'''
        # decorator @needs_repo_fabsetup_custom makes the job
        print('Init completed. Now run this task again.')
        # Next time, the task setup_desktop from
        # ~/.fabsetup-custom/fabfile_/__init__.py will be executed
        # instead

    @task
    @needs_repo_fabsetup_custom
    def setup_webserver():
        '''Run setup tasks to set up a nicely configured webserver.'''
        # decorator @needs_repo_fabsetup_custom makes the job
        print('Init completed. Now run this task again.')
        # Next time, the task setup_webserver from
        # ~/.fabsetup-custom/fabfile_/__init__.py will be executed
        # instead

else:
    from fabric.api import task
    _dir = dirname(dirname(__file__)).rsplit('/fabsetup')[0]

    @task(default=True)
    def list_tasks():
        '''List available tasks.'''
        fabric.operations.local('cd {_dir} && fab -l'.format(_dir=_dir))
        print('\nfabsetup-%s' % fabsetup.__version__)

    import_fabsetup_custom(globals())


@task
@suggest_localhost
@needs_packages('debian-goodies')  # for command 'checkrestart'
def up():
    '''Update and upgrade all packages of the Debian or Ubuntu OS.'''
    run('sudo apt-get update')
    run('sudo apt-get dist-upgrade')
    run('sudo apt-get autoremove')
    run('sudo checkrestart')
    dfh()
    check_reboot()


def check_reboot():
    print(magenta('Reboot required?'))
    # check file '/var/run/reboot-required', cf. http://askubuntu.com/a/171
    res = run('; '.join([
        "prefix='\\033['; postfix='\\033[0m'",
        "if [ -f /var/run/reboot-required ]",
        'then echo "${prefix}31mReboot required!${postfix}"',
        'else echo "${prefix}32mNope.${postfix}"',
        'fi',
    ]))
    if res:
        fabric.operations.local(flo('echo "{res}"'))  # interpolate res


@task
def reboot():
    '''Reboot the server.'''
    fabric.operations.reboot()


@task
@suggest_localhost
def dfh():
    '''Print used disc space.'''
    run('sudo  df -ih')
    run('sudo  df -h')


def git_name_and_email_or_die():
    config = ConfigParser.ConfigParser()
    filename = os.path.expanduser('~/.gitconfig')
    try:
        with open(filename) as fh:
            gitconfig = fh.readlines()
    except IOError:
        print(red('~/.gitconfig does not exist') + ', run:\n')
        print('    git config --global user.name "Your Name"')
        print('    git config --global user.email "your.email@example.com"')
        sys.exit()

    config.readfp(StringIO.StringIO(''.join([line.lstrip()
                                             for line
                                             in gitconfig])))

    name = None
    email = None
    try:
        name = config.get('user', 'name')
    except ConfigParser.NoOptionError:
        print(red('missing user.name in ~/.gitconfig') + ', run:\n')
        print('    git config --global user.name "Your Name"')
        sys.exit()
    try:
        email = config.get('user', 'email')
    except ConfigParser.NoOptionError:
        print(red('missing user.email in ~/.gitconfig') + ', run:\n')
        print('    git config --global user.email "your.email@example.com"')
        sys.exit()

    return name, email


@subtask
def create_files(
        # '/home/theno/.fabsetup-addon-repos/fabsetup-theno-termdown'
        addon_dir,
        username,   # 'theno'
        addonname,  # 'termdown'
        taskname,   # 'termdown'
        author,
        author_email,
        headline='',
        description='',
        touched_files=''):
    filenames = [
        '.gitignore',
        'fabfile-dev.py',
        'fabfile.py',
        'LICENSE',
        'README.md',
        'requirements.txt',
        'setup.py',
        'fabsetup_USER_TASK/fabutils.py',
        'fabsetup_USER_TASK/__init__.py',
        'fabsetup_USER_TASK/_version.py',
    ]
    for filename in filenames:
        install_file_legacy(
            path=flo('~/.fabsetup-addon-repos/fabsetup-USER-ADDON/{filename}'),
            username=username,
            addonname=addonname,
            taskname=taskname,
            headline=headline,
            description=description,
            touched_files=touched_files,
            author=author,
            author_email=author_email,
            USER=username,
            ADDON=addonname,
            TASK=taskname,
        )

    # avoid substitution of USERNAME in path
    install_file_legacy(
        path='~/.fabsetup-addon-repos/fabsetup-{USER}-{ADDON}/'
             'fabsetup_{USER}_{TASK}/files/home/USERNAME/bin/'
             'termdown.template'.format(USER=username,
                                        ADDON=addonname,
                                        TASK=taskname),
        from_path='~/.fabsetup-addon-repos/fabsetup-USER-ADDON/'
                  'fabsetup_USER_TASK/files/home/USERNAME/bin/'
                  'termdown.template')

    print('')
    fabric.operations.local(flo('tree {addon_dir}'))


@subtask
def init_git_repo(basedir):
    basedir_abs = os.path.expanduser(basedir)
    if os.path.isdir(flo('{basedir_abs}/.git')):
        print('git repo already initialized (skip)')
    else:
        fabric.operations.local(flo('cd {basedir} && git init'))
        fabric.operations.local(flo('cd {basedir} && git add .'))
        fabric.operations.local(
            flo('cd {basedir} && git commit -am "Initial commit"'))


@subtask
def create_github_remote_repo(basedir, github_user, github_repo):
    repo_url = cyan(flo('https://github.com/{github_user}/{github_repo}'))
    question = flo('Create remote repo {repo_url} at github.com?')
    if query_yes_no(question, default='yes'):
        run(flo("cd {basedir}  &&  "
                "curl -u '{github_user}' https://api.github.com/user/repos "
                "-d '") + '{"name":"' + flo('{github_repo}"') + "}'")
        run(flo('cd {basedir}  &&  '
                'git remote add origin '
                'git@github.com:{github_user}/{github_repo}.git'))
        run(flo('cd {basedir}  &&  git push origin master'))
    else:
        print('\nplease, do it yourself:\n'
              '  https://help.github.com/articles/'
              'adding-an-existing-project-to-github-using-the-command-line/')


@subtask
def summary(addon_dir, username, taskname):
    print('run your task:')
    print('')
    print('    # with fabsetup as an addon')
    print('    cd .fabsetup')
    print(flo('    fab -d {username}.{taskname}'))
    print(flo('    fab {username}.{taskname}'))
    print('')
    print('    # standalone')
    print(flo('    cd {addon_dir}'))
    print(flo('    pip install -r requirements.txt'))
    print(flo('    fab {username}.{taskname}'))
    print('')
    print('addon development:')
    print('')
    print(flo('    cd {addon_dir}'))
    print('    fab -f fabfile-dev.py -l')
    print('    fab -f fabfile-dev.py test')
    print("    git commit -am 'my commit message'")
    print('    git push origin master  # publish at github')
    print('    fab -f fabfile-dev.py pypi  # publish pip package at pypi')
    print('')
    print('The task code is defined in')
    print(cyan(flo('  {addon_dir}/fabsetup_{username}_{taskname}/__init__.py')))
    print('Your task output should be in markdown style.\n')
    print('More infos: '
          'https://github.com/theno/fabsetup/blob/master/howtos/'
          'fabsetup-addon.md')


@task
@hosts('localhost')
def new_addon():
    '''Create a repository for a new fabsetup-task addon.

    The repo will contain the fabsetup addon boilerplate.

    Running this task you have to enter:
    * your github user account (your pypi account should be the same or similar)
    * addon name
    * task name
    * headline, short description, and touched (and created) files and dirs
      for the task docstring and the README.md

    Created files and dirs:

        ~/.fabsetup-addon-repos/fabsetup-{user}-{addon}
                                ├── fabfile-dev.py
                                ├── fabfile.py
                                ├── fabsetup_{user}_{task}
                                │   ├── files
                                │   │   └── home
                                │   │       └── USERNAME
                                │   │           └── bin
                                │   │               └── termdown.template
                                │   ├── __init__.py  <--.
                                │   └── _version.py      `- task definition
                                ├── .git
                                │   ├── ...
                                │   ├── config
                                │   └── ...
                                ├── .gitignore
                                ├── README.md
                                ├── requirements.txt
                                └── setup.py
    '''
    author, author_email = git_name_and_email_or_die()

    username = query_input('github username:')

    addonname = query_input('\naddon name:', default='termdown')
    addonname = addonname.replace('_', '-').replace(' ', '-')  # minus only
    full_addonname = flo('fabsetup-{username}-{addonname}')
    print('└─> full addon name: {0}\n'.format(
        cyan(full_addonname)))

    taskname = query_input('task name:', default=addonname.replace('-', '_'))
    taskname = taskname.replace('-', '_').replace(' ', '_')  # underscores only
    print('└─> full task name: {0}'.format(
        cyan(flo('{username}.{taskname}\n'))))

    addon_dir = os.path.expanduser(flo(
        '~/.fabsetup-addon-repos/fabsetup-{username}-{addonname}'))

    if os.path.exists(addon_dir):
        print(red(flo('\n{addon_dir} already exists.')))
        print('abort')
    else:
        print('~/.gitconfig')
        print('├─> author: {0} ─> LICENSE, setup.py'.format(cyan(author)))
        print('└─> author email: {0} ─> setup.py'.format(cyan(author_email)))

        headline = query_input(
            '\nshort task headline:',
            default='Install or update termdown.')
        description = query_input(
            'describing infos:',
            default='Command `termdown 25m` is practical '
                    'to time pomodoro sessions.')
        touched_files = query_input(
            'affected files and dirs:',
            default='~/bin/termdown')

        print('\naddon git-repository dir: {0}'.format(cyan(addon_dir)))
        if not query_yes_no('create new addon?', default='yes'):
            print('abort')
        else:
            create_files(addon_dir, username, addonname, taskname,
                         author, author_email,
                         headline, description, touched_files)
            init_git_repo(addon_dir)
            create_github_remote_repo(basedir=addon_dir,
                                      github_user=username,
                                      github_repo=full_addonname)
            summary(addon_dir, username, taskname)


load_pip_addons(globals())
load_repo_addons(globals())
