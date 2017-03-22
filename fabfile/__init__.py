'''Set up and maintain a local or remote (Ubuntu) linux system.'''

import fabric.operations
import sys
from os.path import dirname, isdir, realpath
sys.path.append(dirname(dirname(realpath(__file__))))
from fabsetup.fabutils import task, needs_packages, needs_repo_fabsetup_custom
from fabsetup.fabutils import run, suggest_localhost
from fabsetup.fabutils import FABSETUP_CUSTOM_DIR, import_fabsetup_custom
from fabsetup.utils import flo
from fabsetup.utils import green, blue, magenta

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
