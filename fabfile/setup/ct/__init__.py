import os.path

from fabfile.fabutils import checkup_git_repos, install_packages, run
from fabfile.fabutils import custom_task as task, subtask
from fabfile.fabutils import query_yes_no, print_msg
from fabfile.utils import flo, yellow


@task
def main(branch=None):
    '''Install or update Certificate Transparency (CT) open source project.

    This will update or install the CPP part of the open source ct google code.

    At first, software required for the build process will be downloaded and
    installed (google's github repo depot_tools, and some packages).  Then, the
    build dir `~/ct/` will be prepared and the github repo of CT will be
    downloaded to `~/ct/certificate-transparency`.  The code then will be build
    with gclient (depot_tools).

    Args:
        branch (str): Name of a branch to check out. If None head will be
                      checked out (default).

    More info:
      https://github.com/google/certificate-transparency/blob/master/README.md
      depot_tools (gclient and other commands):
        intro:
          https://www.chromium.org/developers/how-tos/depottools
        howto install:
          https://www.chromium.org/developers/how-tos/install-depot-tools
    '''
    install_build_dependencies()
    build_dir = care_for_build_dir()
    build_ct(build_dir, branch=branch)


@subtask
def install_build_dependencies():
    base_dir = '~/repos'
    repos = [
        # depot_tools ".. includes gclient, gcl, git-cl, repo, and others."
        {
            'url': 'https://chromium.googlesource.com/chromium/tools/'
                   'depot_tools.git',
        },
    ]
    checkup_git_repos(repos, base_dir)

    install_packages([
        'autoconf',
        'automake',
        'clang',
        'cmake',  # cmake+
        'git',
        'make',   # GNU make
        'libtool',
        'shtool',
        'tcl',

        'pkgconf',
        #'pkg-config',  # pkg-config on ubuntu 12.04

        'python',
    ])


@subtask
def care_for_build_dir():
    build_dir = run('readlink -f ~/ct', capture=True)
    build_dir_yellow = yellow(build_dir)
    question_f = flo("delete file '{build_dir_yellow}'?")
    question_d = flo("delete build dir '{build_dir_yellow}'?")
    if os.path.isfile(build_dir) and query_yes_no(question_f, default='yes'):
        run(flo('rm -rf {build_dir}'))
    elif os.path.exists(build_dir) and query_yes_no(question_d, default='yes'):
        run(flo('rm -rf {build_dir}'))
    run(flo('mkdir -p {build_dir}'))
    return build_dir


@subtask
def build_ct(build_dir, branch=None):
    base_dir = '~/repos'
    abs_path = run(flo('readlink -f {base_dir}'), capture=True)

    vars_str = ' '.join([
        flo('PATH="{abs_path}/depot_tools:$PATH"'),  # add depot_tools to PATH
        'CXX=clang++',
        'CC=clang',
    ])

    url = 'https://github.com/google/certificate-transparency.git'
    if branch:
        url = flo('{url}@{branch}')

    cmds = [
        (
            flo("\n### create gclient config file '{build_dir}/.gclient'\n"),
            flo('gclient config --name="certificate-transparency" {url}')
        ),
        (
            '\n### retrieve and build dependencies\n',
            'gclient sync'
        ),
        (
            '\n### build CT software & self-test\n',
            'make -C certificate-transparency check'
        ),
    ]
    for msg, cmd in cmds:
        print_msg(msg)
        cmd_yellow = yellow(cmd)
        if query_yes_no(question=flo("run cmd '{cmd_yellow}' ?")):
            run(flo('cd {build_dir} && {vars_str}  {cmd}'))

    print_msg('\n### installed ct commands\n')
    run(flo('tree -L 2 {build_dir}/certificate-transparency/cpp/ '
            '-I "*test|*.cc|*.h|*.in|*.a|*.o|*.log|*test.py|*.trs|stamp-h1|'
            'tsan_suppressions" --prune'))
