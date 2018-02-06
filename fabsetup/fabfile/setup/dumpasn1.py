# -*- coding: utf-8 -*-
import filecmp
from os.path import isfile, expanduser

from fabsetup.fabutils import run, subtask, task, suggest_localhost, print_msg
from fabsetup.utils import flo


@task
@suggest_localhost
def dumpasn1():
    '''Install latest or update to the latest version of dumpasn1.

    dumpasn1 is a tool for showing DER encoded ASN.1 data structures.
    It is written in C by Peter Gutmann.

    More info:
      https://www.cs.auckland.ac.nz/~pgut001/#standards


    Overwritten files and dirs of this task:

        > tree ~/bin
        ├── dumpasn1 -> dumpasn1-tool/dumpasn1
        ├── dumpasn1.cfg -> dumpasn1-tool/dumpasn1.cfg
        └── dumpasn1-tool
            ├── dumpasn1
            ├── dumpasn1.c
            ├── dumpasn1.cfg
            └── example.der
    '''
    inst_dir = '~/bin/dumpasn1-tool'
    download(inst_dir)
    compile(inst_dir)
    install(inst_dir)
    usage()


@subtask
def download(inst_dir):
    url_script = 'https://www.cs.auckland.ac.nz/~pgut001/dumpasn1.c'
    url_config = 'https://www.cs.auckland.ac.nz/~pgut001/dumpasn1.cfg'
    url_example = 'https://github.com/openssl/openssl/blob/master/test/' \
                  'recipes/ocsp-response.der?raw=true'
    run(flo('mkdir -p {inst_dir}'))
    run(flo('cd {inst_dir}  &&  wget --backups=1  {url_script}'))
    run(flo('cd {inst_dir}  &&  wget -O dumpasn1.cfg  {url_config}'))
    run(flo('cd {inst_dir}  &&  wget -O example.der  {url_example}'))


def _compile(inst_dir):
    run(flo('cd {inst_dir}  &&  gcc dumpasn1.c -o dumpasn1'))


@subtask
def compile(inst_dir):
    installed = flo('{inst_dir}/dumpasn1.c.1')
    latest = flo('{inst_dir}/dumpasn1.c')
    if isfile(expanduser(installed)):
        # wget has downloaded the latest version and moved the existing
        # (installed) version to dumpasn1.c.1
        if filecmp.cmp(expanduser(latest), expanduser(installed)):
            print_msg('no new version of dumpasn1.c (skip)')
        else:
            print_msg('new version of dumpasn1.c  ->  compile it')
            _compile(inst_dir)
        run(flo('rm {installed}'))
    else:
        print_msg('compile dumpasn1.c')
        _compile(inst_dir)


@subtask
def install(inst_dir):
    run(flo('ln -snf dumpasn1-tool/dumpasn1      ~/bin/dumpasn1'))
    run(flo('ln -snf dumpasn1-tool/dumpasn1.cfg  ~/bin/dumpasn1.cfg'))


@subtask
def usage():
    run('dumpasn1 -h  || true')
    print('\nFor example, run:\n')
    print_msg('    dumpasn1  ~/bin/dumpasn1-tool/example.der')
    print_msg('    hexdump -C  ~/bin/dumpasn1-tool/example.der')
