"""Command-line entry point for ``qrg``."""

import argparse
import getpass
import json
import sys

from qr_glance import __version__
from qr_glance.decode import UnreadableImage, read_image
from qr_glance.encode import ERROR_LEVELS, make_qr
from qr_glance.payloads import SECURITY_TYPES, wifi_payload
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


def cmd_wifi(args) -> int:
    password = args.password
    if password is None and args.security != "nopass":
        # Prompting keeps the password out of shell history.
        password = getpass.getpass(f"Password for {args.ssid}: ")
    payload = wifi_payload(args.ssid, password, security=args.security, hidden=args.hidden)
    return _emit(make_qr(payload, error=args.error), args)


def cmd_read(args) -> int:
    status = 0
    records = []
    prefix = len(args.images) > 1
    for path in args.images:
        try:
            found = read_image(path)
        except UnreadableImage as exc:
            print(f"qrg: {exc}", file=sys.stderr)
            status = 2
            continue
        if not found:
            print(f"qrg: {path}: no QR code found", file=sys.stderr)
            status = max(status, 1)
        for code in found:
            if args.json:
                records.append({"file": path, "text": code.text, "format": code.format,
                                "corners": [list(p) for p in code.corners]})
            else:
                print(f"{path}: {code.text}" if prefix else code.text)
    if args.json:
        print(json.dumps(records, indent=2, ensure_ascii=False))
    return status


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

    wifi = sub.add_parser("wifi", help="QR code that joins a Wi-Fi network when scanned")
    wifi.add_argument("--ssid", required=True, help="network name")
    wifi.add_argument("--password", help="network password (default: prompt for it)")
    wifi.add_argument(
        "--security", default="WPA", choices=SECURITY_TYPES,
        help="WPA covers WPA2/WPA3; nopass is an open network (default: WPA)",
    )
    wifi.add_argument("--hidden", action="store_true", help="the network doesn't broadcast its name")
    _add_render_options(wifi)
    wifi.set_defaults(func=cmd_wifi)

    read = sub.add_parser("read", help="decode QR codes from image files")
    read.add_argument("images", nargs="+", metavar="IMAGE", help="PNG, JPEG, ... files to scan")
    read.add_argument("--json", action="store_true", help="print results as JSON with corner points")
    read.set_defaults(func=cmd_read)

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
