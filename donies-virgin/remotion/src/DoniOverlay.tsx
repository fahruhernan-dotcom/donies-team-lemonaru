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
  hookTitle: z.string().default("TAHUKAH KAMU FAKTA MENGEJUTKAN INI?"),
  hookSubtitle: z.string().default("Simak Sampai Habis!"),
  badgeText: z.string().default("🔥 VIRAL INSIGHT"),
  captionsFile: z.string().default("active_captions.json"),
  durationInSeconds: z.number().default(15.0),
  showOutroCTA: z.boolean().default(true),
  outroHeadline: z.string().default("SUBSCRIBE SEKARANG"),
  outroSubheadline: z.string().default("Follow Buat Konten Menarik Tiap Hari!"),
  outroButtonText: z.string().default("KLIK TOMBOL SUBSCRIBE"),
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
  outroHeadline = "SUBSCRIBE SEKARANG",
  outroSubheadline = "Follow Buat Konten Menarik Tiap Hari!",
  outroButtonText = "KLIK TOMBOL SUBSCRIBE",
  storyCardText,
  storyCardDuration,
  subtitleBottom,
}) => {
  const { delayRender, continueRender } = useDelayRender();
  const [handle] = useState(() => delayRender());
  const [captions, setCaptions] = useState<Caption[]>([]);
  const { fps, durationInFrames } = useVideoConfig();

  useEffect(() => {
    loadFont();
  }, []);

  useEffect(() => {
    let active = true;
    const fetchCaptions = async () => {
      try {
        const fileUrl = staticFile(captionsFile);
        const res = await fetch(fileUrl);
        if (!res.ok) {
          throw new Error(`Failed to load ${captionsFile}: ${res.statusText}`);
        }
        const data = await res.json();
        if (active) {
          setCaptions(Array.isArray(data) ? data : []);
          continueRender(handle);
        }
      } catch (err) {
        console.error("Error loading captions:", err);
        if (active) {
          setCaptions([]);
          continueRender(handle);
        }
      }
    };
    fetchCaptions();
    return () => {
      active = false;
    };
  }, [captionsFile, handle, continueRender]);

  const { pages } = useMemo(() => {
    return createTikTokStyleCaptions({
      captions,
      combineTokensWithinMilliseconds: SWITCH_CAPTIONS_EVERY_MS,
    });
  }, [captions]);

  // Hook Title stays for 4.5 seconds
  const hookDurationFrames = Math.min(Math.round(4.5 * fps), durationInFrames);
  // Outro CTA shows for final 4.5 seconds
  const outroStartFrame = Math.max(0, durationInFrames - Math.round(4.5 * fps));

  return (
    <AbsoluteFill className="pointer-events-none">
      {/* 🏷️ 1. DYNAMIC BADGE & HOOK TITLE */}
      <Sequence from={0} durationInFrames={hookDurationFrames}>
        <HookTitle
          title={hookTitle}
          subtitle={hookSubtitle}
          badgeText={badgeText}
        />
      </Sequence>

      {/* 📖 2. STORY COVER CARD (OPTIONAL OVERLAY) */}
      {storyCardText && (
        <Sequence
          from={0}
          durationInFrames={Math.min(
            Math.round((storyCardDuration ?? 8.5) * fps),
            durationInFrames
          )}
        >
          <StoryCoverCard
            storyText={storyCardText}
            durationSec={storyCardDuration ?? 8.5}
          />
        </Sequence>
      )}

      {/* 💬 3. DYNAMIC KINETIC SUBTITLES (SINGLE WORD HORMOZI POP-UP) */}
      {pages.map((page, index) => {
        const startFrame = Math.round((page.startMs / 1000) * fps);
        const durationFrames = Math.max(
          1,
          Math.round(((page.endMs - page.startMs) / 1000) * fps)
        );
        return (
          <Sequence
            key={`page-${index}-${page.startMs}`}
            from={startFrame}
            durationInFrames={durationFrames}
          >
            <SubtitlePage page={page} bottom={subtitleBottom ?? 350} />
          </Sequence>
        );
      })}

      {/* 📣 4. OUTRO CTA CARD */}
      {showOutroCTA && (
        <Sequence from={outroStartFrame} durationInFrames={Math.round(4.5 * fps)}>
          <OutroCTA
            headline={outroHeadline}
            subheadline={outroSubheadline}
            buttonText={outroButtonText}
          />
        </Sequence>
      )}
    </AbsoluteFill>
  );
};
