import pytest

from qr_glance.encode import make_qr
from qr_glance.render import to_terminal, with_quiet_zone

UPPER, LOWER, FULL = "▀", "▄", "█"


def parse(text: str, invert: bool = False) -> list[list[bool]]:
    """Turn rendered output back into rows of modules (True = dark)."""
    top_painted = {UPPER: True, FULL: True}
    bottom_painted = {LOWER: True, FULL: True}
    rows = []
    for line in text.split("\n"):
        tops = [top_painted.get(c, False) for c in line]
        bottoms = [bottom_painted.get(c, False) for c in line]
        rows.append([p == invert for p in tops])
        rows.append([p == invert for p in bottoms])
    return rows


def test_quiet_zone_adds_light_border():
    rows = with_quiet_zone([[1, 0], [0, 1]], border=1)
    assert rows == [
        [False, False, False, False],
        [False, True, False, False],
        [False, False, True, False],
        [False, False, False, False],
    ]


def test_negative_quiet_zone_rejected():
    with pytest.raises(ValueError):
        with_quiet_zone([[1]], border=-1)


@pytest.mark.parametrize("invert", [False, True])
def test_render_round_trips_to_the_same_modules(invert):
    qr = make_qr("https://example.com/some/path")
    text = to_terminal(qr.matrix, border=4, invert=invert)
    expected = with_quiet_zone(qr.matrix, 4)
    # 21x21 + 8 border = 29 rows, padded to 30 with one light row
    expected.append([False] * len(expected[0]))
    assert parse(text, invert=invert) == expected


def test_render_size():
    qr = make_qr("hi")  # version 1, 21 modules
    lines = to_terminal(qr.matrix, border=2).split("\n")
    assert len(lines) == 13  # (21 + 4 + 1 pad) / 2
    assert all(len(line) == 25 for line in lines)


def test_default_mode_paints_light_modules():
    # One dark module plus the light padding row: only the bottom is painted
    assert to_terminal([[1]], border=0) == LOWER
    assert to_terminal([[0]], border=0) == FULL
    assert to_terminal([[1]], border=0, invert=True) == UPPER


@pytest.mark.parametrize("invert", [False, True])
def test_rendered_text_is_scannable(invert):
    """Paint the terminal output as a real terminal would and decode it."""
    import zxingcpp
    from PIL import Image

    text = to_terminal(make_qr("scan me please").matrix, invert=invert)
    rows = parse(text, invert=invert)
    bg, fg = (0, 255) if not invert else (255, 0)  # dark or light terminal
    painted = [[(m == invert) for m in row] for row in rows]
    img = Image.new("L", (len(rows[0]), len(rows)))
    img.putdata([fg if p else bg for row in painted for p in row])
    img = img.resize((img.width * 8, img.height * 8), Image.NEAREST)
    assert [r.text for r in zxingcpp.read_barcodes(img)] == ["scan me please"]
