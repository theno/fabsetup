# -*- coding:utf-8 -*-

import re
import tempfile

from fabric.api import env
from fabric.context_managers import warn_only

from fabsetup.fabutils import install_file_legacy, needs_packages, run, subtask
from fabsetup.fabutils import subsubtask, dn_cn_of_certificate_with_san
from fabsetup.fabutils import task, put, exists, print_msg
from fabsetup.fabutils import needs_repo_fabsetup_custom
from fabsetup.fabutils import FABFILE_DATA_DIR
from fabsetup.utils import flo, query_input, query_yes_no
from fabsetup.utils import filled_out_template
from fabsetup.utils import namedtuple


# FIXME test-run as comment: "usefull commands for debugging: ..."
#    run_tracd(site_dir, bin_dir)
#    run_gunicorn(site_dir)
#    run_wsgi(site_dir)


@task
@needs_packages('nginx', 'python-pip', 'python-pygments', 'git', 'subversion')
@needs_repo_fabsetup_custom  # import of trac_plugins_by_sitename from config.py
def trac():
    '''Set up or update a trac project.

    This trac installation uses python2, git, sqlite (trac-default), gunicorn,
    and nginx.

    The connection is https-only and secured by a letsencrypt certificate.  This
    certificate must be created separately with task setup.server_letsencrypt.

    This task installes or updates to the latest trac version hosted at
    https://pypi.python.org/pypi/Trac

    Created and modified files and dirs of this task:

        ```
        ~/sites/<sitename>      <--- example: sitename = trac.example.com
        │
        ├── backup.sh           <--- create a local backup (deletes dir backup/
        ├── backup                                     |    before it creates
        │   └── <sitename>_tracenv_hotcopy.tar.gz  <--´     the tarball)
        ├── run
        │   └── trac.sock       <--- file-socket for binding to nginx
        ├── scripts
        │   └── tracwsgi.py
        ├── tracenv
        │   ├── conf
        │   │   ├── trac.htpasswd   <--- trac user password hashes
        │   │   └── trac.ini        <--- trac config file
        │   ├── db
        │   │   └── trac.db         <--- sqlite database
        │   ├── files
        │   ├── git
        │   ├── htdocs
        │   ├── log
        │   ├── plugins
        │   ├── README
        │   ├── templates
        │   └── VERSION
        └── virtualenv
            ├── bin
            ├── include
            ├── lib
            ├── local
            └── pip-selfcheck.json
        ```

    How to create a backup tarball "manually":
    `~/sites/<sitename>/backup/tracenv_hotcopy_<yyyy-mm-dd>.tar.gz`:

        ```
        cd ~/sites/<sitename>  &&  rm -rf ./backup
        ./virtualenv/bin/trac-admin ./tracenv  hotcopy ./backup/tracenv_hotcopy
        mkdir -p ./backup  &&  cd ./backup
        tar czf <sitename>_tracenv_hotcopy_$(date +%F).tar.gz  tracenv_hotcopy/
        rm -rf tracenv_hotcopy; ls -hl
        ```

    More infos:
      https://trac.edgewall.org/wiki/TracInstall
      https://trac.edgewall.org/wiki/TracFastCgi#NginxConfiguration
      https://trac.edgewall.org/wiki/TracNginxRecipe
      https://trac.edgewall.org/wiki/Gunicorn
      http://www.obeythetestinggoat.com/book/chapter_08.html#_getting_to_a_production_ready_deployment
      Setting REMOTE_USER for Trac in Gunicorn behind Nginx:
        http://serverfault.com/a/392096
      https://trac.edgewall.org/wiki/TracBackup
    '''
    hostname = re.sub(r'^[^@]+@', '', env.host)  # without username if any
    sitename = query_input(
                   question='\nEnter site-name of Your trac web service',
                   default=flo('trac.{hostname}'))
    username = env.user

    site_dir = flo('/home/{username}/sites/{sitename}')
    bin_dir = flo('{site_dir}/virtualenv/bin')

    # provisioning steps
    install_or_upgrade_virtualenv_pip_package()
    create_directory_structure(site_dir)
    update_virtualenv(site_dir, sitename)
    set_up_trac_plugins(sitename, site_dir, bin_dir)
    set_up_gunicorn(site_dir, sitename)
    configure_nginx(username, sitename, hostname)

    if query_yes_no('\nRestore trac environment from backup tarball?',
                    default='no'):
        restore_tracenv_from_backup_tarball(site_dir, bin_dir)
    elif not tracenv_exists(site_dir):
        init_tracenv(site_dir, bin_dir, username)

    upgrade_tracenv(site_dir, bin_dir)

    set_up_upstart_for_gunicorn(sitename, username, site_dir)


def tracenv_exists(site_dir):
    exists = False
    with warn_only():
        if run(flo('[ -d {site_dir}/tracenv ]')).return_code == 0:
            exists = True
    return exists


@subtask
def install_or_upgrade_virtualenv_pip_package():
    '''Install or upgrade the globally installed pip package virtualenv.'''
    run('sudo pip install --upgrade virtualenv')


@subtask
def create_directory_structure(site_dir):
    '''Only create the site_dir.  The subdirds 'tracenv', 'virtualenv',
    'scripts', and 'run' will be created on each subtask.
    '''
    run(flo('mkdir -p {site_dir}'))


@subsubtask
def stop_gunicorn_daemon(sitename):
    with warn_only():
        run(flo('sudo stop gunicorn-{sitename}'))


@subsubtask
def create_virtualenv(site_dir):
    if not exists(flo('{site_dir}/virtualenv/bin/pip')):
        python_version = 'python2'  # FIXME take latest python via pyenv
        run(flo('virtualenv --python={python_version}  {site_dir}/virtualenv'))


@subtask
def update_virtualenv(site_dir, sitename):
    stop_gunicorn_daemon(sitename)
    create_virtualenv(site_dir)
    run(flo(
        '{site_dir}/virtualenv/bin/'
        'pip install --upgrade  '
        'pip genshi trac gunicorn '

        # https://trac-hacks.org/wiki/MarkdownMacro
        'Markdown '  # required by TracPlugin MarkdownMakro
    ))


TracPlugin = namedtuple(
    typename='TracPlugin',
    field_names='name, homepage, svn_version=None, '
                'git_repo_url=None, git_instead_of_svn=False',
)


@subtask
def set_up_trac_plugins(sitename, site_dir, bin_dir):
    plugins = []
    try:
        from config import trac_plugins_by_sitename
        plugins = trac_plugins_by_sitename.get(sitename, [])
    except ImportError:
        pass  # ignore non-existing config entry
    svn_base_url = 'https://trac-hacks.org/svn'
    plugin_src_basedir = flo('{site_dir}/trac-plugin-src')
    if plugins:
        for plugin in plugins:
            print_msg(flo('### {plugin.name}\n\nInfos: {plugin.homepage}\n'))
            plugin_src_dir = flo('{plugin_src_basedir}/{plugin.name}')
            # FIXME: simplify: All Plugins provide a zip src-file
            # no differing handling between git and svn required here
            if plugin.git_instead_of_svn:
                # git-repo
                if not exists(flo('{plugin_src_dir}/.git')):
                    run(flo('cd {plugin_src_basedir}  &&  '
                            'git clone {plugin.git_repo_url}  {plugin.name}'))
                else:
                    run(flo('cd {plugin_src_dir}  &&  git pull'))

            else:
                # svn-repo
                if exists(plugin_src_dir):
                    run(flo('cd {plugin_src_dir}  &&  svn up'),
                        msg='update plugin repo:')
                else:
                    run(flo('mkdir -p {plugin_src_basedir}'),
                        msg='checkout plugin repo:')
                    run(flo('svn checkout  '
                            '{svn_base_url}/{plugin.name}/{plugin.svn_version} '
                            ' {plugin_src_dir}'))
            run(flo('{bin_dir}/pip install --upgrade {plugin_src_dir}'),
                msg='install plugin:')
    else:
        print_msg('plugins not configured in fabsetup_custom/setup.py:  '
                  'nothing to do')


@subtask
def upgrade_tracenv(site_dir, bin_dir):
    run(flo('{bin_dir}/trac-admin {site_dir}/tracenv  upgrade'))
    run(flo('{bin_dir}/trac-admin {site_dir}/tracenv  wiki upgrade'))


@subtask
def restore_tracenv_from_backup_tarball(site_dir, bin_dir):
    # FIXME stop trac if it is running already
    filename_tarball = query_input('tarball path?')
    run(flo('mkdir -p {site_dir}/tmp'))
    run(flo('tar xf {filename_tarball}  --directory={site_dir}/tmp'))
    # save tracenv if it exists
    run(flo('mv {site_dir}/tracenv  {site_dir}/tracenv.before_$(date +%F).bak'
            ' || true'))
    run(flo('mv {site_dir}/tmp/tracenv_hotcopy  {site_dir}/tracenv'))
    run(flo('rmdir {site_dir}/tmp'))


@subsubtask
def trac_admin(site_dir, username):
    '''Make user `username` becomes a trac admin.'''
    run(flo('{site_dir}/virtualenv/bin/trac-admin {site_dir}/tracenv '
            'permission add {username} TRAC_ADMIN'))
    run(flo('htpasswd -c {site_dir}/tracenv/conf/trac.htpasswd  {username}'))


@subtask
def init_tracenv(site_dir, bin_dir, username):
    run(flo('{bin_dir}/trac-admin  {site_dir}/tracenv  initenv'))
    trac_admin(site_dir, username)


@subtask(doc1=True)
def run_tracd(site_dir, bin_dir):
    '''Run tracd  -- only for testing purposes.'''
    run(flo('{bin_dir}/tracd --port 8000 {site_dir}/tracenv'))


@subtask
def set_up_gunicorn(site_dir, sitename):
    install_file_legacy('~/sites/SITENAME/scripts/tracwsgi.py',
                 SITENAME=sitename, site_dir=site_dir)


@subsubtask
def nginx_site_config(username, sitename, hostname):
#    filename = 'trac_site_config.template'  # TODO DEBUG
    filename = 'trac_site_config_gunicorn.template'
#    filename = 'trac_site_config_gunicorn2.template'
#    filename = 'trac_site_config_wsgi.template'
    fabfile_data_dir = FABFILE_DATA_DIR
    path = flo('{fabfile_data_dir}/files/etc/nginx/sites-available/{filename}')
#    dn_cn = query_input('Common Name (CN) of the Distinguished Named (DN) '
#                        'of the webserver certificate?',
#                        default=flo('haw2icalendar.{hostname}'))
    # dn_cn = flo('{hostname}')
    dn_cn = dn_cn_of_certificate_with_san(sitename)
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
    run(flo('sudo chown  {username}.www-data  '
            '/home/{username}/sites/{sitename}/run'))
    run(flo('sudo chmod g+s /home/{username}/sites/{sitename}/run'))


@subtask
def configure_nginx(username, sitename, hostname):
    nginx_site_config(username, sitename, hostname)
    create_wsgi_socket_dir(username, sitename)
    run('sudo service nginx reload')


@subtask(doc1=True)
def run_gunicorn(site_dir):
    '''Run gunicorn  -- only for testing purposes -- localhost:44433'''
    socket = flo('unix://{site_dir}/run/trac.sock')
    run(flo('cd {site_dir}/scripts && {site_dir}/virtualenv/bin/gunicorn '
            '-w2 tracwsgi:application -b {socket}'))


@subsubtask
def install_gunicorn_upstart_script(sitename, username, site_dir):
    socket = flo('unix://{site_dir}/run/trac.sock')
    num_workers = 2
    install_file_legacy('/etc/init/gunicorn-SITENAME.conf', sudo=True,
                 SITENAME=sitename, site_dir=site_dir, username=username,
                 socket=socket, num_workers=num_workers)


@subsubtask
def start_or_restart_gunicorn_daemon(sitename):
    if 'running' in run(flo('status gunicorn-{sitename}'), capture=True):
        run(flo('sudo restart gunicorn-{sitename}'))
    else:
        run(flo('sudo start gunicorn-{sitename}'))


@subtask
def set_up_upstart_for_gunicorn(sitename, username, site_dir):
    install_gunicorn_upstart_script(sitename, username, site_dir)
    start_or_restart_gunicorn_daemon(sitename)


@subtask(doc1=True)
def run_wsgi(site_dir):
    '''Run wsgi  -- only for testing purposes -- localhost:44433'''
    run(flo('{site_dir}/virtualenv/bin/python {site_dir}/scripts/tracwsgi.py'))
