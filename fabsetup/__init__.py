"""fabric-2 tasks and utils. `Latest sources
<https://github.com/theno/fabsetup/tree/master/fabsetup>`_
"""

import fabric
import invoke
import paramiko

import fabsetup
import fabsetup.fabfile
import fabsetup.addons
from fabsetup._version import __version__  # noqa: F401


def _module_str(module, postfix=""):
    """Print module in pip style"""
    name = module.__name__
    return "{}=={}{}".format(name, module.__version__, postfix)


def version_str():
    """Return versions of fabsetup addons, fabsetup, fabric, paramiko, and
    invoke.
    """
    return "\n".join(
        [_module_str(mod, "-addon-repo") for mod in fabsetup.addons.REPO_MODULES]
        + [_module_str(mod) for mod in fabsetup.addons.PIP_MODULES]  # noqa: W503, E501
        + [
            _module_str(mod) for mod in (fabsetup, fabric, paramiko, invoke)
        ]  # noqa: W503, E501
    )
