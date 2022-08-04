from collections import namedtuple

import fabsetup.utils.docstring


def test_lstripped_lines():
    Test = namedtuple(
        typename="Test",
        field_names=["input", "expected"],
    )

    tests = [
        Test(
            input="""\
foo
    bar
        baz
""",
            expected="""\
foo
bar
    baz
""",
        ),
        Test(
            input="""\
# mytask

    My docstring, each line
    starts with 4 spaces. They
    should be removed.""",
            expected="""\
# mytask

My docstring, each line
starts with 4 spaces. They
should be removed.""",
        ),
    ]

    for test in tests:
        got = fabsetup.utils.docstring.lstripped_lines(test.input)
        assert got == test.expected
