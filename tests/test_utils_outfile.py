import sys
import collections

import fabsetup.utils.outfile


def test_stream_tee(capsys):

    Test = collections.namedtuple(
        typename="Test",
        field_names=[
            "stream1",
            "stream2",
            "output",
            "errput",
            "expected_out",
            "expected_err",
        ],
    )

    tests = [
        # "straight forward"
        Test(
            stream1=sys.stdout,
            stream2=sys.stdout,
            output="foo",
            errput="",
            expected_out="foofoo\n\n",
            expected_err="",
        ),
        Test(
            stream1=sys.stdout,
            stream2=sys.stderr,
            output="bar",
            errput="",
            expected_out="bar\n",
            expected_err="bar\n",
        ),
        Test(
            stream1=sys.stderr,
            stream2=sys.stdout,
            output="baz",
            errput="",
            expected_out="baz\n",
            expected_err="baz\n",
        ),
        # "advanced"
        Test(
            stream1=sys.stdout,
            stream2=sys.stderr,
            output="foo",
            errput="bar",
            expected_out="foo\n",
            expected_err="foo\nbar\n",
        ),
        Test(
            stream1=sys.stdout,
            stream2=sys.stdout,
            output="foo",
            errput="bar",
            expected_out="foofoo\n\n",
            expected_err="bar\n",
        ),
        # kwargs
    ]

    for test in tests:

        # prepare
        default_stdout = sys.stdout
        default_stderr = sys.stderr
        captured = capsys.readouterr()

        # run
        sys.stdout = fabsetup.utils.outfile.stream_tee(
            test.stream1,
            test.stream2,
        )

        if test.output:
            print(test.output)

        if test.errput:
            print(test.errput, file=sys.stderr)

        # check
        captured = capsys.readouterr()
        assert captured.out == test.expected_out
        assert captured.err == test.expected_err

        # restore
        sys.stdout = default_stdout
        sys.stderr = default_stderr
