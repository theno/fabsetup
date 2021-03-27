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
    return "\n".join(
        [line[4:] if line.startswith(" " * 4) else line for line in text.split("\n")]
    )
