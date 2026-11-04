"""Turn text into a QR symbol."""

import segno

ERROR_LEVELS = ("L", "M", "Q", "H")

# Bytes a version 40 code holds in byte mode at each error level
_MAX_BYTES = {"L": 2953, "M": 2331, "Q": 1663, "H": 1273}


def make_qr(data: str, error: str = "M") -> segno.QRCode:
    """Encode ``data`` as a regular (non-micro) QR code at exactly ``error`` level.

    segno would otherwise pick a Micro QR for short text, which many phone
    cameras can't scan, and silently raise the error level when there is room.
    """
    level = error.upper()
    if level not in ERROR_LEVELS:
        raise ValueError(f"error level must be one of {', '.join(ERROR_LEVELS)}, got {error!r}")
    try:
        return segno.make(data, error=level, micro=False, boost_error=False)
    except segno.DataOverflowError:
        size = len(data.encode("utf-8"))
        hint = " (try -e L)" if level != "L" and size <= _MAX_BYTES["L"] else ""
        raise ValueError(
            f"data is too long for a QR code: {size} bytes, the limit at level {level} "
            f"is {_MAX_BYTES[level]} bytes of text{hint}"
        ) from None
