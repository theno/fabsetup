# -*- coding: utf-8 -*-

from os.path import expanduser

from fabric.api import warn_only

from fabsetup.fabutils import checkup_git_repo
from fabsetup.fabutils import suggest_localhost, print_msg
from fabsetup.fabutils import run, subtask, task
from fabsetup.utils import flo


@task
@suggest_localhost
def openssl(version='master', ignore_test_fail=False):
    '''
    Install or update OpenSSL from source (statically linked, no shared libs).

    Args:
        version (str): Git tag or branch to install from. Default: 'master'
        ignore_test_fail: Continue with installation if `make test` fails.
                          Default: False

    Example:
        > fab setup.openssl:version=OpenSSL_1_1_0-stable

    Created files and dirs:

        > tree ~/repos
        └── openssl          <--- checked out git repository with openssl source

        > tree ~/bin
        │
        ├── c_rehash -> openssl-inst/active/bin/c_rehash  \__ command links
        ├── openssl  -> openssl-inst/active/bin/openssl   /
        │
        └── openssl-inst
            ├── active -> OpenSSL_1_1_0-stable     <--- here 1.1.0 is "active"
            ├── master                             <--- installed via:
            │   ├── bin                                 `fab setup.openssl`
            │   ├── include
            │   ├── lib
            │   ├── openssldir   <--- openssl configs and default cert/key store
            │   └── share
            └── OpenSSL_1_1_0-stable              <---.
                ├── bin               installed via: -´
                ├── include     `fab setup.openssl:version=OpenSSL_1_1_0-stable`
                ├── lib
                ├── openssldir   <--- openssl configs and default cert/key store
                └── share
    '''
    src_base = '~/repos'
    srcdir = flo('{src_base}/openssl')

    inst_base = '~/bin/openssl-inst'
    instdir = flo('{inst_base}/{version}')

    # dir for openssl config files, and default certificate and key store
    confdir = flo('{instdir}/openssldir')

    download(src_base, version, srcdir)
    compile(srcdir, instdir, confdir)
    test(srcdir, ignore_test_fail)
    install(srcdir, inst_base, version, instdir)


@subtask
def download(src_base, version, srcdir):
    checkup_git_repo('git://git.openssl.org/openssl.git', base_dir=src_base)
    run(flo('cd {srcdir}  &&  git checkout {version}'))
    run(flo('cd {srcdir}  &&  git pull'))


@subtask
def compile(srcdir, instdir, confdir):
    instdir = expanduser(instdir)
    confdir = expanduser(confdir)

    run(flo('cd {srcdir}  &&  ./config  '
            'no-shared  '  # only create static libraries (no shared libs)
            'no-dso  '     # no support for loading dynamic shared objects
            '--prefix={instdir}  '
            '--openssldir={confdir}'))
    run(flo('cd {srcdir}  &&  make clean'))
    run(flo('cd {srcdir}  &&  make'))


@subtask
def test(srcdir, ignore_fail):
    cmd = flo('cd {srcdir}  &&  make test')
    if ignore_fail:
        with warn_only():
            run(cmd)
    else:
        run(cmd)


@subtask
def install(srcdir, inst_base, version, instdir):
    run(flo('rm -rf {instdir}'),
        msg='remove files from previous installations (if any)')

    run(flo('cd {srcdir}  &&  make install'),
        msg='install/copy files')

    run(flo('cd {inst_base}  &&  ln -snf  {version}  active'),
        msg='activate installed openssl')

    print_msg('link openssl commands')
    run(flo('cd ~/bin  &&  ln -snf {inst_base}/active/bin/openssl  openssl'))
    run(flo('cd ~/bin  &&  ln -snf {inst_base}/active/bin/c_rehash  c_rehash'))
