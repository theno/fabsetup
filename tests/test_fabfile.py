import invoke.context
import fabric.tasks

import fabsetup.fabfile

from tests.test_utils_decorators import MockContext


# cf. https://stackoverflow.com/q/4984647
class AttributeDict(dict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


def test_versions(capsys):

    # versions() is a subtask, so we are at task_depth 2
    c = MockContext()
    c.config.task_depth = 2

    fabsetup.fabfile.versions(c)

    captured = capsys.readouterr()

    assert captured.out.startswith("\033[36m\n## Versions")

    for module in ["fabsetup", "fabric", "invoke", "paramiko"]:
        assert "%s==" % module in captured.out  # noqa: E0100

    assert fabsetup.fabfile.versions.__doc__.split("\n")[0] not in captured.out
    assert "```\nfabsetup" in captured.out
    assert captured.out.endswith("```\n\n")


def test_help(capsys):

    # help() is a subtask, so we are at task_depth 2
    c = MockContext()
    c.config.task_depth = 2

    fabsetup.fabfile.help(c, "command")

    captured = capsys.readouterr()

    assert captured.out == "\033[36m\n## Help\n\033[0m\n    command -h\n\n"


def test_tasks(capsys):

    # tasks() is a subtask, so we are at task_depth 2
    c = MockContext()
    c.config.task_depth = 2

    fabsetup.fabfile.tasks(c, "cmd")

    captured = capsys.readouterr()

    assert captured.out == "\033[36m\n## List tasks\n\033[0m\n    cmd -l\n\n"


def test_task_help(capsys):

    # task_help() is a subtask, so we are at task_depth 2
    c = MockContext()
    c.config.task_depth = 2

    fabsetup.fabfile.task_help(c, "fabsetup")

    captured = capsys.readouterr()

    assert (
        captured.out
        == "\033[36m\n## Show task help\n\033[0m\n    fabsetup <task> --help\n\n"
    )


def test_info(capsys):

    # info() is a task, so we are at task_depth 1

    info_task = fabsetup.fabfile.info

    assert isinstance(info_task, fabric.tasks.Task)

    context = invoke.context.Context()
    info_task(context)

    captured = capsys.readouterr()

    for heading in [
        "# Fabsetup",
        "## Versions",
        "## Help",
        "## List tasks",
        "## Show task help",
    ]:
        assert heading in captured.out

    assert "\n[fabsetup repository]" in captured.out
    assert "fabsetup)\n\n" in captured.out
    # `pytest -s`              => 'pytest ...'
    # `python3.9 -m pytest -s` => 'pytest/__main__.py ...'
    assert ("pytest -h" in captured.out) or ("pytest/__main__.py -h" in captured.out)
    assert ("pytest -l" in captured.out) or ("pytest/__main__.py -l" in captured.out)
    assert ("pytest <task> --help" in captured.out) or (
        "pytest/__main__.py <task> --help" in captured.out
    )


def test_new(capsys):

    # new_task = fabsetup.fabfile.new

    # assert isinstance(new_task, fabric.tasks.Task)

    # context = invoke.context.Context()
    # new_task(context)

    # captured = capsys.readouterr()

    # for text in ['# New Addon', 'Create a new fabsetup addon']:
    #     assert text in captured.out

    # assert '\nTODO: ' in captured.out

    pass
