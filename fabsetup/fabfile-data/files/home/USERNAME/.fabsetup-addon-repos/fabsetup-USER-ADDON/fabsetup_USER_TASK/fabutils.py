import os.path

from fabsetup.fabutils import AddonPackage
from fabsetup.fabutils import install_file_wrapper
from fabsetup.fabutils import install_user_command_wrapper


package = AddonPackage(module_dir=os.path.dirname(__file__))

install_file = install_file_wrapper(package)
install_user_command = install_user_command_wrapper(package)
