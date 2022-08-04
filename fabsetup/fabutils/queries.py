"""User interaction."""

import readline
import sys

import fabsetup.print
import fabsetup.utils.outfile
from fabsetup.utils.colors import magenta, no_color


# adapted from: https://stackoverflow.com/a/2533142
def interactive(prompt, cmd_color, prefill=""):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        tee = fabsetup.utils.outfile.Tee()
        tee.pause()

        result = input(prompt)

        tee.resume(missed_output="{}{}\n".format(prompt, cmd_color(result, bold=True)))

        return result
    finally:
        readline.set_startup_hook()


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    :param question:
        A string that is presented to the user.

    :param default:
        The presumed answer if the user just hits <Enter>.  It must be 'yes'
        (the default), 'no', or `None` (which means an answer of the user is
        required).

    The 'answer' return value is `True` for 'yes' or `False` for 'no'.

    This function originally comes from http://stackoverflow.com/a/3041990
    and has been slightly changed.
    """
    valid = {
        "yes": True,
        "y": True,
        "ye": True,
        "1": True,
        "no": False,
        "n": False,
        "0": False,
    }
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        # sys.stdout.write(question + prompt)
        # choice = input().lower()
        choice = interactive(
            prompt=magenta("{}{}".format(question, prompt)),
            cmd_color=no_color,
            prefill="",
        )
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


# def query_input(question, default=None, color=default_color):
def query_input(question, default=None, color=magenta):
    """Ask a question for input via input() and return their answer.

    :param question:
        A string that is presented to the user.

    :param default:
        The presumed answer if the user just hits <Enter>.

    :param color:
        Optionally set a color, default is ``utils.colors.default_color``

    The 'answer' return value is a str.
    """
    # if default is None or default == "":
    #     prompt = " "
    # elif type(default) == str:
    #     prompt = " [{}] ".format(default)
    # else:
    #     raise ValueError("invalid default answer: '%s'" % default)
    prompt = ""

    while True:
        # sys.stdout.write(color(question + prompt))
        # choice = input()
        choice = interactive(
            prompt="{} ".format(color(question + prompt)),
            cmd_color=no_color,
            prefill=default,
        )
        # if default is not None and choice == "":
        #     return default
        if choice != "":
            return choice
