import re

from fabric.api import env, hide

from ...fabutils import needs_packages, run, task
from ...utils import flo, query_input, query_yes_no


@task
@needs_packages('nginx', 'postgresql', 'python-pip', 'git')
def trac():
    '''Set up a trac project.

    This trac installation uses python2, git, sqlite (trac-default), gunicorn,
    and nginx.

    More infos:
     * https://trac.edgewall.org/wiki/TracInstall
     * https://trac.edgewall.org/wiki/TracFastCgi#NginxConfiguration
     * https://trac.edgewall.org/wiki/TracNginxRecipe
     * https://trac.edgewall.org/wiki/Gunicorn
     * http://www.obeythetestinggoat.com/book/chapter_08.html#_getting_to_a_production_ready_deployment
    '''
    run('sudo pip install --upgrade virtualenv')

    hostname = re.sub(r'^[^@]+@', '', env.host)  # without username if any
    sitename = query_input(
                   question='\nEnter site-name of Your trac web service',
                   default=flo('trac.{hostname}'))
    username = env.user
    site_dir = flo('/home/{username}/sites/{sitename}')
    run('mkdir -p {site_dir}')
    python_version = 'python2'  # FIXME take latest python via pyenv
    run(flo('virtualenv --python={python_version}  {site_dir}/virtualenv'))

    bin_dir = flo('{site_dir}/virtualenv/bin')
    run(flo('{bin_dir}/pip install --upgrade  genshi trac'))

    if query_yes_no('Restore trac environment from backup tarball?', default=None):
        # FIXME stop trac is running already
        filename = query_input('tarball path?')
        run(flo('mkdir -p {site_dir}/tmp'))
        run(flo('tar xf {filename}  --directory={site_dir}/tmp'))
        run(flo('[ -d {site_dir}/tracenv ] && mv {site_dir}/tracenv  {site_dir}/tracenv.bak'))
        run(flo('mv {site_dir}/tmp/tracenv_hotcopy  {site_dir}/tracenv'))
        run(flo('rmdir {site_dir}/tmp'))
        run(flo('{bin_dir}/trac-admin {site_dir}/tracenv  upgrade'))
        run(flo('{bin_dir}/trac-admin {site_dir}/tracenv  wiki upgrade'))
    elif query_yes_no('Create a new trac environment?', default=None):
        run(flo('{bin_dir}/trac-admin  {site_dir}/tracenv  initenv'))

    # test-run:
    run(flo('{bin_dir}/tracd --port 8000 {site_dir}/tracenv'))
