# -*- coding: utf-8 -*-

import os.path

from fabsetup.fabutils import task
from fabsetup.fabutils import subtask, run
from fabsetup.utils import flo


@task
def calibre():
    '''Install or update calibre (ebook management tool).

    More info:
      https://calibre-ebook.com/
      https://calibre-ebook.com/download_linux
      https://github.com/kovidgoyal/calibre

    Files and dirs created by this task:

        > tree  ~/bin
        ├── calibre -> calibre-bin/calibre
        └── calibre-bin
            ├── bin
            ├── calibre
            ├── calibre-complete
            ├── calibre-customize
            ├── calibredb
            ├── calibre-debug
            ├── calibre-parallel
            ├── calibre_postinstall
            ├── calibre-server
            ├── calibre-smtp
            ├── ebook-convert
            ├── ebook-device
            ├── ebook-edit
            ├── ebook-meta
            ├── ebook-polish
            ├── ebook-viewer
            ├── fetch-ebook-metadata
            ├── lib
            ├── lrf2lrs
            ├── lrfviewer
            ├── lrs2lrf
            ├── markdown-calibre
            ├── resources
            └── web2disk
    '''
    install_calibre(instdir='~/bin/calibre-bin')


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
