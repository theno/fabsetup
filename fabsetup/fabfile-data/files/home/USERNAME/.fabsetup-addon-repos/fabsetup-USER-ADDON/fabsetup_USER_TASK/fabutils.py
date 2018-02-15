import os.path

from fabsetup.fabutils import AddonPackage
from fabsetup.fabutils import checkup_git_repo_wrapper
from fabsetup.fabutils import checkup_git_repos_wrapper
from fabsetup.fabutils import install_file_wrapper
from fabsetup.fabutils import install_user_command_wrapper


package = AddonPackage(module_dir=os.path.dirname(__file__))

checkup_git_repo = checkup_git_repo_wrapper(package)
checkup_git_repos = checkup_git_repos_wrapper(package)
install_file = install_file_wrapper(package)
install_user_command = install_user_command_wrapper(package)
