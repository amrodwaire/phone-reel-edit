# Cases not yet proven on a published reel

The main skill was built on SDR 60 fps clips with the sound muted, published to Instagram. The cases below fall outside that. Each one says how far it was checked. When an edit relies on one, tell the user, and look at the result harder than usual.

## HDR source (iPhone HLG or Dolby Vision, Samsung HDR10+)

`probe_source.py` marks these as HLG or PQ. Edited as they are, they come out grey and washed, because the HDR brightness curve gets read as normal video. Transform to Rec.709 first, in the same ffmpeg command that cuts the clip:

```bash
ffmpeg -ss S -t D -i raw.mov -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,setpts=PTS-STARTPTS" -an -c:v libx264 -crf 10 -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv sdr.mp4
```

Then stabilise and grade `sdr.mp4` as usual. ffmpeg needs the zscale filter (libzimg).

- `npl` is the knob for overall brightness. Guides use values from 100 to 1000. Raise it if the picture comes out too bright, lower it if too dark.
- `desat=0` keeps the colour in bright areas.
- A simpler fix is at the source: ask the client to turn HDR video off in the camera settings before filming.

Checked: the command runs on a synthetic HLG clip and writes correct bt709 tags. Not checked: how real iPhone or Samsung HDR footage looks after it. Measure a neutral patch and skin, and compare with how the clip looks on the phone that shot it.

## Variable frame rate

Phones drop or stretch frames, most often in low light. `probe_source.py` prints `VARIABLE` when the average and nominal rates differ. The stabilise command in `SKILL.md` already ends in `fps=60`, which makes the rate constant. For a clip that skips that command, add `fps=30` or `fps=60` to its filter chain before anything counts frames.

Checked: the detection logic only. No variable-rate clip was available to test.

## Slow motion from a 30 fps source

`retime.py` stops when a speed would repeat a frame, and at 30 fps any speed below 1.0 does. In order of preference:

1. Keep the shot at real speed and let the cut carry the pace.
2. Ask for the shot again at 60 fps.
3. Interpolate to 60 fps, then retime as usual:

```bash
ffmpeg -i im30.mp4 -vf "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" -an -c:v libx264 -crf 10 -pix_fmt yuv420p im.mp4
python -I scripts/retime.py im.mp4 c1.mp4 --frames 90 --keys 0:.5
```

Interpolation invents frames. Fingers, pouring liquid, hair and anything crossing an edge can smear or tear. Step through every frame of the result at full size. It is slow: expect well under real-time speed.

Checked: the commands run and give 60 fps on a synthetic clip. Not checked: quality on real footage.

## Someone speaks to the viewer

The main skill mutes the source because its test clips had background talk. When the speech is the content:

- Keep the original audio. Cut on the pauses between sentences, not on the picture.
- Captions follow the speech word for word, in the speaker's dialect. Do not tidy the dialect into formal Arabic.
- A speech-to-text model can draft the captions, but dialect Arabic comes back with errors. A native reader corrects every line before render.
- Show 2 to 4 words at a time, timed to the speech, inside the same safe box, checked with `check_text.py` like any other block.
- Music sits well under the voice. Master the mix with `master.sh`, then check the 300 Hz band figure, which matters more for speech than for music.
- Audio and video must stay in sync through every step: no `-an`, and `retime.py` cannot be used, because it drops the sound.

Checked: nothing here was run on a real reel. No transcription tool is bundled. Treat this as a starting list.

## TikTok and YouTube Shorts

The default safe box (x 110-950, y 220-1475) was proven on Instagram only. `check_text.py --platform` has three more:

| Platform | Box (x0,y0,x1,y1) | Clear of |
|---|---|---|
| tiktok | 60,200,920,1550 | right 160 px, bottom 370 px, top 200 px |
| shorts | 60,200,880,1540 | right 200 px, bottom 380 px, top 200 px |
| all | 110,220,880,1475 | the part inside all three boxes |

TikTok and YouTube publish no safe-zone numbers for organic posts. These come from third-party guides that measured the apps, and the guides disagree by tens of pixels. The apps also change their layout. Upload as a draft or private post and look at it in each app.

One file can serve all three apps if the text passes `--platform all`. Text that is wide on Instagram will fail it, so decide before writing the text.

## Cover

The profile grid shows the middle of the cover, cropped to 3:4. That is the centre 1080x1440 of a 1080x1920 frame, y 240 to 1680. Third-party guides agree on this since the grid changed in January 2025, and Instagram has not published it.

```bash
npx remotion still Reel out/cover.png --frame=N
```

Pick a frame with the subject clear and the hook text on screen. If the text falls outside y 240-1680, add a cover composition with the text moved in. `check_text.py --box 110,240,970,1680` checks a cover's probe frame. Upload the cover with the reel, because the app picks its own frame otherwise.

Checked: the crop arithmetic. Not checked on a live profile.

## Before and after

`grade.py still clip.mp4 T out.png --lut x.cube --compare` writes the source and the graded frame side by side. Send this to the client when the colour change needs their approval.
