# ~*~ coding: utf-8 ~*~
'''Set up and maintain a local or remote (Ubuntu) linux system.'''


import fabric.operations
import os.path
import sys

from os.path import dirname, isdir, realpath
sys.path.append(dirname(dirname(realpath(__file__))))

from fabric.api import hosts

from fabsetup.fabutils import task, needs_packages, needs_repo_fabsetup_custom
from fabsetup.fabutils import run, suggest_localhost, subtask
from fabsetup.fabutils import install_file, exists
from fabsetup.fabutils import FABSETUP_CUSTOM_DIR, import_fabsetup_custom
from fabsetup.utils import flo
from fabsetup.utils import green, blue, magenta, red
from fabsetup.utils import query_input
from fabsetup.addons import load_pip_addons, load_repo_addons

import setup  # load tasks from module setup


if not isdir(FABSETUP_CUSTOM_DIR):

    from fabric.api import task

    @task(default=True)
    @needs_repo_fabsetup_custom
    def INIT():
        '''Init repo `fabsetup_custom` with custom tasks and config.'''
        # decorator @needs_repo_fabsetup_custom makes the job
        print(green('Initialization finished\n'))
        print('List available tasks: ' + blue('fab -l'))
        print('Show details of a task: `fab -d <task>`, eg.: ' +
              blue('fab -d setup_webserver'))

    @task
    @needs_repo_fabsetup_custom
    def setup_desktop():
        '''Run setup tasks to set up a nicely configured desktop pc.'''
        # decorator @needs_repo_fabsetup_custom makes the job
        print('Init completed. Now run this task again.')
        # Next time, the task setup_desktop from
        # fabsetup_custom/fabfile_/__init__.py will be executed
        # instead

    @task
    @needs_repo_fabsetup_custom
    def setup_webserver():
        '''Run setup tasks to set up a nicely configured webserver.'''
        # decorator @needs_repo_fabsetup_custom makes the job
        print('Init completed. Now run this task again.')
        # Next time, the task setup_webserver from
        # fabsetup_custom/fabfile_/__init__.py will be executed
        # instead

else:
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


@subtask
def create_files(addon_dir, username, addonname, taskname,
                 headline, description, touched_files):
    filenames = [
        '.gitignore',
        'fabfile-dev.py',
        'fabfile.py',
        'LICENSE',
        'README.md',
        'requirements.txt',
        'setup.py',
        'fabsetup_USER_TASK/__init__.py',
        'fabsetup_USER_TASK/_version.py',
    ]
    for filename in filenames:
        install_file(
            path=flo('~/.fabsetup-repos/fabsetup-USER-ADDON/{filename}'),
            username=username, taskname=taskname,
            headline=headline, description=description,
            touched_files=touched_files,
            full_username=username,  # TODO
            USER=username, ADDON=addonname, TASK=taskname)
    print('')
    fabric.operations.local(flo('tree {addon_dir}'))


@subtask
def init_git_repo(basedir):
    basedir_abs = os.path.expanduser(basedir)
    if os.path.isdir(flo('{basedir_abs}/.git')):
        print('git repo already initialized (skip)')
    else:
        if not exists('{basedir_abs}/.gitignore'):
            install_file(path=flo('{basedir_abs}/.gitignore'),
                         from_path='~/repos/my_presi/.gitignore')
        fabric.operations.local(flo('cd {basedir} && git init'))
        fabric.operations.local(flo('cd {basedir} && git add .'))
        fabric.operations.local(
            flo('cd {basedir} && git commit -am "Initial commit"'))
    # TODO: ask to push to github


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
    print(flo('  {addon_dir}/fabsetup_{username}_{taskname}/__init__.py'))
    print('Your task output should be in markdown style.')


@task
@hosts('localhost')
def new_addon():
    '''Create a repository for a new fabsetup-task addon.

    The repo will contain the fabsetup addon boilerplate.

    Running this task you have to enter:
    * Your github user account (your pypi account should be the same or similar)
    * Addon / (main) task name
    * Headline and short description for the task docstring and the README.md

    Created files and dirs:

        ~/.fabsetup-repos/fabsetup-{user}-{task}
                          ├── fabfile.py
                          ├── fabfile-dev.py
                          ├── fabsetup_{user}_{task}
                          │   ├── __init__.py  <----- task definition
                          │   └── _version.py
                          ├── README.md
                          ├── requirements.txt
                          └── setup.py
    '''
    username = query_input('github username:')

    addonname = query_input('addon name:', default='termdown')
    addonname = addonname.replace('_', '-').replace(' ', '-')  # minus only

    taskname = query_input('task name:', default=addonname.replace('-', '_'))
    taskname = taskname.replace('-', '_').replace(' ', '_')  # underscores only

    addon_dir = os.path.expanduser(flo(
        '~/.fabsetup-repos/fabsetup-{username}-{addonname}'))

    if os.path.exists(addon_dir):
        print(red(flo('\n{addon_dir} already exists. abort')))
    else:
        headline = query_input(
            'short task headline:',
            default='Install or update termdown.')
        description = query_input(
            'describing infos:',
            default='Command `termdown 25m` is practical '
                    'to time pomodoro sessions.')
        touched_files = query_input(
            'Affected files and dirs:',
            default='~/bin/termdown')

        create_files(addon_dir, username, addonname, taskname,
                     headline, description, touched_files)
        init_git_repo(addon_dir)
        summary(addon_dir, username, taskname)


load_pip_addons(globals())
load_repo_addons(globals())
