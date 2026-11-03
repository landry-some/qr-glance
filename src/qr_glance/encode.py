"""Turn text into a QR symbol."""

import segno

ERROR_LEVELS = ("L", "M", "Q", "H")


def make_qr(data: str, error: str = "M") -> segno.QRCode:
    """Encode ``data`` as a regular (non-micro) QR code at exactly ``error`` level.

    segno would otherwise pick a Micro QR for short text, which many phone
    cameras can't scan, and silently raise the error level when there is room.
    """
    level = error.upper()
    if level not in ERROR_LEVELS:
        raise ValueError(f"error level must be one of {', '.join(ERROR_LEVELS)}, got {error!r}")
    return segno.make(data, error=level, micro=False, boost_error=False)
