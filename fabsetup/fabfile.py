import configparser
import io
import os.path
import re
import string
import sys

import fabsetup
import fabsetup.fabutils.addon
from fabsetup.task import task, subtask
from fabsetup.utils.colors import red, cyan
from fabsetup.fabutils.queries import query_yes_no, query_input

# from fabsetup.print import print_quiet


@subtask(name="Versions", doc=False)
def versions(c):
    """Show version numbers of all available fabsetup addons, fabsetup,
    fabric, paramiko, and invoke.
    """
    # print_quiet('```\n{}\n```\n'.format(fabsetup.version_str()))
    print("```\n{}\n```\n".format(fabsetup.version_str()))


@subtask(name="Help", doc=False)
def help(c, cmd):
    """Show help command"""
    # print_quiet('    {} -h\n'.format(cmd))
    print("    {} -h\n".format(cmd))


@subtask(name="List tasks", doc=False)
def tasks(c, cmd):
    """Show available tasks."""
    # print_quiet('    {} -l\n'.format(cmd))
    print("    {} -l\n".format(cmd))


@subtask(name="Show task help", doc=False)
def task_help(c, cmd):
    """Show task help command."""
    # print_quiet('    {} <task> --help\n'.format(cmd))
    print("    {} <task> --help\n".format(cmd))


@task(default=True, name_="Fabsetup")
def info(c):
    """Show fabsetup info."""
    # print('FOO ', c.config.output.numbered_state) # TODO DEBUG

    print("[fabsetup repository](https://github.com/theno/fabsetup)\n")
    versions(c)
    cmd = sys.argv[0]
    help(c, cmd)

    # # TODO DEVEL
    # c.run("uname -a")
    # from pprint import pprint; pprint(dict(c.config))
    # print("1")
    # c.local('echo "\033[34mfoo\033[0m"')
    # print("\n2")
    # c.local('echo "local stdout-output"')
    # print("\n3")
    # c.run('echo "remote stdout-output"')
    # print("\n4")
    # c.local('>&2 echo "local stderr-output"')
    # print("\n5")
    # c.run('>&2 echo "remote stderr-output"')
    # return

    tasks(c, cmd)
    task_help(c, cmd)

    # print(c.config.task_depth)


def git_name_and_email_or_die():
    config = configparser.ConfigParser()
    filename = os.path.expanduser("~/.gitconfig")
    try:
        with open(filename) as fh:
            gitconfig = fh.readlines()
    except IOError:
        print(red("~/.gitconfig does not exist") + ", run:\n")
        print('    git config --global user.name "Your Name"')
        print('    git config --global user.email "your.email@example.com"')
        sys.exit()

    config.readfp(io.StringIO("".join([line.lstrip() for line in gitconfig])))

    name = None
    email = None
    try:
        name = config.get("user", "name")
    except configparser.NoOptionError:
        print(red("missing user.name in ~/.gitconfig") + ", run:\n")
        print('    git config --global user.name "Your Name"')
        sys.exit()
    try:
        email = config.get("user", "email")
    except configparser.NoOptionError:
        print(red("missing user.email in ~/.gitconfig") + ", run:\n")
        print('    git config --global user.email "your.email@example.com"')
        sys.exit()

    return name, email


def show_or_ask(name, value, default=None):
    if value:
        print("{}: {}".format(name, value))
        return value
    else:
        return query_input("{}:".format(name), default=default)


def sanitize(name, value):
    filtered = re.sub("[^a-zA-Z0-9 _-]", "", value)
    first_is_char = filtered.lstrip(string.digits + " _-")
    lower = first_is_char.lower()
    last_is_char_or_digit = lower.rstrip(" _-")
    underscored = last_is_char_or_digit.replace("-", "_").replace(" ", "_")
    assert len(underscored) > 0, "The %s must have at least one char" % name
    return underscored


@subtask
def gather_from_user_and_task_name(c, username, task_name):
    """Gather username, task name, addon name, full addon name, and addon dir
    from username and task name.

    Query for username and task name if not set already.
    """

    print("```")

    username = show_or_ask("username", username)
    username = sanitize("username", username)

    task_name = show_or_ask("task name", task_name)
    task_name = sanitize("task name", task_name)

    print("└─> task name: {0}".format(cyan(task_name)))

    print("└─> full task name: {0}".format(cyan("{}.{}".format(username, task_name))))

    addon_name = task_name.replace("_", "-")
    full_addon_name = "fabsetup-{}-{}".format(username, addon_name)

    print("└─> addon name: {0}".format(cyan(addon_name)))
    print("└─> full addon name: {0}".format(cyan(full_addon_name)))
    print("```")
    print("")

    addon_dir = os.path.expanduser(
        "~/.fabsetup-addon-repos/fabsetup-{}-{}".format(username, addon_name)
    )

    return (username, task_name, addon_name, full_addon_name, addon_dir)


@subtask
def gather_task_infos(c, headline, description, touched_files):
    """Query for headline, description and touched files if not set already."""
    print("```")

    headline = show_or_ask("headline", headline, default="Install or update termdown.")

    print("")

    description = show_or_ask(
        "description",
        description,
        default="""Termdown (https://github.com/trehn/termdown) is a
    "countdown timer and stopwatch in your terminal".

    This task installs termdown via `pip install --user termdown`.  Also, it
    installs a bash-wrapper script at `~/bin/termdown` which is convenient to
    time pomodoro sessions and pops up a notification when the timer finishes.""",
    )  # noqa: E501

    print("")

    touched_files = show_or_ask(
        "affected files, dirs, and installed packages",
        touched_files,
        default="~/bin/termdown\n        " "pip-package termdown (`--user` install)",
    )

    print("")

    return (headline, description, touched_files)


@subtask
def create_files(
    c,
    # '/home/theno/.fabsetup-addon-repos/fabsetup-theno-termdown'
    addon_dir,
    username,  # 'theno'
    addon_name,  # 'termdown'
    task_name,  # 'termdown'
    author,
    author_email,
    headline="",
    description="",
    touched_files="",
):
    """Create addon files."""

    addon = fabsetup.fabutils.addon.Addon(os.path.dirname(__file__), context=c)

    filenames = [
        "README.md",
        "fabsetup_USER_TASK/__init__.py",
        "fabsetup_USER_TASK/_version.py",
    ]

    for filename in filenames:
        addon.install_file(
            path="~/.fabsetup-addon-repos/fabsetup-USER-ADDON/{}".format(filename),
            local=True,
            username=username,
            addon_name=addon_name,
            task_name=task_name,
            headline=headline,
            description=description,
            touched_files=touched_files,
            author=author,
            author_email=author_email,
            USER=username,
            ADDON=addon_name,
            TASK=task_name,
        )


@subtask
def create_git_repo(c, basedir):
    """Create git repository."""
    basedir_abspath = os.path.expanduser(basedir)
    if os.path.isdir("{}/.git".format(basedir_abspath)):
        print("git repo already initialized (skip)")
    else:
        print("Initialize:")
        c.local("cd {} && git init".format(basedir))

        print("\nAdd all files:")
        c.local("cd {} && git add .".format(basedir))

        print("\nCommit:")
        # $HOME is required for git to find author and author-email config
        homedir = os.path.expanduser("~")
        c.local(
            'cd {} && HOME={}  git commit -am "Initial commit"'.format(basedir, homedir)
        )


@subtask
def summary(c, addon_dir, username, task_name):
    """Summarize addon infos"""
    c.local("tree -aI '.git' %s" % addon_dir)
    print("")
    print("The `%s` contains Your task code" % cyan("__init__.py"))
    print("")
    print("Run Your task:")
    print("")
    print("    fabsetup {}.{}".format(username, task_name))
    print("    fabsetup -H user@host {}.{}".format(username, task_name))
    print("")
    print("More infos: <https://github.com/theno/fabsetup>")


@task(name_="New Fabsetup Addon")
def new(
    c,
    username=None,
    task_name=None,
    headline=None,
    description=None,
    touched_files=None,
):
    """Create a new fabsetup addon.

    The created addon will reside inside of a created git repository and
    contains the fabsetup addon boilerplate code.  Afterwards, You can start to
    add code and functionality to Your addon.

    This task needs the following infos from You:

    * `user` name
    * `task` name
    * `headline`, `description`, and touched (and created) files and dirs for
      the task docstring and the `README.md`

    You can set them by task argument. If You omit any argument You will be
    asked for when this task runs.

    The addon name will be derived from the task name.

    This files and dirs will be created:

    .. code-block:: bash

        ~/.fabsetup-addon-repos/fabsetup-{user}-{addon}
                                │
                                ├── fabsetup_{user}_{task}
                                │   ├── __init__.py  # task definition
                                │   └── _version.py
                                │
                                ├── README.md
                                │
                                ├── requirements.txt
                                ├── setup.py
                                │
                                ├── .gitignore
                                │
                                └── .git
                                    ├── ...
                                    ├── config
                                    └── ...
    """
    author, author_email = git_name_and_email_or_die()

    (
        username,
        task_name,
        addon_name,
        full_addon_name,
        addon_dir,
    ) = gather_from_user_and_task_name(c, username, task_name)

    subtask(name="gather git name and email from global config", doc=False)(
        lambda c: None
    )

    if os.path.exists(addon_dir):
        print(red("{} already exists.".format(addon_dir)))
        print("abort")
    else:
        print("```")
        print("~/.gitconfig")
        print("├─> author: {0} ─> LICENSE, setup.py".format(cyan(author)))
        print("└─> author email: {0} ─> setup.py".format(cyan(author_email)))
        print("```")
        print("")

        headline, description, touched_files = gather_task_infos(
            c, headline, description, touched_files
        )

        print("addon git-repository dir: {0}".format(cyan(addon_dir)))

        if query_yes_no("\ncreate new addon?", default="yes"):
            print("\n```")
            print("")

            create_files(
                c,
                addon_dir,
                username,
                addon_name,
                task_name,
                author,
                author_email,
                headline,
                description,
                touched_files,
            )

            create_git_repo(c, addon_dir)

            summary(c, addon_dir, username, task_name)
        else:
            print("```")
            print("")
            print("abort")
