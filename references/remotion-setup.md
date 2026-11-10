# Starting the Remotion project

Needed once per client or series. After that, each reel is one more file in `src/`.

## Create

```bash
npx create-video@latest --yes --blank --no-tailwind my-reel
cd my-reel
npx remotion add @remotion/media @remotion/google-fonts
```

`remotion add` installs the packages at the same version as `remotion`. Mixed versions fail at render time, so do not install them with a bare `npm i`.

Put the working folder somewhere plain, such as `Videos/my-reel`. DaVinci Resolve cannot open some app-data folders, and the graded clips travel between the two.

## Add the template

Copy `assets/reelTemplate.tsx` to `src/reelTemplate.tsx`. Put the graded clips in `public/clips/` as `shot1.mp4`, `shot2.mp4` and so on.

`src/Root.tsx`:

```tsx
import { Composition } from "remotion";
import { REEL_FPS, REEL_FRAMES, Reel, ReelProbe } from "./reelTemplate";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Reel" component={Reel} width={1080} height={1920} fps={REEL_FPS} durationInFrames={REEL_FRAMES} />
    {/* One frame per text block. Keep durationInFrames equal to the number of blocks. */}
    <Composition id="ReelProbe" component={ReelProbe} width={1080} height={1920} fps={30} durationInFrames={4} />
  </>
);
```

## Fit the template to the reel

1. Set each `Sequence` length to its shot's frame count, and `REEL_FRAMES` to the total.
2. Write the text in `TEXT`. Count the characters of each line against 10 a second.
3. If the number of blocks changes, change the list inside `ReelProbe` and its `durationInFrames`.
4. Change `ACCENT` to the brand's accent colour. Keep white as the main text colour.

## Preview and render

```bash
npx remotion studio
npx remotion still ReelProbe out/p0.png --frame=0
npx remotion render Reel out/reel.mp4 --codec=h264 --crf=15 --muted --color-space=bt709
```

The first render downloads a browser, which takes a few minutes.
