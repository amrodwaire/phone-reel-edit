#!/bin/sh
# Static-gain master: one gain for the whole video (keeps the balance and the quiet bed where it is),
# then a true-peak limiter. Two passes: measure, set the gain for TARGET LUFS, render, re-measure.
# SIDE scales the side (L-R) signal. Ambient beds and whooshes are near-uncorrelated stereo, and
# keeping side 5-15 dB under mid helps the mix survive mono phone speakers.
# LIMIT 0.75 (-2.5 dBFS sample peak) keeps true peak under -1 dBTP after AAC (0.80 gave -0.6).
IN="$1"; OUT="$2"; TARGET="${3:--14}"; SIDE="${4:-0.4}"; LIMIT="${5:-0.75}"
lufs() { ffmpeg -hide_banner -nostats -i "$1" -vn -af "$2ebur128=peak=true" -f null - 2>&1 | awk '/Summary/{s=1} s&&/I:/{print $2; exit}'; }
I0=$(lufs "$IN" "")
G=$(python -I -c "print(round($TARGET - ($I0) + 0.8, 2))")
CH="highpass=f=35,stereotools=slev=${SIDE},volume=${G}dB,alimiter=limit=${LIMIT}:attack=1:release=50:level=disabled"
# The limiter takes more off as the gain rises, so correct the gain three times.
for _ in 1 2 3; do
  I1=$(lufs "$IN" "$CH,")
  G=$(python -I -c "print(round($G + $TARGET - ($I1), 2))")
  CH="highpass=f=35,stereotools=slev=${SIDE},volume=${G}dB,alimiter=limit=${LIMIT}:attack=1:release=50:level=disabled"
done
ffmpeg -v error -y -i "$IN" -c:v copy -af "$CH" -c:a aac -b:a 192k -ar 48000 "$OUT"
# How hard the limiter works: the peak it would have seen minus its ceiling.
P=$(ffmpeg -hide_banner -nostats -i "$IN" -vn -af "highpass=f=35,stereotools=slev=${SIDE},volume=${G}dB,astats=measure_overall=Peak_level:measure_perchannel=none" -f null - 2>&1 | awk '/Peak level dB/{v=$NF} END{print v}')
echo "raw $I0 LUFS -> gain ${G} dB, limiter reduction $(python -I -c "import math; print(round($P - 20*math.log10($LIMIT), 1))") dB"
