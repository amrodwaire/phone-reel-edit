# Driving DaVinci Resolve 21 free with computer use

Resolve free has no Python scripting, so an agent drives it through screenshots and clicks. Copy clips into a plain working folder first (for example `Videos/reel/in`), because Resolve cannot see some app-data folders and says "Path does not exist".

Coordinates below are in a 1456x819 screenshot frame with the default layout on Windows. They are a starting point only: take a screenshot first, because any layout or resolution change moves them.

## Access
- Request access to "DaVinci Resolve", with clipboard write if you will paste values.
- Batched actions fail while the agent's own window has focus. Click the Resolve window first.
- On Windows, if Resolve is minimised, restore it with PowerShell ShowWindow(handle,3) and SetForegroundWindow.

## Pages
Edit (680,804), Color (873,804), Deliver (1067,804).

## Import and timeline
- Edit page: click the timeline (700,700), then `ctrl+i`.
- File name box (340,389). Type `"c1.mp4" "c2.mp4"`, then Return. Keyboard input works only in this box. The Folder box and address bar refuse it, so use the up-arrow (117,52), folder clicks and Select Folder (558,419).
- With clips selected, right-click one (198,145), choose Create New Timeline Using Selected Clips (343,158), then Create (898,472).
- Remove a clip with Backspace. Delete ripples across tracks. `ctrl+z` undoes it.
- `shift+f12` appends the selected pool clip to the timeline.

## Color page
Thumbnails: y 410, x 52, 153, 254, 356. Nodes: 01 (617,186), 02 (711,186). Add a serial node: click the graph (700,280), then `alt+s`.

Numeric field: double-click, `ctrl+a`, type, Return.

| Field | Position |
|---|---|
| Temp, Tint, Cont, Pivot, MD | (154,537) (261,537) (368,537) (475,537) (580,537) |
| Lift Y R G B | (30,702) (66,702) (102,702) (138,702) |
| Gamma Y R G B | (182,702) (218,702) (254,702) (290,702) |
| Gain Y R G B | (334,702) (370,702) (406,702) (442,702) |
| Col Boost, Shad, Hi/Light, Sat, Hue, L.Mix | (88,770) (185,770) (290,770) (387,770) (484,770) (581,770) |

Palettes: Primaries (92,482), Window (411,482).

## Power Window
- Circle icon (42,632).
- Size (471,558), Aspect (583,558), Pan (471,584), Tilt (583,584), Soft 1 (471,665).
- Pan 50 and Tilt 50 are the frame centre. Lower Tilt moves the window down. On the 41% viewer one Pan unit is about 25 px.
- Softness spreads both inward and outward, so the fully affected core is small. A large soft window on a small subject makes a visible spotlight. Check the outer edge does not reach parts that should stay untouched.

## Deliver
- Individual clips, QuickTime H.264, output `<source>_00000000.mov`.
- Add to Render Queue (319,765), Render (1382,400).
- A dialog appears when the files exist. Replace (892,474). Replace only your own test renders.
- Browse (375,197) changes the folder.
- Ten seconds is enough for four short clips.
