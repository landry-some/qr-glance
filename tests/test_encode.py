import pytest

from qr_glance.encode import make_qr


def test_short_text_is_not_micro_qr():
    qr = make_qr("hi")
    assert not qr.is_micro
    assert qr.version == 1


def test_error_level_is_kept_exactly():
    assert make_qr("hi", error="l").error == "L"
    assert make_qr("hi", error="H").error == "H"


def test_bad_error_level():
    with pytest.raises(ValueError, match="error level"):
        make_qr("hi", error="X")
