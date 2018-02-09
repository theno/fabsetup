import os
import imp
import sys
import types

import fabric.tasks

from fabsetup.utils import flo


known_pip_addons = [
    'fabsetup-theno-termdown',
]

addon_modules = {}


def get_or_create_module_r(module_name, base_module=None):
    '''Return a base-module (e.g. 'theno') or a sub-module (e.g.
    'theno.service.raccoon') from the dict addon_modules given by param
    'module_name'.

    If the highest module (e.g. 'theno') not exists, an empty module will be
    created.  This will be continued recursively until the lowest sub-module
    exists which will be returned

    Param 'base_module' is used for recursion only.
    '''
    module_names = module_name.split('.', 1)
    if len(module_names) > 1:
        # e.g. ['theno', 'service.wallabag']
        highest_module_name, module_name_rest = module_names
        highest_module = get_or_create_module_r(highest_module_name,
                                                base_module)
        if base_module:
            # anchor highest_module to its direct base-module
            base_module.__dict__[highest_module_name] = highest_module
        return get_or_create_module_r(module_name_rest,
                                      base_module=highest_module)
    else:  # len(module_names) == 0
        # module name does not contain any '.', e.g.: 'service'
        module = addon_modules.setdefault(module_name,
                                          imp.new_module(module_name))
        if base_module:
            # anchor module to its direct base-module
            base_module.__dict__[module_name] = module
        return module


def add_tasks_r(addon_module, package_module, package_name):
    '''Recursively iterate through 'package_module' and add every fabric task
    to the 'addon_module' keeping the task hierarchy.

    Args:
        addon_module(types.ModuleType)
        package_module(types.ModuleType)
        package_name(str): Required, to avoid redundant addition of tasks

    Return: None
    '''
    module_dict = package_module.__dict__
    for attr_name, attr_val in module_dict.items():

        if isinstance(attr_val, fabric.tasks.WrappedCallableTask):
            addon_module.__dict__[attr_name] = attr_val

        elif attr_name != package_name \
                and isinstance(attr_val, types.ModuleType) \
                and attr_val.__name__.startswith('fabsetup_') \
                and attr_name.split('.')[-1] != package_name:

            submodule_name = flo('{addon_module.__name__}.{attr_name}')
            submodule = get_or_create_module_r(submodule_name)
            package_module = attr_val

            add_tasks_r(submodule, package_module, package_name)
            addon_module.__dict__[attr_name] = submodule


def load_addon(username, package_name, _globals):
    '''Load an fabsetup addon given by 'package_name' and hook it in the
    base task namespace 'username'.

    Args:
        username(str)
        package_name(str)
        _globals(dict): the globals() namespace of the fabric script.

    Return: None
    '''
    addon_module = get_or_create_module_r(username)
    package_module = __import__(package_name)
    add_tasks_r(addon_module, package_module, package_name)
    _globals.update({username: addon_module})
    del package_module
    del addon_module


def load_pip_addons(_globals):
    '''Load all known fabsetup addons which are installed as pypi pip-packages.

    Args:
        _globals(dict): the globals() namespace of the fabric script.

    Return: None
    '''
    for package_name in known_pip_addons:
        _, username = package_username(package_name)
        try:
            load_addon(username, package_name.replace('-', '_'), _globals)
        except ImportError:
            pass  # swallow error in case of non-installed addon


def package_username(repo):
    '''
        >>> package_user('fabsetup-theno-termdown')
        (termdown, theno)

    '''
    package = repo.replace('-', '_')
    username = repo.split('-')[1]
    return package, username


def load_repo_addons(_globals):
    '''Load all fabsetup addons which are stored under ~/.fabsetup-addon-repos
    as git repositories.

    Args:
        _globals(dict): the globals() namespace of the fabric script.

    Return: None
    '''
    repos_dir = os.path.expanduser('~/.fabsetup-addon-repos')
    if os.path.isdir(repos_dir):
        basedir, repos, _ = next(os.walk(repos_dir))
        for repo_dir in [os.path.join(basedir, repo)
                         for repo in repos
                         # omit dot dirs like '.rope'
                         # or 'fabsetup-theno-termdown.disabled'
                         if '.' not in repo]:
            sys.path.append(repo_dir)
            package_name, username = package_username(repo_dir.split('/')[-1])
            load_addon(username, package_name, _globals)
