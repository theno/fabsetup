import os.path
import subprocess


class Pandoc:
    def __init__(self, command="/usr/bin/pandoc"):
        self.command = command

    def command_available(self):
        process = subprocess.Popen(
            [self.command, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        process.communicate()
        return process.returncode == 0

    def add_toc(self, filename):
        process = subprocess.Popen(
            [
                self.command,
                "--from",
                "markdown",
                "--to",
                "markdown",
                "--toc",
                "--toc-depth=6",
                "--standalone",
                # "--markdown-headings",  # not available on ubuntu 16.04
                # "atx",
                # "setext",
                # "--atx-headers",  # deprecated, works with ubuntu 16.04
                "--output",
                os.path.abspath(os.path.expanduser(filename)),
                os.path.abspath(os.path.expanduser(filename)),
            ],
        )
        process.communicate()
        return process.returncode == 0

    def create_html(self, filename_from, filename_to, css_url, inline):

        options = []

        if css_url:
            options += [
                "--css",
                os.path.abspath(os.path.expanduser(css_url)),
            ]

        if inline:
            options += ["--self-contained"]

        cmd = (
            [
                self.command,
                "--from",
                "markdown",
                "--to",
                "html",
            ]
            + options
            + [
                "--output",
                os.path.abspath(os.path.expanduser(filename_to)),
                os.path.abspath(os.path.expanduser(filename_from)),
            ]
        )
        # print(' '.join(cmd))  # TODO DEVEL
        process = subprocess.Popen(cmd)
        process.communicate()
        return process.returncode == 0
