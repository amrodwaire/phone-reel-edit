# phone-reel-edit

An agent skill (Claude Code `SKILL.md` format) for turning phone footage into vertical Reels, Shorts or TikToks with Arabic on-screen text.

مهارة لتحويل فيديوهات التلفون لريلز عمودية، مع كتابة عربي على الفيديو: قص وتثبيت وتبطيء، تعديل ألوان على DaVinci Resolve، كتابة بـ Remotion مع فحص تلقائي للتداخل، موسيقى على القطعات، وضبط الصوت لسماعات التلفون.

## What it covers
- A source check that says what each clip needs before cutting: HDR transform, constant frame rate, crop (`scripts/probe_source.py`).
- Cutting, stabilising and clean half-speed slow motion with ffmpeg (`scripts/retime.py`).
- Colour correction two ways, with target numbers and a measuring script (`scripts/measure_grade.py`):
  - without opening an editor, as a 3D LUT built from numbers and applied by ffmpeg (`scripts/grade.py`);
  - in DaVinci Resolve free when one part of the frame needs its own fix, with a control map for driving Resolve with computer use (`references/resolve-ui.md`).
- Arabic text in Remotion (`assets/reelTemplate.tsx`, setup in `references/remotion-setup.md`) with reading-speed rules and an automatic check for overlap, safe zones and contrast against the picture (`scripts/check_text.py`).
- Placing music so its beats land on the cuts (`scripts/beat_offset.py`).
- Loudness mastering at -14 LUFS with a limiter and a true-peak report (`scripts/master.sh`), and a phone-speaker loudness check.
- Checks before publishing.
- Cases checked on test clips only, each labelled with how far it was checked: HDR sources, 30 fps slow motion, speech, TikTok and Shorts, covers (`references/other-cases.md`).

## Install
Copy the folder into your skills directory, for example `~/.claude/skills/phone-reel-edit/`.

## Requirements
- ffmpeg and ffprobe, built with vidstab (and zscale for HDR sources)
- Python 3 with numpy and Pillow
- DaVinci Resolve 21 (free), only for fixes to one part of the frame
- Node.js and a Remotion project for text

## Notes
Most rules come from a real product reel that went wrong at that step first. `references/research.md` explains why each rule exists and lists the sources. The Resolve coordinates are for one screen layout; take a screenshot before trusting them.

## License
MIT. See `LICENSE`.
