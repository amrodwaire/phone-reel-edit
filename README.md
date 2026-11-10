# phone-reel-edit

An agent skill (Claude Code `SKILL.md` format) for turning phone footage into vertical Reels, Shorts or TikToks with Arabic on-screen text.

مهارة لتحويل فيديوهات التلفون لريلز عمودية، مع كتابة عربي على الفيديو: قص وتثبيت وتبطيء، تعديل ألوان على DaVinci Resolve، كتابة بـ Remotion مع فحص تلقائي للتداخل، موسيقى على القطعات، وضبط الصوت لسماعات التلفون.

## What it covers
- Cutting, stabilising and clean half-speed slow motion with ffmpeg (`scripts/retime.py`).
- Colour correction in DaVinci Resolve free, with a node order, target numbers and a measuring script (`scripts/measure_grade.py`), plus a control map for driving Resolve with computer use (`references/resolve-ui.md`).
- Arabic text in Remotion (`assets/reelTemplate.tsx`) with reading-speed rules and an automatic overlap and safe-zone check (`scripts/check_text.py`).
- Placing music so its beats land on the cuts (`scripts/beat_offset.py`).
- Loudness mastering at -14 LUFS with a true-peak limiter (`scripts/master.sh`) and a phone-speaker loudness check.
- Checks before publishing.

## Install
Copy the folder into your skills directory, for example `~/.claude/skills/phone-reel-edit/`.

## Requirements
- ffmpeg and ffprobe, built with vidstab
- Python 3 with numpy and Pillow
- DaVinci Resolve 21 (free) for colour
- Node.js and a Remotion project for text

## Notes
Every rule comes from a real product reel that went wrong at that step first. `references/research.md` explains why each rule exists and lists the sources. The Resolve coordinates are for one screen layout; take a screenshot before trusting them.
