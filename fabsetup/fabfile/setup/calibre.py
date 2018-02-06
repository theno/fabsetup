# -*- coding: utf-8 -*-

from os.path import dirname, join

from fabsetup.fabutils import task
from fabsetup.fabutils import subtask, run, print_msg
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
        │
        ├── calibre-tmp   <--- temporary dir for (re-) install
        └── calibre-bin   <--- installation dir of calibre
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
    inst_parent = dirname(instdir)
    inst_tmp = join(inst_parent, 'calibre-tmp')

    run(flo('mkdir -p {inst_tmp}'),
        msg='### assure, inst base-dir exists\n')

    run(flo('wget -nv -O- '
            'https://raw.githubusercontent.com/kovidgoyal/calibre/master/setup/'
            'linux-installer.py | '
            'python -c "import sys; '
            'main=lambda x,y:sys.stderr.write(\'Download failed\\n\'); '
            'exec(sys.stdin.read()); main(\'{inst_tmp}\', True)"'),
        msg='\n### download and run calibre installer script\n')

    # calibre-installer installs into {inst_tmp}/calibre/; needs to be moved
    print_msg('\n### replace old install (if exists) by new installation\n')
    run(flo('rm -rf  {instdir}'))
    run(flo('mv  {inst_tmp}/calibre  {instdir}'))
    run(flo('rmdir  {inst_tmp}'))

    run(flo('ln -snf  {instdir}/calibre  ~/bin/calibre'),
        msg='\n### link calibre command to dir `~/bin` (should be in PATH)\n')
