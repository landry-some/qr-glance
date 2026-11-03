import zxingcpp
from PIL import Image

from qr_glance.cli import main


def test_saves_png_that_decodes(tmp_path, capsys):
    out = tmp_path / "code.png"
    assert main(["make", "save me", "-o", str(out), "--scale", "4", "--border", "2"]) == 0
    img = Image.open(out)
    assert img.size == ((21 + 4) * 4,) * 2
    assert [r.text for r in zxingcpp.read_barcodes(img)] == ["save me"]
    assert capsys.readouterr().out == f"saved {out} (1-M, 100 px)\n"


def test_saves_svg(tmp_path):
    out = tmp_path / "code.SVG"
    assert main(["make", "save me", "-o", str(out)]) == 0
    assert "<svg" in out.read_text()


def test_rejects_unknown_extension(tmp_path, capsys):
    out = tmp_path / "code.jpg"
    assert main(["make", "x", "-o", str(out)]) == 2
    assert not out.exists()
    assert ".png or .svg" in capsys.readouterr().err


def test_rejects_bad_scale(tmp_path):
    assert main(["make", "x", "-o", str(tmp_path / "a.png"), "--scale", "0"]) == 2


def test_rejects_negative_border_for_files(tmp_path):
    assert main(["make", "x", "-o", str(tmp_path / "a.png"), "--border", "-2"]) == 2


def test_missing_directory_is_a_clean_error(tmp_path, capsys):
    out = tmp_path / "nope" / "a.png"
    assert main(["make", "x", "-o", str(out)]) == 1
    err = capsys.readouterr().err
    assert err.startswith("qrg: ") and "Traceback" not in err
