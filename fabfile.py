# import inspect

from fabsetup.task import task, subtask


@subtask
def subtesttask(c):
    """My subtask.

    Another paragraph.
    """
    # c.run("echo hihi")
    c.run('echo -e "hihi\nhoho"')
    c.run("echo hoho 1>&2")
    c.run("head -n 10 fabfile.py")
    c.run("ls doesnotexist", warn=True)
    pass


@task
def testtask(c):
    """My fabric test task.

    Which tests things.
    """
    # print("harhar")
    # c.run("echo gnaulp")
    subtesttask(c)
    # print(subtest)
    # print(dir(subtest))
    # print(type(subtest))
    # print(isinstance(subtest, object))
    # print(subtest.__name__)
    # print(subtest.__qualname__)
    # print(subtest.__annotations__)
    # print(subtest.__dir__())
    # from pprint import pprint
    # pprint(subtest.__dict__['__wrapped__'].__dict__)
    # pprint(dir(subtest.__dict__['__wrapped__']))
    # pprint(subtest.__dict__['__wrapped__'].__name__)
    # pprint(subtest.__name__)
    # pprint(subtest.__kwdefaults__)
    # pprint(inspect.getsource(subtest))
    # pprint(inspect.getsourcelines(subtest))
    # pprint(inspect.getsourcelines(subtest)[0][0])

    # pprint(dir(inspect))
    # pprint(inspect.signature(subtest))
    # pprint(dir(inspect.signature(subtest)))
