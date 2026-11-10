#!/usr/bin/env python
"""Numbers for a graded frame: levels, colour casts on neutral patches, skin hue.

Usage:
  python -I measure_grade.py frame.png --patch counter:40,60,200,220 --skin 100,1450,1000,1920

Levels: luma at the 0.5, 50 and 99.5 percentiles, and the share of pixels at 250 or above.
Patches: mean RGB and the cast. On a neutral surface R, G and B should sit within about 3.
Skin: median luma, hue and chroma of skin-like pixels in the region.
Hue is atan2(Cr, Cb) in degrees. The vectorscope skin line sits at about 123.
"""
import argparse

import numpy as np
from PIL import Image


def yuv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return y, (b - y) / 1.8556, (r - y) / 1.5748


def box(text):
    return [int(v) for v in text.split(",")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frame")
    ap.add_argument("--patch", action="append", default=[], help="name:x0,y0,x1,y1")
    ap.add_argument("--skin", action="append", default=[], help="x0,y0,x1,y1")
    a = ap.parse_args()
    img = np.asarray(Image.open(a.frame).convert("RGB"), dtype=float)
    y, _, _ = yuv(img)
    print(
        f"levels Y p0.5 {np.percentile(y, 0.5):.1f}  p50 {np.percentile(y, 50):.1f}  "
        f"p99.5 {np.percentile(y, 99.5):.1f}  at 250+ {(img.max(2) >= 250).mean() * 100:.2f}%"
    )
    for item in a.patch:
        name, coords = item.split(":")
        x0, y0, x1, y1 = box(coords)
        m = img[y0:y1, x0:x1].reshape(-1, 3).mean(0)
        print(f"{name:16s} RGB {m[0]:6.1f} {m[1]:6.1f} {m[2]:6.1f}  R-B {m[0] - m[2]:+.1f}  G-mean {m[1] - (m[0] + m[2]) / 2:+.1f}")
    for coords in a.skin:
        x0, y0, x1, y1 = box(coords)
        yy, cb, cr = yuv(img[y0:y1, x0:x1])
        hue = np.degrees(np.arctan2(cr, cb)) % 360
        chroma = np.hypot(cb, cr)
        mask = (hue > 70) & (hue < 150) & (chroma > 8) & (yy > 40)
        if mask.sum() < 500:
            print(f"skin {coords}: too few skin pixels")
            continue
        print(
            f"skin {coords}: {mask.sum()} px  Y p50 {np.median(yy[mask]):.0f}  "
            f"hue p50 {np.median(hue[mask]):.1f}  chroma p50 {np.median(chroma[mask]):.1f}"
        )


main()
