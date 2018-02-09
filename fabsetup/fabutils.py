import doctest
import os.path
import re
import sys
import tempfile
from functools import wraps
from os.path import dirname, expanduser, isdir, isfile, join

import fabric.api
import fabric.contrib.files
import fabric.operations
import utlz
from fabric.context_managers import quiet
from fabric.state import env
from fabric.network import needs_host

from utils import flo, print_full_name, print_doc1, blue, cyan, yellow, magenta
from utils import filled_out_template, query_yes_no, default_color
from utils import update_or_append_line as update_or_append_local
from utils import comment_out_line as comment_out_local
from utils import uncomment_or_update_or_append_line as uua_local


FABSETUP_DIR = dirname(__file__)
FABFILE_DATA_DIR = join(FABSETUP_DIR, 'fabfile-data')
FABSETUP_CUSTOM_DIR = join(expanduser('~'), '.fabsetup-custom')


def suggest_localhost(func):
    '''Decorator: prompt user for value of env.host_string with default to
    'localhost' when env.host_string is empty.

    Modification of decorator function fabric.network.needs_host
    '''
    from fabric.network import handle_prompt_abort, to_dict

    @wraps(func)
    def host_prompting_wrapper(*args, **kwargs):
        while not env.get('host_string', False):
            handle_prompt_abort("the target host connection string")
            host_string = raw_input("No hosts found. Please specify "
                                    "host string for connection [localhost]: ")
            if host_string == '':
                host_string = 'localhost'
            env.update(to_dict(host_string))
        return func(*args, **kwargs)

    host_prompting_wrapper.undecorated = func

    return host_prompting_wrapper


@needs_host
def _func(kwargs, func_local=fabric.api.local, func_remote=fabric.api.run):
    env.host = env.host_string
    func = func_remote
    print_msg(kwargs.pop('msg', None))
    if env.host_string == 'localhost':
        func = func_local
    else:
        kwargs.pop('capture', None)
    return func, kwargs


def run(*args, **kwargs):
    func, kwargs = _func(kwargs)
    return func(*args, **kwargs)


def exists(*args, **kwargs):
    func, kwargs = _func(kwargs, func_local=os.path.exists,
                         func_remote=fabric.contrib.files.exists)
    if func == os.path.exists:
        args_list = list(args)
        args_list[0] = os.path.expanduser(args[0])
        args = tuple(args_list)
    return func(*args, **kwargs)


def put(*args, **kwargs):
    func, kwargs = _func(kwargs, func_remote=fabric.operations.put)
    if func == fabric.api.local:
        from_, to = [os.path.expanduser(arg) for arg in args]
        args = [flo('cp  {from_}  {to}')]
        kwargs = {}
    return func(*args, **kwargs)


def import_fabsetup_custom(globals_):
    # import custom tasks from ~/.fabsetup-custom/fabfile_/__init__.py
    sys.path = [FABSETUP_CUSTOM_DIR] + sys.path
    import fabfile_ as _
    globals_.update(_.__dict__)
    del _


def needs_repo_fabsetup_custom(func):
    '''Decorator, ensures that fabsetup-custom exists and it is a git repo.'''
    from fabric.api import local

    @wraps(func)
    def wrapper(*args, **kwargs):
        custom_dir = FABSETUP_CUSTOM_DIR
        presetting_dir = join(FABFILE_DATA_DIR, 'presetting-fabsetup-custom')
        if not isdir(custom_dir):
            print(yellow('\n** **     Init ') +
                  yellow('~/.fabsetup-custom', bold=True) +
                  yellow('      ** **\n'))
            print(yellow(flo('** Create files in dir {custom_dir} **')))
            local(flo('mkdir -p {custom_dir}'))
            local(flo('cp -r --no-clobber {presetting_dir}/. {custom_dir}'))
            import_fabsetup_custom(globals())
        else:
            with quiet():
                local(flo('cp -r --no-clobber {presetting_dir}/. {custom_dir}'))

        if not isdir(join(custom_dir, '.git')):
            print(yellow(
                '\n** Git repo ~/.fabsetup-custom: init and first commit **'))
            local(flo('cd {custom_dir} && git init'))
            local(flo('cd {custom_dir} && git add .'))
            local(flo('cd {custom_dir} && git commit -am "Initial commit"'))
            print(yellow("** Done. Don't forget to create a backup of your "
                         '~/.fabsetup-custom repo **\n'))
            print(yellow("** But do not make it public, it's custom **\n",
                         bold=True))
        else:
            with quiet():
                cmd = flo('cd {custom_dir} && git status --porcelain')
                res = local(cmd, capture=True)
                if res:
                    print(yellow('\n** git repo  ') +
                          magenta('~/.fabsetup-custom  ') +
                          yellow('has uncommitted changes: **'))
                    print(cmd)
                    print(yellow(res, bold=True))
                    print(yellow("** Don't forget to commit them and make a "
                                 "backup of your repo **\n"))
        return func(*args, **kwargs)
    return wrapper


def _non_installed(packages):
    non_installed = []
    with quiet():
        for pkg in packages:
            if run(flo('dpkg --status {pkg}')).return_code != 0:
                non_installed.append(pkg)
    return non_installed


def needs_packages(*packages):
    '''Decorator: ensure that packages are installed on host given by fabric
    argument `-H` (local or remote).
    '''
    def real_decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            non_installed = _non_installed(packages)
            if non_installed:
                what_for = 'in order to run this task'
                install_packages(non_installed, what_for=what_for)
            return func(*args, **kwargs)

        return wrapper

    return real_decorator


def task(func, *args, **kwargs):
    '''Composition of decorator functions for inherent self-documentation on
    task execution.

    On execution, each task prints out its name and its first docstring line.
    '''
    prefix = '\n# '
    tail = '\n'
    return fabric.api.task(
        print_full_name(color=magenta,
                        prefix=prefix,
                        tail=tail)(print_doc1(func)),
        *args,
        **kwargs)


def custom_task(func, *args, **kwargs):
    '''Decorator task() composed with decorator needs_repo_fabsetup_custom().
    '''
    return task(needs_repo_fabsetup_custom(func, *args, **kwargs))


def subtask(*args, **kwargs):
    '''Decorator which prints out the name of the decorated function on
    execution.
    '''
    depth = kwargs.get('depth', 2)
    prefix = kwargs.get('prefix', '\n' + '#' * depth + ' ')
    tail = kwargs.get('tail', '\n')
    doc1 = kwargs.get('doc1', False)
    color = kwargs.get('color', cyan)

    def real_decorator(func):
        if doc1:
            return print_full_name(color=color, prefix=prefix,
                                   tail=tail)(print_doc1(func))
        return print_full_name(color=color, prefix=prefix, tail=tail)(func)

    invoked = bool(not args or kwargs)
    if not invoked:
        # invoke decorator function which returns the wrapper function
        return real_decorator(func=args[0])
    return real_decorator


def subsubtask(*args, **kwargs):

    def real_decorator(func):
        return subtask(depth=3, color=default_color, *args, **kwargs)(func)

    invoked = bool(not args or kwargs)
    if not invoked:
        # invoke decorator function which returns the wrapper function
        return real_decorator(func=args[0])
    return real_decorator


def _is_sudoer(what_for=''):
    '''Return True if current user is a sudoer, else False.

    Should be called non-eager if sudo is wanted only.
    '''
    if env.get('nosudo', None) is None:
        if what_for:
            print(yellow(what_for))
        with quiet():
            # possible outputs:
            #  en: "Sorry, user winhost-tester may not run sudo on <hostname>"
            #  en: "sudo: a password is required"     (=> is sudoer)
            #  de: "sudo: Ein Passwort ist notwendig" (=> is sudoer)
            output = run('sudo -nv', capture=True)
            env.nosudo = not (output.startswith('sudo: ') or output == '')
        if env.nosudo:
            print('Cannot execute sudo-commands')
    return not env.nosudo


def _has_dpkg():
    '''Return True if command dpkg is available, else False.'''
    return run('which dpkg').return_code == 0


def install_packages(packages,
                     what_for='for a complete setup to work properly'):
    '''Try to install .deb packages given by list.

    Return True, if packages could be installed or are installed already, or if
    they cannot be installed but the user gives feedback to continue.

    Else return False.
    '''
    res = True
    non_installed_packages = _non_installed(packages)
    packages_str = '  '.join(non_installed_packages)
    if non_installed_packages:
        with quiet():
            dpkg = _has_dpkg()
        hint = '  (You may have to install them manually)'
        do_install = False
        go_on = True
        if dpkg:
            if _is_sudoer('Want to install dpkg packages'):
                do_install = True
            else:
                do_install is False  # cannot install anything
                info = yellow(' '.join([
                    'This deb packages are missing to be installed',
                    flo("{what_for}: "), ', '.join(non_installed_packages),
                ]))
                question = '  Continue anyway?'
                go_on = query_yes_no(info + hint + question, default='no')
        else:
            # dpkg == False, unable to determine if packages are installed
            do_install = False  # cannot install anything
            info = yellow(' '.join([
                flo('Required {what_for}: '),
                ', '.join(non_installed_packages),
            ]))
            go_on = query_yes_no(info + hint + '  Continue?', default='yes')
        if not go_on:
            sys.exit('Abort')
        if do_install:
            command = flo('sudo  apt-get install {packages_str}')
            res = run(command).return_code == 0
    return res


def install_package(package):
    '''Install Ubuntu package given by param package.'''
    install_packages([package])


# TODO: base_dir must be compliant to addons
@needs_packages('git')
def checkup_git_repos(repos, base_dir='~/repos',
                      verbose=False, prefix='', postfix=''):
    '''Checkout or update git repos.

    repos must be a list of dicts each with an url and optional with a name
    value.
    '''
    run(flo('mkdir -p {base_dir}'))
    for repo in repos:
        cur_base_dir = repo.get('base_dir', base_dir)
        checkup_git_repo(url=repo['url'], name=repo.get('name', None),
                         base_dir=cur_base_dir, verbose=verbose,
                         prefix=prefix, postfix=postfix)


# TODO: base_dir must be compliant to addons
def checkup_git_repo(url, name=None, base_dir='~/repos',
                     verbose=False, prefix='', postfix=''):
    '''Checkout or update a git repo.'''
    if not name:
        match = re.match(r'.*/(.+)\.git', url)
        assert match, flo("Unable to extract repo name from '{url}'")
        name = match.group(1)
    assert name is not None, flo('Cannot extract repo name from repo: {url}')
    assert name != '', flo('Cannot extract repo name from repo: {url} (empty)')
    if verbose:
        name_blue = blue(name)
        print_msg(flo('{prefix}Checkout or update {name_blue}{postfix}'))
    if not exists(base_dir):
        run(flo('mkdir -p {base_dir}'))
    if not exists(flo('{base_dir}/{name}/.git')):
        run(flo('  &&  '.join([
                'cd {base_dir}',
                'git clone  {url}  {name}'])),
            msg='clone repo')
    else:
        if verbose:
            print_msg('update: pull from origin')
        run(flo('cd {base_dir}/{name}  &&  git pull'))
    return name


def _install_file_from_template_legacy(from_template, to_, **substitutions):
    from_str = filled_out_template(from_template, **substitutions)
    with tempfile.NamedTemporaryFile(prefix='fabsetup') as tmp_file:
        with open(tmp_file.name, 'w') as fp:
            fp.write(from_str)
        to_dir = dirname(to_)
        run(flo('mkdir -p  {to_dir}'))
        put(tmp_file.name, to_)


def install_file_legacy(path, sudo=False, from_path=None, **substitutions):
    '''Install file with path on the host target.

    The from file is the first of this list which exists:
     * custom file
     * custom file.template
     * common file
     * common file.template
    '''
    # source paths 'from_custom' and 'from_common'
    from_path = from_path or path
    # remove beginning '/' (if any), eg '/foo/bar' -> 'foo/bar'
    from_tail = join('files', from_path.lstrip(os.sep))
    if from_path.startswith('~/'):
        from_tail = join('files', 'home', 'USERNAME',
                         from_path[2:])  # without beginning '~/'
    from_common = join(FABFILE_DATA_DIR, from_tail)
    from_custom = join(FABSETUP_CUSTOM_DIR, from_tail)

    # target path 'to_' (path or tempfile)
    for subst in ['SITENAME', 'USER', 'ADDON', 'TASK']:
        sitename = substitutions.get(subst, False)
        if sitename:
            path = path.replace(subst, sitename)
    to_ = path
    if sudo:
        to_ = join(os.sep, 'tmp', 'fabsetup_' + os.path.basename(path))
    path_dir = dirname(path)

    # copy file
    if isfile(from_custom):
        run(flo('mkdir -p  {path_dir}'))
        put(from_custom, to_)
    elif isfile(from_custom + '.template'):
        _install_file_from_template_legacy(from_custom + '.template', to_=to_,
                                    **substitutions)
    elif isfile(from_common):
        run(flo('mkdir -p  {path_dir}'))
        put(from_common, to_)
    else:
        _install_file_from_template_legacy(from_common + '.template', to_=to_,
                                    **substitutions)
    if sudo:
        run(flo('sudo mv --force  {to_}  {path}'))


def install_user_command_legacy(command, **substitutions):
    '''Install command executable file into users bin dir.

    If a custom executable exists it would be installed instead of the "normal"
    one.  The executable also could exist as a <command>.template file.
    '''
    path = flo('~/bin/{command}')
    install_file_legacy(path, **substitutions)
    run(flo('chmod 755 {path}'))


AddonPackage = utlz.namedtuple(
    typename='Names',
    field_names=['module_dir'],
    lazy_vals={
        # fabsetup_theno_termdown
        'module_name': lambda self: self.module_dir.rsplit('/', 1)[-1],

        # fabsetup-theno-termdown
        'package_name': lambda self: self.module_dir.rsplit('/', 2)[-2],

        # /home/theno/.fabsetup-addon-repos/fabsetup-theno-termdown
        'package_dir': lambda self: dirname(self.module_dir),

        # /home/theno/.fabsetup-addon-repos/fabsetup-theno-termdown/fabsetup_theno_termdown/files
        'default_files_basedir': lambda self: join(self.module_dir, 'files'),

        # /home/theno/.fabsetup-custom/fabsetup-theno-termdown
        'custom_dir': lambda self: join(FABSETUP_CUSTOM_DIR,
                                        self.package_name),

        # /home/theno/.fabsetup-custom/fabsetup-theno-termdown/config.py
        'custom_config': lambda self: join(self.custom_dir, 'config.py'),

        # /home/theno/.fabsetup-custom/fabsetup-theno-termdown/files
        'custom_files_basedir': lambda self: join(FABSETUP_CUSTOM_DIR,
                                                  self.package_name, 'files'),
    })


def _determine_froms(addon_package, path):
    '''Return 2-Tuple (from_custom, from_default) for a given path.

    Example:

        >>> FABSETUP_CUSTOM_DIR = '/home/theno/.fabsetup-custom'
        >>>
        >>> # path is an abpath
        ...
        >>> addon_package = AddonPackage(module_dir='/home/theno/'
        ...                              '.fabsetup-addon-repos/'
        ...                              'fabsetup-theno-termdown/'
        ...                              'fabsetup_theno_termdown')
        >>> _determine_froms(addon_package, path='/absolute/path/foo.bar')
        ('/home/theno/.fabsetup-custom/fabsetup-theno-termdown/files/absolute/path/foo.bar', '/home/theno/.fabsetup-addon-repos/fabsetup-theno-termdown/fabsetup_theno_termdown/files/absolute/path/foo.bar')
        >>>
        >>> # with home-dir expansion
        ...
        >>> addon_package = AddonPackage(module_dir='/home/theno/'
        ...                              '.fabsetup-addon-repos/'
        ...                              'fabsetup-theno-termdown/'
        ...                              'fabsetup_theno_termdown')
        >>> _determine_froms(addon_package, path='~/foo/bar.baz')
        ('/home/theno/.fabsetup-custom/fabsetup-theno-termdown/files/home/USERNAME/foo/bar.baz', '/home/theno/.fabsetup-addon-repos/fabsetup-theno-termdown/fabsetup_theno_termdown/files/home/USERNAME/foo/bar.baz')

    '''
    # from_tail
    if path.startswith('~/'):
        path_tail = path[2:]  # path without beginning '~/'
        from_tail = join('home', 'USERNAME', path_tail)
    else:
        # remove beginning '/' (if any), eg '/foo/bar' -> 'foo/bar'
        from_tail = path.lstrip(os.sep)

    from_default = join(addon_package.default_files_basedir, from_tail)
    from_custom = join(addon_package.custom_files_basedir, from_tail)

    return from_custom, from_default


# FIXME: move to -> utlz
def _substituted(string, substitutions):
    substituted = string
    for key, val in substitutions.items():
        substituted = string.replace(key, val)
    return substituted


def install_file_wrapper(addon_package):

    def _install_file(from_path, to_path, sudo):
        path_dir = dirname(to_path)
        if sudo:
            tmp_file = join(
                os.sep, 'tmp',
                addon_package.package_name + '_' + os.path.basename(to_path))
            print(flo('temporary file: {tmp_file}'))
            put(from_path, tmp_file)
            run(flo('mkdir -p  {path_dir}'))
            run(flo('sudo mv --force  {tmp_file}  {to_path}'))
        else:
            run(flo('mkdir -p  {path_dir}'))
            put(from_path, to_path)

    def install_file(path, sudo=False, from_path=None, **substitutions):
        '''Install file with path on the host target.

        Args:
            path(str): Where file has to be installed to
            sudo(bool): If True install as superuser, eg. when path='/root/foo'
            from_path([None] or str): Optional path where the file comes from
            substitutions: kwargs with substitutions when installing a file
                           from a template.

        If from_path is None, the from file will become the first in this list
        which exists:
         * custom_files_basedir/path/to/file
         * custom_files_basedir/path/to/file.template
         * default_files_basedir/path/to/file
         * default_files_basedir/path/to/file.template

        'custom_files_basedir' is the dir `files` in the custom addon dir under
        ~/.fabsetup-custom.

        'default_files_basedir' is the dir `files` in the module dir of the
        addon-package.

        'path/to_file' is path as an relative path, a '~' will be expanded
        to 'home/USERNAME'.
        '''
        if from_path is None:

            from_custom, from_default = _determine_froms(addon_package, path)

            from_custom_template = flo('{from_default}.template')
            from_default_template = flo('{from_default}.template')

            if isfile(from_custom):
                from_path = from_custom
            elif isfile(from_custom_template):
                from_path = from_custom_template
            elif isfile(from_default):
                from_path = from_default
            else:
                from_path = from_default_template

        to_path = _substituted(path, substitutions)

        if from_path.endswith('.template'):
            from_str = filled_out_template(from_path, **substitutions)
            with tempfile.NamedTemporaryFile(
                    prefix=addon_package.package_name) as tmp_file:
                print(flo('template: {from_path}'))
                print(flo('filled out template: {tmp_file.name}'))
                with open(tmp_file.name, 'w') as fp:
                    fp.write(from_str)
                _install_file(tmp_file.name, to_path, sudo)
        else:
            _install_file(from_path, to_path, sudo)

    return install_file


def install_user_command_wrapper(addon_package):

    def install_user_command(command, **substitutions):
        '''Install command executable file into users bin dir ('~/bin/').

        If a custom executable exists it would be installed instead of the
        "normal" one.  The executable also could exist as a <command>.template
        file.
        '''
        path = flo('~/bin/{command}')
        install_file = install_file_wrapper(addon_package)
        install_file(path, **substitutions)
        run(flo('chmod 755 {path}'))

    return install_user_command


# FIXME: should be moved to utils.py
def print_msg(msg):
    if msg is not None:
        print(cyan(flo('{msg}')))


@needs_host
def update_or_append_line(filename, prefix, new_line, keep_backup=True,
                          append=True):
    '''Search in file 'filename' for a line starting with 'prefix' and replace
    the line by 'new_line'.

    If a line starting with 'prefix' not exists 'new_line' will be appended.
    If the file not exists, it will be created.

    Return False if new_line was appended, else True (i.e. if the prefix was
    found within of the file).
    '''
    result = None
    if env.host_string == 'localhost':
        result = update_or_append_local(filename, prefix, new_line,
                                        keep_backup, append)
    else:
        tmp_dir = tempfile.mkdtemp(suffix='', prefix='fabsetup_')
        # fabric.api.local(flo('chmod 777 {tmp_dir}'))
        local_path = os.path.join(tmp_dir, os.path.basename(filename))
        fabric.operations.get(remote_path=filename, local_path=local_path,
                              use_sudo=True, temp_dir='/tmp')
        result = update_or_append_local(local_path, prefix, new_line,
                                        keep_backup, append)
        put(local_path, remote_path=filename, use_sudo=True, temp_dir='/tmp')
        with quiet():
            fabric.api.local(flo('rm -rf {tmp_dir}'))
    return result


def comment_out_line(filename, line, comment='#'):
    '''Comment line out by putting a comment sign in front of the line.

    If the file does not contain the line, the files content will not be
    changed (but the file will be touched in every case).
    '''
    return comment_out_local(filename, line, comment,
                             update_or_append_line=update_or_append_line)


def uncomment_or_update_or_append_line(filename, prefix, new_line, comment='#',
                                       keep_backup=True):
    '''Remove the comment of an commented out line and make the line "active".

    If such an commented out line not exists it would be appended.
    '''
    return uua_local(filename, prefix, new_line, comment, keep_backup,
                     update_or_append_line=update_or_append_line)


def _line_2_pair(line):
    '''Return bash variable declaration as name-value pair.

    Name as lower case str. Value itself only without surrounding '"' (if any).

    For example, _line_2_pair('NAME="Ubuntu"') will return ('name', 'Ubuntu')
    '''
    key, val = line.split('=')
    return key.lower(), val.strip('"')


def _fetch_os_release_infos():
    '''Return variable content of file '/etc/os-release' as dict.

    Return-example (in case of an Ubuntu 16.04):
        {
            'name': 'Ubuntu',
            'version': '16.04.1 LTS (Xenial Xerus)',
            'version_id': '16.04',
            ...
        }
    '''
    os_release_dict = {}
    lines = []
    with fabric.api.hide('output'):
        lines = run('cat /etc/os-release', capture=True).split('\n')
    os_release_dict = dict([_line_2_pair(line.strip('\r'))
                            for line in lines
                            if line.strip() != ''])
    return os_release_dict


def is_os(name, version_id=None):
    '''Return True if OS name in /etc/lsb-release of host given by fabric param
    `-H` is the same as given by argument, False else.

    If arg version_id is not None only return True if it is the same as in
    /etc/lsb-release, too.

    Args:
        name: 'Debian GNU/Linux', 'Ubuntu'
        version_id(None or str): None,
                                '14.04', (Ubuntu)
                                '16.04', (Ubuntu)
                                '8', (Debian)
    '''
    result = False
    os_release_infos = _fetch_os_release_infos()

    if name == os_release_infos.get('name', None):

        if version_id is None:
            result = True
        elif version_id == os_release_infos.get('version_id', None):
            result = True

    return result


def is_debian(version_id=None):
    return is_os(name='Debian GNU/Linux', version_id=version_id)


def is_ubuntu(version_id=None):
    return is_os(name='Ubuntu', version_id=version_id)


def is_raspbian(version_id=None):
    return is_os(name='Raspbian GNU/Linux', version_id=version_id)


def is_osmc(version_id=None):
    return is_os(name='OSMC', version_id=version_id)


def dn_cn_of_certificate_with_san(domain):
    '''Return the Common Name (cn) from the Distinguished Name (dn) of the
    certificate which contains the `domain` in its Subject Alternativ Name (san)
    list.

    Needs repo ~/.fabsetup-custom.

    Return None if no certificate is configured with `domain` in SAN.
    '''
    cn_dn = None
    from config import domain_groups
    cns = [domains[0]
           for domains
           in domain_groups
           if domain in domains]
    if cns:
        if len(cns) > 1:
            print_msg(yellow(flo('Several certificates are configured to '
                                 'contain {domain} '
                                 '(You should clean-up your config.py)\n')))
        cn_dn = cns[0]
    return cn_dn


if __name__ == '__main__':
    doctest.testmod()
