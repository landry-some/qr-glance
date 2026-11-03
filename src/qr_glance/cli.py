"""Command-line entry point for ``qrg``."""

import argparse
import sys

from qr_glance import __version__
from qr_glance.encode import ERROR_LEVELS, make_qr
from qr_glance.render import to_terminal

IMAGE_TYPES = (".png", ".svg")


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
    parser.add_argument(
        "-o", "--output", metavar="FILE",
        help="save as an image instead of printing (.png or .svg)",
    )
    parser.add_argument(
        "--scale", type=int, default=10, metavar="PX",
        help="pixels per module in saved images (default: 10)",
    )


def _emit(qr, args) -> int:
    if args.output is None:
        print(to_terminal(qr.matrix, border=args.border, invert=args.invert))
        return 0

    if not args.output.lower().endswith(IMAGE_TYPES):
        print(f"qrg: output must end in {' or '.join(IMAGE_TYPES)}", file=sys.stderr)
        return 2
    if args.scale < 1:
        print("qrg: --scale must be at least 1", file=sys.stderr)
        return 2
    if args.border < 0:
        raise ValueError("quiet zone can't be negative")
    # Files are always dark-on-light; --invert only matters for the terminal.
    qr.save(args.output, scale=args.scale, border=args.border)
    print(f"saved {args.output} ({qr.designator}, {qr.symbol_size(scale=args.scale, border=args.border)[0]} px)")
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
    except OSError as exc:
        print(f"qrg: {exc.filename or ''}: {exc.strerror or exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
