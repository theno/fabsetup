import os.path
import pytest
import sys


# for skipif(), see: https://docs.pytest.org/en/latest/skipping.html
@pytest.mark.skipif(sys.version_info < (2, 7),
                    reason="paramiko does not support Python-2.6")
def test_git_ssh_or_die():
    from fabsetup.fabfile import git_ssh_or_die
    thisdir = os.path.dirname(__file__)

    key_dir = os.path.join(thisdir, 'data', 'test_git_ssh_or_die', 'with_key')
    git_ssh_or_die(username='theno', key_dir=key_dir)

    key_dir = os.path.join(thisdir, 'data', 'test_git_ssh_or_die',
                           'does_not_exist')
    # for pytest.raises(), see:
    # https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        git_ssh_or_die(username='theno', key_dir=key_dir)
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    key_dir = os.path.join(thisdir, 'data', 'test_git_ssh_or_die', 'no_key')
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        git_ssh_or_die(username='theno', key_dir=key_dir)
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 2

    key_dir = os.path.join(thisdir, 'data', 'test_git_ssh_or_die',
                           'key_no_github')
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        git_ssh_or_die(username='theno', key_dir=key_dir)
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 3
