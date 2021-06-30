"""While preserving output handles write stdout and stderr to outfile."""

import fileinput
import os
import os.path
import re
import sys


# Adapted from:
# * https://www.tentech.ca/2011/05/stream-tee-in-python-saving-stdout-to-file-while-keeping-the-console-alive/
# * https://gist.github.com/anandkunal/327585
# * https://softwareadept.xyz/2020/07/getattr-vs-__getattr__-vs-__getattribute__/
class stream_tee:
    """Tee `stream1` to `stream2`.

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

    def __init__(self, stream1, stream2):
        self.stream1 = stream1
        self.stream2 = stream2
        self.__missing_method_name = None

    def __getattribute__(self, name):
        return object.__getattribute__(self, name)

    def __getattr__(self, name):
        self.__missing_method_name = name
        return getattr(self, "__methodmissing__")

    def __methodmissing__(self, *args, **kwargs):
        callable2 = getattr(self.stream2, self.__missing_method_name)
        callable2(*args, **kwargs)

        callable1 = getattr(self.stream1, self.__missing_method_name)
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

            sys.stdout = stream_tee(sys.stdout, self.outfile_handle)
            sys.stderr = stream_tee(sys.stderr, self.outfile_handle)

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
