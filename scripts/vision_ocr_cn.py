#!/usr/bin/env python3
"""Apple Vision OCR for Chinese images — the direct PyObjC path.

Why not just use `ocrmac`:
  The `ocrmac` PyPI wrapper validates `language_preference` against a
  hardcoded list of six Latin languages and raises `ValueError` on
  `zh-Hans`. This bypasses the wrapper and talks to Vision directly so
  Simplified/Traditional Chinese actually works.

Requires:
    pip install pyobjc Pillow

Usage as library:
    from vision_ocr_cn import ocr_image
    text = ocr_image("/path/to/photo.jpg")
"""

import io
import sys
from pathlib import Path

from PIL import Image
import Quartz
from Vision import VNImageRequestHandler, VNRecognizeTextRequest
from Foundation import NSData


def ocr_pil(pil_img, languages=("zh-Hans", "zh-Hant", "en-US"),
            accurate: bool = True, correct: bool = True) -> str:
    """Run Vision OCR on a PIL image. Returns line-joined plaintext."""
    buf = io.BytesIO()
    pil_img.convert("RGB").save(buf, format="PNG")
    ns_data = NSData.dataWithBytes_length_(buf.getvalue(), buf.tell())
    src = Quartz.CGImageSourceCreateWithData(ns_data, None)
    if src is None:
        return ""
    cg_image = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    if cg_image is None:
        return ""

    req = VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(0 if accurate else 1)
    req.setUsesLanguageCorrection_(bool(correct))
    req.setRecognitionLanguages_(list(languages))

    handler = VNImageRequestHandler.alloc().initWithCGImage_options_(cg_image, None)
    ok, err = handler.performRequests_error_([req], None)
    if not ok:
        return ""

    out = []
    for obs in (req.results() or []):
        cands = obs.topCandidates_(1)
        if cands and len(cands):
            s = cands[0].string()
            if s:
                out.append(str(s))
    return "\n".join(out)


def ocr_image(path) -> str:
    img = Image.open(path)
    return ocr_pil(img)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: vision_ocr_cn.py <image>")
        sys.exit(1)
    text = ocr_image(sys.argv[1])
    print(text)
