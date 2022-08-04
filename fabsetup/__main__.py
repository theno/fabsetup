"""Executable of fabsetup"""

import os.path
import subprocess

import fabric.executor
import invoke

import fabsetup
import fabsetup.fabfile
import fabsetup.addons
import fabsetup.utils.outfile
import fabsetup.utils.pandoc

import fabsetup.main


def main(namespace=invoke.Collection.from_module(fabsetup.fabfile)):

    pip_addons = fabsetup.addons.load_pip_addons()
    repo_addons = fabsetup.addons.load_repo_addons()

    for addon in pip_addons + repo_addons:
        fabsetup.addons.merge_or_add_r(namespace, collection=addon)

    exit_code = 0

    try:

        program = fabsetup.main.Fabsetup(
            name="Fabsetup",
            version=fabsetup.__version__,
            executor_class=fabric.executor.Executor,
            # config_class=fabric.main.Config,
            config_class=fabsetup.main.FabsetupConfig,
            namespace=namespace,
        )

        program.run()

    except SystemExit as exc:

        exit_code = exc.code

    finally:

        if program.config.outfile.name and program.tee:
            program.tee.stop()

            outfile_abspath = os.path.abspath(
                os.path.expanduser(program.config.outfile.name)
            )

            if not program.config.outfile.keep_color:

                # remove color codes

                fabsetup.utils.outfile.remove_color_codes(outfile_abspath)

                if hasattr(program, "pandoc") and program.config.outfile.pandoc.toc:

                    # horizontal line + toc

                    with open(outfile_abspath, "r") as fh_in:
                        data = fh_in.read()

                    with open(outfile_abspath, "w") as fh_out:
                        fh_out.write("----\n\n" + data)

                    program.pandoc.add_toc(outfile_abspath)

            if program.config.outfile.prepend_executed_fabsetup_command:

                # fabsetup command

                command_postfix = "" if program.config.outfile.pandoc.toc else "----\n"

                with open(outfile_abspath, "r") as fh_in:
                    data = fh_in.read()

                with open(outfile_abspath, "w") as fh_out:
                    # eg.
                    #     ```
                    #     /path/to/bin/fabsetup taskname
                    #     [0]
                    #     ```
                    #
                    #     ...output of fabsetup task execution...
                    #
                    fh_out.write(
                        "{}```\n{}\n[{}]\n```\n\n{}".format(
                            program.config.outfile.fabsetup_command_prefix,
                            program.command,
                            exit_code,
                            command_postfix,
                        )
                        + data
                    )

            if program.config.outfile.pandoc.html.name:

                # markdown -> html

                program.pandoc.create_html(
                    filename_from=program.config.outfile.name,
                    filename_to=program.config.outfile.pandoc.html.name,
                    css_url=os.path.join(
                        os.path.dirname(__file__),
                        "utils",
                        "css",
                        "outfile.css",
                    ),
                    # css_url="~/.fabsetup-runs/outfile.css",
                    # css_url='https://raw.githubusercontent.com/KeithLRobertson/markdown-viewer/master/lib/sss/sss.css',
                    inline=True,
                )

        if program.config.run_finally:
            subprocess.run(program.config.run_finally, shell=True)


if __name__ == "__main__":
    main()
