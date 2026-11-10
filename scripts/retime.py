#!/usr/bin/env python
"""Retime a 60 fps intermediate to 30 fps using real frames, with a smooth speed curve.

Usage:
  python -I retime.py in.mp4 out.mp4 --start 0.6 --frames 96 \
      --keys 0:.6,1.3:.6,1.6:1,2:1,2.4:.5,3.2:.5

--start  seconds into the intermediate where the shot begins
--frames output frames at 30 fps
--keys   output_time:speed pairs, joined linearly. 0:.5 alone is steady half speed.

Speeds at or above 0.5 use only real frames. The script stops if a speed would repeat a frame.
Output is H.264 yuv420p, tagged bt709 tv range, starting at time zero.
"""
import argparse
import subprocess

import numpy as np


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
        stdout=subprocess.PIPE,
        check=True,
        text=True,
    ).stdout
    w, h = out.strip().splitlines()[0].split(",")[:2]
    return int(w), int(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--frames", type=int, required=True)
    ap.add_argument("--keys", default="0:.5")
    ap.add_argument("--src-fps", type=int, default=60)
    a = ap.parse_args()
    fps = 30
    pairs = [tuple(float(v) for v in k.split(":")) for k in a.keys.split(",")]
    t = np.arange(a.frames) / fps
    speed = np.interp(t, [p[0] for p in pairs], [p[1] for p in pairs])
    source = np.concatenate([[0], np.cumsum(speed[:-1] / fps)]) + a.start
    index = [int(round(s * a.src_fps)) for s in source]
    if any(b <= c for c, b in zip(index, index[1:])):
        raise SystemExit("A frame would repeat. Keep speed at 0.5 or above, or use a higher source frame rate.")
    want = set(index)
    w, h = probe(a.input)
    size = w * h * 3 // 2
    dec = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", a.input, "-f", "rawvideo", "-pix_fmt", "yuv420p", "-"],
        stdout=subprocess.PIPE,
    )
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-g", "15", "-bf", "0", "-pix_fmt", "yuv420p",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", a.output],
        stdin=subprocess.PIPE,
    )
    n = 0
    wrote = 0
    while True:
        chunk = dec.stdout.read(size)
        if len(chunk) < size:
            break
        if n in want:
            enc.stdin.write(chunk)
            wrote += 1
        n += 1
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print(f"read {n}, wrote {wrote} of {len(index)}, source {index[0] / a.src_fps:.2f} to {index[-1] / a.src_fps:.2f} s")
    if wrote != len(index):
        raise SystemExit("The intermediate is too short for these settings.")


main()
