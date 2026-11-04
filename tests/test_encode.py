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


def test_too_long_data_names_the_limit():
    with pytest.raises(ValueError, match=r"too long .* 3000 bytes.* level M is 2331 bytes of text \(try -e L\)"):
        make_qr("x" * 3000)


def test_too_long_at_level_l_has_no_hint():
    with pytest.raises(ValueError) as exc:
        make_qr("x" * 3000, error="L")
    assert "try" not in str(exc.value)


def test_level_l_fits_more_than_level_m():
    assert make_qr("x" * 2900, error="L").version == 40


def test_no_hint_when_even_level_l_is_too_small():
    with pytest.raises(ValueError) as exc:
        make_qr("x" * 5000)
    assert "try" not in str(exc.value)
