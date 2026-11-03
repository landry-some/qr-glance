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

## Install

Needs Python 3.11 or newer.

```bash
git clone https://github.com/landry-some/qr-glance.git
cd qr-glance
python3 -m venv .venv
.venv/bin/pip install -e .
```

This puts the `qrg` command in `.venv/bin/`. Activate the venv
(`source .venv/bin/activate`) or call `.venv/bin/qrg` directly.

## Usage

### Print a QR code in the terminal

```bash
qrg make "https://example.com/some/page"
echo "text from a pipe" | qrg make
```

The code is drawn with Unicode half-block characters, two modules per
character cell. By default it assumes a dark terminal background. On a light
background, add `--invert` so the phone sees dark modules on a light field.

Options for `make` (and `wifi`):

| Option | Meaning |
|---|---|
| `-e, --error L\|M\|Q\|H` | error correction level, default `M` |
| `--invert` | for light-background terminals |
| `--border N` | quiet zone in modules, default `4` |
| `-o, --output FILE` | save to `FILE.png` or `FILE.svg` instead of printing |
| `--scale PX` | pixels per module in saved images, default `10` |

Short text always gets a regular QR code, never a Micro QR, because most
phone cameras ignore Micro QR.

### Save an image

```bash
qrg make "https://example.com" -o link.png --scale 8
qrg make "some text" -o code.svg
```

### Share a Wi-Fi network

```bash
qrg wifi --ssid HomeNet            # prompts for the password
qrg wifi --ssid Cafe --security nopass
qrg wifi --ssid HomeNet --hidden -o wifi.png
```

Phone cameras on iOS and Android offer to join the network when they scan it.
`--security` is `WPA` (also WPA2/WPA3, the default), `WEP` or `nopass`. Leave
out `--password` and `qrg` asks for it, so it doesn't end up in your shell
history.

### Read codes from images

```bash
qrg read examples/sample-url.png
qrg read screenshot.png photo.jpg       # prefixes each result with the file name
qrg read --json screenshot.png          # text, format and corner points
```

Every QR code found is printed on its own line. Any format Pillow can open
works (PNG, JPEG, GIF, BMP, WebP, ...), and light-on-dark codes are found too.

Exit codes for `read`: `0` every file had a code, `1` at least one file had
none, `2` a file was missing or not an image.

## Run the tests

```bash
.venv/bin/pip install -e '.[test]'
.venv/bin/pytest
```

The tests render codes, save them, and decode them again with zxing-cpp, so no
network or extra fixtures are needed.

## Status

v0.1: `make`, `wifi` and `read` work. Planned work is in
[ROADMAP.md](ROADMAP.md).

## License

MIT, see [LICENSE](LICENSE).
