import sys

# import pytest

import fabsetup.main
import fabsetup.__main__


# # # test main.py # # #


def test_defaults():
    defaults = fabsetup.main.Defaults()
    def_dict = defaults.as_dict()
    assert def_dict == {
        "outfile": {
            "dir": "",
            "basename_formatter": "fabsetup_{now}{tasks}{hosts}.md",
            "now_format": "%F_%H-%M-%S",
            "name": "",
            "keep_color": False,
            "pandoc": {
                "command": "pandoc",
                "html": {
                    "dir": "",
                    "name": "",
                    "css": {
                        "disabled": False,
                        "inline": True,
                        "url": "",
                        "auto_remove_markdown_file": True,
                    },
                },
                "toc": False,
            },
            "prepend_executed_fabsetup_command": True,
            "fabsetup_command_prefix": "*Executed fabsetup command:*\n\n",
            "command_output_prefix": "(stdout) ",
            "command_errput_prefix": "(STDERR) ",
        },
        "output": {
            "color": {
                "cmd_local": "green",
                "cmd_remote": "yellow",
                "docstring": "blue",
                "error": "red",
                "full_name": "no_color",
                "subtask_heading": "cyan",
                "task_heading": "magenta",
                # "question": "default_color",
            },
            "color_off": False,
            "hide_command_line": False,
            "hide_code_block": False,
            "hide_docstring": False,
            "hide_heading": False,
            "hide_print": False,
            "numbered": True,
            "numbered_state": "0",
            "task_depth": 1,
        },
        "run": {
            "interactive": False,
        },
        "load_invoke_tasks_file": False,
        "load_fabric_fabfile": False,
        # "search_root": None,
        "run_before": "",
        "run_finally": "",
    }


# # # test __main__.py # # #


def test_print_version(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["program-name", "--version"])

    # with pytest.raises(SystemExit) as excinfo:
    #     fabsetup.__main__.main()
    #
    # expected = "SystemExit(0)"
    # if sys.version_info.major == 3 and sys.version_info.minor in [5, 6]:
    #     # fallback for Python 3.5 and Python 3.6
    #     expected = "SystemExit(0,)"
    # assert excinfo.value.__repr__() == expected
    fabsetup.__main__.main()

    captured = capsys.readouterr()

    for text in ["fabsetup", "fabric", "paramiko", "invoke"]:
        assert text in captured.out


def test_task_list_opener(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["program-name", "--list"])

    # with pytest.raises(SystemExit) as excinfo:
    #     fabsetup.__main__.main()
    #
    # expected = "SystemExit(0)"
    # if sys.version_info.major == 3 and sys.version_info.minor in [5, 6]:
    #     # fallback for Python 3.5 and Python 3.6
    #     expected = "SystemExit(0,)"
    # assert excinfo.value.__repr__() == expected
    fabsetup.__main__.main()

    captured = capsys.readouterr()

    for text in ["Tasks:", "info", "new", "Default task: info"]:
        assert text in captured.out


def test_print_help(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["program-name", "--help"])

    # with pytest.raises(SystemExit) as excinfo:
    #     fabsetup.__main__.main()
    #
    # expected = "SystemExit(0)"
    # if sys.version_info.major == 3 and sys.version_info.minor in [5, 6]:
    #     # fallback for Python 3.5 and Python 3.6
    #     expected = "SystemExit(0,)"
    # assert excinfo.value.__repr__() == expected
    fabsetup.__main__.main()

    captured = capsys.readouterr()

    for text in [
        "Usage: program-name",
        "task1 [--task1-opts] ... taskN [--taskN-opts]",
        "Core options:",
        "Tasks:",
        "info",
        "new",
        "Default task: info",
    ]:
        assert text in captured.out


def test_main_info(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["program-name", "info"])

    fabsetup.__main__.main()

    captured = capsys.readouterr()

    for text in ["program-name", "Versions", "Help", "List tasks", "Show task help"]:
        assert text in captured.out
