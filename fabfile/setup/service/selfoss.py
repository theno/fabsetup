import random
import re
import tempfile

from fabric.api import env

from fabfile.fabutils import checkup_git_repo, exists, needs_packages, put, run
from fabfile.fabutils import custom_task as task, subtask, subsubtask
from fabfile.fabutils import comment_out_line, print_msg, install_file
from fabfile.fabutils import update_or_append_line
from fabfile.fabutils import uncomment_or_update_or_append_line
from fabfile.utils import flo, query_input, filled_out_template


@task
@needs_packages('git', 'nginx')
def selfoss(reset_password=False):
    '''Install, update and set up selfoss.

    This selfoss installation uses sqlite (selfoss-default), php5-fpm and nginx.

    The connection is https-only and secured by a letsencrypt certificate.  This
    certificate must be created separately with task setup.server_letsencrypt.

    More infos:
      https://selfoss.aditu.de/
      https://github.com/SSilence/selfoss/wiki
      https://www.heise.de/ct/ausgabe/2016-13-RSS-Reader-Selfoss-hat-die-Nachrichtenlage-im-Blick-3228045.html
      https://ct.de/yqp7
    '''
    hostname = re.sub(r'^[^@]+@', '', env.host)  # without username if any
    sitename = query_input(
                   question='\nEnter site-name of Your trac web service',
                   default=flo('selfoss.{hostname}'))
    username = env.user

    site_dir = flo('/home/{username}/sites/{sitename}')

    checkout_latest_release_of_selfoss()
    create_directory_structure(site_dir)

    restored = install_selfoss(sitename, site_dir, username)

    nginx_site_config(username, sitename, hostname)
    enable_php5_socket_file()

    if not restored or reset_password:
        setup_selfoss_user(username, sitename, site_dir)

    print_msg('\n## reload nginx and restart php\n')
    run('sudo service nginx reload')
    run('sudo service php5-fpm restart')


@subtask
def checkout_latest_release_of_selfoss():
    if not exists('~/repos/selfoss/.git'):
        checkup_git_repo('https://github.com/SSilence/selfoss.git')
    else:
        run('cd ~/repos/selfoss && git fetch')
    latest_tag = 'git describe --abbrev=0 --tags --match "[0-9.]*" origin'
    run(flo('cd ~/repos/selfoss && git checkout $({latest_tag})'))


@subsubtask
def save_settings_and_data(site_dir):
    config_saved = False
    data_dir_saved = False

    run(flo('mkdir -p {site_dir}/bak'))

    if exists(flo('{site_dir}/selfoss/config.ini')):
        run(flo('cp {site_dir}/selfoss/config.ini  {site_dir}/bak/config.ini'),
            msg='save config.ini')
        config_saved = True

    if exists(flo('{site_dir}/selfoss/data')):
        run(flo('sudo  rsync -a --owner --group --delete --force  '
                '{site_dir}/selfoss/data  {site_dir}/bak'), msg='save data dir')
        data_dir_saved = True

    result = False
    if config_saved or data_dir_saved:
        result = True
    else:
        print_msg('nothing to save')
    return result


@subsubtask
def restore_settings_and_data(site_dir):
    config_restored = False
    data_dir_restored = False

    if exists(flo('{site_dir}/bak/config.ini')):
        run(flo('cp {site_dir}/bak/config.ini  {site_dir}/selfoss/config.ini'),
            msg='restore config.ini')
        config_restored = True

    if exists(flo('{site_dir}/bak/data')):
        run(flo('sudo  rsync -a --owner --group --delete --force  '
                '{site_dir}/bak/data  {site_dir}/selfoss'),
            msg='restore data dir')

    result = False
    if config_restored or data_dir_restored:
        result = True
    else:
        print_msg('nothing to restore')
    return result


@subsubtask
def install_spout_fulltextrssGoogleBot(sitename):
    install_file('~/sites/SITENAME/selfoss/spouts/rss/fulltextrssGoogleBot.php',
                 SITENAME=sitename)


@subtask
def install_selfoss(sitename, site_dir, username):
    save_settings_and_data(site_dir)
    run(flo("sudo  rsync -a --delete --force --exclude='.git'  ~/repos/selfoss "
            ' {site_dir}'), msg='\n### install files')
    restored = restore_settings_and_data(site_dir)
    install_spout_fulltextrssGoogleBot(sitename)
    print_msg('\n### set write permissions for group www-data')
    for dirname in ['data/cache', 'data/favicons', 'data/logs',
                    'data/thumbnails', 'data/sqlite', 'public']:
        run(flo('sudo chown --recursive  www-data.www-data  '
                '{site_dir}/selfoss/{dirname}'))
    return restored


@subsubtask
def selfoss_username(username, sitename):
    selfoss_username = query_input('selfoss user name:', default=username)
    update_or_append_line(flo('~/sites/{sitename}/selfoss/config.ini'),
                          prefix='username=',
                          new_line=flo('username={selfoss_username}'))


@subsubtask
def selfoss_password(sitename):
    password = query_input('selfoss password:')
    res = run(flo('curl -d password="{password}" -d form_submit="send" '
                  '--insecure https://{sitename}/password 2>/dev/null | '
                  'grep "Generated Password"'),
              capture=True)
    match = re.search(r'value="([^"]+)"', res)
    pw_hash = match.group(1)
    print(flo('{pw_hash}'))
    update_or_append_line(flo('~/sites/{sitename}/selfoss/config.ini'),
                          prefix='password=',
                          new_line=flo('password={pw_hash}'))


@subtask
def setup_selfoss_user(username, sitename, site_dir):
    if not exists(flo('{site_dir}/selfoss/config.ini')):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
        salt = ''.join(random.SystemRandom().choice(chars) for _ in range(150))
        install_file('~/sites/SITENAME/selfoss/config.ini',
                     SITENAME=sitename, salt=salt)

    run('sudo service nginx reload')
    run('sudo service php5-fpm restart')

    selfoss_username(username, sitename)
    selfoss_password(sitename)


@subtask
def enable_php5_socket_file():
    filename = '/etc/php5/fpm/pool.d/www.conf'
    print_msg('comment out "listen = 127.0.01:9000"')
    comment_out_line(filename, comment=';', line='listen = 127.0.0.1:9000')
    line = 'listen = /var/run/php5-fpm.sock'
    print_msg(flo('\nuncomment "{line}"'))
    uncomment_or_update_or_append_line(filename, prefix=line, new_line=line,
                                       comment=';')
    run('sudo service php5-fpm restart', msg='\nrestart php5-fpm daemon')


@subtask
def create_directory_structure(site_dir):
    '''Only create the site_dir.  The subdirds 'tracenv', 'virtualenv',
    'scripts', and 'run' will be created on each subtask.
    '''
    run(flo('mkdir -p {site_dir}'))


@subtask
def nginx_site_config(username, sitename, hostname):
    filename = 'selfoss_site_config.template'
    path = flo('fabfile_data/files/etc/nginx/sites-available/{filename}')
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
    run(flo('sudo  ln -snf ../sites-available/{sitename}  '
            '/etc/nginx/sites-enabled/{sitename}'))
