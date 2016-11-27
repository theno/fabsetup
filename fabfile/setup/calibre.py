import os.path

from fabfile.fabutils import custom_task as task  # here, every task is custom
from fabfile.fabutils import subtask, run
from fabfile.utils import flo


@task
def calibre():
    '''Install or update calibre (ebook management tool).

    More info:
      https://calibre-ebook.com/
      https://calibre-ebook.com/download_linux
      https://github.com/kovidgoyal/calibre
    '''
    instdir = '~/bin/calibre-bin'
    install_calibre(instdir)


@subtask
def install_calibre(instdir):
    inst_parent = os.path.dirname(instdir)
    run(flo('mkdir -p {inst_parent}'))
    run(flo('wget -nv -O- '
            'https://raw.githubusercontent.com/kovidgoyal/calibre/master/setup/'
            'linux-installer.py | '
            'python -c "import sys; '
            'main=lambda x,y:sys.stderr.write(\'Download failed\\n\'); '
            'exec(sys.stdin.read()); main(\'{inst_parent}\', True)"'))

    # calibre-installer installs into {inst_parent}/calibre/; needs to be moved
    run(flo('rm -rf  {instdir}'))
    run(flo('mv  {inst_parent}/calibre  {instdir}'))

    run(flo('ln -snf  {instdir}/calibre  ~/bin/calibre'))
