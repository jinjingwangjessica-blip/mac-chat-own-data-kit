# Setup

macOS 14+, Apple Silicon, Xcode Command Line Tools installed.

## 1. Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install cryptography zstandard pyobjc pillow
```

## 2. ffmpeg (for video thumbnails and voice conversion)

```bash
brew install ffmpeg
```

## 3. SIP (System Integrity Protection)

Memory reading requires SIP disabled. **Re-enable when you're done.**

```bash
# Reboot to Recovery Mode (hold power until "Options" on Apple Silicon).
# Open Terminal from the Utilities menu, then:
csrutil disable
# Reboot.

# After finishing all extraction work:
csrutil enable
```

## 4. Python 3.9 for lldb

The key-extraction step needs lldb Python bindings. Xcode ships a
compatible Python 3.9 at:

```
/Applications/Xcode.app/Contents/Developer/usr/bin/python3
```

Call `find_key_memscan.py` with that interpreter and lldb on PYTHONPATH:

```bash
PYTHONPATH=$(lldb -P) /Applications/Xcode.app/Contents/Developer/usr/bin/python3 \
    scripts/find_key_memscan.py --process MyClient --db-dir <path> --out keys.json
```

Other scripts (`decrypt_db_pure.py`, `parse_messages.py`, `vision_ocr_cn.py`,
`tiled_ocr.py`) work with regular Python 3.10+ in the venv.

## 5. Installing PyObjC if Apple Vision OCR fails

`pip install pyobjc` pulls a large dep tree. If you only need the Vision
and Quartz bits:

```bash
pip install pyobjc-framework-Vision pyobjc-framework-Quartz \
            pyobjc-framework-Cocoa
```

## Troubleshooting

- **`csrutil: command not found`** — you're not in Recovery Mode.
- **lldb attach "no memory regions found"** — wrong Python interpreter,
  or SIP still enabled. Verify both.
- **`ocrmac` refuses `zh-Hans`** — expected; use our `vision_ocr_cn.py`
  instead.
- **`ImageSize W: ... H: ... is invalid for analysis`** — screenshot
  exceeds 8192 px; use `tiled_ocr.py`.
- **`pip install cryptography` fails** — ensure Xcode CLT is installed:
  `xcode-select --install`.
