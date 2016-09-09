import re
import tempfile

from fabric.api import env, hide

from ...fabutils import install_file, needs_packages, run, subtask, subsubtask
from ...fabutils import task, put
from ...utils import cyan, flo, print_full_name, query_input, query_yes_no
from ...utils import filled_out_template


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
    set_up_gunicorn(site_dir, sitename)
    configure_nginx(username, sitename, hostname)

#TODO DEBUG
#    if query_yes_no('\nRestore trac environment from backup tarball?',
#                    default=None):
#        restore_tracenv_from_backup_tarball(site_dir, bin_dir)
#    elif query_yes_no('\nCreate a new trac environment?', default=None):
#        init_tracenv(site_dir, bin_dir)

    # FIXME test-run:
#    run_tracd(site_dir, bin_dir)
    run_gunicorn(site_dir)
#    run_wsgi(site_dir)


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


@subsubtask
def upgrade_tracenv(site_dir, bin_dir):
    run(flo('{bin_dir}/trac-admin {site_dir}/tracenv  upgrade'))
    run(flo('{bin_dir}/trac-admin {site_dir}/tracenv  wiki upgrade'))


@subtask
def restore_tracenv_from_backup_tarball(site_dir, bin_dir):
    # FIXME stop trac if it is running already
    filename = query_input('tarball path?')
    run(flo('mkdir -p {site_dir}/tmp'))
    run(flo('tar xf {filename}  --directory={site_dir}/tmp'))
#    run(flo('[ -d {site_dir}/tracenv ] && '
#            'mv {site_dir}/tracenv  {site_dir}/tracenv.before_$(date +%F).bak'
#            ' || true'))
    run(flo('mv {site_dir}/tracenv  {site_dir}/tracenv.before_$(date +%F).bak'
            ' || true'))
    run(flo('mv {site_dir}/tmp/tracenv_hotcopy  {site_dir}/tracenv'))
    run(flo('rmdir {site_dir}/tmp'))
    upgrade_tracenv(site_dir, bin_dir)


@subtask
def init_tracenv(site_dir, bin_dir):
    run(flo('{bin_dir}/trac-admin  {site_dir}/tracenv  initenv'))


@subtask(doc1=True)
def run_tracd(site_dir, bin_dir):
    '''Run tracd  -- only for testing purposes.'''
    run(flo('{bin_dir}/tracd --port 8000 {site_dir}/tracenv'))


@subtask
def set_up_gunicorn(site_dir, sitename):
    install_file('~/sites/SITENAME/scripts/tracwsgi.py',
                 SITENAME=sitename, site_dir=site_dir)


@subsubtask
def nginx_site_config(username, sitename, hostname):
#    filename = 'trac_site_config.template'  # TODO DEBUG
    filename = 'trac_site_config_gunicorn.template'
#    filename = 'trac_site_config_gunicorn2.template'
#    filename = 'trac_site_config_wsgi.template'
    path = flo('fabfile_data/files/etc/nginx/sites-available/{filename}')
#    dn_cn = query_input('Common Name (CN) of the Distinguished Named (DN) '
#                        'of the webserver certificate?',
#                        default=flo('haw2icalendar.{hostname}'))
    dn_cn = flo('{hostname}')
    from_str = filled_out_template(path, username=username, sitename=sitename,
                                   hostname=hostname, dn_cn=dn_cn)
    with tempfile.NamedTemporaryFile(prefix=filename) as tmp_file:
        with open(tmp_file.name, 'w') as fp:
            fp.write(from_str)
        put(tmp_file.name, flo('/tmp/{filename}'))
    to = flo('/etc/nginx/sites-available/{sitename}')
    run(flo('sudo mv /tmp/{filename} {to}'))
    run(flo('sudo chown root.root {to}'))
    run(flo('sudo chmod 644 {to}'))
    run(flo(' '.join([
            'sudo  ln -snf ../sites-available/{sitename}',
            '/etc/nginx/sites-enabled/{sitename}',
    ])))


@subsubtask
def create_wsgi_socket_dir(username, sitename):
    run(flo('mkdir -p /home/{username}/sites/{sitename}/run'))
    run(flo('sudo chown {username}.www-data /home/{username}/sites/{sitename}/run'))
    run(flo('sudo chmod g+s /home/{username}/sites/{sitename}/run'))


@subtask
def configure_nginx(username, sitename, hostname):
    nginx_site_config(username, sitename, hostname)
    create_wsgi_socket_dir(username, sitename)
    run('sudo service nginx reload')


@subtask(doc1=True)
def run_gunicorn(site_dir):
    '''Run gunicorn  -- only for testing purposes -- localhost:44433'''
#    run(flo('cd {site_dir}/scripts && {site_dir}/virtualenv/bin/gunicorn -w2 tracwsgi:application -b 0.0.0.0:8000'))
    socket = flo('unix://{site_dir}/run/trac.sock')
    run(flo('cd {site_dir}/scripts && {site_dir}/virtualenv/bin/gunicorn -w2 tracwsgi:application -b {socket}'))


@subtask(doc1=True)
def run_wsgi(site_dir):
    '''Run wsgi  -- only for testing purposes -- localhost:44433'''
    run(flo('{site_dir}/virtualenv/bin/python {site_dir}/scripts/tracwsgi.py'))
