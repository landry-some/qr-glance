import base64
import io
import json

import pytest
import segno
from PIL import Image

from qr_glance.cli import main


@pytest.fixture
def code_png(tmp_path):
    def make(text, name="code.png", **kw):
        path = tmp_path / name
        segno.make(text, micro=False).save(path, scale=6, **kw)
        return str(path)
    return make


def test_reads_one_image(code_png, capsys):
    assert main(["read", code_png("hello there")]) == 0
    assert capsys.readouterr().out == "hello there\n"


def test_reads_unicode(code_png, capsys):
    assert main(["read", code_png("café ☕ 東京")]) == 0
    assert capsys.readouterr().out == "café ☕ 東京\n"


def test_reads_jpeg_with_inverted_colours(tmp_path, capsys):
    png = tmp_path / "a.png"
    segno.make("dark mode", micro=False).save(png, scale=6, dark="white", light="black")
    jpg = tmp_path / "a.jpg"
    Image.open(png).convert("RGB").save(jpg, quality=80)
    assert main(["read", str(jpg)]) == 0
    assert capsys.readouterr().out == "dark mode\n"


def _grid(tmp_path, code_png, rows, rise=0):
    """Paste one code per text into a grid image, row by row, and return its path.

    Each code sits ``rise`` pixels higher than the one to its left, like a tilted photo.
    """
    tiles = [[Image.open(code_png(t, f"{t}.png")) for t in row] for row in rows]
    size = max(t.width for row in tiles for t in row)
    width = max(map(len, tiles))
    grid = Image.new("L", (size * width, size * len(tiles) + rise * width), 255)
    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            grid.paste(tile, (x * size, y * size + rise * (width - 1 - x)))
    path = tmp_path / "grid.png"
    grid.save(path)
    return str(path)


def test_reads_two_codes_in_one_image(tmp_path, code_png, capsys):
    assert main(["read", _grid(tmp_path, code_png, [["left", "right"]])]) == 0
    assert capsys.readouterr().out == "left\nright\n"


def test_codes_come_top_left_first(tmp_path, code_png, capsys):
    path = _grid(tmp_path, code_png, [["a1", "a2", "a3"], ["b1", "b2", "b3"]])
    assert main(["read", path]) == 0
    assert capsys.readouterr().out.split() == ["a1", "a2", "a3", "b1", "b2", "b3"]


def test_tilted_row_still_reads_left_to_right(tmp_path, code_png, capsys):
    path = _grid(tmp_path, code_png, [["a1", "a2", "a3"], ["b1", "b2", "b3"]], rise=20)
    assert main(["read", path]) == 0
    assert capsys.readouterr().out.split() == ["a1", "a2", "a3", "b1", "b2", "b3"]


def test_stacked_codes_come_top_first(tmp_path, code_png, capsys):
    path = _grid(tmp_path, code_png, [["top"], ["middle"], ["bottom"]])
    assert main(["read", "--json", path]) == 0
    assert [r["text"] for r in json.loads(capsys.readouterr().out)] == ["top", "middle", "bottom"]


def test_multiple_files_get_a_prefix(code_png, capsys):
    a, b = code_png("one", "a.png"), code_png("two", "b.png")
    assert main(["read", a, b]) == 0
    assert capsys.readouterr().out == f"{a}: one\n{b}: two\n"


def test_json_output(code_png, capsys):
    path = code_png("json please")
    assert main(["read", "--json", path]) == 0
    [record] = json.loads(capsys.readouterr().out)
    assert record["file"] == path
    assert record["text"] == "json please"
    assert record["format"] == "QRCode"
    assert len(record["corners"]) == 4


BINARY = b"\xff\xfe\x00 binary \x80\x01"


def test_binary_payload_is_printed_as_base64(code_png, capsys):
    assert main(["read", code_png(BINARY)]) == 0
    captured = capsys.readouterr()
    assert base64.b64decode(captured.out.strip()) == BINARY
    assert "binary data, shown as base64" in captured.err


def test_binary_payload_as_hex(code_png, capsys):
    assert main(["read", "--binary", "hex", code_png(BINARY)]) == 0
    assert capsys.readouterr().out == BINARY.hex() + "\n"


def test_binary_payload_in_json(code_png, capsys):
    assert main(["read", "--json", "--binary", "hex", code_png(BINARY)]) == 0
    [record] = json.loads(capsys.readouterr().out)
    assert record["text"] is None
    assert record["hex"] == BINARY.hex()


def test_latin1_text_is_not_treated_as_binary(code_png, capsys):
    assert main(["read", code_png("héllo".encode("latin-1"))]) == 0
    captured = capsys.readouterr()
    assert captured.out == "héllo\n"
    assert captured.err == ""


def test_image_without_code_exits_1(tmp_path, code_png, capsys):
    blank = tmp_path / "blank.png"
    Image.new("L", (100, 100), 255).save(blank)
    good = code_png("ok")
    assert main(["read", str(blank), good]) == 1
    captured = capsys.readouterr()
    assert "blank.png: no QR code found" in captured.err
    assert captured.out == f"{good}: ok\n"


def test_missing_and_non_image_files_exit_2(tmp_path, capsys):
    text = tmp_path / "notes.txt"
    text.write_text("not an image")
    assert main(["read", str(tmp_path / "gone.png"), str(text), str(tmp_path)]) == 2
    err = capsys.readouterr().err
    assert "gone.png: no such file" in err
    assert "notes.txt: not a readable image" in err
    assert "is a directory" in err


def test_json_with_nothing_found_is_an_empty_list(tmp_path, capsys):
    blank = tmp_path / "blank.png"
    Image.new("L", (50, 50), 255).save(blank)
    assert main(["read", "--json", str(blank)]) == 1
    assert json.loads(capsys.readouterr().out) == []


class _Stdin:
    def __init__(self, data):
        self.buffer = io.BytesIO(data)


def test_reads_image_bytes_from_stdin(code_png, monkeypatch, capsys):
    with open(code_png("piped in"), "rb") as f:
        monkeypatch.setattr("sys.stdin", _Stdin(f.read()))
    assert main(["read", "-"]) == 0
    assert capsys.readouterr().out == "piped in\n"


def test_stdin_that_is_not_an_image_exits_2(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", _Stdin(b"plain text"))
    assert main(["read", "-"]) == 2
    assert "stdin: not a readable image" in capsys.readouterr().err
