#!/usr/bin/env python3
"""Tiled Chinese OCR for screenshots that exceed Apple Vision's 8192-pixel
dimension limit.

Why: Vision silently downscales (or rejects with "ImageSize invalid for
analysis" via VisionKit) on images taller than 8192 px. Long Chinese notes
on phone screenshots are routinely 10,000–12,000 px tall, so the naive
`VNRecognizeTextRequest` path produces ~30 characters of garbage.

Approach: split the image vertically into overlapping 3500-pixel tiles
(with 250-pixel overlap so characters straddling a boundary appear in
one tile). OCR each tile, then deduplicate lines by trimmed-string
equality (cheap but effective for reading-order Chinese text).

Usage:
    python tiled_ocr.py path/to/tall_screenshot.jpg
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

from vision_ocr_cn import ocr_pil

TILE_H = 3500
OVERLAP = 250
MAX_DIM = 8192


def tiled_ocr(path) -> str:
    img = Image.open(path)
    w, h = img.size
    if w <= MAX_DIM and h <= MAX_DIM:
        return ocr_pil(img)
    # If width is the oversize dim, rotate so tall columns become rows.
    if w > MAX_DIM and h <= MAX_DIM:
        return ocr_pil(img.transpose(Image.ROTATE_270))

    chunks = []
    seen_lines = set()
    y = 0
    while y < h:
        bottom = min(y + TILE_H, h)
        tile = img.crop((0, y, w, bottom))
        tw, th = tile.size
        if tw > MAX_DIM:
            # Extreme-aspect fallback: downscale the tile width.
            ratio = MAX_DIM / tw
            tile = tile.resize((MAX_DIM, int(th * ratio)), Image.LANCZOS)
        text = ocr_pil(tile)
        new_lines = []
        for line in text.split("\n"):
            key = line.strip()
            if not key or key in seen_lines:
                continue
            seen_lines.add(key)
            new_lines.append(line)
        if new_lines:
            chunks.append("\n".join(new_lines))
        if bottom == h:
            break
        y += TILE_H - OVERLAP
    return "\n".join(chunks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", help="path to image")
    args = ap.parse_args()
    print(tiled_ocr(args.image))


if __name__ == "__main__":
    main()
