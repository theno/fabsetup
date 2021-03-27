import collections
import importlib
import sys

import invoke
import pytest

import fabsetup.addons


def test_module_username():

    Test = collections.namedtuple(
        typename="Test",
        field_names=["input", "expected"],
    )

    tests = [
        Test(
            # package name
            input="fabsetup-USER-TASK",
            # module name, user name
            expected=("fabsetup_USER_TASK", "USER"),
        ),
        Test(
            input="fabsetup-theno-termdown",
            expected=("fabsetup_theno_termdown", "theno"),
        ),
    ]

    for test in tests:
        got = fabsetup.addons.module_username(test.input)
        assert got == test.expected


class MockModule:
    def __init__(self, name):
        self.__name__ = name

    # required for mutmut
    def __version__(self):
        return "0.1.0"

    def __eq__(self, other):
        return self.__name__.__eq__(other.__name__)

    # for comprehensible error message on test failure
    def __repr__(self):
        return "MockModule({name})".format(name=self.__name__)


@pytest.fixture
def mock_import_module(monkeypatch):
    def import_module(modulename):
        return MockModule(name=modulename)

    monkeypatch.setattr(importlib, "import_module", import_module)


def test_load_addon(mock_import_module):

    Test = collections.namedtuple(
        typename="Test",
        field_names=["input_args", "expected"],
    )

    tests = [
        Test(
            input_args=["fabsetup-username-taskname"],
            expected={
                "module": MockModule("fabsetup_username_taskname"),
                "collection": {
                    "name": "username",
                },
            },
        ),
        Test(
            input_args=["fabsetup-theno-termdown"],
            expected={
                "module": MockModule("fabsetup_theno_termdown"),
                "collection": {
                    "name": "theno",
                },
            },
        ),
        Test(
            input_args=["fabsetup-theno-service-nginx"],
            expected={
                "module": MockModule("fabsetup_theno_service_nginx"),
                "collection": {
                    "name": "theno",
                },
            },
        ),
    ]

    for test in tests:
        got_module, got_collection = fabsetup.addons.load_addon(*test.input_args)

        assert got_module == test.expected["module"]

        assert type(got_collection) == invoke.Collection

        assert got_collection.name == test.expected["collection"]["name"]


def test_load_pip_addons_import_error():
    assert fabsetup.addons.PIP_MODULES == []

    got_collections = fabsetup.addons.load_pip_addons()

    assert got_collections == []
    assert fabsetup.addons.PIP_MODULES == []


def test_load_pip_addons(mock_import_module):
    assert fabsetup.addons.PIP_MODULES == []

    got_collections = fabsetup.addons.load_pip_addons()

    assert type(got_collections) == list
    assert type(got_collections[0]) == invoke.Collection
    assert len(fabsetup.addons.PIP_MODULES) != 0
    assert len(fabsetup.addons.PIP_MODULES) <= len(
        fabsetup.addons.KNOWN_PIP_PACKAGE_ADDONS
    )
    # FIXME: possibly not correct. matching task namespaces should be merged
    assert len(fabsetup.addons.PIP_MODULES) == len(
        fabsetup.addons.KNOWN_PIP_PACKAGE_ADDONS
    )


def test_repos_dir():

    # check that userprefix '~' has been expanded
    assert fabsetup.addons.REPOS_DIR.startswith("/")


def create_fabsetup_addon(tmpdir, package_name, tasks):
    package_dir = tmpdir.mkdir(package_name)
    module_name = package_name.replace("-", "_")
    module_dir = package_dir.mkdir(module_name)

    fabfile = module_dir.join("__init__.py")
    code = (
        "from fabsetup.task import task\n\n"
        "from {module_name}._version import __version__\n\n".format(
            module_name=module_name
        )
    )
    for task_name in tasks:
        code += (
            "@task\n"
            "def {task_name}(c):\n"
            '    """docstring of {task_name}"""\n'
            "    pass\n\n\n".format(task_name=task_name)
        )
    fabfile.write(code)

    version_file = module_dir.join("_version.py")
    version_file.write('__version__ = "0.1.0"')


def test_load_repo_addons(tmpdir):

    assert fabsetup.addons.REPO_MODULES == []

    data = [
        ("fabsetup-theno-termdown", ["termdown"]),
        ("fabsetup-theno-foo", ["foo"]),
        ("fabsetup-someone-bar", ["bar", "baz"]),
        ("fabsetup-someone-bla.disabled", ["bla"]),
    ]

    for package_name, tasks in data:
        create_fabsetup_addon(tmpdir, package_name, tasks)

    tmpdir.mkdir("fabsetup-someone-baz.disabled")
    tmpdir.mkdir(".rope")

    fabsetup.addons.REPOS_DIR = tmpdir
    if sys.version_info.major == 3 and sys.version_info.minor == 5:
        # fallback for Python 3.5
        fabsetup.addons.REPOS_DIR = str(tmpdir)

    got_collections = fabsetup.addons.load_repo_addons()

    assert type(got_collections) == list
    assert type(got_collections[0]) == invoke.Collection

    assert fabsetup.addons.REPO_MODULES != []


def tasks_of(collection):
    return sorted([task.name for task in collection.tasks.values()])


def colls_of(collection):
    return sorted([coll.name for coll in collection.collections.values()])


def first_sub_coll(collection):
    return [coll for coll in sorted(collection.collections.values())][0]


def test_merge_or_add_r(tmpdir):

    fabsetup.addons.REPO_MODULES = []
    assert fabsetup.addons.REPO_MODULES == []

    # create repo addons
    data = [
        ("fabsetup-namespace-task1", ["task1", "task2"]),
        ("fabsetup-sub-zzz", ["aaa", "bbb"]),
        ("fabsetup-theno-bar", ["bar", "bar1", "bar2", "bar3"]),
        ("fabsetup-theno-baz", ["baz"]),
        ("fabsetup-theno-foo", ["foo", "foo1", "foo2"]),
    ]
    for package_name, tasks in data:
        create_fabsetup_addon(tmpdir, package_name, tasks)

    fabsetup.addons.REPOS_DIR = tmpdir
    if sys.version_info.major == 3 and sys.version_info.minor == 5:
        # fallback for Python 3.5
        fabsetup.addons.REPOS_DIR = str(tmpdir)

    got_collections = fabsetup.addons.load_repo_addons()
    assert type(got_collections) == list
    assert fabsetup.addons.REPO_MODULES != []

    namespace = got_collections[0]
    sub_col = got_collections[1]
    col1 = got_collections[2]
    col2 = got_collections[3]
    col3 = got_collections[4]

    assert type(namespace) == invoke.Collection
    assert type(col1) == invoke.Collection
    assert type(col2) == invoke.Collection
    assert type(col3) == invoke.Collection
    assert type(sub_col) == invoke.Collection

    assert namespace.name == "namespace"

    assert col1.name == "theno"
    assert tasks_of(col1) == ["bar", "bar1", "bar2", "bar3"]
    assert colls_of(col1) == []
    assert col2.name == "theno"
    assert tasks_of(col2) == ["baz"]
    assert colls_of(col2) == []
    assert col3.name == "theno"
    # assert tasks_of(col3) == ['foo', 'foo1', 'foo2']  # TODO DEBUG
    assert tasks_of(col3) == ["foo"]  # TODO DEBUG
    assert colls_of(col3) == []
    assert sub_col.name == "sub"
    assert tasks_of(sub_col) == ["aaa", "bbb"]
    assert colls_of(sub_col) == []

    assert tasks_of(namespace) == ["task1", "task2"]
    assert colls_of(namespace) == []

    fabsetup.addons.merge_or_add_r(namespace, col1)

    assert tasks_of(namespace) == ["task1", "task2"]
    assert colls_of(namespace) == ["theno"]
    assert tasks_of(first_sub_coll(namespace)) == ["bar", "bar1", "bar2", "bar3"]

    fabsetup.addons.merge_or_add_r(namespace, col2)

    assert tasks_of(namespace) == ["task1", "task2"]
    assert colls_of(namespace) == ["theno"]
    assert tasks_of(first_sub_coll(namespace)) == ["bar", "bar1", "bar2", "bar3", "baz"]

    fabsetup.addons.merge_or_add_r(col3, sub_col)
    fabsetup.addons.merge_or_add_r(namespace, col3)

    assert tasks_of(namespace) == ["task1", "task2"]
    assert colls_of(namespace) == ["theno"]
    assert tasks_of(first_sub_coll(namespace)) == [
        "bar",
        "bar1",
        "bar2",
        "bar3",
        "baz",
        "foo",
    ]
    assert tasks_of(first_sub_coll(first_sub_coll(namespace))) == ["aaa", "bbb"]
