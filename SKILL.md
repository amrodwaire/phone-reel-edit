---
name: phone-reel-edit
description: Editing playbook for turning phone footage into vertical Reels, Shorts or TikToks with Arabic on-screen text. Covers cutting, stabilising and slow motion with ffmpeg, colour correction in DaVinci Resolve free, Arabic text in Remotion with an automatic overlap and safe-zone check, cutting music to the edits, loudness mastering for phone speakers, and checks before publishing. Use it whenever a vertical video is cut, re-cut, graded, captioned, sped up or slowed down, even for a small change to text or colour, and when the user says منتاج، مونتاج، ريل، ألوان، إضاءة، كتابة عالفيديو، بطيء، سريع, or names DaVinci, Resolve, Remotion or CapCut.
---

# Phone reel editing

Each rule here comes from a real reel that failed at that step first. `references/research.md` holds the reasons and sources. `references/resolve-ui.md` maps the DaVinci Resolve controls for driving it with computer use.

Pipeline: phone source, ffmpeg cut and stabilise, DaVinci Resolve colour, Remotion text, ffmpeg sound and master.

## Before cutting
1. Read the brand rules for the client, if there are any: banned words, contact line, AI labelling, and what needs approval before posting.
2. Check the source with ffprobe: resolution, frame rate, SDR or HDR. Typical phone clips are SDR bt709 at about 30 or 60 fps. Background talk means the original sound stays muted.
3. If you use a second AI model as a reviewer, discuss the idea with it before deciding, then verify what it says. `references/research.md` lists the kinds of mistakes a reviewer model made.

## Pace
- One idea per reel. The text sets the length, not a target number. A test reel needed 18.6 s because the client could not finish reading at 10.5 s or 13.5 s.
- Budget 10 Arabic characters a second, counted from when a line appears. That is slow on purpose: the viewer is also watching the picture on a phone.
- Two reveals per shot where possible, and at least 1.5 s between them. Lines that appear together count as one reveal.
- A native reader's verdict on pace outranks any model's.
- The strongest visual and the hook text are on screen at frame 0, with no fade from black.
- Avoid a sudden 3x speed-up. Ramp gently through a bad moment instead.

60 fps played at 0.5x gives real frames at 30 fps, so no interpolation is needed. Stabilise to a 60 fps intermediate, then retime:

```bash
ffmpeg -ss S -t D -i raw.mp4 -vf "vidstabdetect=shakiness=6:accuracy=15:result=x.trf" -f null -
ffmpeg -ss S -t D -i raw.mp4 -vf "vidstabtransform=input=x.trf:smoothing=14:zoom=2:optzoom=0:interpol=bicubic,crop=W:H:X:Y,scale=1080:1920:flags=lanczos,fps=60" -an -c:v libx264 -preset veryfast -crf 10 -pix_fmt yuv420p im.mp4
python -I scripts/retime.py im.mp4 c1.mp4 --start 0.4 --frames 99 --keys 0:.5
```

Run `scripts/` paths from this skill's folder. ffmpeg needs the vidstab filters. Every clip must start at time zero, because a non-zero start shows as black frames at the head in Resolve. Add `setpts=PTS-STARTPTS` when using `-ss` with a time filter, and check `start_time` with ffprobe.

A hand drifting into the last frames of a still shot can be hidden by holding an earlier frame: `trim=end_frame=N,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0.6`.

## Colour in DaVinci Resolve free
Copy the clips into a plain folder Resolve can see (it cannot open some app-data folders and says "Path does not exist"). Put them on a new timeline and open the Parade scope.

Work in this order, because each step depends on the one before:
1. **Balance node.** Gain for the white level, Temp for the cast. Positive Temp warms. The same surface in two shots must match.
2. **Contrast node.** Contrast and Pivot, Lift for deep blacks, a small Sat move of 5 or less.
3. **Subject node, only when a global move would hurt something else.** Use a soft Power Window. On the test reel a window fixed a hand's skin and left the product colours untouched.
4. Render, measure, adjust, and repeat. Two passes were enough.

```bash
python -I scripts/measure_grade.py frame.png --patch counter:40,60,200,220 --skin 100,1450,1000,1920
```

Targets:
- Neutral surfaces: R, G and B within about 3 to 5. White around 195 to 215 for a bright look.
- Skin hue near 123 degrees. Keep it natural, because the vectorscope line is a reference, not a target.
- Highlights under about 2% of pixels at 250+.
- Product colours stay true when the video sells a product.

What moves what:
- Tint barely moved a red palm. Per-channel Gamma fixed it: G up, R and B down a little.
- Temp +300 overshot a blue cast where +130 was right. Start small.

## Arabic text in Remotion
`assets/reelTemplate.tsx` is a working template. It keeps each text block as data and has a probe composition for the text check.

Rules:
- A heavy Arabic face (the template uses Alexandria 800), white plus one accent colour, no boxes, a soft shadow.
- Sizes 62 to 124 px on a 1080x1920 frame. A phone needs them that big.
- Line box 1.5 for Arabic. At 1.22 the letter tails hit the next line.
- Every letter inside x 110-950 and y 220-1475, so Instagram's right rail and bottom bar cover nothing.
- `whiteSpace: nowrap`, so a line never wraps by surprise.
- Hook on at frame 0. Later lines about 1 s apart, with a 6-frame rise and fade.
- A soft dark band behind the text keeps the subject visible below it.
- Customer quotes stay word for word, with no name or photo unless the customer agreed.
- Say what the viewer is seeing. Do not let a label imply it is the only option.

After any text change, render the probe frames and check them:

```bash
npx remotion still ReelProbe out/p0.png --frame=0
python -I scripts/check_text.py out/p0.png out/p1.png out/p2.png out/p3.png
```

It fails when the ink of two lines comes within 14 px or a letter leaves the safe box. Then look at full-size frames at the end of every shot. A thumbnail sheet hides collisions, and things moving behind the text only show at full size. On the test reel a spoon crossed a line. A small zoom with a corner origin moved it clear and also cropped a stray finger.

## Render and sound

```bash
npx remotion render Reel out/reel.mp4 --codec=h264 --crf=15 --muted --color-space=bt709
python -I scripts/beat_offset.py music.ogg --cuts 3.3,6.5,10.3 --length 13.5 --from 0 --to 40
```

`--color-space=bt709` matters. Without it Remotion writes full-range bt470bg with unknown primaries.

Cut the music from the best offset, fade the last 1.2 s, join with `-c:v copy`, then master with the 0.7 limiter ceiling. It keeps true peak near -3 dB, while 0.75 reached -0.6 dB after AAC:

```bash
sh scripts/master.sh in.mov out.mp4 -14 0.4 0.7
```

Phone speakers lose most sound below 300 Hz, so check that band:

```bash
ffmpeg -hide_banner -nostats -i out.mp4 -vn -af "highpass=f=300:poles=2,highpass=f=300:poles=2,lowpass=f=12000,ebur128" -f null - 2>&1 | tail -12
```

Aim for -20 LUFS or louder in that band on a -14 LUFS master. A bass-heavy track measured -23.9 and sounded dull on phones. Draw the waveform and spectrum too, because a reviewer model's timestamps do not always match them.

AI-generated music or voice needs the platform's AI label. Generate music slightly longer than the reel, because a track cut short cannot be extended cleanly.

## Checks before calling it done
- ffprobe shows `yuv420p, tv, bt709, bt709, bt709`, and the right duration and frame count.
- `check_text.py` prints PASS.
- Look at full-size frames yourself, including the first and last frames and the frame before each cut.
- If a reviewer model watches the final mp4, give it the decisions already made so it does not reopen them.
- State what was not checked. An agent cannot hear the audio or see the file on a phone.
- After replacing a file that is already uploaded somewhere, re-upload it, verify it from the public link, and update anything scheduled that points to the old file.

Publishing needs the client's approval.
