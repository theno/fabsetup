"""Function decorator helper."""


def invoked(args, kwargs):
    """Return True if `args` is None or if `kwargs` is not None.

    This means if a decorator which calls `invoked()` decorates a function
    invoked, i.e. with braces containing zero or more `kwargs`, `invoked()`
    returns True.  And returns False, if the decorator decorates a function
    non-invoked, i.e. without braces.

    Examples:

        >>> import json  # print dict `kwargs` in order

        >>> def decorator(*args, **kwargs):
        ...
        ...     def inner(func):
        ...         print('inner')
        ...         return func
        ...
        ...     if invoked(args, kwargs):
        ...         print('invoked',
        ...               args,
        ...               json.dumps(kwargs, sort_keys=True))
        ...         return inner
        ...
        ...     print('not invoked')
        ...     return inner(func=args[0])

        >>> # non-invoked decorator
        >>>
        >>> @decorator
        ... def foo():
        ...     pass
        not invoked
        inner

        >>> # "manually" apply non-invoked decorator
        >>>
        >>> def foo():
        ...     pass
        ...
        >>> foo = decorator(foo)
        not invoked
        inner

        >>> # invoke decorator without kwargs
        >>>
        >>> @decorator()
        ... def foo():
        ...     pass
        invoked () {}
        inner

        >>> # invoke decorator with kwargs
        >>>
        >>> @decorator(a=1, b=2)
        ... def foo():
        ...     pass
        invoked () {"a": 1, "b": 2}
        inner

        >>> # "manually" apply decorator with kwargs
        >>>
        >>> def foo(args, kwargs):
        ...     pass
        ...
        >>> tmp = decorator(0, a=1, b=2)
        invoked (0,) {"a": 1, "b": 2}
        >>> foo = tmp(foo)
        inner

        >>> # invoke decorator with args but without kwargs
        >>> # (not possible)
        >>>
        >>> @decorator(0, 1, 2)
        ... def foo():
        ...     pass
        Traceback (most recent call last):
            ...
        TypeError: 'int' object is not callable
    """
    return bool((not args) or kwargs)
