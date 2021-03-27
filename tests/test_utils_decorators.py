import pytest

import fabsetup.utils.decorators
import fabsetup.utils.colors


# cf. https://stackoverflow.com/q/4984647
class AttributeDict(dict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


class MockContext:
    def __init__(self, user="username", host="hostname"):
        self.config = AttributeDict(
            {
                "run": {
                    "env": {},
                },
                "task_depth": 1,
            }
        )
        self.user = user
        self.host = host


# used by test_print_doc() and test_print_full_name()
def func(c):
    """func's docstring"""
    pass


def test_print_doc(capsys):
    c = MockContext()

    captured = capsys.readouterr()

    output_with_defaults = "\033[34mfunc's docstring\n\033[0m\n"

    # decorate non-called (without parenthesis)
    decorated = fabsetup.utils.decorators.print_doc(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == output_with_defaults

    # decorate called (with parenthesis)
    decorated = fabsetup.utils.decorators.print_doc()(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == output_with_defaults

    # `color` option
    # default: color = kwargs.get('color', blue)
    decorated = fabsetup.utils.decorators.print_doc(color=fabsetup.utils.colors.red)(
        func
    )
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == "\033[31mfunc's docstring\n\033[0m\n"

    # `bold` option
    # default: bold = kwargs.get('bold', False)
    decorated = fabsetup.utils.decorators.print_doc(bold=True)(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == "\033[1;34mfunc's docstring\n\033[0m\n"

    # `prefix` option
    # default: prefix = kwargs.get('prefix', '')
    decorated = fabsetup.utils.decorators.print_doc(prefix="PREFIX")(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == "\033[34mPREFIXfunc's docstring\n\033[0m\n"

    # `tail` option
    # default: tail = kwargs.get('tail', '\n')
    decorated = fabsetup.utils.decorators.print_doc(tail="TAIL")(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == "\033[34mfunc's docstringTAIL\033[0m\n"

    # all kwargs together
    # color = kwargs.get('color', blue)
    # bold = kwargs.get('bold', False)
    # prefix = kwargs.get('prefix', '')
    # tail = kwargs.get('tail', '\n')
    decorated = fabsetup.utils.decorators.print_doc(
        color=fabsetup.utils.colors.green,
        bold=True,
        prefix="PRE",
        tail="TAI",
    )(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == "\033[1;32mPREfunc's docstringTAI\033[0m\n"

    with pytest.raises(AttributeError) as excinfo:

        def func_without_docstring():
            pass

        decorated = fabsetup.utils.decorators.print_doc(func_without_docstring)
        decorated(c)

    assert str(excinfo.value).endswith(" has no docstring\033[0m")


def test_print_full_name(capsys):
    c = MockContext()

    captured = capsys.readouterr()

    output_with_defaults = "func\n"

    # decorate non-called (without parenthesis)
    decorated = fabsetup.utils.decorators.print_full_name(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == output_with_defaults

    # decorate called (with parenthesis)
    decorated = fabsetup.utils.decorators.print_full_name()(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == output_with_defaults

    # `color` option
    # default: color = kwargs.get('color', no_color)
    decorated = fabsetup.utils.decorators.print_full_name(
        color=fabsetup.utils.colors.blue
    )(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == "\033[34mfunc\033[0m\n"

    # `bold` option
    # default: bold = kwargs.get('bold', False)
    decorated = fabsetup.utils.decorators.print_full_name(bold=True)(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == "\033[1;0mfunc\033[0m\n"

    # `prefix` option
    # default: prefix = kwargs.get('prefix', '')
    decorated = fabsetup.utils.decorators.print_full_name(prefix="PREFIX")(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == "PREFIXfunc\n"

    # `tail` option
    # default: tail = kwargs.get('tail', '')
    decorated = fabsetup.utils.decorators.print_full_name(tail="TAIL")(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == "funcTAIL\n"

    # `name` option
    # default: name = kwargs.get('name', None)
    decorated = fabsetup.utils.decorators.print_full_name(name="NAME")(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == "NAME\n"

    # all kwargs together
    # color = kwargs.get('color', no_color)
    # bold = kwargs.get('bold', False)
    # prefix = kwargs.get('prefix', '')
    # tail = kwargs.get('tail', '')
    # name = kwargs.get('name', None)
    decorated = fabsetup.utils.decorators.print_full_name(
        color=fabsetup.utils.colors.green,
        bold=True,
        prefix="PRE",
        tail="TAI",
        name="NAM",
    )(func)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == "\033[1;32mPRENAMTAI\033[0m\n"
