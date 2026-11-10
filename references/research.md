# Research behind this skill

A study made while editing a real product reel, with measurements of the result. A second model (Gemini) reviewed it. Web advice here comes mostly from tutorials and forums, not Blackmagic or Meta, so treat it as practical guidance.

## Colour order
Sources agree on this order: confirm the input and output colour space, open the scopes, fix exposure and neutral balance, shape contrast, match neighbouring shots, then add a look. Use qualifiers, Power Windows or tracking only where global controls cannot solve the problem. The Resolve Club guide labels the chain Balance, Contrast, Subject, Look. Those are jobs, not required positions, and a simple clip may need only two nodes.

Scopes: waveform for exposure, parade for colour casts on neutral areas, vectorscope for saturation and skin. The skin line is a reference for average skin hue, not a target to force on every face.

## Free versus Studio
Free has nodes, primaries, curves, standard scopes, qualifiers, Power Windows, tracking, LUTs and Resolve Color Management. Studio adds temporal and spatial noise reduction, Magic Mask, Speed Warp and extra Resolve FX. Sources conflict on Optical Flow in free. 60 fps footage does not need it.

## Phone footage
A phone that is not shooting flat or log usually records Rec.709, so no transform is needed. The test clips were Samsung SDR bt709 HEVC at about 60 fps. HDR clips need a transform to Rec.709 first.

## Instagram delivery
- 1080x1920, H.264, 30 fps, AAC 48 kHz. Bitrate advice runs 8-16 Mbps. These are editorial starting points, not Instagram rules.
- Safe zones are not standardised. Common advice: keep the top 250 px and bottom 350 px clear of key text, and avoid the right rail. No official Meta spec was found.
- A colour tag is not a conversion. Check the file on a second device, and post a test where possible.
- When uploading from a phone, turn on the highest quality setting.

## Text timing
No measured seconds-per-word rule exists for Reels. A working rule: about 3 words a second for Arabic overlays on moving video, and a visual change every 2-4 seconds.

## What the test reel taught
- A viewer read «مكس 4 نكهات» as Mix being the only flavour. Name what the viewer sees, then say what else exists.
- 10.5 s with 3 lines in 2.6 s felt fast. The reviewer model called 13.5 s right, and the native reader still could not finish. The final cut was 18.6 s.
- The client saw overlapping text that a low-resolution contact sheet hid. Line boxes at 1.22 made Arabic tails hit the next line. Measure the ink; do not trust the eye at thumbnail size.
- Measuring exposed faults the eye missed: an earlier grade added a blue cast, and a hand's skin sat 19 degrees off the skin line.
- Remotion's default colour space wrote full-range bt470bg with unknown primaries.

## Reading speed
- Netflix sets reading limits per language: 9 CPS for Chinese adult programmes, 12 for Korean, 22 for Telugu. The Arabic figure could not be confirmed from the guide page. Subtitle limits assume a prepared reader, so the 10 CPS used here is a deliberately slower working rule, not a published standard.
- Final budget on the test reel: 4 s, 4 s, 6 s, and a 4.6 s end card.

## Sound
- Phone-band loudness (300 Hz and up, on a -14 LUFS master): a bass-heavy track -23.9, a bright acoustic guitar track -17.7, an AI-generated nylon-guitar track with a phone EQ -19.8.
- The bass-heavy track had most of its energy under 200 Hz, with hits every 2 s and quiet between them. On a phone it sounded dark and heavy. One listen from a reviewer model is an opinion, not a verdict.
- Phone EQ that helped: `bass=g=-4:f=160:t=q:w=0.8,equalizer=f=2500:t=o:w=1.5:g=2`.

## Where the reviewer model was wrong
Verify a reviewer model every time. On the test reel it:
- proposed "correcting" a customer's dialect words, though quotes stay verbatim
- misjudged which Arabic dialect some words belonged to
- suggested 66 and 48 px text, too small for a phone
- gave invented numeric moves for Resolve, so measure instead
- misread Arabic from low-resolution frames twice
- said a real grade changed nothing

It was right about shortening the pace, about not grading one shot globally, about matching two neighbouring shots, and about moving the contact line up.

## Sources
- https://davinciresolveclub.com/how-to-color-grade-davinci-resolve/
- https://davinciresolveclub.com/davinci-resolve-instagram-reels-export-settings/
- https://cursa.app/en/page/davinci-resolve-color-page-basics-scopes-primary-correction-and-consistent-shots
- https://www.4kshooters.net/2022/11/28/how-to-properly-color-grade-your-phone-footage-in-resolve-18
- https://photography.tutsplus.com/tutorials/how-to-read-scopes-in-resolve-waveform-parade-histogram-vectorscope--cms-41868
- https://www.hopperhq.com/blog/instagram-reel-size/
- https://tryuncle.com/learn/davinci-resolve/how-to-speed-ramp-in-davinci-resolve
