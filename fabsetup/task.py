import inspect
import getpass
import os
import socket
import sys
from functools import wraps

import fabric
import fabric.connection
import invoke.context
from invoke.util import debug

import fabsetup.fabutils.queries
from fabsetup.utils.decorators import print_doc, print_full_name
from fabsetup.utils.colors import yellow, green, cyan, magenta, config_color
from fabsetup.utils.decorate import invoked
from fabsetup.print import print_default, print_code_block
from fabsetup.print import print_command_line


def issue_16_workaround(context):
    """In a given ``context`` set the os ssh-agent socket filename if it
    exists.

    Workaround for `Fabric issue 16
    <https://github.com/fabric/patchwork/issues/16>`_ provided by `max-arnold
    <https://github.com/fabric/patchwork/issues/16#issuecomment-390384999>`_.

    :param invoke.context.Context context:
        The given context.

    Example:

        >>> # Note: issue_16_workaround() is applied in
        >>> #       fabsetup.task.task()
        >>> #       so this example uses fabric's task
        >>> from fabric import task
        >>> @task
        ... def mytask(c):
        ...     # c is of type `fabric.connection.Connection` which is
        ...     # derived from `invoke.context.Context`
        ...     issue_16_workaround(c)
        ...     c.run('uname -a')
    """  # noqa: E501
    ssh_agent = os.environ.get("SSH_AUTH_SOCK", None)
    if ssh_agent:
        context.config["run"]["env"]["SSH_AUTH_SOCK"] = ssh_agent


def issue_833_workaround():
    """Assign `inspect.getfullargspec` to `inspect.getargspec` if it not exists.

    Workaround for `Invoke issue 833
    <https://github.com/pyinvoke/invoke/issues/833>`_ provided by `ian-em
    <https://github.com/pyinvoke/invoke/issues/833#issuecomment-1293148106>`_.
    """
    import inspect

    if not hasattr(inspect, 'getargspec'):
            inspect.getargspec = inspect.getfullargspec


issue_833_workaround()


def from_config(config, path, default):
    res = config
    for item in path:
        res = res.get(item, None)
        if not res:
            break
    if not res:
        return default
    return res


def increment_numbered_state(c):

    c.config["output"] = c.config.get("output", {})
    c.config["output"]["numbered_state"] = c.config["output"].get("numbered_state", "0")

    copy = [int(i) for i in c.config["output"]["numbered_state"].split(".")]
    copy[-1] += 1
    c.config["output"]["numbered_state"] = ".".join([str(i) for i in copy])
    return c.config["output"]["numbered_state"]


def append_numbered_index(c):
    copy = [int(i) for i in c.config["output"]["numbered_state"].split(".")]
    copy.append(0)
    c.config["output"]["numbered_state"] = ".".join([str(i) for i in copy])


def remove_numbered_index(c):
    copy = [int(i) for i in c.config["output"]["numbered_state"].split(".")]
    copy.pop()
    c.config["output"]["numbered_state"] = ".".join([str(i) for i in copy])


def get_task_depth(c, default=1):
    c.config["output"] = c.config.get("output", {})
    c.config["output"]["task_depth"] = c.config["output"].get("task_depth", default)
    return int(c.config["output"]["task_depth"])


def wrapped_run_method(c, run_method, remote, **kwargs):
    """Wrap ``run_method`` with internal function
    ``cmd_in_markdown_codeblock()``.

    A call of such a wrapped run method (``c.run()`` or ``c.local()``) prints
    out its command and output inside of a markdown codeblock.

    :param run_method:
        Required, ``c.run()``, or ``c.local()``

    :param bool remote:
        Required, if ``True``, ``run_method`` is treated as a ``run()``
        method, if ``False``, as a ``local()`` method.

    :param str prefix_formatter:
        Optional, default: ``'\\n```{language}\\n'``

    :param str cmd_placeholder:
        Will be printed instead of the actual``cmd``.
        Optional, default: ``None``

    :param str local_cmd_formatter:
        Optional, default: ``'{user}@{host}{prompt_end}{cmd}'``

    :param str remote_cmd_formatter:
        Optional, default: ``'{user}@{host}{prompt_end}{cmd}'``

    :param str return_code_formatter:
        Optional, default: ``'[{return_code}]\\n'``

    :param str postfix_formatter:
        Optional, default: ``3*'`'+'\\n'``

    :param dict format_kwargs:
        Optional, default: ``dict(language='', prompt_end='> ')``

    :param str command_output_prefix:
        Optional, default: ``"(stdout) "`` (without quotation marks).

    :param str command_errput_prefix:
        Optional, default: ``"(STDERR) "`` (without quotation marks).
    """

    # workaround: do not wrap if already wrapped
    # it is possible that a task function would be wrapped more than once
    # i can reproduce it, but the reason is unclear, needs more debugging/test
    if hasattr(run_method, "wrapped_with_cmd_in_markdown_codeblock"):
        return run_method

    interactive = bool(kwargs.get("interactive", False))  # non-interactive by default

    prefix_formatter = kwargs.get(
        "prefix_formatter",
        # '\n```{language}\n{cmd_text}\n'
        "\n```{language}\n",
    )
    local_cmd_formatter = kwargs.get(
        "local_cmd_formatter", "{user}@{host}{prompt_end}{cmd}"
    )
    remote_cmd_formatter = kwargs.get(
        "remote_cmd_formatter", "{user}@{host}{prompt_end}{cmd}"
    )
    return_code_formatter = kwargs.get("return_code_formatter", "[{return_code}]\n")
    postfix_formatter = kwargs.get("postfix_formatter", "```\n")
    format_kwargs = {
        **{
            # "language": "",  # 'sh'
            "language": "sh",
            "prompt_end": "> ",
        },
        **kwargs.get("format_kwargs", {}),
    }

    command_output_prefix = kwargs.get("command_output_prefix", "")  # "(stdout) ")
    command_errput_prefix = kwargs.get("command_errput_prefix", "")  # "(STDERR) ")

    # wrapped_run_method.num_calls += 1

    @wraps(run_method)
    def cmd_in_markdown_codeblock(cmd, *args, **kwargs):

        # # TODO DEBUG
        # cmd_in_markdown_codeblock.num_calls += 1
        # print('\n# INTERNALS:\n')
        # print('* wrapped_run_method.num_calls: {}'.format(
        #     wrapped_run_method.num_calls))
        # print('* cmd_in_markdown_codeblock.num_calls: {}'.format(
        #     cmd_in_markdown_codeblock.num_calls))
        # print('* {}'.format(cmd))
        # from inspect import getframeinfo, stack
        # for i in reversed(range(1, 10)):
        #     _caller = getframeinfo(stack()[i][0])
        #     print('* {}. caller: {}:{} {}'.format(
        #         i, _caller.filename, _caller.lineno, stack()[i][3]))
        # print('')

        inner_interactive = c.config["run"].get("interactive", False) or bool(
            kwargs.pop("interactive", interactive)
        )

        inner_prefix_formatter = kwargs.pop("prefix_formatter", prefix_formatter)
        inner_cmd_placeholder = kwargs.pop("cmd_placeholder", None)
        inner_local_cmd_formatter = kwargs.pop(
            "local_cmd_formatter", local_cmd_formatter
        )
        inner_remote_cmd_formatter = kwargs.pop(
            "remote_cmd_formatter", remote_cmd_formatter
        )
        inner_return_code_formatter = kwargs.pop(
            "return_code_formatter", return_code_formatter
        )
        inner_postfix_formatter = kwargs.pop("postfix_formatter", postfix_formatter)
        inner_format_kwargs = {**format_kwargs, **kwargs.pop("format_kwargs", {})}

        inner_command_output_prefix = kwargs.pop(
            "command_output_prefix", command_output_prefix
        )
        inner_command_errput_prefix = kwargs.pop(
            "command_errput_prefix", command_errput_prefix
        )

        if kwargs.get("hide", None) is True:
            # no output, no markdown codeblock
            return run_method(cmd, *args, **kwargs)

        # kwargs['hide'] != True

        # begin codeblock

        color_local = config_color(c.config, ["output", "color", "cmd_local"], green)
        color_remote = config_color(c.config, ["output", "color", "cmd_remote"], yellow)

        user = getpass.getuser()
        host = socket.gethostname()
        cmd_arg = color_local(
            inner_cmd_placeholder if inner_cmd_placeholder else cmd, bold=True
        )
        cmd_formatter = inner_local_cmd_formatter

        if remote:
            user = c.user
            host = c.host
            cmd_arg = color_remote(cmd, bold=True)
            cmd_formatter = inner_remote_cmd_formatter

        cmd_text_kwargs = {
            **{"user": user, "host": host, "cmd": "" if inner_interactive else cmd_arg},
            **inner_format_kwargs,
        }
        cmd_text = cmd_formatter.format(**cmd_text_kwargs)

        prefix = inner_prefix_formatter.format(
            **{
                **dict(
                    # language='',
                    cmd_text=cmd_text  # when required by custom formatter
                    # TODO documentate usecase
                ),
                **inner_format_kwargs,
            }
        )

        # if inner_interactive and prefix.endswith('\n'):
        #     prefix = prefix[:-1]

        # print_quiet(prefix, end='')
        print_code_block(prefix, end="")

        if inner_interactive:
            cmd = fabsetup.fabutils.queries.interactive(
                prompt=cmd_text,
                cmd_color=color_remote if remote else color_local,
                prefill=cmd,
            )
        else:
            print_command_line(cmd_text, end="")
            print("")

        try:
            if hasattr(sys.stdout, "add_prefix"):
                sys.stdout.add_prefix = True
                sys.stdout.stream2_line_prefix = inner_command_output_prefix
            if hasattr(sys.stderr, "add_prefix"):
                sys.stderr.add_prefix = True
                sys.stderr.stream2_line_prefix = inner_command_errput_prefix

            res = run_method(cmd, *args, **kwargs)

            # import sys
            # from fabsetup.utils import red
            # res = run_method(cmd, *args, **{**kwargs, **{'hide': 'both'}})

            # if kwargs.get('hide', '') not in ['stdout', 'both']:
            #     print(res.stdout, end='')
            # if kwargs.get('hide', '') not in ['stderr', 'both']:
            #     err_str = res.stderr
            #     if len(err_str) > 0:
            #         print('stderr: {}'.format(res.stderr), end='')

            if hasattr(sys.stdout, "add_prefix"):
                sys.stdout.add_prefix = False
            if hasattr(sys.stderr, "add_prefix"):
                sys.stderr.add_prefix = False

            if res.return_code != 0:
                return_code = inner_return_code_formatter.format(
                    return_code=res.return_code
                )
                # print_briefly(return_code, end='')
                print_default(return_code, end="")

            # end codeblock

        finally:
            # sys.stdout.flush()
            # sys.stderr.flush()
            # print('```', flush=True)
            postfix = inner_postfix_formatter.format(**kwargs)
            # print_quiet(postfix, end='')
            print_code_block(postfix, end="")

        return res

    # cmd_in_markdown_codeblock.num_calls = 0  # TODO DEBUG

    cmd_in_markdown_codeblock.wrapped_with_cmd_in_markdown_codeblock = True

    return cmd_in_markdown_codeblock


# wrapped_run_method.num_calls = 0  # TODO DEBUG


def task(*args, **kwargs):
    '''Decorator based on `fabric.tasks.task
    <https://docs.fabfile.org/en/latest/api/tasks.html#fabric.tasks.task>`_
    with the following modifications:

    * On task execution produce Markdown formatted output:

      + print task name as H1 heading by using
        ``fabsetup.utils.print_full_name()``
      + print task docstring as paragraph by using
        ``fabsetup.utils.print_doc()``.
      + ``c.run()`` and ``c.local()`` command calls from inside of a decorated
        function and its output are printed as markdown codeblocks with the
        power of ``fabsetup.task.wrapped_run_method()``.

    * The context method ``c.local()`` exists and works even when no hosts are
      given by `(Fabric) argument
      <https://docs.fabfile.org/en/latest/cli.html#cmdoption-h>`_
      ``-H, --hosts``. In such a case, ``c.local()`` and ``c.run()`` are the
      same.  This feature is a monkey-patch, addresses
      `Fabric issue 1789
      <https://github.com/fabric/fabric/issues/1789#issuecomment-424116753>`_,
      `issue 1591
      <https://github.com/fabric/fabric/issues/1591#issuecomment-296903582>`_,
      and `issue 98
      <https://github.com/fabric/fabric/issues/98>`_.

    * Apply workaround for `Fabric issue 16
      <https://github.com/fabric/patchwork/issues/16>`_ by using
      ``fabsetup.task.issue_16_workaround()``.

    Wraps and extends Fabric's ``@task`` and `Invoke's
    <https://docs.pyinvoke.org/en/latest/api/tasks.html#invoke.tasks.task>`_
    ``@task`` with the following additional keyword arguments:

    :param str `name_`:
        Optionally set a custom task name.

    :param bool doc:
        If ``True``, print the task's docstring on task execution (default).

    :param str prefix_formatter:
        Optional, default: ``'\\n```{language}\\n'``

    :param str local_cmd_formatter:
        Optional, default: ``'{user}@{host}{prompt_end}{cmd}'``

    :param str remote_cmd_formatter:
        Optional, default: ``'{user}@{host}{prompt_end}{cmd}'``

    :param str return_code_formatter:
        Optional, default: ``'[{return_code}]\\n'``

    :param str postfix_formatter:
        Optional, default: ``3*'`'+'\\n'``

    :param dict format_kwargs:
        Optional, default: ``dict(language='', prompt_end='> ')``

    :param str command_output_prefix:
        Optional, default: ``"(stdout) "`` (without quotation marks).

    :param str command_errput_prefix:
        Optional, default: ``"(STDERR) "`` (without quotation marks).

    Example:

    .. code-block::

        >>> from fabsetup.task import task
        >>>
        >>> @task()
        ... def termdown(c):
        ...     """Install and set up termdown"""
        ...     c.run('echo setup..')

        .>> termdown(c)

        # termdown

        Install and set up termdown

        ```
        myuser@myhost> echo setup..
        setup..
        ```
    '''  # noqa: E501
    # read environment variable in case of invoke or fab execution
    depth = kwargs.pop("depth", os.environ.get("FABSETUP_OUTPUT_TASK_DEPTH", None))
    output_numbered = kwargs.pop(
        "output_numbered", os.environ.get("FABSETUP_OUTPUT_NUMBERED", None)
    )
    numbered_state = kwargs.pop(
        "numbered_state", os.environ.get("FABSETUP_OUTPUT_NUMBERED_STATE", None)
    )

    name_ = kwargs.pop("name_", None)
    doc = kwargs.pop("doc", True)

    wrap_keys = (
        "interactive",
        "prefix_formatter",
        "local_cmd_formatter",
        "remote_cmd_formatter",
        "return_code_formatter",
        "postfix_formatter",
        "format_kwargs",
        "command_output_prefix",
        "command_errput_prefix",
    )

    wrap_kwargs = {key: kwargs[key] for key in kwargs if key in wrap_keys}
    task_kwargs = {key: kwargs[key] for key in kwargs if key not in wrap_keys}

    def real_decorator(func):
        @wraps(func)
        def wrapped_func(c, *argz, **kwargz):

            issue_16_workaround(c)

            if "interactive" in kwargz:
                wrap_kwargs["interactive"] = kwargz["interactive"]

            wrap_kwargs["command_output_prefix"] = kwargs.get(
                "command_output_prefix",
                from_config(
                    c.config,
                    ["output", "command_output_prefix"],
                    "",  # "(stdout) ",
                ),
            )
            wrap_kwargs["command_errput_prefix"] = kwargs.get(
                "command_errput_prefix",
                from_config(
                    c.config,
                    ["output", "command_errput_prefix"],
                    "",  # "(STDERR) ",
                ),
            )

            if (
                isinstance(c, fabric.connection.Connection)
                and hasattr(c, "host")
                and c.host != "localhost"
            ):
                # `fabsetup` or `fab` was called with -H argument

                debug(f"called with `-H {c.user}@{c.host}`".format(c))

                c.run = wrapped_run_method(
                    c, run_method=c.run, remote=True, **wrap_kwargs
                )
                c.local = wrapped_run_method(
                    c, run_method=c.local, remote=False, **wrap_kwargs
                )

                def put_scp(local, remote, recursive=False):

                    rcsv = ""
                    if recursive:
                        rcsv = " -r"

                    res = c.local(
                        "scp{rcsv} {local} {c.user}@{c.host}:{remote}".format(
                            rcsv=rcsv,
                            local=local,
                            remote=remote,
                            c=c,
                        )
                    )
                    return res

                c.put = put_scp

            elif hasattr(c, "host") and c.host == "localhost":

                debug("`-H localhost` is used")

                c.local = wrapped_run_method(
                    c, run_method=c.local, remote=False, **wrap_kwargs
                )
                c.run = c.local

                def put_cp(local, remote, recursive=False):

                    rcsv = ""
                    if recursive:
                        rcsv = " -r"

                    res = c.local(
                        "cp{rcsv} {local} {remote}".format(
                            rcsv=rcsv,
                            local=local,
                            remote=remote,
                        )
                    )
                    return res

                c.put = put_cp

            else:
                # type of c is invoke.context.Context
                # `fabsetup` or `fab` was called without -H argument
                # or `invoke` was called

                debug("no `-H` argument used")

                c.run = wrapped_run_method(
                    c,
                    run_method=c.run,
                    remote=False,
                    local_cmd_formatter=wrap_kwargs.pop(
                        "local_cmd_formatter",
                        "{cmd}"
                        # "local_cmd_formatter", "{prompt_end}{cmd}"
                    ),
                    **wrap_kwargs,
                )
                c.local = c.run

                def put_cp(local, remote, recursive=False):

                    rcsv = ""
                    if recursive:
                        rcsv = " -r"

                    res = c.local(
                        "cp{rcsv} {local} {remote}".format(
                            rcsv=rcsv,
                            local=local,
                            remote=remote,
                        )
                    )
                    return res

                c.put = put_cp

            # TODO: raise c is no context or connection TypeError

            color = config_color(c.config, ["output", "color", "task_heading"], magenta)

            cur_depth = get_task_depth(c, default=int(depth or 1))

            if output_numbered:
                c.config["output"]["numbered"] = True

            if numbered_state:
                c.config["output"] = c.config.get("output", {})
                c.config["output"]["numbered_state"] = numbered_state

            wrapped = print_full_name(
                color=color,
                prefix="\n" + "#" * cur_depth + " ",
                tail="\n",
                name=name_,
                numbered=increment_numbered_state(c),
                # )(print_doc(prefix="*This task performs:*\n\n")(func) if doc else func)
            )(print_doc(prefix="")(func) if doc else func)

            append_numbered_index(c)
            c.config.output["task_depth"] = cur_depth + 1

            res = wrapped(c, *argz, **kwargz)

            remove_numbered_index(c)
            c.config.output["task_depth"] = cur_depth

            return res

        # @wraps is not enough monkeypatching, also signature of func must be
        # copied for cloned identity, cf. https://stackoverflow.com/a/43616267
        # invoke uses `inspect.getargspec(func)` to determine signature of func
        wrapped_func.__signature__ = inspect.signature(func)

        task_args = args
        if len(args) == 1:
            task_args = []  # when decorated as `@task`

        return fabric.task(*task_args, **task_kwargs)(wrapped_func)

    if invoked(args, kwargs):
        return real_decorator  # when decorated as `@task(...)`
    return real_decorator(func=args[0])  # when decorated as `@task`


def subtask(*args, **kwargs):
    """Decorator which prints out the name and docstring of the decorated
    function on execution.

    The output is markdown formatted and colored: A cyan colored H2 heading
    containing the name of the subtask and a non-colored paragraph with the
    docstring of the subtask.

    :param int depth:
        Optionally set the order of the markdown heading which contains the
        subtask name. The default is `2`.

    :param str prefix:
        Optionally set a custom prefix of the heading,
        default: ``'\\n## '``.

    :param str tail:
        Optionally set a custom tail of the heading,
        default: ``'\\n'``.

    :param bool doc:
        If ``True`` (the default) print the docstring as a paragraph.

    :param fabsetup.utils.color-function color:
        Optionally set a custom color of the heading,
        default: ``fabsetup.utils.cyan``.

    :param str name:
        Optionally define a name which is printed as the heading text instead
        of the name of the subtask function (default: ``None``).

    Example:

        >>> import invoke.context
        >>> c = invoke.context.Context()
        >>>
        >>> @subtask
        ... def mysubtask(c):
        ...     'This is my subtask'
        ...     print('foo')
        ...
        >>>
        >>> mysubtask(c)
        \033[36m
        ## mysubtask
        \033[0m
        \033[34mThis is my subtask
        \033[0m
        foo

    """
    depth = kwargs.pop("depth", None)
    prefix = kwargs.get("prefix", None)
    tail = kwargs.get("tail", "\n")
    doc = kwargs.get("doc", True)
    color = kwargs.get("color", None)
    name = kwargs.get("name", None)

    def real_decorator(func):
        @wraps(func)
        def wrapped_func(c, *argz, **kwargz):
            # wrapped = func

            # arg = print_doc(func) if doc else func

            c_or_self = c
            if not isinstance(c, invoke.context.Context):
                # method-type subtask
                c = c_or_self.c

            cur_depth = depth
            if cur_depth is None:
                cur_depth = get_task_depth(c, default=2)

            col = color or config_color(
                c.config, ["output", "color", "subtask_heading"], cyan
            )

            pfx = prefix
            if pfx is None:
                pfx = "\n" + "#" * cur_depth + " "

            wrapped = print_full_name(
                color=col,
                prefix=pfx,
                tail=tail,
                name=name,
                numbered=increment_numbered_state(c),
            )(print_doc(func) if doc else func)

            append_numbered_index(c)
            c.config.output["task_depth"] = cur_depth + 1

            res = wrapped(c_or_self, *argz, **kwargz)

            remove_numbered_index(c)
            c.config.output["task_depth"] = cur_depth

            return res

        return wrapped_func

    if invoked(args, kwargs):
        return real_decorator  # when decorated as `@subtask(...)`
    return real_decorator(func=args[0])  # when decorated as `@subtask`


# def subsubtask(*args, **kwargs):
#     """Decorator which prints out the name and docstring of the decorated
#     function on execution.
#
#     The output is markdown formatted and colored: A cyan colored H3 heading
#     containing the name of the subtask and a non-colored paragraph with the
#     docstring of the subtask.
#
#     :param int depth:
#         Optionally set the order of the markdown heading which contains the
#         subtask name. The default is ``2``.
#
#     :param str prefix:
#         Optionally set a custom prefix of the heading,
#         default: ``'\\n### '``.
#
#     :param str tail:
#         Optionally set a custom tail of the heading,
#         default: ``'\\n'``.
#
#     :param bool doc:
#         If ``True`` (the default) print the docstring as a paragraph.
#
#     :param fabsetup.utils.color-function color:
#         Optionally set a custom color of the heading,
#         default: ``fabsetup.utils.no_color``.
#
#     :param str name:
#         Optionally set a str which is printed as the heading text instead of
#         the name of the subsubtask function (default: ``None``).
#
#     Example:
#
#         >>> @subsubtask(doc=False)
#         ... def mysubsubtask():
#         ...     print('bar')
#         ...
#         >>> mysubsubtask()
#         <BLANKLINE>
#         ### mysubsubtask
#         <BLANKLINE>
#         bar
#
#     """
#     depth = kwargs.pop("depth", int(os.environ.get("FABSETUP_TASK_DEPTH", 1)) + 2)
#
#     def real_decorator(func):
#         color = kwargs.pop("color", no_color)
#         return subtask(depth=depth, color=color, *args, **kwargs)(func)
#
#     if invoked(args, kwargs):
#         return real_decorator
#     return real_decorator(func=args[0])
