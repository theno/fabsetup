import re

from fabric.api import env, hide

from ...fabutils import needs_packages, run, subtask, task
from ...utils import cyan, flo, print_full_name, query_input, query_yes_no


@task
@needs_packages('nginx', 'postgresql', 'python-pip', 'git')
def trac():
    '''Set up a trac project.

    This trac installation uses python2, git, sqlite (trac-default), gunicorn,
    and nginx.

    More infos:
      https://trac.edgewall.org/wiki/TracInstall
      https://trac.edgewall.org/wiki/TracFastCgi#NginxConfiguration
      https://trac.edgewall.org/wiki/TracNginxRecipe
      https://trac.edgewall.org/wiki/Gunicorn
      http://www.obeythetestinggoat.com/book/chapter_08.html#_getting_to_a_production_ready_deployment
    '''
    hostname = re.sub(r'^[^@]+@', '', env.host)  # without username if any
    sitename = query_input(
                   question='\nEnter site-name of Your trac web service',
                   default=flo('trac.{hostname}'))
    username = env.user

    site_dir = flo('/home/{username}/sites/{sitename}')
    bin_dir = flo('{site_dir}/virtualenv/bin')

    # provisioning steps
    install_or_upgrade_virtualenv()
    create_directory_structure(site_dir)
    create_virtualenv(site_dir)

    if query_yes_no('\nRestore trac environment from backup tarball?',
                    default=None):
        restore_tracenv_from_backup_tarball(site_dir, bin_dir)
    elif query_yes_no('\nCreate a new trac environment?', default=None):
        init_tracenv(site_dir, bin_dir)

    # FIXME test-run:
    run_tracd(site_dir, bin_dir)


@subtask
def install_or_upgrade_virtualenv():
    run('sudo pip install --upgrade virtualenv')


@subtask
def create_directory_structure(site_dir):
    run(flo('mkdir -p {site_dir}'))


@subtask
def create_virtualenv(site_dir):
    python_version = 'python2'  # FIXME take latest python via pyenv
    run(flo('virtualenv --python={python_version}  {site_dir}/virtualenv'))
    run(flo('{site_dir}/virtualenv/bin/'
            'pip install --upgrade  genshi trac gunicorn'))


@subtask
def restore_tracenv_from_backup_tarball(site_dir, bin_dir):
    # FIXME stop trac is running already
    filename = query_input('tarball path?')
    run(flo('mkdir -p {site_dir}/tmp'))
    run(flo('tar xf {filename}  --directory={site_dir}/tmp'))
    run(flo('[ -d {site_dir}/tracenv ] && '
            'mv {site_dir}/tracenv  {site_dir}/tracenv.bak'))
    run(flo('mv {site_dir}/tmp/tracenv_hotcopy  {site_dir}/tracenv'))
    run(flo('rmdir {site_dir}/tmp'))
    run(flo('{bin_dir}/trac-admin {site_dir}/tracenv  upgrade'))
    run(flo('{bin_dir}/trac-admin {site_dir}/tracenv  wiki upgrade'))


@subtask
def init_tracenv(site_dir, bin_dir):
    run(flo('{bin_dir}/trac-admin  {site_dir}/tracenv  initenv'))


@subtask(doc1=True)
def run_tracd(site_dir, bin_dir):
    '''Run tracd  -- only for testing purpose.'''
    run(flo('{bin_dir}/tracd --port 8000 {site_dir}/tracenv'))
