import fabsetup.utils.decorate


def test_invoked():

    # some dummy args and kwargs
    args = ["argv0", "argv1"]
    kwargs = {"kwarg1": 1, "kwarg2": 2}

    # not args or kwargs
    assert fabsetup.utils.decorate.invoked(None, None) is True
    assert fabsetup.utils.decorate.invoked(None, kwargs) is True
    assert fabsetup.utils.decorate.invoked(args, kwargs) is True

    # args and not kwargs (in this case args[0] is the decorated function)
    assert fabsetup.utils.decorate.invoked(args, None) is False
