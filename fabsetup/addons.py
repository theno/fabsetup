"""Functions to load tasks of available fabsetup addons.

``load_pip_addons()`` and ``load_repo_addons()``  will be used in
``fabsetup.__main__.main()`` to add fabsetup addons to fabsetup.
"""

import os
import importlib
import sys

import invoke


KNOWN_PIP_PACKAGE_ADDONS = [
    "fabsetup-theno-termdown",
]

REPOS_DIR = os.path.expanduser("~/.fabsetup-addon-repos")

REPO_MODULES = []
PIP_MODULES = []


def module_username(package_name):
    """Return a ``(module-name, user-name)`` pair derived from a given fabsetup
    addon ``package_name``.

    A fabsetup addon package-name has a name format
    ``fabsetup-USERNAME-TASKNAME`` where ``USERNAME`` is a pypi and
    git{hub,lab,...} user-name and ``TASKNAME`` is the name of the (main) task
    function of the fabsetup addon.

    :param str package_name:
        Package name of the fabsetup addon, e.g. ``'fabsetup-theno-termdown'``.

    :returns:
        Two-tuple of (`str`, `str`).

    Example:

        >>> module_username('fabsetup-theno-termdown')
        ('fabsetup_theno_termdown', 'theno')

    """
    assert package_name.startswith("fabsetup-")
    module = package_name.replace("-", "_")
    username = package_name.split("-")[1]
    return module, username


def load_addon(package_name):
    """Load fabsetup addon ``package_name`` and return it as a
    ``(module, collection)`` pair.

    :param str package_name:
        Package name of the fabsetup addon, e.g. ``'fabsetup-theno-termdown'``.

    :returns:
        Two-tuple ("fabsetup_USERNAME_TASKNAME", `invoke.Collection`).
    """
    module_name, username = module_username(package_name)
    module = importlib.import_module(module_name)
    collection = invoke.Collection.from_module(module, name=username)
    return module, collection


def load_pip_addons():
    """Load all known fabsetup addons which are installed as pypi pip-packages.

    The loaded collections are returned as a list and also stored in list
    attribute ``fabsetup.addons.PIP_MODULES``.

    :returns:
        list of `[invoke.Collection`, `invoke.Collection, ...]`,
    """
    collections = []

    for package_name in KNOWN_PIP_PACKAGE_ADDONS:

        try:
            module, collection = load_addon(package_name)
            collections.append(collection)
            PIP_MODULES.append(module)

        except ImportError:
            pass  # swallow error in case of non-installed addon

    return collections


def load_repo_addons():
    """Load all fabsetup addons which are stored under
    ``~/.fabsetup-addon-repos`` as git repositories.

    The loaded collections are returned as a list and also stored in
    ``fabsetup.addons.REPO_MODULES``.

    :returns:
        list of `[invoke.Collection`, `invoke.Collection, ...]`,
    """
    collections = []

    if os.path.isdir(REPOS_DIR):

        dirpath, dirnames, _ = next(os.walk(REPOS_DIR))

        for repo_dirpath in [
            os.path.join(dirpath, repo_addon)
            # for repo_addon in dirnames  # TODO DEBUG
            for repo_addon in sorted(dirnames)
            # omit dot dirs like '.rope'
            # or 'fabsetup-theno-termdown.disabled'
            if "." not in repo_addon
        ]:

            sys.path.append(repo_dirpath)

            # eg. package_name = 'fabsetup-theno-termdown'
            package_name = repo_dirpath.split("/")[-1]

            module, collection = load_addon(package_name)
            collections.append(collection)
            REPO_MODULES.append(module)

    return collections


def merge_or_add_r(namespace, collection):
    """Recursively add ``collection`` as sub-collection to (mutable)
    ``namespace``.

    If ``namespace`` already contains a same-named sub-collection, the tasks
    and sub-namespaces of ``collection`` each will be added to the same-named
    sub-collection, i.e. merged into it.

    :param invoke.Collection namespace:
        Target collection

    :param invoke.Collection collection:
        The collection where tasks and sub-collections will be taken or merged
        from.
    """
    colls = [
        coll for coll in namespace.collections.values() if coll.name == collection.name
    ]
    if colls:
        # same named collection already exists
        same_name = colls[0]

        # merge tasks
        for task in collection.tasks.values():
            same_name.add_task(task)

        # merge sub-collections
        for sub_col in collection.collections.values():
            merge_or_add_r(same_name, sub_col)
    else:
        # add
        namespace.add_collection(collection)
