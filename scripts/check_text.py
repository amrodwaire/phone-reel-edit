#!/usr/bin/env python
"""Check on-screen text from flat probe frames: each line in its own colour on black.

Usage:
  python -I check_text.py [--gap 14] [--platform instagram] probe0.png probe1.png ...
  python -I check_text.py probe0.png probe1.png --real shot0.png shot1.png

Line colours, in stack order: red, green, blue, yellow, magenta, cyan, white. Seven lines a frame at most.
Fails when the ink of two neighbouring lines comes closer than --gap px,
or when any letter leaves the safe box.

--platform picks the safe box: instagram (default), tiktok, shorts, or all (the part safe on all three).
           Only the instagram box was tested on a published reel. The others come from third-party
           guides, because TikTok and YouTube publish no numbers for organic posts.
--box      x0,y0,x1,y1 overrides the platform box. For a cover use --box 110,240,970,1680,
           the part of the cover the profile grid shows.
--real     the real frame for each probe frame, same order, with every line fully on screen.
           Compares each line's colour with the picture right around its letters and fails
           under --min-contrast (3.0, the WCAG figure for large text).
"""
import argparse
import sys

import numpy as np
from PIL import Image, ImageFilter

PALETTE = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)]
BOXES = {
    "instagram": (110, 220, 950, 1475),
    "tiktok": (60, 200, 920, 1550),
    "shorts": (60, 200, 880, 1540),
    "all": (110, 220, 880, 1475),
}


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


def grow(mask, px):
    """The mask widened by px in every direction (px < 0 shrinks it)."""
    img = Image.fromarray((mask * 255).astype(np.uint8))
    size = 2 * abs(px) + 1
    img = img.filter(ImageFilter.MaxFilter(size) if px > 0 else ImageFilter.MinFilter(size))
    return np.asarray(img) > 127


def luminance(rgb):
    c = rgb / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return lin @ np.array([0.2126, 0.7152, 0.0722])


def contrast(real, ink, all_ink):
    """WCAG contrast between a line's letters and the hardest part of the picture around them."""
    core = grow(ink, -2)
    if core.sum() < 30:
        core = ink
    ring = grow(ink, 14) & ~grow(all_ink, 3)
    if ring.sum() < 30:
        return None
    text = float(np.median(luminance(real[core])))
    around = luminance(real[ring])
    # Light text is hardest to read over the brightest surroundings, dark text over the darkest.
    back = float(np.percentile(around, 90 if text > np.median(around) else 10))
    hi, lo = max(text, back), min(text, back)
    return (hi + 0.05) / (lo + 0.05)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", type=int, default=14)
    ap.add_argument("--platform", choices=sorted(BOXES), default="instagram")
    ap.add_argument("--box")
    ap.add_argument("--real", nargs="+", default=[])
    ap.add_argument("--min-contrast", type=float, default=3.0)
    ap.add_argument("frames", nargs="+")
    a = ap.parse_args()
    x0, y0, x1, y1 = [int(v) for v in a.box.split(",")] if a.box else BOXES[a.platform]
    if a.real and len(a.real) != len(a.frames):
        sys.exit("--real needs one real frame for each probe frame, in the same order.")
    print(f"safe box x {x0}-{x1} y {y0}-{y1}")
    bad = 0
    for n, f in enumerate(a.frames):
        ms = masks(f)
        print(f"{f}: {len(ms)} lines")
        if not ms:
            continue
        real = None
        if a.real:
            real = np.asarray(Image.open(a.real[n]).convert("RGB"), dtype=float)
            if real.shape[:2] != ms[0].shape:
                sys.exit(f"{a.real[n]} is not the same size as {f}.")
            all_ink = np.any(ms, axis=0)
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
            if real is not None:
                c = contrast(real, m, all_ink)
                if c is not None:
                    weak = c < a.min_contrast
                    bad += weak
                    print(f"    contrast {c:.1f}{'  HARD TO READ' if weak else ''}")
    print("PASS" if not bad else f"FAIL: {bad} problems")
    sys.exit(1 if bad else 0)


main()
