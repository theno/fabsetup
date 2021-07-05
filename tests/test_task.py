import collections
import getpass
import importlib
import os
import socket
import sys

import fabric.main
import invoke.main

import fabsetup.__main__
import fabsetup.task
import fabsetup.utils.colors

from tests.test_utils_decorators import MockContext


# cf. https://stackoverflow.com/q/4984647
class AttributeDict(dict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


def test_issue_16_workaround(monkeypatch):

    context = MockContext()
    monkeypatch.setitem(os.environ, "SSH_AUTH_SOCK", "my-ssh-agent")
    fabsetup.task.issue_16_workaround(context)
    assert context.config["run"]["env"]["SSH_AUTH_SOCK"] == "my-ssh-agent"

    context = MockContext()
    monkeypatch.delitem(os.environ, "SSH_AUTH_SOCK")
    fabsetup.task.issue_16_workaround(context)
    assert "SSH_AUTH_SOCK" not in context.config["run"]["env"]


def create_mocked_run_method(return_code):
    def mocked_run_method(cmd, **kwargs):
        """mocked run method"""

        if not kwargs.get("hide", False):
            print("foo")

        Result = collections.namedtuple(typename="Result", field_names=["return_code"])
        return Result(return_code)

    return mocked_run_method


MarkdownTest = collections.namedtuple(
    typename="MarkdownTest",
    field_names=[
        "remote",
        "kwargs",
        "return_code",
        "expected_output",
    ],
)


markdown_tests = [
    MarkdownTest(
        remote=True,
        kwargs={},
        return_code=0,
        expected_output="\n```sh\nusername@hostname> "
        "\033[1;33mecho foo\033[0m\nfoo\n```\n",
    ),
    MarkdownTest(
        remote=False,
        kwargs={
            "format_kwargs": {
                "user": "USER",
                "host": "HOST",
            },
        },
        return_code=12,
        expected_output="\n```sh\nUSER@HOST> "
        "\033[1;32mecho foo\033[0m\nfoo\n[12]\n```\n",
    ),
    MarkdownTest(
        remote=True,
        kwargs={
            "prefix_formatter": "```{language}\n",
            "local_cmd_formatter": "LOCAL{prompt_end}{cmd}",
            "remote_cmd_formatter": "REMOTE{prompt_end}{cmd}",
            "return_code_formatter": ">> {return_code} <<\n",
            "postfix_formatter": "```\n\n----\n",
            "format_kwargs": {
                "language": "sh",
                "prompt_end": "$ ",
            },
        },
        return_code=0,
        expected_output="```sh\nREMOTE$ \033[1;33mecho foo\033[0m\nfoo\n"
        "```\n\n----\n",
    ),
    MarkdownTest(
        remote=False,
        kwargs={
            "prefix_formatter": "```{language}\n",
            "local_cmd_formatter": "LOCAL{prompt_end}{cmd}",
            "remote_cmd_formatter": "REMOTE{prompt_end}{cmd}",
            "return_code_formatter": ">> {return_code} <<\n",
            "postfix_formatter": "```\n\n----\n",
            "format_kwargs": {
                "language": "bash",
                "prompt_end": "$ ",
            },
        },
        return_code=123,
        expected_output="```bash\nLOCAL$ \033[1;32mecho foo\033[0m\nfoo\n"
        ">> 123 <<\n```\n\n----\n",
    ),
]


def test_wrapped_run_method(capsys):

    context = MockContext()

    for test in markdown_tests:
        run = fabsetup.task.wrapped_run_method(
            context,
            create_mocked_run_method(test.return_code),
            remote=test.remote,
            **test.kwargs
        )
        run("echo foo")
        captured = capsys.readouterr()
        assert captured.out == test.expected_output

    # test workaround:
    # attribute wrapped_with_cmd_in_markdown_codeblock

    test = MarkdownTest(
        remote=True,
        kwargs={},
        return_code=0,
        expected_output="\n```sh\nusername@hostname> "
        "\033[1;33mecho foo\033[0m\nfoo\n```\n",
    )

    mocked_run = create_mocked_run_method(test.return_code)

    assert hasattr(mocked_run, "wrapped_with_cmd_in_markdown_codeblock") is False

    run1 = fabsetup.task.wrapped_run_method(
        context, mocked_run, remote=test.remote, **test.kwargs
    )

    assert hasattr(run1, "wrapped_with_cmd_in_markdown_codeblock") is True
    assert run1.wrapped_with_cmd_in_markdown_codeblock is True

    run2 = fabsetup.task.wrapped_run_method(
        context, run1, remote=test.remote, **test.kwargs
    )

    assert hasattr(run2, "wrapped_with_cmd_in_markdown_codeblock") is True
    assert run2.wrapped_with_cmd_in_markdown_codeblock is True

    assert id(create_mocked_run_method) != id(run1)
    assert id(run1) == id(run2)

    # test hide output

    run3 = fabsetup.task.wrapped_run_method(
        context,
        create_mocked_run_method(0),
        remote=True,
    )
    run3("echo foo", hide=True)

    captured = capsys.readouterr()

    assert captured.out == ""


def test_cmd_in_markdown_codeblock(capsys):

    context = MockContext()

    for test in markdown_tests:
        wrapped_run = fabsetup.task.wrapped_run_method(
            context,
            create_mocked_run_method(test.return_code),
            remote=test.remote,
        )
        wrapped_run("echo foo", **test.kwargs)
        captured = capsys.readouterr()
        assert captured.out == test.expected_output


def test_cmd_in_markdown_codeblock_wraps():

    context = MockContext()

    run = create_mocked_run_method(return_code=0)

    wrapped_run = fabsetup.task.wrapped_run_method(
        context,
        run,
        remote=True,
    )

    assert run.__name__ == wrapped_run.__name__
    assert run.__doc__ == wrapped_run.__doc__


def test_cmd_in_markdown_codeblock_getuser(capsys, monkeypatch):
    """test getpass.getuser(), socket.gethostname(),
    user = c.user, host = c.host
    """

    monkeypatch.setattr(getpass, "getuser", lambda: "getpass-getuser")
    monkeypatch.setattr(socket, "gethostname", lambda: "socket-gethostname")

    context = MockContext(user="c-user", host="c-host")

    tests = [
        MarkdownTest(
            remote=False,
            kwargs={},
            return_code=0,
            expected_output="\n```sh\ngetpass-getuser@socket-gethostname> "
            "\033[1;32mecho foo\033[0m\nfoo\n```\n",
        ),
        MarkdownTest(
            remote=False,
            kwargs={
                "format_kwargs": {
                    "user": "USER",
                    "host": "HOST",
                },
            },
            return_code=12,
            expected_output="\n```sh\nUSER@HOST> "
            "\033[1;32mecho foo\033[0m\nfoo\n[12]\n```\n",
        ),
        MarkdownTest(
            remote=True,
            kwargs={},
            return_code=0,
            expected_output="\n```sh\nc-user@c-host> "
            "\033[1;33mecho foo\033[0m\nfoo\n```\n",
        ),
    ]

    for test in tests:
        wrapped_run = fabsetup.task.wrapped_run_method(
            context,
            create_mocked_run_method(test.return_code),
            remote=test.remote,
        )
        wrapped_run("echo foo", **test.kwargs)
        captured = capsys.readouterr()
        assert captured.out == test.expected_output


TaskTest = collections.namedtuple(
    typename="Test",
    field_names=[
        "invoked_str",  # defines task kwargs
        "expected_output_formatter",
    ],
)


def create_fabfile_and_invokefile(tmpdir, invoked_str):

    fabfile = tmpdir.join("fabfile.py")
    invfile = tmpdir.join("tasks.py")

    code_formatter = '''\
from fabsetup.task import task

@task{invoked_str}
def mytask(c):
    """docstring of mytask"""
    c.run('echo "c.run()"')
    c.local('echo "c.local()"')
'''

    code = code_formatter.format(
        # run_method_name=run_method_name,
        invoked_str=invoked_str,
    )

    fabfile.write(code)
    invfile.write(code)


def run_test_task(test, capsys, monkeypatch, tmpdir):
    """Based on ``test`` data create task with remote and local command and
    execute it with fabsetup, fabric, and invoke.
    """
    # TODO DEBUG
    # tmpd = tmpdir.mkdir('task{}'.format(test.invoked_str))
    tmpd = tmpdir

    # create_fabfile_and_invokefile(tmpd, run_method_name, test.kwargs)
    create_fabfile_and_invokefile(tmpd, test.invoked_str)
    tmppath = str(tmpd)

    # TODO DEBUG
    # print(tmppath)
    captured = capsys.readouterr()

    username = getpass.getuser()
    hostname = socket.gethostname()

    user_host = "%s@%s" % (username, hostname)
    user_localhost = "%s@%s" % (username, "localhost")

    run_prompt = "%s> " % user_host
    local_prompt = "%s> " % user_localhost

    for argv, start_func, format_kwargs in [
        (
            [
                "fabsetup",
            ],
            fabsetup.__main__.main,
            {
                "run_prompt": "",
                "run_color": "32",
                "local_prompt": "",
            },
        ),
        (
            [
                "fabsetup",
                "--hosts",
                user_localhost,
            ],
            fabsetup.__main__.main,
            {
                "run_prompt": local_prompt,
                "run_color": "33",
                "local_prompt": run_prompt,
            },
        ),
        (
            [
                "fab",
            ],
            fabric.main.program.run,
            {
                "run_prompt": "",
                "run_color": "32",
                "local_prompt": "",
            },
        ),
        (
            [
                "fab",
                "--hosts",
                user_localhost,
            ],
            fabric.main.program.run,
            {
                "run_prompt": local_prompt,
                "run_color": "33",
                "local_prompt": run_prompt,
            },
        ),
        (
            [
                "invoke",
            ],
            invoke.main.program.run,
            {
                "run_prompt": "",
                "run_color": "32",
                "local_prompt": "",
            },
        ),
    ]:
        start_func_args = []

        if argv[0] == "fabsetup":

            sys.path.insert(0, tmppath)

            fabfile = importlib.import_module("fabfile")
            reloaded_fabfile = importlib.reload(fabfile)
            namespace = invoke.Collection.from_module(reloaded_fabfile)
            start_func_args.append(namespace)

            monkeypatch.setattr(
                sys,
                "argv",
                argv
                + [
                    "--unnumbered",
                    "mytask",
                ],
            )

        else:
            monkeypatch.setattr(
                sys,
                "argv",
                argv
                + [
                    "--search-root",
                    tmppath,
                    "mytask",
                ],
            )

        start_func(*start_func_args)

        captured = capsys.readouterr()

        if argv[0] == "fabsetup":
            sys.path.pop(0)

        # print(captured.out)
        assert captured.out == test.expected_output_formatter.format(**format_kwargs)


def test_task_no_args(capsys, monkeypatch, tmpdir):
    """Decorate ``mytask`` non-invoked: ``@task``"""
    task_test = TaskTest(
        invoked_str="",
        expected_output_formatter="""\
\033[35m
# mytask
\033[0m
\033[34mdocstring of mytask
\033[0m

```sh
{run_prompt}\033[1;{run_color}mecho "c.run()"\033[0m
c.run()
```

```sh
{local_prompt}\033[1;32mecho "c.local()"\033[0m
c.local()
```
""",
    )

    run_test_task(task_test, capsys, monkeypatch, tmpdir)


# def test_task_docfalse(capsys, monkeypatch, tmpdir):
#     '''Decorate ``mytask`` invoked, suppress docstring output'''
#     task_test = TaskTest(
#         invoked_str='(doc=False)',
#         expected_output_formatter='''\
# \033[35m
# # mytask
# \033[0m
#
# ```
# {run_prompt}\033[1;{run_color}mecho "c.run()"\033[0m
# c.run()
# ```
#
# ```
# {local_prompt}\033[1;32mecho "c.local()"\033[0m
# c.local()
# ```
# ''')
#
#     run_test_task(task_test, capsys, monkeypatch, tmpdir)


def test_task_invoked(capsys, monkeypatch, tmpdir):
    """Decorate ``mytask`` invoked with formatter kwargs, suppress docstring
    output
    """
    task_test = TaskTest(
        invoked_str="("
        "name_='My Task', "
        "doc=False, "
        "prefix_formatter='\\n```{language}"
        "\\n# execute\\n', "
        "local_cmd_formatter='{prompt_end}{cmd}', "
        "remote_cmd_formatter='{prompt_end}{cmd}', "
        "return_code_formatter='# return code: {return_code}', "
        "postfix_formatter='```\\n\\n', "
        "format_kwargs={'language': 'sh', 'prompt_end': '$ '}, "
        ")",
        expected_output_formatter="""\
\033[35m
# My Task
\033[0m

```sh
# execute
$ \033[1;{run_color}mecho "c.run()"\033[0m
c.run()
```


```sh
# execute
$ \033[1;32mecho "c.local()"\033[0m
c.local()
```

""",
    )

    run_test_task(task_test, capsys, monkeypatch, tmpdir)


def mysubtask(c):
    """This is my subtask"""
    print("some output")


def test_subtask(capsys):

    # mysubtask() is a subtask, so we are at task_depth 2
    c = MockContext()
    # c.config.output["task_depth"] = 2
    fabsetup.task.get_task_depth(c, default=2)

    captured = capsys.readouterr()

    output_with_defaults = """\
\033[36m
## mysubtask
\033[0m
\033[34mThis is my subtask
\033[0m
some output
"""

    # decorate non-called (without parenthesis)
    decorated = fabsetup.task.subtask(mysubtask)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == output_with_defaults

    # decorate called (without parenthesis)
    decorated = fabsetup.task.subtask()(mysubtask)
    decorated(c)
    captured = capsys.readouterr()
    assert captured.out == output_with_defaults

    # default: depth = kwargs.get('depth', None)
    decorated = fabsetup.task.subtask(depth=5)(mysubtask)
    decorated(c)
    c.config.output["task_depth"] = 2  # "reset" task depth
    captured = capsys.readouterr()
    assert (
        captured.out
        == """\
\033[36m
##### mysubtask
\033[0m
\033[34mThis is my subtask
\033[0m
some output
"""
    )

    # default: prefix = kwargs.get('prefix', '\n' + '#' * depth + ' ')
    decorated = fabsetup.task.subtask(prefix="\n\n# ")(mysubtask)
    decorated(c)
    captured = capsys.readouterr()
    assert (
        captured.out
        == """\
\033[36m

# mysubtask
\033[0m
\033[34mThis is my subtask
\033[0m
some output
"""
    )

    # default: tail = kwargs.get('tail', '\n')
    decorated = fabsetup.task.subtask(tail="\n\n")(mysubtask)
    decorated(c)
    captured = capsys.readouterr()
    assert (
        captured.out
        == """\
\033[36m
## mysubtask

\033[0m
\033[34mThis is my subtask
\033[0m
some output
"""
    )

    # default: doc = kwargs.get('doc', True)
    decorated = fabsetup.task.subtask(doc=False)(mysubtask)
    decorated(c)
    captured = capsys.readouterr()
    assert (
        captured.out
        == """\
\033[36m
## mysubtask
\033[0m
some output
"""
    )

    # default: color = kwargs.get('color', cyan)
    decorated = fabsetup.task.subtask(color=fabsetup.utils.colors.blue)(mysubtask)
    decorated(c)
    captured = capsys.readouterr()
    assert (
        captured.out
        == """\
\033[34m
## mysubtask
\033[0m
\033[34mThis is my subtask
\033[0m
some output
"""
    )

    # default: name = kwargs.get('name', None)
    decorated = fabsetup.task.subtask(name="The Subtask")(mysubtask)
    decorated(c)
    captured = capsys.readouterr()
    assert (
        captured.out
        == """\
\033[36m
## The Subtask
\033[0m
\033[34mThis is my subtask
\033[0m
some output
"""
    )

    # all kwargs together
    # depth = kwargs.get('depth', 2)
    # prefix = kwargs.get('prefix', '\n' + '#' * depth + ' ')
    # tail = kwargs.get('tail', '\n')
    # doc = kwargs.get('doc', True)
    # color = kwargs.get('color', cyan)
    # name = kwargs.get('name', None)
    decorated = fabsetup.task.subtask(
        depth=4,  # useless because kwarg prefix also is set
        prefix="Prefix",
        tail="Tail",
        doc=False,
        color=fabsetup.utils.colors.red,
        name="Name",
    )(mysubtask)
    decorated(c)
    captured = capsys.readouterr()
    assert (
        captured.out
        == """\
\033[31mPrefixNameTail\033[0m
some output
"""
    )


# def mysubsubtask():
#     """This is my subsubtask"""
#     print("another output")
#
#
# def test_subsubtask(capsys):
#
#     captured = capsys.readouterr()
#
#     output_with_defaults = """\
#
# ### mysubsubtask
#
# \033[34mThis is my subsubtask
# \033[0m
# another output
# """
#
#     # decorate non-called (without parenthesis)
#     decorated = fabsetup.task.subsubtask(mysubsubtask)
#     decorated()
#     captured = capsys.readouterr()
#     assert captured.out == output_with_defaults
#
#     # decorate called (without parenthesis)
#     decorated = fabsetup.task.subsubtask()(mysubsubtask)
#     decorated()
#     captured = capsys.readouterr()
#     assert captured.out == output_with_defaults
#
#     # `prefix` option
#     # default: prefix = kwargs.get('prefix', '\n' + '#' * depth + ' ')
#     decorated = fabsetup.task.subsubtask(prefix="\n\n# ")(mysubsubtask)
#     decorated()
#     captured = capsys.readouterr()
#     assert (
#         captured.out
#         == """\
#
#
# # mysubsubtask
#
# \033[34mThis is my subsubtask
# \033[0m
# another output
# """
#     )
#
#     # `tail` option
#     # default: tail = kwargs.get('tail', '\n')
#     decorated = fabsetup.task.subsubtask(tail="\n\n")(mysubsubtask)
#     decorated()
#     captured = capsys.readouterr()
#     assert (
#         captured.out
#         == """\
#
# ### mysubsubtask
#
#
# \033[34mThis is my subsubtask
# \033[0m
# another output
# """
#     )
#
#     # `doc` option
#     # default: doc = kwargs.get('doc', True)
#     decorated = fabsetup.task.subsubtask(doc=False)(mysubsubtask)
#     decorated()
#     captured = capsys.readouterr()
#     assert (
#         captured.out
#         == """\
#
# ### mysubsubtask
#
# another output
# """
#     )
#
#     # `color` option
#     # default: color = kwargs.get('color', cyan)
#     decorated = fabsetup.task.subsubtask(color=fabsetup.utils.colors.blue)(mysubsubtask)
#     decorated()
#     captured = capsys.readouterr()
#     assert (
#         captured.out
#         == """\
# \033[34m
# ### mysubsubtask
# \033[0m
# \033[34mThis is my subsubtask
# \033[0m
# another output
# """
#     )
#
#     # `name` option
#     # default: name = kwargs.get('name', None)
#     decorated = fabsetup.task.subsubtask(name="The subsubtask")(mysubsubtask)
#     decorated()
#     captured = capsys.readouterr()
#     assert (
#         captured.out
#         == """\
#
# ### The subsubtask
#
# \033[34mThis is my subsubtask
# \033[0m
# another output
# """
#     )
#
#     # all kwargs together
#     # depth = kwargs.get('depth', 2)
#     # prefix = kwargs.get('prefix', '\n' + '#' * depth + ' ')
#     # tail = kwargs.get('tail', '\n')
#     # doc = kwargs.get('doc', True)
#     # color = kwargs.get('color', cyan)
#     # name = kwargs.get('name', None)
#     decorated = fabsetup.task.subsubtask(
#         depth=4,  # useless because kwarg prefix also is set
#         prefix="Prefix",
#         tail="Tail",
#         doc=False,
#         color=fabsetup.utils.colors.red,
#         name="Name",
#     )(mysubsubtask)
#     decorated()
#     captured = capsys.readouterr()
#     assert (
#         captured.out
#         == """\
# \033[31mPrefixNameTail\033[0m
# another output
# """
#     )


# import pytest

# with pytest.raises(TypeError) as excinfo:
#     decorated()
# trace_msg = "got multiple values for keyword argument 'depth'"
# assert trace_msg in str(excinfo.value)
