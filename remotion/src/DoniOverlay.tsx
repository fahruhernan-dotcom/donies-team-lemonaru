import { Caption, createTikTokStyleCaptions } from "@remotion/captions";
import React, { useEffect, useMemo, useState } from "react";
import {
  AbsoluteFill,
  CalculateMetadataFunction,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useDelayRender,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { loadFont, TheBoldFont } from "./load-font";
import { HookTitle } from "./components/HookTitle";
import SubtitlePage from "./CaptionedVideo/SubtitlePage";
import { OutroCTA } from "./components/OutroCTA";
import { StoryCoverCard } from "./components/StoryCoverCard";

const SWITCH_CAPTIONS_EVERY_MS = 0; // 0ms = Strict Single-Word-by-Word Captioning (Alex Hormozi / MrBeast Style)

export const doniOverlaySchema = z.object({
  hookTitle: z.string().default("KENAPA KUCING SUKA DUDUK GINI?"),
  hookSubtitle: z.string().default("Duduk Sila Kayak Bapak-Bapak!"),
  badgeText: z.string().default("🐱 FAKTA ANABUL VIRAL"),
  captionsFile: z.string().default("doni-cat_belly_trap_scratch-captions.json"),
  durationInSeconds: z.number().default(15.0),
  showOutroCTA: z.boolean().default(true),
  storyCardText: z.string().optional(),
  storyCardDuration: z.number().optional(),
  subtitleBottom: z.number().optional(),
});

export type DoniOverlayProps = z.infer<typeof doniOverlaySchema>;

export const calculateDoniOverlayMetadata: CalculateMetadataFunction<
  DoniOverlayProps
> = async ({ props }) => {
  const fps = 30;
  const dur = props.durationInSeconds ?? 15.0;
  return {
    fps,
    durationInFrames: Math.round(dur * fps),
  };
};

export const DoniOverlay: React.FC<DoniOverlayProps> = ({
  hookTitle,
  hookSubtitle,
  badgeText,
  captionsFile,
  durationInSeconds,
  showOutroCTA,
  storyCardText,
  storyCardDuration,
  subtitleBottom,
}) => {
  const { delayRender, continueRender } = useDelayRender();
  const [handle] = useState(() => delayRender());
  const [captions, setCaptions] = useState<Caption[]>([]);
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();

  useEffect(() => {
    Promise.all([
      loadFont(),
      fetch(staticFile(captionsFile))
        .then((res) => res.json())
        .then((data) => setCaptions(data))
        .catch(() => setCaptions([])),
    ])
      .then(() => continueRender(handle))
      .catch(() => continueRender(handle));
  }, [captionsFile, continueRender, handle]);

  const { pages } = useMemo(() => {
    return createTikTokStyleCaptions({
      combineTokensWithinMilliseconds: SWITCH_CAPTIONS_EVERY_MS,
      captions: captions ?? [],
    });
  }, [captions]);

  const watermarkOpacity = interpolate(frame, [0, 20], [0, 0.85], {
    extrapolateRight: "clamp",
  });

  const totalFrames = Math.round(durationInSeconds * fps);
  const outroStartFrame = Math.max(0, totalFrames - 4.5 * fps);

  return (
    <AbsoluteFill className="overflow-hidden select-none" style={{ backgroundColor: "transparent" }}>
      {/* 🐾 1. WATERMARK */}
      <div
        style={{
          fontFamily: TheBoldFont,
          opacity: watermarkOpacity,
        }}
        className="absolute top-12 right-8 bg-black/60 backdrop-blur-sm border border-white/20 px-4 py-1.5 rounded-full text-white text-lg tracking-wider flex items-center gap-2 pointer-events-none"
      >
        <span>🐾</span>
        <span>@DoniesDaily</span>
      </div>

      {/* 🎣 2. ANIMATED HOOK TITLE */}
      <HookTitle
        title={hookTitle}
        subtitle={hookSubtitle}
        badgeText={badgeText}
      />

      {/* 📖 2.5 STORY COVER CARD (COVERS ORIGINAL TIKTOK ENGLISH BOX) */}
      {storyCardText && (
        <StoryCoverCard
          text={storyCardText}
          durationInSeconds={storyCardDuration ?? 42.0}
        />
      )}

      {/* 💬 3. SYNCHRONIZED TIKTOK/CAPCUT CAPTIONS */}
      {pages.map((page, index) => {
        const nextPage = pages[index + 1] ?? null;
        const subtitleStartFrame = (page.startMs / 1000) * fps;
        const maxDurationFrames = 2.5 * fps;
        const subtitleEndFrame = nextPage
          ? Math.min(
              (nextPage.startMs / 1000) * fps,
              subtitleStartFrame + maxDurationFrames
            )
          : subtitleStartFrame + maxDurationFrames;
        const durFrames = Math.max(1, subtitleEndFrame - subtitleStartFrame);

        // Don't overlap with outro
        if (subtitleStartFrame >= outroStartFrame) return null;

        return (
          <Sequence
            key={index}
            from={subtitleStartFrame}
            durationInFrames={durFrames}
          >
            <SubtitlePage
              page={page}
              bottom={subtitleBottom ?? (storyCardText ? 210 : 350)}
            />
          </Sequence>
        );
      })}

      {/* 📣 4. OUTRO CTA CARD */}
      {showOutroCTA && (
        <Sequence from={outroStartFrame} durationInFrames={Math.round(4.5 * fps)}>
          <OutroCTA
            headline="SUBSCRIBE @DoniesDaily"
            subheadline="Follow Buat Fakta Anabul Tiap Hari! 🐾"
            buttonText="KLIK TOMBOL SUBSCRIBE"
          />
        </Sequence>
      )}
    </AbsoluteFill>
  );
};
