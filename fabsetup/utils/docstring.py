"""Manipulate docstring."""


def lstripped_lines(text):
    """Return multiline string ``text`` each line stripped by four spaces if
    they exist.

    Example:

        >>> s = '# task\\n\\n    docstring\\n     some'
        >>> print(s)
        # task
        <BLANKLINE>
            docstring
             some
        >>> t = lstripped_lines(s)
        >>> t
        '# task\\n\\ndocstring\\n some'
        >>> print(t)
        # task
        <BLANKLINE>
        docstring
         some

    """
    # return "\n".join(
    #     [line[4:] if line.startswith(" " * 4) else line for line in text.split("\n")]
    # )
    lines = []
    indent = 4
    multiplier = 0
    for line in text.split("\n"):
        if not multiplier:
            rest = line
            while rest.startswith(" " * indent):
                rest = rest[indent:]
                multiplier = (multiplier or 0) + 1
        lines.append(line[indent * multiplier :])
    return "\n".join(lines)
