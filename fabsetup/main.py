"""Executable of fabsetup"""

import datetime
import os
import os.path
import pprint
import subprocess
import sys

# import fabric
import fabric.config
# import fabric.connection
import fabric.main
import invoke
import invoke.main
import invoke.config
# import invoke.context
import invoke.parser
from invoke.util import debug

import fabsetup.addons
import fabsetup.print
import fabsetup.utils.outfile
import fabsetup.utils.pandoc
# import fabsetup.fabutils.queries


class FabsetupConfig(fabric.config.Config):
    """A `fabric.config.Config` subclass which is an `invoke.config.Config`
    subclass for prefix manipulation.

    This enables for `fabsetup` prefixed config files and `FABSETUP_` prefixed
    environment variables utilising the `same mechanics as Fabric
    <https://docs.fabfile.org/en/latest/concepts/configuration.html#configuration>`_.
    """

    prefix = "fabsetup"
    """The prefix used by Fabsetup => ``fabsetup.yaml, FABSETUP_ENV_VAR, ...``"""

    @staticmethod
    def _as_dict_r(obj):
        if type(obj) is dict:
            res = {}
            for k, v in obj.items():
                res[k] = FabsetupConfig._as_dict_r(v)
            return res
        if not hasattr(obj, "__dict__"):
            return obj
        else:
            try:
                return FabsetupConfig._as_dict_r(dict(obj))
            except TypeError:
                return obj

    def as_dict(self):
        """Return this ``fabsetup.main.FabsetupConfig`` as dict.

        This dict is printed in ``fabstup.main.execute`` using
        ``pprint.pprint()``.
        """
        return FabsetupConfig._as_dict_r(self)

    @staticmethod
    def global_defaults():
        """Create and return default configurations from Fabsetup, Fabric and
        Invoke defaults.

        Extends `fabric.config.Config.global_defaults
        <https://docs.fabfile.org/en/latest/api/config.html#fabric.config.Config.global_defaults>`_
        which extends `invoke.config.Config.global_defaults()
        <https://docs.pyinvoke.org/en/stable/api/config.html#invoke.config.Config.global_defaults>`_.

        :returns:
            `dict` with merged defaults.
        """
        defaults = fabric.config.Config.global_defaults()
        ours = {
            "outfile": {
                "dir": "",
                "basename_formatter": "fabsetup_{now}{tasks}{hosts}.md",
                "now_format": "%F_%H-%M-%S",
                "name": "",
                "keep_color": False,
                "pandoc": {
                    "command": "pandoc",
                    "html": {
                        "dir": "",
                        "name": "",
                        "css": {
                            "disabled": False,
                            "inline": True,
                            "url": "",
                            "auto_remove_markdown_file": True,
                        },
                    },
                    "toc": False,
                },
                "prepend_executed_fabsetup_command": True,
                "fabsetup_command_prefix": "*Executed fabsetup command:*\n\n",
                "command_output_prefix": "(stdout) ",
                "command_errput_prefix": "(STDERR) ",
            },
            "output": {
                "color": {
                    "cmd_local": "green",
                    "cmd_remote": "yellow",
                    "docstring": "blue",
                    "error": "red",
                    "full_name": "no_color",
                    "subtask_heading": "cyan",
                    "task_heading": "magenta",
                    # "question": "default_color",
                },
                "color_off": False,
                "hide_command_line": False,
                "hide_code_block": False,
                "hide_docstring": False,
                "hide_heading": False,
                "hide_print": False,
                "numbered": True,
                "numbered_state": "0",
                "task_depth": 1,
            },
            "run": {
                "interactive": False,
            },
            "load_invoke_tasks_file": False,
            "load_fabric_fabfile": False,
            # "search_root": None,
            "run_before": "",
            "run_finally": "",
        }
        invoke.config.merge_dicts(defaults, ours)
        return defaults


class Fabsetup(fabric.main.Fab):
    """Fabsetup's CLI entrypoint and parser configuration.

    It is build on top of Fabric's and Invoke's core functionality for same.
    """

    def __init__(self, *args, **kwargs):
        self.tee = None
        super().__init__(*args, **kwargs)

    def core_args(self):
        """Create core arguments.

        Overwrites `fabric.main.Fab.core_args()`.

        :returns:
            List of core args each of type `invoke.parser.argument.Argument`.
        """
        core_args = super().core_args()
        extra_args = [
            invoke.Argument(
                names=("hide-code-block",),
                kind=bool,
                default=False,
                help="Do not wrap commands in markdown code blocks.",
            ),
            invoke.Argument(
                names=("hide-command-line",),
                kind=bool,
                default=False,
                help="Hide executed commands.",
            ),
            invoke.Argument(
                names=("hide-command-output",),
                kind=bool,
                default=False,
                help="Hide output of executed commands. Same as `--hide=both`.",
            ),
            invoke.Argument(
                names=("hide-docstring",),
                kind=bool,
                default=False,
                help="Hide ((sub-) sub-) task docstrings.",
            ),
            invoke.Argument(
                names=("hide-heading",),
                kind=bool,
                default=False,
                help="Hide markdown headings.",
            ),
            invoke.Argument(
                names=("hide-print",),
                kind=bool,
                default=False,
                help="Hide `print()` output.",
            ),
            invoke.Argument(
                names=("unnumbered",),
                kind=bool,
                default=False,
                help="Unnumbered headings",
            ),
            invoke.Argument(
                names=("interactive",),
                kind=bool,
                default=False,
                help="Confirm and optionally change every command "
                "(disables `--hide-command-line`).",
            ),
            invoke.Argument(
                names=("color-keep",),
                kind=bool,
                default=False,
                help="Do not remove ANSI escape sequences from outfile.",
            ),
            invoke.Argument(
                names=("color-off",),
                kind=bool,
                default=False,
                help="Fabsetup output without ANSI color codes. "
                "Output of executed commands still could be colored.",
            ),
            invoke.Argument(
                names=("outfile",),
                kind=str,
                default="",
                help="Write markdown output (stdout and stderr) to file.",
            ),
            invoke.Argument(
                names=("pandoc-add-toc",),
                kind=str,
                default="",
                help="Add table of contents to outfile.",
            ),
            invoke.Argument(
                names=("pandoc-html-file",),
                kind=str,
                default="",
                help="Convert outfile to html file.",
            ),
            invoke.Argument(
                names=("known-addons",),
                kind=bool,
                default=False,
                help="List known Fabsetup addons.",
            ),
            invoke.Argument(
                names=("show-config",),
                kind=bool,
                default=False,
                help="Show effective configuration and exit.",
            ),
            invoke.Argument(
                names=("load-inv",),
                kind=bool,
                default=False,
                help="Load tasks.py file (invoke module file[s]).",
            ),
            invoke.Argument(
                names=("load-fab",),
                kind=bool,
                default=False,
                help="Load fabfile.py (fabric module file[s]).",
            ),
            # invoke.Argument(
            #     names=("search-root", "r"),
            #     # kind=str,
            #     # default=None,
            #     help="Change root directory used for finding task module files. Only effective in combination with `--load-inv` or `--load-fab`",
            # ),
        ]
        return core_args + extra_args + self.task_args()

    def parse_core(self, argv):

        super().parse_core(argv)

    def parse_cleanup(self):
        """Add list of known fabsetup addons to program output.

        Overwrites `invoke.program.Program.parse_cleanup()`.
        """

        # wrap_in_code_block = (
        #     self.args.list.value or self.args.help.value
        # ) and self.config.outfile.name

        # if wrap_in_code_block:
        #     self.tee.pause()
        #     self.tee.resume(missed_output="\n```\n")

        try:
            super().parse_cleanup()

        finally:

            # if wrap_in_code_block:
            #     self.tee.pause()
            #     self.tee.resume(missed_output="```\n")
            pass

        if self.args.get("known-addons").value:
            print("# Known Fabsetup Addons\n")
            print("* ", end="")
            print(
                "".join(
                    [
                        "fabsetup-theno-termdown  ",
                        "[Set up and install termdown]",
                        "(https://pypi.org/project/fabsetup-theno-termdown)",
                    ]
                )
            )
            raise invoke.exceptions.Exit

    def _load(self, program, collection_name):
        program.config = self.config

        # FIXME: hacky, duplicate config instead
        program.config.tasks.collection_name = "fabfile"
        program.config.run.replace_env = True
        if collection_name == "inv":
            program.config.tasks.collection_name = "tasks"
            program.config.run.replace_env = False  # TODO respect defaults

        # program.argv = []
        # program.parse_core_args()

        parser = invoke.parser.Parser(initial=self.initial_context, ignore_unknown=True)
        program.core = parser.parse_argv(self.argv[1:])

        # cf. invoke.program.Program.task_args()
        program.args["collection"] = self.args["collection"]
        program.args["no-dedupe"] = self.args["no-dedupe"]
        program.args["search-root"] = self.args["search-root"]  # required

        program.parse_collection()
        program.collection.name = collection_name

        fabsetup.addons.merge_or_add_r(self.collection, program.collection)

    def load_invoke_tasks(self):
        if self.config.load_invoke_tasks_file:
            self._load(invoke.main.program, collection_name="inv")

    def load_fabric_tasks(self):
        if self.config.load_fabric_fabfile:
            self._load(fabric.main.program, collection_name="fab")

    def parse_tasks(self):

        self.update_config()

        self.load_invoke_tasks()
        self.load_fabric_tasks()

        # self.parse_collection()
        # self.parse_tasks()

        super().parse_tasks()

    def update_config(self):

        self.config.load_shell_env()

        super().update_config()

        # self.config['run']['interactive'] is only used by fabsetup,
        # not by fabric nor by invoke
        if self.args.interactive.value:
            self.config.run.interactive = True

        if self.args.get("color-off").value:
            self.config.output.color_off = True

        if self.args.get("hide-code-block").value:
            self.config.output.hide_code_block = True

        if self.args.get("hide-command-line").value:
            self.config.output.hide_command_line = True

        if self.args.get("hide-command-output").value:
            self.config.run.hide = "both"

        if self.args.get("hide-docstring").value:
            self.config.output.hide_docstring = True

        if self.args.get("hide-heading").value:
            self.config.output.hide_heading = True

        if self.args.get("hide-print").value:
            self.config.output.hide_print = True

        if self.args.get("unnumbered").value:
            self.config.output.numbered = False

        if self.args.get("color-keep").value:
            self.config.outfile.keep_color = True

        if self.args.get("outfile").value:
            self.config.outfile.name = self.args.get("outfile").value

        if self.args.get("load-inv").value:
            self.config.load_invoke_tasks_file = True

        if self.args.get("load-fab").value:
            self.config.load_fabric_fabfile = True

    def control_output(self):

        if self.config.output.color_off:
            fabsetup.utils.colors.ENABLED = False

        if self.config.output.hide_code_block:
            fabsetup.print.print_code_block.enabled = False

        if self.config.output.hide_command_line:
            fabsetup.print.print_command_line.enabled = False

        if self.config.output.hide_docstring:
            fabsetup.print.print_docstring.enabled = False

        if self.config.output.hide_heading:
            fabsetup.print.print_heading.enabled = False

        if self.config.output.hide_print:
            fabsetup.print.print_default.enabled = False

    def control_outfile(self):

        # auto-set self.config.outfile.name

        if not self.config.outfile.name:

            outfile_dir = self.config.outfile.dir

            if outfile_dir:

                now = datetime.datetime.now()
                now_str = now.strftime(self.config.outfile.now_format)

                # eg. `fabsetup task1 task2 long.task.name` results
                # in: tasks_str = "_task1_task2_long-task-name"
                # eg. `fabsetup` (no tasks given) results
                # in: tasks_str = ""
                tasks_str = "".join(
                    ["_{}".format(task.name.replace(".", "-")) for task in self.tasks]
                )

                # eg. hosts_str = "_host1_user@host2"
                # eg. hosts_str = "_user@host"
                # eg. hosts_str = ""
                hosts = []
                hs = self.core[0].as_kwargs["H"]
                if hs:
                    hosts = hs.split(",")
                hosts_str = "".join(["_{}".format(user_host) for user_host in hosts])

                # eg.
                # basename = "fabsetup_2021-02-21_10-30-01_taskname_user@host.md"
                basename = self.config.outfile.basename_formatter.format(
                    now=now_str,
                    tasks=tasks_str,
                    hosts=hosts_str,
                )

                self.config.outfile.name = os.path.join(
                    os.path.abspath(os.path.expanduser(outfile_dir)),
                    basename,
                )

        if self.config.outfile.name and not self.config.outfile.pandoc.html.name:

            html_dir = self.config.outfile.pandoc.html.dir

            if html_dir:

                html_basename = (
                    os.path.basename(self.config.outfile.name).rsplit(".")[0] + ".html"
                )

                self.config.outfile.pandoc.html.name = os.path.join(
                    os.path.abspath(os.path.expanduser(html_dir)),
                    html_basename,
                )

        if self.config.outfile.pandoc.html.name:

            self.pandoc = fabsetup.utils.pandoc.Pandoc(
                self.config.outfile.pandoc.command
            )

            if not self.pandoc.command_available():
                print(
                    "command {} not available".format(
                        self.config.outfile.pandoc.command
                    )
                )
                raise invoke.exceptions.Exit

        if self.config.outfile.name:

            outfile_abspath = os.path.abspath(
                os.path.expanduser(self.config.outfile.name)
            )

            outfile_dirname = os.path.dirname(outfile_abspath)
            if not os.path.exists(outfile_dirname):
                os.makedirs(outfile_dirname)

            debug("outfile_abspath: '{}'".format(outfile_abspath))

            self.tee = fabsetup.utils.outfile.Tee()
            self.tee.set_outfile(
                outfile_abspath,
                # prefix="```sh\n{}\n```\n\n----\n".format(" ".join(sys.argv[:])),
                # prefix="----\n",
                prefix="",
            )
            self.tee.start()

            self.command = " ".join(sys.argv[:])

    def execute(self):
        """Add hooks to ``invoke.program.`` in order to run external command
        before fabsetup task execution, control output and outfile of fabsetup
        task execution and show effective fabsetup config.
        """
        if self.config.run_before:
            subprocess.run(self.config.run_before, shell=True)

        self.control_output()
        self.control_outfile()

        debug("\n" + pprint.pformat(dict(self.config)))

        if self.args.get("show-config").value:
            # pprint.pprint(dict(self.config))
            pprint.pprint(self.config.as_dict())
            raise invoke.exceptions.Exit

        super().execute()

    def run(self, argv=None, exit=True):
        """"""

        # self.create_config()
        # self.parse_core(argv)
        # self.parse_collection()
        # self.parse_tasks()
        # # self.parse_cleanup()
        # self.update_config()

        super().run(argv=argv, exit=True)

    def print_version(self):
        print(fabsetup.version_str())

    # overrides invoke.program.Program.task_list_opener()
    # return 'Tasks:' instead of 'Subcommands:'
    def task_list_opener(self, *args, **kwargs):
        res = super().task_list_opener(*args, **kwargs)
        if res == "Subcommands":
            return "Tasks"
        return res

    # overrides invoke.program.Program.print_help()
    # print 'task..' instead of 'subcommand..'
    def print_help(self):

        usage_suffix = "task1 [--task1-opts] ... taskN [--taskN-opts]"
        print("Usage: {} [--core-opts] {}".format(self.binary, usage_suffix))
        print("")

        print("Core options:")
        print("")
        self.print_columns(self.initial_context.help_tuples())

        if self.namespace is not None:
            self.list_tasks()
