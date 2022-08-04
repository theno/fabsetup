from collections import namedtuple

import fabsetup.utils.colors


def test_wrap_with():
    expected = "\033[1;CODEmTEXT\033[0m"

    assert fabsetup.utils.colors._wrap_with("CODE")("TEXT", True) == expected

    Test = namedtuple(
        typename="Test",
        field_names=["color", "bold", "expected"],
    )

    tests = [
        Test(
            color=fabsetup.utils.colors.black,
            bold=True,
            expected=expected.replace("CODE", "30"),
        ),
        Test(
            color=fabsetup.utils.colors.red,
            bold=True,
            expected=expected.replace("CODE", "31"),
        ),
        Test(
            color=fabsetup.utils.colors.green,
            bold=True,
            expected=expected.replace("CODE", "32"),
        ),
        Test(
            color=fabsetup.utils.colors.yellow,
            bold=True,
            expected=expected.replace("CODE", "33"),
        ),
        Test(
            color=fabsetup.utils.colors.blue,
            bold=True,
            expected=expected.replace("CODE", "34"),
        ),
        Test(
            color=fabsetup.utils.colors.magenta,
            bold=True,
            expected=expected.replace("CODE", "35"),
        ),
        Test(
            color=fabsetup.utils.colors.cyan,
            bold=True,
            expected=expected.replace("CODE", "36"),
        ),
        Test(
            color=fabsetup.utils.colors.white,
            bold=True,
            expected=expected.replace("CODE", "37"),
        ),
        Test(
            color=fabsetup.utils.colors.default_color,
            bold=True,
            expected=expected.replace("CODE", "0"),
        ),
    ]

    for test in tests:
        assert test.color("TEXT", bold=test.bold) == test.expected
        assert test.color("TEXT", bold=False) == test.expected.replace("1;", "")
        # kwarg bold defaults to False
        assert test.color(text="TEXT") == test.expected.replace("1;", "")

    no_color_tests = [
        Test(
            color=fabsetup.utils.colors.no_color,
            bold=True,
            expected=expected.replace("CODE", "0"),
        ),
        Test(color=fabsetup.utils.colors.no_color, bold=False, expected="TEXT"),
    ]

    for test in no_color_tests:
        assert test.color("TEXT", test.bold) == test.expected
