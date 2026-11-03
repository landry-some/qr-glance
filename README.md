# qr-glance

`qrg` is a small command-line tool for QR codes. It draws a QR code straight in
the terminal so you can scan it with a phone, saves it as PNG or SVG, and reads
the text back out of image files such as screenshots.

## Who it's for

People who live in a terminal and keep needing to move a URL, a snippet of text
or a Wi-Fi password between their computer and their phone, without pasting it
into a QR website or pointing a phone at their own screen to read a screenshot.

## Built with

- Python 3.11+
- [segno](https://pypi.org/project/segno/) to encode the QR symbol
- [zxing-cpp](https://pypi.org/project/zxing-cpp/) and [Pillow](https://pypi.org/project/pillow/) to decode images
- pytest for tests

All three runtime libraries install as wheels, so no system packages (zbar,
OpenCV) are needed.

## Status

v0.1 in progress. Planned work is in [ROADMAP.md](ROADMAP.md).

## License

MIT, see [LICENSE](LICENSE).
