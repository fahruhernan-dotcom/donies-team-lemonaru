# 🧠 DELIVERABLE 03: `PRESERVED_LOGIC.md`
## Complete Record of Preserved Agentic Intelligence, Hierarchy & Operational Protocols

**Clone Instance:** DONIES VIRGIN (`donies-virgin/`)  
**Objective:** Guarantee 100% Behavioral Parity with Original Donies Daily  

---

### 1. The 15 Iron Laws (Hukum Besi) Preserved in Donies Virgin

Donies Daily's production stability relies on 15 deterministic engineering laws. In **Donies Virgin**, all 15 laws are preserved verbatim in code and agent souls:

1. **Hukum Besi #1 — Strict Shorts Duration Limits:** Total video duration MUST remain between `10.0s` and `59.9s`. Cleo rejects any render exceeding `59.9s`.
2. **Hukum Besi #2 — 1080x1920 (9:16) Vertical Broadcast Geometry:** Enforced in Remotion `Root.tsx` and asserted by `ffprobe` in `doni_qc_gate.py`.
3. **Hukum Besi #3 — Audio-First Master Clock:** The video duration is governed 100% by the voiceover stem (`{topic}_master.mp3`). Video never dictates audio length; audio dictates video duration down to 3 decimal places.
4. **Hukum Besi #4 — Acoustic Punctuation & Emotion Tags:** Luna must embed speech pacing tags (`[gasps]`, `[curious]`, `...`) to guide ElevenLabs natural speech cadence.
5. **Hukum Besi #5 — 4.5s Second-Hook Open Loop:** Luna must insert a narrative re-hook at second 4.5 to defeat the algorithmic swipe-away reflex before YouTube's 5s drop-off point.
6. **Hukum Besi #6 — 108–124 Word Script Guard:** Scripts are strictly calibrated for a 50–58 second delivery at ~140 words per minute.
7. **Hukum Besi #7 — Speech-Beat Scene Cutting via Opus:** Milo (`claude-opus-5-5-high`) maps individual sentences to catalog clips, producing 14–18 fast dynamic cuts.
8. **Hukum Besi #8 — Anti-Fatigue Clip Usage Tracking:** `virgin_clip_usage` records every footage cut used per video. Milo penalizes recently used clips to prevent audience fatigue.
9. **Hukum Besi #9 — Authentic Footage Priority:** In the asset selection scoring algorithm, authentic channel-owner footage (`channel_authentic`) receives a `+12` priority bonus, while AI-generated clips (`ai_generated`) receive a `-10` penalty.
10. **Hukum Besi #10 — Hybrid ProRes Alpha Composition:** Remotion renders only the transparent graphic overlay (`.mov` ProRes 4444 with alpha channel) at `/tmp/virgin_overlays/{topic}_overlay.mov`, which is then multiplexed over raw background footage using FFmpeg. This prevents VPS CPU exhaustion.
11. **Hukum Besi #11 — Hormozi Single-Word Kinetic Captions:** Word-by-word pop-up captioning (`SWITCH_CAPTIONS_EVERY_MS = 0`) using `TheBoldFont` and `Montserrat Bold` with yellow highlight (`#FFD700`).
12. **Hukum Besi #12 — EBU R128 Loudness Normalization:** FFmpeg `loudnorm` filter normalizes final audio to target `-14.0` to `-19.0 LUFS` (optimal `-14.5 LUFS`) with true peak at `-1.0 dBFS`.
13. **Hukum Besi #13 — In-Place Self-Healing Retry Loop (3x):** If Cleo's post-render QC fails, `doni_production_sprint.py` triggers an in-place revision loop (up to 3 retries) reusing the cached ProRes overlay before escalating or falling back.
14. **Hukum Besi #14 — 10-Frame Multi-Vision Temporal Asset Ingestion:** B-roll video assets must be analyzed across 10 chronological frames (9% to 91% duration) by Gemini Vision to extract rich semantic actions, emotions, and camera movements.
15. **Hukum Besi #15 — Mandatory Verbal & Visual Outro CTA:** Every video must conclude with an explicit verbal and visual Follow/Subscribe call-to-action in the script and on the Remotion outro card.

---

### 2. Cognitive Model Routing Parity

The exact model tiering from Donies Daily is preserved in `donies-virgin/config/team_config.yaml`:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   COGNITIVE MODEL ROUTING ARCHITECTURE                 │
├──────────────────────┬─────────────────────────┬───────────────────────┤
│ Agent                │ Assigned Model          │ Provider / Port       │
├──────────────────────┼─────────────────────────┼───────────────────────┤
│ 👑 Ketua Doni        │ gemini-4-argon-high     │ CLIProxyAPI (:8317)   │
│ 📊 Mochi             │ gemini-4-argon-high     │ CLIProxyAPI (:8317)   │
│ ✍️ Luna              │ claude-sonnet-5-5-high  │ CLIProxyAPI (:8317)   │
│ 🎬 Milo              │ claude-opus-5-5-high    │ CLIProxyAPI (:8317)   │
│ 🎙️ Kak Ceria / Vivan │ ElevenLabs v2/v4 Turbo  │ ElevenLabs API        │
│ 🛡️ Cleo QC Gate      │ 0-Token Deterministic   │ FFmpeg / ffprobe      │
│ 👁️ Vision Ingestion   │ gemini-3.8-flash-high   │ CLIProxyAPI (:8317)   │
└──────────────────────┴─────────────────────────┴───────────────────────┘
```

---

### 3. Orchestration & State Machine Parity

1. **Daily Standup & Telemetry Review:**
   - 07:30 WIB & 17:30 WIB automated execution via `doni_working_hours_standup.py`.
   - 9-step workflow: Mochi pulls telemetry -> Doni Stage 1 Strategy -> Luna script queue check -> Milo visual planning -> Cleo QC checklist -> Database sync.
2. **Autonomous Production Sprint:**
   - Organic jitter calculation: `morning` (08:xx), `midday_serial` (12:xx), `evening` (18:xx).
   - Cooldown guard: minimum 110 minutes between uploads.
   - Max daily cap: 3 Shorts per day.
3. **SQLite Swarm Matrix:**
   - Real-time inter-agent communication via `data/virgin_agents_chat.db` with identical schemas for `agent_messages` and `agent_traces`.
