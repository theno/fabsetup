# -*- coding: utf-8 -*-

'''Fabric tasks for the setup of some services.'''

import re
import tempfile

from fabric.api import env, hide, sudo, warn_only
from fabric.contrib.files import exists

from fabsetup.fabutils import checkup_git_repo, install_packages
from fabsetup.fabutils import needs_packages, task, run, suggest_localhost, put
from fabsetup.fabutils import FABFILE_DATA_DIR
from fabsetup.utils import flo, query_yes_no
from fabsetup.utils import query_input, blue, cyan, magenta, filled_out_template

from selfoss import selfoss
from trac import trac


@task
@needs_packages('nginx')
def owncloud():
    '''Set up owncloud.

    Package 'owncloud' pulls package 'mysql' which asks for a password.
    '''
    hostname = re.sub(r'^[^@]+@', '', env.host)  # without username if any
    sitename = query_input(
                   question='\nEnter site-name of Your Owncloud web service',
                   default=flo('owncloud.{hostname}'), color=cyan)
    username = env.user

    fabfile_data_dir = FABFILE_DATA_DIR

    print(magenta(' install owncloud'))
    repository = ''.join([
        'http://download.opensuse.org/repositories/',
        'isv:/ownCloud:/community/Debian_7.0/',
    ])
    with hide('output'):
        sudo(flo('wget -O - {repository}Release.key | apt-key add -'))
        filename = '/etc/apt/sources.list.d/owncloud.list'
        sudo(flo("echo 'deb {repository} /' > {filename}"))
        sudo('apt-get update')
    install_packages([
        'owncloud',
        'php5-fpm',
        'php-apc',
        'memcached',
        'php5-memcache',
    ])

    # This server uses nginx. owncloud pulls apache2 => Disable apache2
    print(magenta(' disable apache'))
    with hide('output'):
        sudo('service apache2 stop')
        sudo('update-rc.d apache2 disable')

    print(magenta(' nginx setup for owncloud'))
    filename = 'owncloud_site_config.template'
    path = flo('{fabfile_data_dir}/files/etc/nginx/sites-available/{filename}')
    from_str = filled_out_template(path, username=username, sitename=sitename,
                                   hostname=hostname)
    with tempfile.NamedTemporaryFile(prefix=filename) as tmp_file:
        with open(tmp_file.name, 'w') as fp:
            fp.write(from_str)
        put(tmp_file.name, flo('/tmp/{filename}'))
    to = flo('/etc/nginx/sites-available/{sitename}')
    sudo(flo('mv /tmp/{filename} {to}'))
    sudo(flo('chown root.root {to}'))
    sudo(flo('chmod 644 {to}'))
    sudo(flo(' '.join([
            'ln -snf ../sites-available/{sitename}',
            '/etc/nginx/sites-enabled/{sitename}',
    ])))

    # php5 fpm fast-cgi config

    template = 'www.conf'
    to = flo('/etc/php5/fpm/pool.d/{template}')
    from_ = flo('{fabfile_data_dir}/files{to}')
    put(from_, '/tmp/')
    sudo(flo('mv /tmp/{template} {to}'))
    sudo(flo('chown root.root {to}'))
    sudo(flo('chmod 644 {to}'))

    template = 'php.ini'
    to = flo('/etc/php5/fpm/{template}')
    from_ = flo('{fabfile_data_dir}/files{to}')
    put(from_, '/tmp/')
    sudo(flo('mv /tmp/{template} {to}'))
    sudo(flo('chown root.root {to}'))
    sudo(flo('chmod 644 {to}'))

    sudo('service php5-fpm restart')

    sudo('service nginx reload')


@task
@needs_packages('nginx')
@needs_packages('software-properties-common')  # for cmd 'add-apt-repository'
def fdroid():
    '''Set up an F-Droid App Repo.

    More infos:
     * https://f-droid.org/wiki/page/Setup_an_FDroid_App_Repo
     * https://f-droid.org/wiki/page/Installing_the_Server_and_Repo_Tools
    '''
    hostname = re.sub(r'^[^@]+@', '', env.host)  # without username if any
    sitename = query_input(
                   question='\nEnter site-name of Your F-Droid web service',
                   default=flo('fdroid.{hostname}'))
    username = env.user

    fabfile_data_dir = FABFILE_DATA_DIR

    print(magenta(' install fdroidserver'))
    res = run('dpkg --get-selections | '
              'grep -q "^fdroidserver[[:space:]]*install$" >/dev/null',
              warn_only=True)
    package_installed = res.return_code == 0
    question = 'package fdroidserver already installed, update? ' \
               '(needs some time)'
    if package_installed and not query_yes_no(question, default='no'):
        print('skip update')
    else:
        with hide('output'):
            sudo('yes "" | add-apt-repository  ppa:guardianproject/ppa')
            sudo('apt-get update')
            # why 'android-libhost-dev' (avoid "Failed to get apk information"
            # on 'fdroid update --create-metadata'):
            # https://f-droid.org/forums/topic/failed-to-get-apk-information-2/#post-15777
            install_packages(['fdroidserver', 'android-libhost-dev'])
            sudo('yes "" | add-apt-repository --remove  '
                 'ppa:guardianproject/ppa')
            sudo('apt-get update')

    site_dir = flo('/home/{username}/sites/{sitename}')
    apks_dir   = flo('{site_dir}/apks')
    fdroid_dir = flo('{site_dir}/fdroid')
    repo_dir   = flo('{site_dir}/fdroid/repo')

    print(magenta(' init f-droid repo'))
    question = ' '.join(['already initialized, initialize again?',
                         '(creates a new repo key)'])
    if exists(repo_dir) and not query_yes_no(question, default='no'):
        print('skip initialization')
    else:
        with warn_only():
            run(flo('rm -rf  {fdroid_dir}'))
        run(flo('mkdir -p  {repo_dir}'))
        run(flo('cd {fdroid_dir}  &&  fdroid init'))
        run(flo('cd {site_dir}  &&  tree'))

    print(magenta(' update apk files of the fdroid repo'))
    run(flo('mkdir -p  {apks_dir}'))
    run(flo('rm -rf {repo_dir}/*.apk'))
    run(flo("find {apks_dir} -type f | rename 's/ /_/g'"))
    run(flo("find {apks_dir} -type f | rename 's/[^[:ascii:]]//g'"))
    run(flo('chmod 644 {apks_dir}/*.apk'))
    run(flo('cp -v {apks_dir}/*.apk  {repo_dir}'), warn_only=True)
    run(flo('cd {fdroid_dir}  &&  fdroid update --create-metadata'))

    print(magenta(' setup nginx for F-Droid'))

    run(flo('echo -e "User-agent: *\\nDisallow: /" > {fdroid_dir}/robots.txt'))

    filename = 'fdroid_site_config.template'
    path = flo('{fabfile_data_dir}/files/etc/nginx/sites-available/{filename}')
    from_str = filled_out_template(path, username=username, sitename=sitename,
                                   hostname=hostname)
    with tempfile.NamedTemporaryFile(prefix=filename) as tmp_file:
        with open(tmp_file.name, 'w') as fp:
            fp.write(from_str)
        put(tmp_file.name, flo('/tmp/{filename}'))
    to = flo('/etc/nginx/sites-available/{sitename}')
    sudo(flo('mv /tmp/{filename} {to}'))
    sudo(flo('chown root.root {to}'))
    sudo(flo('chmod 644 {to}'))
    sudo(flo(' '.join([
            'ln -snf ../sites-available/{sitename}',
            '/etc/nginx/sites-enabled/{sitename}',
    ])))

    sudo('service nginx reload')


@task
def vnc_raspi_osmc():
    '''Install and configure dispmanx_vnc server on osmc (raspberry pi).

    More Infos:
     * https://github.com/patrikolausson/dispmanx_vnc
     * https://discourse.osmc.tv/t/howto-install-a-vnc-server-on-the-raspberry-pi/1517
     * tightvnc:
       * http://raspberry.tips/raspberrypi-einsteiger/raspberry-pi-einsteiger-guide-vnc-einrichten-teil-4/
       * http://jankarres.de/2012/08/raspberry-pi-vnc-server-installieren/
    '''
    print(blue('Install dependencies'))
    install_packages([
            'git',
            'build-essential',
            'rbp-userland-dev-osmc',
            'libvncserver-dev',
            'libconfig++-dev',
    ])

    print(blue('Build vnc server for raspberry pi using dispmanx '
               '(dispmanx_vnc)'))
    checkup_git_repo(url='https://github.com/patrikolausson/dispmanx_vnc.git')
    run('mkdir -p ~/repos')
    run('cd ~/repos/dispmanx_vnc  &&  make')

    print(blue('set up dispmanx_vnc as a service'))
    with warn_only():
        run('sudo systemctl  stop  dispmanx_vncserver.service')
    username = env.user
    builddir = flo('/home/{username}/repos/dispmanx_vnc')
    run(flo('sudo  cp  {builddir}/dispmanx_vncserver  /usr/bin'))
    run('sudo  chmod +x  /usr/bin/dispmanx_vncserver')
    fabfile_data_dir = FABFILE_DATA_DIR
    put('{fabfile_data_dir}/files/etc/dispmanx_vncserver.conf', '/tmp/')
    run('sudo mv  /tmp/dispmanx_vncserver.conf  /etc/dispmanx_vncserver.conf')
    put('{fabfile_data_dir}/files/etc/systemd/system/dispmanx_vncserver.service',
        '/tmp/')
    run('sudo mv  /tmp/dispmanx_vncserver.service  '
        '/etc/systemd/system/dispmanx_vncserver.service')
    run('sudo systemctl start dispmanx_vncserver.service')
    run('sudo systemctl enable dispmanx_vncserver.service')
    run('sudo systemctl daemon-reload')


@task
def lms():
    '''Install and start a Logitech Media Server (lms).

    More infos:
     * http://wiki.slimdevices.com/index.php/Logitech_Media_Server
     * http://wiki.slimdevices.com/index.php/DebianPackage
     * http://www.mysqueezebox.com/download
     * XSqueeze on Kodi:
       * http://kodi.wiki/view/Add-on:XSqueeze
       * http://forum.kodi.tv/showthread.php?tid=122199
    '''
    # cf. http://wiki.slimdevices.com/index.php/DebianPackage#installing_7.9.0
    cmds = '''\
url="http://www.mysqueezebox.com/update/?version=7.9.0&revision=1&geturl=1&os=deb"
latest_lms=$(wget -q -O - "$url")
mkdir -p ~/.logitech_media_server_sources
cd ~/.logitech_media_server_sources
wget $latest_lms
lms_deb=${latest_lms##*/}
sudo dpkg -i $lms_deb
'''
    run(cmds)
    run('sudo usermod -aG audio  squeezeboxserver')
    with warn_only():
        run('sudo addgroup lms')
    run('sudo usermod -aG lms  squeezeboxserver')
    username = env.user
    run(flo('sudo usermod -aG audio  {username}'))
    print('\n    Set correct folder permissions manually, eg:')
    print('    > ' + cyan(flo('chown -R {username}.lms  <path/to/your/media>')))
    hostname = env.host
    print(flo('\n    lms frontend available at http://{hostname}:9000'))


@task
@suggest_localhost
def samba():
    '''Install smb server samba and create a share (common read-write-access).

    More infos:
     * https://wiki.ubuntuusers.de/Samba%20Server/
    '''
    username = env.user
    install_packages(['samba'])
    run(flo('sudo smbpasswd -a {username}'))

    path = '$HOME/shared'
    sharename = 'shared'
    comment = '"smb share; everyone has full access (read/write)"'
    acl = flo('Everyone:F,{username}:F guest_ok=y')

    with warn_only():
        run(flo('mkdir {path}'))
    run(flo('sudo net usershare add {sharename} {path} {comment} {acl}'))
    run(flo('sudo net usershare info {sharename}'))
