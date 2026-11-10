#!/usr/bin/env python
"""Find where to start a music track so its onsets land on the video cuts.

Usage:
  python -I beat_offset.py music.ogg --cuts 3.3,6.5,10.3 --length 13.5 --from 0 --to 40

Prints the five best start offsets in seconds, with a score. Higher is better.
The score only sees attacks in the sound, so listen to the result before using it.
"""
import argparse
import subprocess

import numpy as np

SR = 22050
HOP = 256


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--cuts", required=True)
    ap.add_argument("--length", type=float, required=True)
    ap.add_argument("--from", dest="start", type=float, default=0.0)
    ap.add_argument("--to", type=float, default=60.0)
    a = ap.parse_args()
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", a.audio, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        stdout=subprocess.PIPE,
        check=True,
    ).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    n = len(x) // HOP
    energy = np.array([np.sqrt((x[i * HOP : i * HOP + 1024] ** 2).mean() + 1e-9) for i in range(n)])
    onset = np.maximum(0, np.diff(np.log(energy + 1e-3), prepend=0))
    onset = np.convolve(onset, np.ones(4) / 4, "same")
    dt = HOP / SR
    total = len(x) / SR
    cuts = [float(c) for c in a.cuts.split(",")]
    results = []
    for off in np.arange(a.start, min(a.to, total - a.length), 0.01):
        score = sum(onset[int((off + c) / dt) - 1 : int((off + c) / dt) + 2].max() for c in cuts)
        results.append((float(score), round(float(off), 2)))
    results.sort(reverse=True)
    print(f"track {total:.2f} s")
    for score, off in results[:5]:
        print(f"offset {off:7.2f}  score {score:.3f}")


main()
