import sys

# import pytest

import fabsetup.__main__


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
