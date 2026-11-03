"""Command-line entry point for ``qrg``."""

import argparse
import sys

from qr_glance import __version__
from qr_glance.encode import ERROR_LEVELS, make_qr
from qr_glance.render import to_terminal


def _read_data(text: str | None) -> str:
    if text is not None and text != "-":
        return text
    data = sys.stdin.read()
    # Drop the single newline that `echo` and heredocs add.
    return data[:-1] if data.endswith("\n") else data


def _add_render_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-e", "--error", default="M", type=str.upper, choices=ERROR_LEVELS,
        help="error correction level (default: M)",
    )
    parser.add_argument(
        "--invert", action="store_true",
        help="for terminals with a light background",
    )
    parser.add_argument(
        "--border", type=int, default=4, metavar="N",
        help="quiet zone width in modules (default: 4)",
    )


def _emit(qr, args) -> int:
    print(to_terminal(qr.matrix, border=args.border, invert=args.invert))
    return 0


def cmd_make(args) -> int:
    data = _read_data(args.text)
    if not data:
        print("qrg: nothing to encode", file=sys.stderr)
        return 2
    return _emit(make_qr(data, error=args.error), args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qrg", description="Make QR codes in the terminal and read them from images.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    make = sub.add_parser("make", help="encode text as a QR code")
    make.add_argument("text", nargs="?", help="text to encode (default: read stdin)")
    _add_render_options(make)
    make.set_defaults(func=cmd_make)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ValueError as exc:
        # segno raises a ValueError subclass when data doesn't fit, and we do for bad input
        print(f"qrg: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
