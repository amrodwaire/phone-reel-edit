#!/usr/bin/env python
"""Colour correction without opening DaVinci Resolve: build a 3D LUT from numbers, apply it with ffmpeg.

It covers whole-frame moves only: balance, lift, gamma, contrast, saturation and a highlight knee.
A fix for one part of the frame (a Power Window) still needs Resolve.
A .cube exported from Resolve (right-click a thumbnail, Generate LUT) works with `apply` and `still` too.

Usage:
  python -I grade.py still clip.mp4 1.5 before.png
  python -I grade.py make look.cube --frame before.png --neutral 40,60,200,220 --white 205 \
      --contrast 1.06 --pivot 0.4 --lift -0.02 --sat 1.05
  python -I grade.py still clip.mp4 1.5 check.png --lut look.cube --compare
  python -I grade.py apply clip.mp4 graded.mp4 --lut look.cube

make   --neutral is a patch that should be grey or white. Its R, G and B are made equal.
       --white sets the level that patch ends at (0-255). Without it the patch keeps its brightness.
       --gain r,g,b multiplies the channels by hand instead. --gamma takes one value or r,g,b.
       --knee 0.85 bends values above it towards 1.0, so a gain does not clip the highlights hard.
still  writes one frame as PNG. --compare puts the source on the left and the graded frame on the right.
apply  writes H.264 yuv420p tagged bt709, tv range. --denoise light|medium runs before the LUT,
       --sharpen 0.1-0.6 runs after it.

The order inside the LUT is: gain, lift, gamma, contrast around the pivot, saturation, knee.
All of it works on the encoded 0-1 values, which is how Resolve's primaries behave in a project
without colour management.
"""
import argparse
import json
import os
import subprocess

import numpy as np

SIZE = 33
LUMA = np.array([0.2126, 0.7152, 0.0722])
DENOISE = {"light": "hqdn3d=2:1.5:3:3", "medium": "hqdn3d=4:3:6:4.5"}


def triple(text):
    parts = [float(v) for v in str(text).split(",")]
    return np.array(parts * 3 if len(parts) == 1 else parts)


def make(a):
    gain = triple(a.gain)
    if a.neutral:
        from PIL import Image

        x0, y0, x1, y1 = [int(v) for v in a.neutral.split(",")]
        img = np.asarray(Image.open(a.frame).convert("RGB"), dtype=float)
        mean = img[y0:y1, x0:x1].reshape(-1, 3).mean(0)
        target = a.white if a.white else float(mean @ LUMA)
        gain = gain * target / mean
        print(f"patch RGB {mean[0]:.1f} {mean[1]:.1f} {mean[2]:.1f} -> {target:.1f}")
    print(f"gain R {gain[0]:.3f} G {gain[1]:.3f} B {gain[2]:.3f}")
    gamma = triple(a.gamma)
    axis = np.linspace(0, 1, SIZE)
    # .cube order: red changes fastest, then green, then blue.
    b, g, r = np.meshgrid(axis, axis, axis, indexing="ij")
    rgb = np.stack([r, g, b], -1).reshape(-1, 3)
    rgb = rgb * gain
    rgb = rgb + a.lift * (1 - rgb)
    rgb = np.clip(rgb, 0, None) ** (1 / gamma)
    rgb = (rgb - a.pivot) * a.contrast + a.pivot
    y = (rgb @ LUMA)[:, None]
    rgb = y + (rgb - y) * a.sat
    if a.knee:
        k = a.knee
        over = rgb > k
        rgb = np.where(over, k + (1 - k) * np.tanh((rgb - k) / (1 - k)), rgb)
    rgb = np.clip(rgb, 0, 1)
    with open(a.cube, "w", encoding="ascii", newline="\n") as f:
        f.write(f"TITLE \"grade.py\"\nLUT_3D_SIZE {SIZE}\n")
        for row in rgb:
            f.write(f"{row[0]:.6f} {row[1]:.6f} {row[2]:.6f}\n")
    print(f"wrote {a.cube}")


def source_tags(path):
    """Matrix and range of the source. Untagged video is treated as bt709 tv range, not ffmpeg's bt601 default."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_space,color_range,color_transfer", "-of", "json", path],
        stdout=subprocess.PIPE,
        check=True,
        text=True,
    ).stdout
    s = json.loads(out)["streams"][0]
    if s.get("color_transfer") in ("arib-std-b67", "smpte2084"):
        raise SystemExit("HDR source. Transform it to Rec.709 first (probe_source.py prints the filter).")
    matrix = s.get("color_space", "unknown")
    matrix = {"unknown": "bt709", "bt470bg": "bt601", "smpte170m": "bt601"}.get(matrix, matrix)
    rng = {"pc": "pc", "tv": "tv"}.get(s.get("color_range", "tv"), "tv")
    return matrix, rng


def chain(path, lut, denoise=None, sharpen=0.0):
    matrix, rng = source_tags(path)
    steps = []
    if denoise:
        steps.append(DENOISE[denoise])
    steps.append(f"scale=in_color_matrix={matrix}:in_range={rng}:out_range=pc,format=gbrp")
    if lut:
        # ffmpeg reads ':' in a filter value as a separator, so run from the LUT's folder and pass the bare name.
        steps.append(f"lut3d=file={os.path.basename(lut)}:interp=tetrahedral")
    if sharpen:
        steps.append(f"cas=strength={sharpen}")
    return steps, (os.path.dirname(os.path.abspath(lut)) if lut else None)


def still(a):
    steps, cwd = chain(a.input, a.lut)
    src = os.path.abspath(a.input)
    out = os.path.abspath(a.output)
    if a.compare and a.lut:
        plain, _ = chain(a.input, None)
        graph = f"[0:v]split[a][b];[a]{','.join(plain)}[l];[b]{','.join(steps)}[r];[l][r]hstack"
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(a.time), "-i", src, "-filter_complex", graph, "-frames:v", "1", out]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(a.time), "-i", src, "-vf", ",".join(steps), "-frames:v", "1", out]
    subprocess.run(cmd, check=True, cwd=cwd)
    print(f"wrote {a.output}")


def apply(a):
    steps, cwd = chain(a.input, a.lut, a.denoise, a.sharpen)
    steps.append("scale=in_range=pc:out_color_matrix=bt709:out_range=tv,format=yuv420p")
    cmd = [
        "ffmpeg", "-v", "error", "-y", "-i", os.path.abspath(a.input), "-vf", ",".join(steps),
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf), "-pix_fmt", "yuv420p",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
        os.path.abspath(a.output),
    ]
    subprocess.run(cmd, check=True, cwd=cwd)
    print(f"wrote {a.output}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("cube")
    m.add_argument("--frame")
    m.add_argument("--neutral", help="x0,y0,x1,y1 of a patch that should be grey or white")
    m.add_argument("--white", type=float, help="level the neutral patch ends at, 0-255")
    m.add_argument("--gain", default="1")
    m.add_argument("--lift", type=float, default=0.0)
    m.add_argument("--gamma", default="1")
    m.add_argument("--contrast", type=float, default=1.0)
    m.add_argument("--pivot", type=float, default=0.435)
    m.add_argument("--sat", type=float, default=1.0)
    m.add_argument("--knee", type=float, default=0.0)
    m.set_defaults(run=make)
    s = sub.add_parser("still")
    s.add_argument("input")
    s.add_argument("time", type=float)
    s.add_argument("output")
    s.add_argument("--lut")
    s.add_argument("--compare", action="store_true")
    s.set_defaults(run=still)
    p = sub.add_parser("apply")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--lut")
    p.add_argument("--denoise", choices=sorted(DENOISE))
    p.add_argument("--sharpen", type=float, default=0.0)
    p.add_argument("--crf", type=int, default=12)
    p.set_defaults(run=apply)
    a = ap.parse_args()
    if a.cmd == "make" and a.neutral and not a.frame:
        raise SystemExit("--neutral needs --frame")
    a.run(a)


main()
