#!/usr/bin/env python
"""Report what a phone clip is before any cut, and what that means for the edit.

Usage:
  python -I probe_source.py clip.mp4 [more.mp4 ...]

Prints the displayed size (after rotation), frame rate and whether it varies, bit depth,
colour tags, HDR or Dolby Vision, audio, and a non-zero start time. Then it lists the
steps this clip needs: an HDR transform, a constant frame rate, a crop to 9:16, or
frame interpolation before any slow motion.
"""
import json
import subprocess
import sys

HDR_TRANSFERS = {"arib-std-b67": "HLG", "smpte2084": "PQ"}
TONEMAP = (
    "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
    "zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
)


def rate(text):
    try:
        n, d = text.split("/")
        return float(n) / float(d) if float(d) else 0.0
    except ValueError:
        return 0.0


def report(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
        stdout=subprocess.PIPE,
        check=True,
        text=True,
        encoding="utf-8",
    ).stdout
    info = json.loads(out)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    if video is None:
        print(f"{path}: no video stream")
        return
    audio = [s for s in info["streams"] if s["codec_type"] == "audio"]
    side = video.get("side_data_list", [])
    rotation = 0
    for item in side:
        if "rotation" in item:
            rotation = int(round(float(item["rotation"])))
    rotation = int(video.get("tags", {}).get("rotate", rotation))
    w, h = video["width"], video["height"]
    if abs(rotation) % 180 == 90:
        w, h = h, w
    real = rate(video.get("r_frame_rate", "0/1"))
    avg = rate(video.get("avg_frame_rate", "0/1"))
    variable = bool(avg) and abs(real - avg) / avg > 0.005
    transfer = video.get("color_transfer", "unknown")
    hdr = HDR_TRANSFERS.get(transfer)
    dolby = any("DOVI" in item.get("side_data_type", "") for item in side)
    start = float(video.get("start_time", 0) or 0)
    duration = float(info["format"].get("duration", 0) or 0)

    print(f"{path}")
    print(f"  picture   {w}x{h} as displayed (rotation {rotation}), {video['codec_name']}, {video.get('pix_fmt')}")
    print(f"  rate      {avg:.3f} fps average, {real:.3f} fps nominal{'  VARIABLE' if variable else ''}")
    print(
        f"  colour    matrix {video.get('color_space', 'unknown')}, transfer {transfer}, "
        f"primaries {video.get('color_primaries', 'unknown')}, range {video.get('color_range', 'unknown')}"
        f"{'  ' + hdr + ' HDR' if hdr else ''}{'  Dolby Vision' if dolby else ''}"
    )
    print(f"  length    {duration:.2f} s, start {start:.3f} s, audio {'yes' if audio else 'no'}")

    todo = []
    if hdr:
        todo.append(f"HDR source. Transform to Rec.709 before anything else:\n      -vf \"{TONEMAP}\"")
    elif video.get("color_space", "unknown") == "unknown":
        todo.append("No colour tags. ffmpeg assumes bt601 for untagged video, so pass the matrix yourself (grade.py does).")
    if variable:
        todo.append("Variable frame rate. Put fps=60 (or fps=30) in the intermediate so every later step counts frames the same way.")
    if avg and avg < 50:
        todo.append("Under 50 fps. Speeds below 1.0 have no real frames to use. Keep real speed, or interpolate first (see SKILL.md).")
    if abs(w * 16 - h * 9) > 16:
        if w * 16 > h * 9:
            cw = int(h * 9 / 16) // 2 * 2
            todo.append(f"Not 9:16. A centre crop is crop={cw}:{h}:{(w - cw) // 2}:0. Move X to keep the subject in frame.")
        else:
            ch = int(w * 16 / 9) // 2 * 2
            todo.append(f"Not 9:16. A centre crop is crop={w}:{ch}:0:{(h - ch) // 2}. Move Y to keep the subject in frame.")
    if min(w, h) < 1080:
        todo.append("Shorter side is under 1080 px. Scaling up will not add detail, so avoid extra zoom.")
    if start > 0.001:
        todo.append("Start time is not zero. Add setpts=PTS-STARTPTS when cutting.")
    if not todo:
        todo.append("Nothing special. SDR, constant rate, 9:16.")
    for line in todo:
        print(f"  - {line}")


if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    print(__doc__)
else:
    for clip in sys.argv[1:]:
        report(clip)
