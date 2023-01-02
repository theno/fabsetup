"""With a locally installed `Pandoc <https://pandoc.org/>`_ add a table of
content (toc) to Markdown files and create HTML from Markdown files.
"""

import os
import os.path
import pathlib
import subprocess

from invoke.util import debug


class Pandoc:
    """Pandoc command execution interface.

    :param str `command`:
        Optionally, path to Pandoc executable.
    """

    def __init__(self, command="/usr/bin/pandoc"):
        self.command = command

    def command_available(self):
        """Check if pandoc command is available.

        Return `True` if command is available, else `False`.
        """
        process = subprocess.Popen(
            [self.command, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        process.communicate()
        return process.returncode == 0

    def add_toc(self, filename):
        """Add a table of content to a Markdown file (inplace).

        :param str `filename`:
            Name of the Markdown file.

        :returns:
            `True` if toc has been added, else `False`.
        """
        fname = os.path.abspath(os.path.expanduser(filename))
        # fname_stem = pathlib.Path(fname).stem
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
                # "--metadata pagetitle=\"{stem}\"".format(stem=fname_stem),
                "--output",
                fname,
                fname,
            ],
        )
        process.communicate()
        return process.returncode == 0

    def create_html(self, filename_from, filename_to, css_url="", inline=False):
        """From a Markdown file create an HTML file.

        Recursively create parent dirs of ``filename_to`` if they not exist.

        :param str `filename_from`:
            Name of the Markdown file.

        :param str `filename_to`:
            Name of the HTML file.

        :param str `css_url`:
            Optional, URL of a CSS file.

        :param bool `inline`:
            Optionally embed CSS inline into the HTML file.

        :returns:
            `True` if HTML file has been created, else `False`.
        """
        os.makedirs(
            os.path.dirname(os.path.abspath(os.path.expanduser(filename_to))),
            exist_ok=True,
        )

        fname_from = os.path.abspath(os.path.expanduser(filename_from))

        fname_to = os.path.abspath(os.path.expanduser(filename_to))
        fname_to_stem = pathlib.Path(fname_to).stem

        options = [
            # "--standalone",
            "--include-after-body",
            os.path.join(os.path.dirname(__file__), "css", "html-script.js"),
            '--metadata=pagetitle:"{stem}"'.format(stem=fname_to_stem),
        ]

        if css_url:
            options += [
                "--css",
                # os.path.abspath(os.path.expanduser(css_url)),
                css_url,
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
                fname_to,
                fname_from,
            ]
        )
        # print(' '.join(cmd))  # TODO DEVEL
        debug(cmd)
        process = subprocess.Popen(cmd)
        process.communicate()
        return process.returncode == 0
