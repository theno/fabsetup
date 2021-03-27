import fileinput
import re
import sys


class stream_tee(object):
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


# singleton in python: https://stackoverflow.com/q/6760685
class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instance


class Tee(metaclass=Singleton):
    def __init__(self):

        self.default_stdout = None
        self.default_stderr = None

        self.outfile_handle = None

        self.outfile_name = None
        self.prefix = None

    def set_outfile(self, filename, prefix=""):

        self.outfile_name = filename
        self.prefix = prefix

    def _start(self, append=False):

        mode = "a" if append else "w"

        if self.outfile_name:

            self.default_stdout = sys.stdout
            self.default_stderr = sys.stderr

            self.outfile_handle = open(self.outfile_name, mode)

            sys.stdout = stream_tee(sys.stdout, self.outfile_handle)
            sys.stderr = stream_tee(sys.stderr, self.outfile_handle)

    def start(self):

        self._start()

        if self.prefix:

            self.outfile_handle.write(self.prefix)
            self.prefix = None

    def stop(self):

        if self.outfile_handle:

            self.outfile_handle.close()

            sys.stdout = self.default_stdout
            sys.stderr = self.default_stderr

    def pause(self):
        self.stop()

    def resume(self, missed_output=""):
        self._start(append=True)
        if missed_output:
            self.outfile_handle.write(missed_output)


# regex source: https://stackoverflow.com/a/15780675
def remove_color_codes(filename):
    with fileinput.input(filename, inplace=True) as text:
        for line in text:
            print(
                re.sub(
                    r"\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?", "", line
                ),
                end="",
            )
