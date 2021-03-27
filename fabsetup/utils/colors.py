"""Wrap text with ANSI escape color sequences.

Code originally comes from `Fabric-1
<https://github.com/fabric/fabric/blob/1.10/fabric/colors.py>`_,
``default_color`` and ``no_color`` were added.

Examples:

.. code-block::

    .>> print(blue('foo'))
    \\033[34mfoo\\033[0m

    .>> print(red('bar', bold=True))
    \\033[1;31mbar\\033[0m

    .>> print(no_color('baz'))
    baz

`Color codes
<https://en.wikipedia.org/wiki/ANSI_escape_code#3-bit_and_4-bit>`_:

.. code-block::

    black:   30
    red:     31
    green:   32
    yellow:  33
    blue:    34
    magenta: 35
    cyan:    36
    white:   37

    default_color: 0
"""


def _wrap_with(color_code):
    """Color wrapper.

    Examples:

        >>> blue = _wrap_with('34')
        >>> print(blue('text'))
        \033[34mtext\033[0m

    Repeat examples of module docstring for doctest
    without escaped backslash:

        >>> print(blue('foo'))
        \033[34mfoo\033[0m

        >>> print(red('bar', bold=True))
        \033[1;31mbar\033[0m

        >>> print(no_color('baz'))
        baz

    """

    def inner(text, bold=False):

        if not ENABLED:
            return text

        code = color_code

        # no color hook
        if color_code is None:
            if bold:
                code = "0"  # set to default color
            else:
                return text

        if bold:
            code = "1;{code}".format(code=code)

        return "\033[{code}m{text}\033[0m".format(code=code, text=text)

    return inner


black = _wrap_with("30")
red = _wrap_with("31")
green = _wrap_with("32")
yellow = _wrap_with("33")
blue = _wrap_with("34")
magenta = _wrap_with("35")
cyan = _wrap_with("36")
white = _wrap_with("37")
default_color = _wrap_with("0")

no_color = _wrap_with(None)
"""By default, return text unchanged.

If ``bold`` is ``True``, return wrapped using default color code in bold style.
"""

ENABLED = True


def color_by_name(name):
    return {
        "black": black,
        "red": red,
        "green": green,
        "yellow": yellow,
        "blue": blue,
        "magenta": magenta,
        "cyan": cyan,
        "white": white,
        "default_color": default_color,
        "no_color": no_color,
    }.get(name, None)


def config_color(config, path, default):
    res = config
    for item in path:
        res = res.get(item, None)
        if not res:
            break
    if not res:
        return default
    return color_by_name(res)
