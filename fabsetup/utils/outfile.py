"""While preserving output handles write stdout and stderr to outfile."""

import fileinput
import os
import os.path
import re
import sys

import fabsetup.utils.colors


# Adapted from:
# * https://www.tentech.ca/2011/05/stream-tee-in-python-saving-stdout-to-file-while-keeping-the-console-alive/
# * https://gist.github.com/anandkunal/327585
# * https://softwareadept.xyz/2020/07/getattr-vs-__getattr__-vs-__getattribute__/
class stream_tee:
    """Tee `stream1` to `stream2`.

    Basically, stream_tee returns a wrapper of ``stream1`` which hooks in every
    method call for a method of ``stream1`` to be called on ``stream2``, too.

    :param typing.TextIO stream1:
        First filehandle.

    :param typing.TextIO stream2:
        Second filehandle.

    :param fabsetup.utils.colors.color-function stream1_color:
        Optionally set a color for stream1.

    :param str stream2_line_prefix:
        Optionally set line prefix for stream2 which will be prepended to each
        line written.

    :param list<str> stream2_no_prefix_lines:
        Optionally define lines which woud not prepended by a prefix when
        written.

    :returns:
        `stream1` wrapper which applies the tee feature.

    Examples:

        >>> # Prepare
        >>> import sys
        >>> import tempfile
        >>> stdout_orig = sys.stdout

        >>> # First Example
        >>> outfile_handle = tempfile.TemporaryFile()
        >>> sys.stdout = stream_tee(sys.stdout, outfile_handle)
        >>> # output would be written to stdout and outfile

        >>> # Reset
        >>> sys.stdout = stdout_orig

        >>> # Second Example
        >>> sys.stdout = stream_tee(sys.stdout, sys.stdout)
        >>> print("out")
        outout
        <BLANKLINE>

    """

    def __init__(self, stream1, stream2, **kwargs):
        self.stream1 = stream1
        self.stream2 = stream2
        self.__missing_method_name = None

        self.stream1_color = kwargs.get("stream1_color", None)

        self.stream2_line_prefix = kwargs.get("stream2_line_prefix", None)
        self.stream2_no_prefix_lines = kwargs.get("stream2_no_prefix_lines", [],) + [
            ""
        ]  # put no prefix on empty strings without newline at the end
        self.add_prefix = False

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    def __getattr__(self, name):
        self.__missing_method_name = name
        return getattr(self, "__methodmissing__")

    def __methodmissing__(self, *args, **kwargs):

        # hook into callable2

        callable2 = getattr(self.stream2, self.__missing_method_name)
        prefix = self.stream2_line_prefix
        if self.add_prefix and self.__missing_method_name == "write" and prefix:
            callable2(
                "".join(
                    "{}{}\n".format(prefix, line)
                    for line in args[0].split("\n")
                    if line not in self.stream2_no_prefix_lines
                ),
                *args[1:],
                **kwargs,
            )
        else:
            callable2(*args, **kwargs)

        # apply method to callable1

        callable1 = getattr(self.stream1, self.__missing_method_name)
        if self.stream1_color and self.__missing_method_name == "write":
            return callable1(
                self.stream1_color(args[0]),
                *args[1:],
                **kwargs,
            )
        return callable1(*args, **kwargs)


# Adapted from this discussion on how to create a singleton in Python:
# https://stackoverflow.com/q/6760685
class Singleton(type):
    """Singleton metaclass."""

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


class Tee(metaclass=Singleton):
    """Single instance class in order to write both, stdout and stderr into a
    file and also to keep stdout and stderr output active.

    Uses `fabsetup.outfile.Singleton` as metaclass.
    """

    def __init__(self):
        """foo bar baz"""

        self.default_stdout = None
        self.default_stderr = None

        self.outfile_handle = None

        self.outfile_name = None
        self.prefix = None

        self.outfile_stdout_line_prefix = None
        self.outfile_stdout_no_prefix_lines = []
        self.outfile_stderr_line_prefix = None

    def set_outfile(self, filename, prefix=""):
        """Define the outfile where stdout and stderr will be written to.

        Recursively create parent dirs of ``filename`` if they not exist.

        If the outfile already exists it will be overwritten.

        :param str `filename`:

        :param str `prefix`:
            Optionally write `prefix` to outfile at first.
        """
        self.outfile_name = filename
        self.prefix = prefix

        os.makedirs(
            os.path.dirname(os.path.abspath(os.path.expanduser(filename))),
            exist_ok=True,
        )

    def _start(self, append=False):

        mode = "a" if append else "w"

        if self.outfile_name:

            self.default_stdout = sys.stdout
            self.default_stderr = sys.stderr

            self.outfile_handle = open(self.outfile_name, mode)

            sys.stdout = stream_tee(
                sys.stdout,
                self.outfile_handle,
                # stream2_line_prefix="(stdout) ",
            )
            # TODO: configurable errstream color
            sys.stderr = stream_tee(
                sys.stderr,
                self.outfile_handle,
                stream1_color=fabsetup.utils.colors.red,
                # stream2_line_prefix="(STDERR) ",
            )

    def start(self):
        """Set up stdout, stderr and outfile handles and if given write prefix
        to outfile.

        Uses `fabsetup.utils.outfile.stream_tee()`.
        """
        self._start()

        if self.prefix:

            self.outfile_handle.write(self.prefix)
            self.prefix = None

    def stop(self):
        """Reset stdout and stderr to previous handles and close outfile handle."""
        if self.outfile_handle:

            self.outfile_handle.close()

            sys.stdout = self.default_stdout
            sys.stderr = self.default_stderr

    def pause(self):
        """Alias for `stop()`"""
        self.stop()

    def resume(self, missed_output=""):
        """Set up like in `start()` but append to outfile.

        Optionally write `missed_output` to outfile.

        :param str `missed_output`:
        """
        self._start(append=True)
        if missed_output:
            self.outfile_handle.write(missed_output)


# regex source: https://stackoverflow.com/a/15780675
def remove_color_codes(filename):
    """Remove ANSI color codes from a file inplace.

    :param str `filename`:
    """
    with fileinput.input(filename, inplace=True) as text:
        for line in text:
            print(
                re.sub(
                    r"\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?", "", line
                ),
                end="",
            )
