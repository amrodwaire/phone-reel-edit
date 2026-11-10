import { loadFont } from "@remotion/google-fonts/Alexandria";
import { Video } from "@remotion/media";
import type React from "react";
import { Easing, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";

// Template for a 1080x1920 reel with Arabic text over graded phone clips.
// Put the graded clips in public/clips/ (shot1.mp4 ...). Register Reel and ReelProbe in Root.tsx
// with fps REEL_FPS, REEL_FRAMES frames for Reel, and 4 frames for ReelProbe.
// Text stays inside x 110-950 and y 220-1475, clear of Instagram's right rail and bottom bar.
// Budget about 10 Arabic characters a second from when each line appears.

export const W = 1080;
export const H = 1920;

const { fontFamily: font } = loadFont("normal", { weights: ["700", "800"], subsets: ["arabic", "latin"] });

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ACCENT = "#F7C948";
const INK = "#2A1B12";
const PAPER = "#F8F1E7";

export const REEL_FPS = 30;
export const REEL_FRAMES = 558; // 120 + 120 + 180 + 138

const Clip: React.FC<{ name: string; punch?: boolean; shiftY?: number; zoom?: number; origin?: string; drift?: number }> = ({
  name,
  punch = true,
  shiftY = 0,
  zoom = 1,
  origin = "50% 50%",
  drift = 0,
}) => {
  const f = useCurrentFrame();
  // A small punch-in on the first frames marks the cut.
  const hit = punch ? interpolate(f, [0, 6], [1.045, 1], { ...clamp, easing: Easing.out(Easing.cubic) }) : 1;
  const s = hit + interpolate(f, [0, 138], [0, drift], clamp);
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", transformOrigin: origin, transform: `translateY(${shiftY}px) scale(${s * zoom})` }}>
      <Video src={staticFile(`clips/${name}.mp4`)} muted objectFit="cover" style={{ position: "absolute", width: W, height: H }} />
    </div>
  );
};

type TextLine = { text: string; size: number; at?: number; color?: string; instant?: boolean; mt?: number; lh?: number; ltr?: boolean };
type TextBlock = { top: number; ink?: boolean; lines: TextLine[] };

// One entry per line. at = frame the line appears; lh = line box as a multiple of the font size;
// mt = extra space above the line; ltr = for numbers and Latin text. Check every block with
// scripts/check_text.py on the ReelProbe frames.
export const TEXT: Record<"one" | "two" | "three" | "end", TextBlock> = {
  one: {
    top: 1190,
    lines: [
      { text: "سؤال يشدّ من أول ثانية", size: 66, color: ACCENT, instant: true },
      { text: "والجواب هون", size: 100, at: 48 },
    ],
  },
  two: {
    top: 1092,
    lines: [
      { text: "بعدين", size: 64, at: 3 },
      { text: "اسم المنتج", size: 112, color: ACCENT, at: 3 },
      { text: "سطر قصير عنه", size: 70, at: 51 },
    ],
  },
  three: {
    top: 224,
    lines: [
      { text: "هاد اللي بتشوفوه", size: 88, color: ACCENT, at: 6 },
      { text: "وفي غيره كمان", size: 78, at: 54, mt: 14 },
      { text: "خيار · خيار", size: 62, at: 102 },
      { text: "خيار · خيار", size: 62, at: 102 },
    ],
  },
  end: {
    top: 1000,
    ink: true,
    lines: [
      { text: "«كلام الزبونة", size: 72, at: 3, lh: 1.5 },
      { text: "زي ما كتبته»", size: 72, at: 3, lh: 1.5 },
      { text: "تعليق زبونة", size: 42, at: 3, color: "#A8761A", lh: 1.5, mt: 24 },
      { text: "للطلب: ع الخاص أو واتساب", size: 46, at: 48, lh: 1.45, mt: 12 },
      { text: "07X XXX XXXX", size: 98, at: 48, lh: 1.2, ltr: true },
    ],
  },
};

// check_text.py tells lines apart by these colours, so a block holds seven lines at most.
// Split a longer block into two blocks, each with its own probe frame.
const PROBE = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff", "#ffffff"];

const Line: React.FC<{ line: TextLine; ink?: boolean; probe?: string }> = ({ line, ink, probe }) => {
  const f = useCurrentFrame();
  const { text, size, at = 0, color = ink ? INK : "#FFFFFF", instant, mt = 0, lh = 1.5, ltr } = line;
  const p = instant || probe ? 1 : interpolate(f, [at, at + 6], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <div
      style={{
        fontFamily: font,
        fontWeight: 800,
        fontSize: size,
        lineHeight: lh,
        marginTop: mt,
        color: probe ?? color,
        direction: ltr ? "ltr" : "rtl",
        textAlign: "center",
        whiteSpace: "nowrap",
        opacity: p,
        transform: `translateY(${(1 - p) * 16}px)`,
        textShadow: ink || probe ? "none" : "0 2px 4px rgba(0,0,0,.45), 0 6px 26px rgba(0,0,0,.5)",
      }}
    >
      {text}
    </div>
  );
};

const Stack: React.FC<{ block: TextBlock; probe?: boolean }> = ({ block, probe }) => (
  <div style={{ position: "absolute", top: block.top, left: 110, right: 130, textAlign: "center" }}>
    {block.lines.map((line, i) => (
      <Line key={`${i}-${line.text}`} line={line} ink={block.ink} probe={probe ? PROBE[i] : undefined} />
    ))}
  </div>
);

// Flat colours on black, one frame per block, for scripts/check_text.py.
export const ReelProbe: React.FC = () => {
  const f = useCurrentFrame();
  const block = [TEXT.one, TEXT.two, TEXT.three, TEXT.end][f];
  return (
    <div style={{ position: "absolute", inset: 0, background: "#000" }}>
      <Stack block={block} probe />
    </div>
  );
};

// A soft dark band behind the text keeps the subject visible below it.
const Shade: React.FC<{ from: "top" | "bottom" }> = ({ from }) => (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background:
        from === "bottom"
          ? "linear-gradient(to top, rgba(14,10,18,.2) 0%, rgba(14,10,18,.5) 22%, rgba(14,10,18,.5) 34%, transparent 46%)"
          : "linear-gradient(to bottom, rgba(14,10,18,.5) 0%, rgba(14,10,18,.38) 28%, transparent 40%)",
    }}
  />
);

const End: React.FC = () => (
  <>
    <div style={{ position: "absolute", inset: 0, background: `linear-gradient(to top, ${PAPER} 0%, ${PAPER} 50%, transparent 62%)` }} />
    <Stack block={TEXT.end} />
  </>
);

export const Reel: React.FC = () => {
  return (
    <div style={{ position: "absolute", inset: 0, background: PAPER }}>
      <Sequence name="shot 1" from={0} durationInFrames={120}>
        <Clip name="shot1" punch={false} zoom={1.05} origin="50% 100%" />
        <Shade from="bottom" />
        <Stack block={TEXT.one} />
      </Sequence>
      <Sequence name="shot 2" from={120} durationInFrames={120}>
        <Clip name="shot2" />
        <Shade from="bottom" />
        <Stack block={TEXT.two} />
      </Sequence>
      <Sequence name="shot 3" from={240} durationInFrames={180}>
        {/* A small zoom from a corner can push something unwanted out of frame. */}
        <Clip name="shot3" zoom={1.1} origin="0% 0%" />
        <Shade from="top" />
        <Stack block={TEXT.three} />
      </Sequence>
      <Sequence name="end card" from={420} durationInFrames={138}>
        <Clip name="shot4" shiftY={-300} punch={false} drift={0.03} origin="50% 30%" />
        <End />
      </Sequence>
    </div>
  );
};
