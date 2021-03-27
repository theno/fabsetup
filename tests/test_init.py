import collections

import fabsetup.__init__


def test_module_str():
    class MockModule:
        def __init__(self, module_name, version):
            self.__name__ = module_name
            self.__version__ = version

    Test = collections.namedtuple(
        typename="Test", field_names=["args", "kwargs", "expected"]
    )

    tests = [
        Test(
            args=[MockModule("module_name", "1.2.3")],
            kwargs={},
            expected="module_name==1.2.3",
        ),
        Test(
            args=[MockModule("module_name", "1.2.3")],
            kwargs={"postfix": "-addon-repo"},
            expected="module_name==1.2.3-addon-repo",
        ),
        Test(
            args=[],
            kwargs={
                "module": MockModule("module_name", "1.2.3"),
            },
            expected="module_name==1.2.3",
        ),
        Test(
            args=[],
            kwargs={
                "module": MockModule("module_name", "1.2.3"),
                "postfix": "-addon-repo",
            },
            expected="module_name==1.2.3-addon-repo",
        ),
    ]

    for test in tests:
        assert fabsetup.__init__._module_str(*test.args, **test.kwargs) == test.expected


def test_version_str():
    version_str = fabsetup.__init__.version_str()
    assert "-addon-repo\n" in version_str  # TODO mock addon repo module
    assert "fabsetup==" in version_str
    assert "\nfabric==" in version_str
    assert "\nparamiko==" in version_str
    assert "\ninvoke==" in version_str
