"""Find and decode QR codes in image files."""

import io
import sys
from dataclasses import dataclass
from pathlib import Path

import zxingcpp
from PIL import Image, UnidentifiedImageError

_QR_FORMATS = (
    zxingcpp.BarcodeFormat.QRCode,
    zxingcpp.BarcodeFormat.MicroQRCode,
    zxingcpp.BarcodeFormat.RMQRCode,
)


class UnreadableImage(Exception):
    """The file is missing or isn't an image Pillow can open."""


@dataclass
class Found:
    text: str
    format: str
    # Corner points, clockwise from the top-left of the symbol
    corners: list[tuple[int, int]]
    # Raw payload; ``binary`` is True when it isn't text, so ``text`` is garbled
    data: bytes = b""
    binary: bool = False


def _corners(position) -> list[tuple[int, int]]:
    points = (position.top_left, position.top_right, position.bottom_right, position.bottom_left)
    return [(p.x, p.y) for p in points]


def read_image(path: str | Path) -> list[Found]:
    """Return every QR code zxing can find in the image at ``path``.

    Codes come in reading order: top to bottom, then left to right.
    A ``path`` of ``-`` reads the image bytes from stdin.
    """
    source = path
    if str(path) == "-":
        source, path = io.BytesIO(sys.stdin.buffer.read()), "stdin"
    try:
        with Image.open(source) as img:
            # Grayscale sidesteps palette and alpha modes zxing can't take directly.
            gray = img.convert("L")
    except FileNotFoundError as exc:
        raise UnreadableImage(f"{path}: no such file") from exc
    except IsADirectoryError as exc:
        raise UnreadableImage(f"{path}: is a directory") from exc
    except (UnidentifiedImageError, OSError) as exc:
        raise UnreadableImage(f"{path}: not a readable image") from exc

    found = [
        Found(text=r.text, format=r.format.name, corners=_corners(r.position),
              data=r.bytes, binary=r.content_type == zxingcpp.ContentType.Binary)
        for r in zxingcpp.read_barcodes(gray, formats=_QR_FORMATS)
    ]
    # zxing's own order depends on where its scan happens to hit first.
    return _reading_order(found)


def _reading_order(codes: list[Found]) -> list[Found]:
    """Sort codes into rows, top row first, each row left to right.

    A code joins the current row when its centre is above that row's lowest
    edge, so codes in a slightly tilted photo still count as one row.
    """
    rows: list[list[Found]] = []
    bottom = None
    for code in sorted(codes, key=lambda c: min(y for _, y in c.corners)):
        ys = [y for _, y in code.corners]
        if bottom is not None and (min(ys) + max(ys)) / 2 < bottom:
            rows[-1].append(code)
            bottom = max(bottom, max(ys))
        else:
            rows.append([code])
            bottom = max(ys)
    return [code for row in rows for code in sorted(row, key=lambda c: min(x for x, _ in c.corners))]
