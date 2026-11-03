"""Draw a QR matrix with Unicode half-block characters.

Each character cell holds two modules stacked vertically, which keeps the code
roughly square in a terminal font and half as tall as one row per module.

A terminal can only paint the foreground colour, so we paint whichever modules
match the foreground. On the usual dark-background terminal the foreground is
light, so we paint the light modules and leave the dark ones as background.
``invert=True`` flips that for light-background terminals.
"""

from collections.abc import Sequence

# (top painted, bottom painted) -> character
_CELLS = {
    (False, False): " ",
    (True, False): "▀",  # upper half block
    (False, True): "▄",  # lower half block
    (True, True): "█",  # full block
}


def with_quiet_zone(matrix: Sequence[Sequence[int]], border: int) -> list[list[bool]]:
    """Return the matrix as booleans (True = dark) surrounded by ``border`` light modules."""
    if border < 0:
        raise ValueError("quiet zone can't be negative")
    width = len(matrix[0]) + 2 * border
    blank = [False] * width
    rows = [list(blank) for _ in range(border)]
    for row in matrix:
        rows.append([False] * border + [bool(m) for m in row] + [False] * border)
    rows.extend(list(blank) for _ in range(border))
    return rows


def to_terminal(matrix: Sequence[Sequence[int]], border: int = 4, invert: bool = False) -> str:
    """Render ``matrix`` (truthy = dark module) as lines of half-block characters."""
    rows = with_quiet_zone(matrix, border)
    if len(rows) % 2:
        # Pad with a light row so the last line still has a bottom half.
        rows.append([False] * len(rows[0]))

    lines = []
    for top, bottom in zip(rows[0::2], rows[1::2]):
        # Paint light modules normally, dark ones when inverted.
        lines.append("".join(_CELLS[(t == invert, b == invert)] for t, b in zip(top, bottom)))
    return "\n".join(lines)
