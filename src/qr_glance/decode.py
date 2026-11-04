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


def _corners(position) -> list[tuple[int, int]]:
    points = (position.top_left, position.top_right, position.bottom_right, position.bottom_left)
    return [(p.x, p.y) for p in points]


def read_image(path: str | Path) -> list[Found]:
    """Return every QR code zxing can find in the image at ``path``.

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

    return [
        Found(text=r.text, format=r.format.name, corners=_corners(r.position))
        for r in zxingcpp.read_barcodes(gray, formats=_QR_FORMATS)
    ]
