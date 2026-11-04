# Roadmap

Planned work after v0.1. Estimates are rough, in hours.

## Features

- [ ] Payload helpers for URL, email, geo location and vCard contacts (3 h)
- [ ] `qrg read --clipboard` to decode an image copied to the clipboard (3 h)
- [ ] Read image bytes from stdin (`maim -s | qrg read -`) (1 h)
- [ ] Real pixel output in terminals with the kitty graphics protocol or sixel (4 h)
- [ ] ASCII-only render mode for terminals without Unicode block characters (1 h)
- [ ] Compact quarter-block render mode that fits bigger codes in small windows (2 h)
- [ ] Batch generation: one image per line of a text or CSV file (2 h)
- [ ] PDF and EPS output (1 h)
- [ ] `--copy` to put the generated PNG on the clipboard (2 h)

## Bugs and edge cases

- [x] Clear error message when the data is too long for any QR version (1 h)
- [ ] Warn when the code is wider than the terminal instead of wrapping it (1 h)
- [ ] Stable ordering when one image holds several codes (top-left first) (1 h)
- [ ] Preprocessing for low-contrast, blurry or rotated photos before decoding (2 h)
- [ ] Binary (non-UTF-8) payloads: print them as hex or base64 instead of failing (1 h)
- [ ] Handle `NO_COLOR` and dumb terminals when rendering (1 h)

## Refactors

- [ ] Move renderers behind a small interface so new modes don't touch the CLI (1 h)
- [ ] Config file (`~/.config/qr-glance/config.toml`) for default error level, scale and invert (2 h)

## Tests

- [ ] Golden-file tests for each render mode (1 h)
- [ ] Hypothesis round-trip tests: random text, make an image, read it back (2 h)
- [ ] GitHub Actions CI on Linux, macOS and Windows (2 h)

## Docs

- [ ] Usage examples in `--help` for every subcommand (1 h)
- [ ] Shell completions for bash, zsh and fish (1 h)
- [ ] README demo screenshots of the terminal output (1 h)
- [ ] Man page generated from the argparse definitions (1 h)

Total: about 38 hours.
