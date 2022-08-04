"""Function decorators."""

# import inspect  # TODO DEBUG
import sys
from functools import wraps

import invoke.context

from fabsetup.utils.colors import blue, red, no_color, config_color
from fabsetup.utils.docstring import lstripped_lines
from fabsetup.utils.decorate import invoked
from fabsetup.print import print_heading, print_docstring


# for decorator with arguments see: http://stackoverflow.com/a/5929165
def print_doc(*args, **kwargs):
    '''Print the docstring of the decorated function.

    May be invoked as a simple, argument-less decorator (i.e. ``print_doc``)
    or with named arguments ``color``, ``bold``, ``prefix``, or ``tail``
    (eg. ``print_doc(color=utils.red, bold=True, prefix=' ')``).

    :param color:
        Optionally define another color, default is color is
        ``utils.colors.blue``.

    :param bool bold:
        Optionally print docstring in bold letters, default is ``False``.

    :param str prefix:
        Optionally set a prefix, default is '' (empty string).

    :param str tail:
        Optionally set a tail, default is '\\n'.

    Examples:

        >>> # a context/connection is required
        >>> import invoke.context
        >>> c = invoke.context.Context()

        >>> # argument-less
        >>> @print_doc
        ... def func(c):
        ...     """docstring of func"""
        ...     pass
        >>>
        >>> func(c)
        \033[34mdocstring of func
        \033[0m

        >>> # with named arguments
        >>> @print_doc(color=no_color, tail='\\n\\nNote! foobar')
        ... def func(c):
        ...     """docstring of func"""
        ...     pass
        >>>
        >>> func(c)
        docstring of func
        <BLANKLINE>
        Note! foobar

    '''
    # output settings from kwargs or take defaults
    color = kwargs.get("color", None)
    bold = kwargs.get("bold", False)
    prefix = kwargs.get("prefix", "")
    tail = kwargs.get("tail", "\n")

    def real_decorator(func):
        """real decorator function"""

        @wraps(func)
        def wrapper(c, *args, **kwargs):
            """the wrapper function"""

            c_or_self = c
            if not isinstance(c, invoke.context.Context):
                # method-type subtask
                # cf. https://github.com/pyinvoke/invoke/issues/347
                c = c_or_self.c

            col = color or config_color(
                c.config, ["output", "color", "docstring"], blue
            )
            err_col = color or config_color(c.config, ["output", "color", "error"], red)
            try:
                # prgf = first_paragraph(func.__doc__)
                prgf = lstripped_lines(func.__doc__)
                print_docstring(col(prefix + prgf + tail, bold))
            except AttributeError as exc:
                msg = err_col("\n\n{}() has no docstring".format(func.__name__))
                raise type(exc)(str(exc) + msg).with_traceback(sys.exc_info()[2])

            return func(c_or_self, *args, **kwargs)

        # wrapper.__signature__ = inspect.signature(func)  # TODO DEBUG

        return wrapper

    if invoked(args, kwargs):
        return real_decorator  # when decorated as `@print_doc(...)`
    return real_decorator(func=args[0])  # when decorated as `@print_doc`


def print_full_name(*args, **kwargs):
    """Print the full name of the decorated function.

    May be invoked as a simple, argument-less decorator (i.e.
    ``print_full_name``) or with named arguments ``color``, ``bold``,
    ``prefix``, or ``tail`` (eg.
    ``print_full_name(color=utils.red, bold=True, prefix='')``).

    :param color:
        Optionally define another color, default is color is ``no_color``.

    :param bool bold:
        Optionally print docstring in bold letters, default is ``False``.

    :param str prefix:
        Optionally set a prefix, default is '' (empty string).

    :param str tail:
        Optionally set a tail, default is '\\\\n'.

    :param str name:
        Optionally set for another function name.

    :param [int] numbered:
        Optionally set a numeration identifier

    Examples:

        >>> # a context/connection is required
        >>> import invoke.context
        >>> c = invoke.context.Context()

        >>> # argument-less
        >>> @print_full_name
        ... def func(c):
        ...     pass
        >>>
        >>> func(c)
        func

        >>> # with named arguments
        >>> @print_full_name(color=red, prefix='# ', tail=' mytail')
        ... def func(c):
        ...     pass
        >>>
        >>> func(c)
        \033[31m# func mytail\033[0m

    """
    color = kwargs.get("color", None)
    bold = kwargs.get("bold", False)
    prefix = kwargs.get("prefix", "")
    tail = kwargs.get("tail", "")
    # doc_tail = kwargs.get('doc_tail', '')
    name = kwargs.get("name", None)
    # numbered = kwargs.get("numbered", None)
    numbered = kwargs.get("numbered", [9, 9, 9, 9])  # TODO DEVEL

    def real_decorator(func):
        """real decorator function"""

        @wraps(func)
        def wrapper(c, *args, **kwargs):
            """the wrapper function"""

            c_or_self = c
            if not isinstance(c, invoke.context.Context):
                # method-type subtask
                # cf. https://github.com/pyinvoke/invoke/issues/347
                c = c_or_self.c

            col = color or config_color(
                c.config, ["output", "color", "full_name"], no_color
            )

            # first_line = ''
            # try:
            #     first_line = func.__module__ + '.' + func.__qualname__
            # except AttributeError as exc:
            #     first_line = func.__name__

            # first_line = func.__module__ + '.' + func.__qualname__
            first_line = name
            if name is None:
                # first_line = \
                #     func.__module__.replace('fabsetup_', '').split('_')[0] \
                #     + '.' + func.__qualname__
                first_line = func.__qualname__

            # if numbered and c.config.output.numbered:
            if (
                numbered
                and c.config.get("output")
                and c.config["output"].get("numbered")
            ):
                first_line = "{} {}".format(numbered, first_line)

            print_heading(col(prefix + first_line + tail, bold))

            return func(c_or_self, *args, **kwargs)

        # wrapper.__signature__ = inspect.signature(func)   # TODO DEBUG

        return wrapper

    if invoked(args, kwargs):
        return real_decorator  # when decorated as `@print_full_name(...)`
    return real_decorator(func=args[0])  # when decorated as `@print_full_name`
