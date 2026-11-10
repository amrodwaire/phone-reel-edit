#!/usr/bin/env python
"""Check on-screen text from flat probe frames: each line in its own colour on black.

Usage: python -I check_text.py [--gap 14] [--box 110,220,950,1475] probe0.png probe1.png ...
Line colours, in stack order: red, green, blue, yellow, magenta, cyan.
Fails when the ink of two neighbouring lines comes closer than --gap px,
or when any letter leaves the safe box.
"""
import argparse
import sys

import numpy as np
from PIL import Image

PALETTE = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]


def masks(path):
    a = np.asarray(Image.open(path).convert("RGB")) > 110
    out = []
    for p in PALETTE:
        m = np.ones(a.shape[:2], bool)
        for c in range(3):
            m &= a[..., c] == bool(p[c])
        if m.sum() > 50:
            out.append(m)
    return out


def column_gap(upper, lower):
    """Smallest vertical distance between two inks, looking 6 px to each side of every column."""
    best = None
    h, w = upper.shape
    has_upper = upper.any(0)
    has_lower = lower.any(0)
    bottoms = h - 1 - np.argmax(upper[::-1], axis=0)
    tops = np.argmax(lower, axis=0)
    for x in np.where(has_upper)[0]:
        for nx in range(max(0, x - 6), min(w, x + 7)):
            if has_lower[nx]:
                gap = int(tops[nx]) - int(bottoms[x]) - 1
                best = gap if best is None else min(best, gap)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", type=int, default=14)
    ap.add_argument("--box", default="110,220,950,1475")
    ap.add_argument("frames", nargs="+")
    a = ap.parse_args()
    x0, y0, x1, y1 = [int(v) for v in a.box.split(",")]
    bad = 0
    for f in a.frames:
        ms = masks(f)
        print(f"{f}: {len(ms)} lines")
        for i, m in enumerate(ms):
            ys, xs = np.where(m)
            inside = xs.min() >= x0 and xs.max() <= x1 and ys.min() >= y0 and ys.max() <= y1
            bad += not inside
            note = "" if inside else "  OUTSIDE BOX"
            print(f"  line {i}: x {xs.min()}-{xs.max()} y {ys.min()}-{ys.max()}{note}")
            if i:
                g = column_gap(ms[i - 1], m)
                clear = g is None or g >= a.gap
                bad += not clear
                note = "" if clear else "  TOO CLOSE"
                print(f"    gap to line {i - 1}: {g}{note}")
    print("PASS" if not bad else f"FAIL: {bad} problems")
    sys.exit(1 if bad else 0)


main()
