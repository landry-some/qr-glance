import io

import pytest

from qr_glance.cli import main
from qr_glance.encode import make_qr
from qr_glance.render import to_terminal


def test_make_prints_the_rendered_code(capsys):
    assert main(["make", "hello"]) == 0
    out = capsys.readouterr().out
    assert out == to_terminal(make_qr("hello").matrix) + "\n"


def test_make_reads_stdin_and_drops_trailing_newline(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("hello\n"))
    assert main(["make"]) == 0
    assert capsys.readouterr().out == to_terminal(make_qr("hello").matrix) + "\n"


def test_make_options(capsys):
    assert main(["make", "hello", "-e", "h", "--invert", "--border", "1"]) == 0
    expected = to_terminal(make_qr("hello", error="H").matrix, border=1, invert=True)
    assert capsys.readouterr().out == expected + "\n"


def test_make_empty_input(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    assert main(["make"]) == 2
    assert "nothing to encode" in capsys.readouterr().err


def test_make_too_much_data(capsys):
    assert main(["make", "x" * 5000]) == 2
    assert capsys.readouterr().err.startswith("qrg: data is too long for a QR code: 5000 bytes")


def test_make_negative_border(capsys):
    assert main(["make", "hi", "--border", "-1"]) == 2


def test_bad_error_level_is_an_argparse_error():
    with pytest.raises(SystemExit):
        main(["make", "hi", "-e", "z"])
