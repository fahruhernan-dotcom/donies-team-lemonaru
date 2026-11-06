# 🛠️ MASTER SYSTEM AUDIT — DELIVERABLE 07: TOOLS, MODELS & INFRASTRUCTURE AUDIT (`07_TOOLS_INFRASTRUCTURE.md`)

**Audit Phase:** Phase 6 — Tools, Models & Infrastructure Audit  
**Target Ecosystem:** `@DoniesDaily` (`UCNPtjF2aB0wvWHI0q7hhcCg`) Autonomous Multi-Agent Production Studio  
**Canonical Workspace:** `/home/ubuntu/apps/ugc-lemonaru` & `/home/ubuntu/tools`  
**Audit Date:** 2026-11-06  
**Auditor Role:** Principal AI Systems Architect & Reverse Engineering Specialist  
**Audit Posture:** Read-Only, Evidence-Grounded, Zero-Hallucination

---

## 📑 EXECUTIVE SUMMARY

The `@DoniesDaily` autonomous production pipeline operates on a resource-constrained Linux VPS environment (**Ubuntu 24.04 LTS, 2 vCPUs, 4GB RAM**) yet achieves television broadcast-grade vertical video output (`1080x1920`, `30 FPS`, `-14 to -16.6 LUFS`, zero-cutoff, single-word kinetic captions) at a cadence of **3 Shorts per day**. 

To overcome hardware limitations and API rate/cost bottlenecks, the architecture separates **Cognitive LLM Reasoning** (routed through a local multi-account OpenAI-compatible proxy on `:8317`) from **0-Token Deterministic Workers** (FFmpeg DSP, `ffprobe` QC gates, SQLite/PostgreSQL state machines, and randomized jitter schedulers) and **Hybrid Video Compositing** (decoupling React Remotion transparent UI overlays from multi-scene FFmpeg video assembly).

---

## 1. MODEL ROUTING & AI PROVIDERS

### 1.1 CLIProxyAPI (`:8317`) Multi-Account Load Balancer Architecture
All cognitive LLM calls across the DoniesDaily squad are centralized through a local reverse-proxy and credential-pooling gateway:
- **Endpoint:** `http://127.0.0.1:8317/v1/chat/completions` (configured via `CPA_BASE_URL` in `/home/ubuntu/tools/doni_scriptwriter.py` and hardcoded in `/home/ubuntu/tools/doni_working_hours_standup.py`).
- **Authentication:** Local bearer token (`Authorization: Bearer cpa-secret-key-12345` / `CPA_API_KEY`).
- **Multi-Account Pool:** Load-balances upstream requests across multi-seat provider accounts (`support.ternakos` & `anakbawangstore`), insulating the production pipeline from single-account rate limits (`HTTP 429`) and quota exhaustion during heavy multi-agent standup and rendering sprints.

```mermaid
graph LR
    subgraph "DoniesDaily Squad (Local Python Workers)"
        DONI["🐱 Doni (Orchestrator)"]
        MOCHI["📊 Mochi (Analytics)"]
        LUNA["✍️ Luna (Scriptwriter)"]
        MILO["🎬 Milo (Visual Director)"]
        CERIA["🎙️ Kak Ceria (Community/Audio)"]
        INGEST["👁️ Ingest Engine (10-Frame Vision)"]
        VIVAN["🎧 Vivan (TTS & Harvester)"]
        CLEO["🛡️ Cleo (Broadcast QC)"]
    end

    subgraph "Local AI Gateway (:8317)"
        CPA["CLIProxyAPI<br/>127.0.0.1:8317/v1/chat/completions<br/>Pool: support.ternakos + anakbawangstore"]
    end

    subgraph "Upstream AI & Media Providers"
        ARGON["gemini-4-argon-high"]
        SONNET["claude-sonnet-5-5-high"]
        OPUS["claude-opus-5-5-high"]
        FLASH["gemini-3.8-flash-high"]
        EL["ElevenLabs API<br/>(v4 Turbo / Multilingual v2)"]
        DET["0-Token Local Execution<br/>(FFmpeg / ffprobe / psql)"]
    end

    DONI --> CPA
    MOCHI --> CPA
    LUNA --> CPA
    MILO --> CPA
    CERIA --> CPA
    INGEST --> CPA

    CPA -->|"Standup & Forensics"| ARGON
    CPA -->|"Script & Community"| SONNET
    CPA -->|"Remotion Cut Plan"| OPUS
    CPA -->|"10-Frame Vision"| FLASH

    VIVAN -->|"REST API (Voice: ZowYWFat3iypr7PwKMPb)"| EL
    CLEO -->|"Deterministic CLI"| DET
```

### 1.2 Comprehensive Model & Provider Mapping

| Agent / Component | Assigned Model / Engine | Provider / Route | Specific Operational Role & Evidence File | Temp / Params |
| :--- | :--- | :--- | :--- | :--- |
| **🐱 Doni** (Lead Producer) | `gemini-4-argon-high` | CLIProxyAPI (`:8317`) | Morning/Evening Standup Leadership Evaluation (Tahap 1 & Tahap 2 Verdict) and Post-Production Broadcast Audit (`tools/doni_working_hours_standup.py`, `tools/doni_production_sprint.py`). | `temp: 0.4`, `timeout: 45s` |
| **📊 Mochi** (Analytics Lead) | `gemini-4-argon-high` | CLIProxyAPI (`:8317`) | YouTube Studio Advanced Mode telemetry autopsy, 100-point retention curve forensics (`audienceWatchRatio`), and dynamic rule generation into `ai_brain.doniesdaily_learnings` (`tools/doni_evaluator.py`). | Analytic deterministic mode |
| **✍️ Luna** (Scriptwriter) | `claude-sonnet-5-5-high` | CLIProxyAPI (`:8317`) | Autonomous topic ideation, 108–135 word Long-Form Shorts copywriting, acoustic punctuation engineering, and phonetic dictionary enforcement (`tools/doni_scriptwriter.py`). | `temp: 0.65`, `max_tokens: 8192`, `timeout: 90s` |
| **🎙️ Kak Ceria** (Community Lead) | `claude-sonnet-5-5-high` | CLIProxyAPI (`:8317`) | Contextual, warm Indonesian community comment replies (`tools/doni_replier_runner.sh`, `souls/KAK_CERIA_SOUL.md`). | Persona-aligned |
| **🎬 Milo** (Remotion Editor) | `claude-opus-5-5-high` | CLIProxyAPI (`:8317`) | Mandatory high-precision Remotion scene cut planning (`select_footage_by_speech_beats()` in `doni_hybrid_renderer.py` & `generate_shotlist()` in `doni_visual_director.py`), mapping narrative sentences to 14–18 unique clips with anti-fatigue weighting. | High-reasoning editorial mode |
| **👁️ Vision Ingestion & Hermes** | `gemini-3.8-flash-high` | CLIProxyAPI (`:8317`) | 10-Frame Multi-Vision chronological behavior analysis (`tools/ingest_fahru_footage.py`) extracting `slug`, `title`, 2-sentence `description`, 12–18 bilingual `tags`, `emotion`, and `action`; also powers daily Hermes holding operations. | Multimodal parallel 10-frame base64 |
| **🎧 Vivan** (Voice Synthesis) | ElevenLabs v4 Turbo / Multilingual v2 | ElevenLabs REST API | Synthesizes primary voice profile **Vivan** (`ZowYWFat3iypr7PwKMPb`) or alternative **Kak Ceria** (`d15jrIAARvF899pDoC6T`) with forced character-to-word timestamp alignment (`src/elevenlabs_tts.py`). | `stability: 0.40`, `similarity_boost: 0.75`, `speed: 1.08x` |
| **🛡️ Cleo, Vivan Harvester, Jitter** | **0-Token Deterministic** | Local Python / C Binaries | `src/doni_qc_gate.py` (`ffprobe`/`ffmpeg`), `src/vivan_dataset_harvester.py` (24kHz WAV slicer), and `check_and_consume_jitter_window()` (`tools/doni_production_sprint.py`). | **0 LLM Tokens** (100% deterministic) |

### 1.3 Token Economics, Latency Profiles & Cost Implications
1. **Strict Cognitive Tiering:**
   - **High-Cost / Deep Reasoning (`claude-opus-5-5-high` & `gemini-4-argon-high`):** Restricted to high-leverage architectural decisions—specifically Mochi's retention curve forensics, Doni's executive verdicts, and Milo's timeline assembly where semantic mismatches directly cause viewer drop-off.
   - **Mid-Tier Creative (`claude-sonnet-5-5-high`):** Assigned to Luna's Indonesian copywriting and Kak Ceria's comment replies, where linguistic warmth and idiom naturalness ("anabul", "si oren", "babu kucing") outperform raw analytical models.
   - **High-Throughput Multimodal (`gemini-3.8-flash-high`):** Used for 10-frame JPEG vision ingestion (`scale='min(720,iw)':-1`, `q:v 3`), minimizing vision token payload while preserving temporal comprehension across 9%–91% of clip duration.
2. **Credit Preservation Guards (ElevenLabs):**
   - In `src/doni_remotion_flow_pipeline.py` (`synthesize_audio_and_captions`), the pipeline checks if `master_audio_path` and `captions_path` already exist on disk and validates duration via `ffprobe`. If present, it reuses the cached audio stem (`🎙️ Found cached audio & captions... reusing`), preventing redundant ElevenLabs character credit burn during video rendering retries.
   - Simultaneously, **Vivan** (`src/vivan_dataset_harvester.py`) slices every paid ElevenLabs generation into clean `3–10s`, `24kHz mono WAV` + `.lab` transcript pairs inside `assets/audio/vivan_dataset/` toward a 150–200 clip (~20 minute) self-hosted voice cloning target, creating an exit path from recurring TTS API costs.

---

## 2. RENDERING & VIDEO ENGINEERING INFRASTRUCTURE

### 2.1 React Remotion Engine Architecture (`/home/ubuntu/apps/ugc-lemonaru/remotion`)
In accordance with **Hukum Besi #15 (Milo Remotion Mandate)**, shortcut FFmpeg `.ass`/`subtitles` filters are strictly prohibited. All kinetic typography and broadcast graphics are rendered via a React/TypeScript Remotion project located at `/home/ubuntu/apps/ugc-lemonaru/remotion`.

#### Verified Component Inventory:
| Component File Path | Schema / Props | Technical Implementation & Behavior |
| :--- | :--- | :--- |
| `remotion/src/DoniOverlay.tsx` | `doniOverlaySchema` (Zod): `hookTitle`, `hookSubtitle`, `badgeText`, `captionsFile`, `durationInSeconds`, `showOutroCTA`, `storyCardText`, `storyCardDuration`, `subtitleBottom` | Master transparent overlay composition (`backgroundColor: "transparent"`, `fps: 30`). Loads caption tokens from `public/{captionsFile}` using `useDelayRender()`. Enforces **Hukum Besi #8 & #15** via `SWITCH_CAPTIONS_EVERY_MS = 0` inside `createTikTokStyleCaptions()`, forcing strict 1-word-per-page pop-ups. |
| `remotion/src/DoniShort/index.tsx` | Full Composite Short Schema | Full-stack Remotion composition utilized by `doni_remotion_flow_pipeline.py` (`DoniShort`) combining background video, watermark, hook banner, and kinetic captions. Also houses `<Still id="DoniThumbnail" />` for high-CTR thumbnail generation (**Hukum Besi #10**). |
| `remotion/src/components/HookTitle.tsx` | `title`, `subtitle`, `badgeText` | Top hook banner (`top-28 left-6 right-6 z-50`). Uses spring entrance animation (`damping: 12, mass: 0.8, stiffness: 140`) from frame `0–15`, continuous sinusoidal wobble (`Math.sin(frame / 8) * 1.5`), and interpolates exit fade/slide-up (`translateY: 0 -> -60px`) across frames `75–95` (`2.5s–3.16s`). Styled with `bg-black/85 backdrop-blur-md border-4 border-amber-300 rounded-3xl`. |
| `remotion/src/CaptionedVideo/SubtitlePage.tsx` | `page`, `bottom` | Renders active single-word kinetic tokens in the lower third (default or calibrated `bottom: 210px`) with neon yellow active highlight (`#FFE600`) and thick black stroke (`20px`) per **Hukum Besi #8**. |
| `remotion/src/components/StoryCoverCard.tsx` | `text`, `bottom` (`430`), `left` (`40`), `right` (`40`), `minHeight` (`240`), `durationInSeconds` (`42.0`) | Engineered on `2026-11-06` to completely occlude burned-in English text boxes on repurposed viral TikToks (e.g., `G2XVkRuZoKg`). Renders a solid `#FFFFFF` rounded card (`borderRadius: 28px`, `zIndex: 40`) with `#0f172a` Georgia serif typography and smooth 10-frame fade-in / 15-frame fade-out. |
| `remotion/src/components/OutroCTA.tsx` | `headline`, `subheadline`, `buttonText`, `startFromEndFrames` (`100` / `4.5s`) | Triggers at `durationInFrames - startFromEndFrames` (`outroStartFrame = Math.max(0, totalFrames - 4.5 * fps)` in `DoniOverlay.tsx`). Renders a `0.45` opacity black dim overlay and a spring-scaled (`damping: 12, mass: 0.7, stiffness: 160`) CTA card enforcing **Hukum Besi #15** (Follow & Subscribe closure). |
| `remotion/src/load-font.ts` | `TheBoldFont` | Loads custom local display typography (`theboldfont.ttf` / `Montserrat Bold` / `LilitaOne`) prior to frame rendering via `continueRender(handle)`. |

### 2.2 The Hybrid Rendering Pipeline (ProRes 4444 Alpha + FFmpeg Compositor)
```mermaid
sequenceDiagram
    autonumber
    participant MILO as 🎬 Milo (doni_hybrid_renderer.py)
    participant REM as ⚛️ Remotion Engine (DoniOverlay)
    participant TMP as 💾 /tmp Ephemeral Storage
    participant FFM as ⚙️ FFmpeg Compositor
    participant CLEO as 🛡️ Cleo (doni_qc_gate.py)
    participant YT as 📺 YouTube Data API v3

    MILO->>REM: Render UI Overlay (30fps, transparent bg, 1-word captions)
    REM->>TMP: Output /tmp/{topic}_remotion_overlay.mov (ProRes 4444, ~100-250MB)
    Note over MILO,TMP: Cached across in-place QC retries (saves 2-4 min/retry)
    MILO->>FFM: Slice & concat 14-18 unique 9:16 B-roll clips (Hukum Besi #13)
    Note over FFM: Apply setpts stretch if clip < 1.5x slice_dur (Emergency Force-Fit)
    FFM->>FFM: Composite B-roll + ProRes 4444 Overlay + 0.08s Remotion Poster Frame + 3-Layer Audio Mix
    FFM->>CLEO: Output /home/ubuntu/apps/ugc-lemonaru/output/{topic}_master.mp4
    CLEO->>CLEO: Assert 1080x1920, dur_video >= dur_audio, 0 black frames, -14..-19 LUFS
    CLEO->>YT: Upload MP4 + Set Custom Thumbnail
    YT-->>MILO: Confirm PUBLIC video_id
    MILO->>TMP: Unlink /tmp/{topic}_remotion_overlay.mov (Hukum Besi #5 Disk Hygiene)
```

#### Why Hybrid Rendering Was Implemented (Architectural Root-Cause Analysis):
1. **Hardware Bottleneck (2 vCPUs / 4GB RAM):** Rendering full `1080x1920` H.264 video with 14–18 decoded high-bitrate `.mp4` `<OffthreadVideo>` streams simultaneously inside Headless Chromium (Remotion's `<Composition>` renderer) causes severe CPU thrashing, frame-seeking timeouts, and Chromium Out-Of-Memory (`OOM`) crashes on a 4GB RAM VPS.
2. **Decoupled Alpha Overlay Solution:**
   - **Step 1 (Remotion UI-Only Pass):** Remotion renders **only** the lightweight vector/DOM overlay (`DoniOverlay.tsx`: watermark, `HookTitle`, `StoryCoverCard`, single-word subtitles, `OutroCTA`) with `backgroundColor: "transparent"` into an intermediate Apple ProRes 4444 file with alpha channel (`/tmp/{topic}_remotion_overlay.mov`, ~100–250MB).
   - **Step 2 (Overlay Caching Across Self-Healing Retries):** As documented in `ActiveContext.md` (`2026-11-06 02:41 WIB`), if Cleo rejects a video due to a background footage issue, the cached `/tmp/{topic}_remotion_overlay.mov` is reused in-place, saving **2–4 minutes of CPU rendering time** per retry.
   - **Step 3 (Native C FFmpeg Muxing & Ephemeral Purge):** FFmpeg natively decodes, scales, applies `setpts` force-fit guards, concatenates the 14–18 background clips, overlays the ProRes 4444 `.mov`, injects the `0.08s` Remotion cover poster frame (**Hukum Besi #10**), and mixes the audio stems at native C speed without browser memory overhead. Once confirmed live on YouTube, `/tmp/{topic}_remotion_overlay.mov` is unlinked to comply with **Hukum Besi #5 (Disk Hygiene)**.

---

## 3. AUDIO, VOICE & SFX INFRASTRUCTURE

### 3.1 ElevenLabs TTS & Acoustic Punctuation (`src/elevenlabs_tts.py`)
- **Voice Profiles:**
  - Primary: **Vivan** (`ZowYWFat3iypr7PwKMPb`) — Warm, expressive, highly articulated male storytelling voice.
  - Alternative: **Kak Ceria** (`d15jrIAARvF899pDoC6T`) — Energetic Indonesian female voice.
- **Synthesis Parameters:** `stability = 0.40`, `similarity_boost = 0.75`, `speed = 1.08x`.
- **Dynamic Emotion Tagging (Hukum Besi #4):** Enforces varied ElevenLabs v4 expression tags (`[curious]`, `[gasps]`, `[laughs]`, `[excited]`, `[sighs]`, and sparse `[whispers]`), stripping `[tag]` tokens from the exported Remotion `captions.json` (`doni-{topic_key}-captions.json`) while preserving exact millisecond `startMs` and `endMs` word boundaries.
- **Phonetic Pre-Processor (`tools/doni_scriptwriter.py`):** Automatically regex-rewrites scientific/English terms before TTS dispatch (`Flehmen` $\rightarrow$ `Fley-men`, `Jacobson` $\rightarrow$ `Jekob-sen`, `HES-7` $\rightarrow$ `Hes Tujuh`, `FRAPs` $\rightarrow$ `Freps`, `Zoomies` $\rightarrow$ `Zuumis`, `UV` $\rightarrow$ `Yu-Vi`, `Catnip` $\rightarrow$ `Ket-nip`).

### 3.2 Vivan Fine-Tuning Dataset Harvester (`src/vivan_dataset_harvester.py`)
- Operated by sub-unit **@Vivan** (`souls/VIVAN_SOUL.md`) at **0 LLM tokens**.
- Every time a fresh voiceover is synthesized, the harvester automatically segments clean vocal sentences (`3–10 seconds`), converts them to `24kHz mono PCM WAV` alongside matching `.lab` text transcripts, and stores them in `/home/ubuntu/apps/ugc-lemonaru/assets/audio/vivan_dataset/`.
- Reports cumulative clip count and duration at daily standups until reaching the **150–200 clips (~20 minutes)** threshold required for autonomous local voice cloning.

### 3.3 Multi-Layer Audio DSP & EBU R128 Normalization
1. **Standard 2-Layer Mix (`src/doni_remotion_flow_pipeline.py`):**
   ```bash
   ffmpeg -y -i {raw_voice} -stream_loop -1 -i assets/audio/cat_playful_bgm.mp3 \
     -filter_complex "[0:a]volume=1.25,highpass=f=80,dynaudnorm[voice];[1:a]volume=0.08[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]" \
     -map "[aout]" -c:a libmp3lame -q:a 2 {master_audio_path}
   ```
2. **Advanced 3-Layer Broadcast Mix & Loudnorm (Hybrid / Serial Pipeline):**
   - Mixes **100% Vivan/Kak Ceria Voiceover** + **20%–40% Original Video Ambience/Meow/Piano** + **20% Playful BGM (`cat_playful_bgm.mp3`)**.
   - Normalizes final master audio via FFmpeg `loudnorm` / EBU R128 targeting **-14.5 to -16.6 LUFS** (True Peak `-1.0 dBFS`, LRA `9–11`), audited deterministically by Cleo (`src/doni_qc_gate.py` via `ffmpeg -af ebur128`).

### 3.4 Curated Viral SFX Reservoir (`src/doni_sfx_helper.py` & `sfx_catalog.json`)
To execute pattern-interrupts at the critical `4.5s` and `7.5s` retention drop-off walls (`ai_brain.doniesdaily_learnings` Rules #6–#13), 10 viral sound effects were precision-sliced with micro-fades (anti-pop/click) into `/home/ubuntu/apps/ugc-lemonaru/assets/audio/sfx/` and mirrored to `/home/ubuntu/apps/ugc-lemonaru/remotion/public/sfx/`:

| # | SFX Filename | Duration | Narrative / Pattern-Interrupt Role |
| :- | :--- | :--- | :--- |
| 1 | `sfx_taco_bell_bong.mp3` | `1.60s` | Taco Bell Bong — Epiphany / Hook realization |
| 2 | `sfx_vine_boom.mp3` | `1.85s` | Vine Boom — Shock / Plot twist / Cat sudden aggression |
| 3 | `sfx_yellow_undertale_chime.mp3` | `0.80s` | Undertale Text Chime — Trivia / Scientific fact reveal |
| 4 | `sfx_violin_screech_horror.mp3` | `2.70s` | Psycho Violin Screech — Comedic tension / Dramatic stare |
| 5 | `sfx_correct_ding.mp3` | `0.80s` | Correct Chime — Successful training trick / Polite cat behavior |
| 6 | `sfx_anime_wow.mp3` | `1.35s` | Anime Wow — Cute / Adorable ("Gemas / Takjub") moment |
| 7 | `sfx_akh_groan_fail.mp3` | `1.50s` | Akhh Shout — Silly protest / Frustration |
| 8 | `sfx_kaching_cash_register.mp3` | `1.00s` | Cash Register — Wet food landing / Reward given |
| 9 | `sfx_tindeck_toy_squeak.mp3` | `0.80s` | Toy Squeak — Scooting / Blepping ("Melet") / Goofy movement |
| 10 | `sfx_dry_fart_meme.mp3` | `0.70s` | Dry Fart Meme — Anticlimax / Defeated sigh ("Pasrah") |

---

## 4. VISUAL FOOTAGE SOURCING INFRASTRUCTURE

### 4.1 Google Flow / Veo2 AI Generation (`src/flow_cdp_operator.py`)
- Connects to a persistent Google Chrome session running inside a virtual framebuffer (`Xvfb :99`) exposing Chrome DevTools Protocol (CDP) on `127.0.0.1:9222` with user data persisted at `/home/ubuntu/apps/ugc-lemonaru/data/chrome_persistent`.
- Automates multi-scene vertical (`9:16`) AI video generation based on Milo's 5-zone Style Bible (`souls/MILO_SOUL.md`), saving outputs to `/home/ubuntu/apps/ugc-lemonaru/assets/cat_videos/flow_renders/{topic_key}/`.
- **Graceful Degradation:** If Google Flow CDP encounters UI changes or generation timeouts, `prepare_flow_scenes()` automatically falls back to local verified footage pools without crashing the sprint.

### 4.2 Authentic Owner Footage Ingestion Pipeline (`tools/ingest_fahru_footage.py`)
Enforces **Hukum Besi #1, #2, and #14 (10-Frame Multi-Vision Protocol)**:
1. **Intake Channels:** Direct Telegram DM video upload to Hermes (`--file <path>`) or batch VPS folder drop (`/home/ubuntu/apps/ugc-lemonaru/assets/cat_videos/fahru_clips/` via `--scan`).
2. **10-Frame Temporal Extraction:** Executes `ffmpeg` to extract exactly 10 chronological JPEG frames (`scale='min(720,iw)':-1`, `q:v 3`) at timestamps:
   $$ts_i = \text{duration} \times \left(\frac{i + 1}{11}\right) \quad \text{for } i \in \{0, 1, \dots, 9\}$$
   capturing the full temporal arc from initial posture (9%) through mid-action (27%–63%) to climax reaction (91%).
3. **Multimodal Cataloging:** Sends all 10 base64 frames in parallel to `gemini-3.8-flash-high` to generate a strict JSON metadata record, renames the file to `asli_fahru_{6_to_12_word_descriptive_slug}.mp4`, prepends it to `data/cat_assets_catalog.json` (`category: "fahru_sent"`, `cluster: "fahru_clips"`), and broadcasts a receipt to `#donies` in `agents_chat.db`.

### 4.3 Asset Catalog & Two-Pass Semantic Routing (`data/cat_assets_catalog.json`)
- **Current Verified Scale:** **45 total active clips** (**20 authentic Fahru clips** prefixed `asli_fahru_*` + **25 AI render clips** prefixed `ai_gen_{cluster}_*`), plus isolated serial directories (`/home/ubuntu/apps/ugc-lemonaru/content_series/spook_kitten_training/`).
- **Gated Category Bias & Anti-Fatigue Ledger (`ai_brain.doniesdaily_clip_usage`):**
  - Authentic `fahru_sent` clips receive a **+12 priority boost** (only when semantically relevant to the sentence), while `google_flow_render` clips receive a **-10 penalty** (acting as fallback/interleaving stock).
  - Two-pass allocation prioritizes Hook segments (`index 0, 1` with `1.5x` weight) and Climax segments (`1.3x` weight) first.
  - Queries `ai_brain.doniesdaily_clip_usage` to penalize recently used clips and strictly enforces **Hukum Besi #13** (zero clip or AI-cluster repetition within a single video; `audit_footage_assembly()` in `src/doni_qc_gate.py` aborts before render if `len(clip_strs) != len(unique_clips)`).

---

## 5. PUBLISHING & CHANNEL AUTOMATION

### 5.1 YouTube Data API v3 Publisher (`src/youtube_api_publisher.py`)
- Performs direct, browserless resumable uploads (`2MB` chunks, `mimetype="video/mp4"`, `categoryId="15"` Pets & Animals, `selfDeclaredMadeForKids=False`) via the official Google API Python client.
- Automatically appends `#Shorts` to titles if omitted and uploads the custom Remotion Still thumbnail via `youtube.thumbnails().set()`.
- Reconciles PostgreSQL state post-upload: updates `ai_brain.doniesdaily_content_ideas.status = 'published'` and inserts full telemetry metadata (`video_id`, `short_url`, `clips_used`, `duration_sec`) into `ai_brain.doniesdaily_posts`.

### 5.2 Self-Healing OAuth 2.0 Mechanism (`tools/doni_oauth_auto_healer.py`)
- **Primary Token Store:** `/home/ubuntu/.config/youtube/doniesdaily_oauth.json` (`token`, `refresh_token`, `client_id`, `client_secret`, `scopes`).
- **Auto-Healing Fallback:** In `YouTubeAPIPublisher._ensure_valid_token()`, if standard `self.creds.refresh(Request())` fails (e.g., `invalid_grant` or expired testing refresh token), it catches the exception and invokes `/home/ubuntu/tools/doni_oauth_auto_healer.py` via subprocess. The healer attaches to the persistent Chrome CDP session (`:9222`), completes the Google OAuth consent flow headlessly, writes the fresh token pair back to `/home/ubuntu/.config/youtube/doniesdaily_oauth.json`, and reloads `self.creds` seamlessly without human intervention.

### 5.3 Unified Cadence Dispatcher & Jitter Gatekeeper
Active schedules are governed by PostgreSQL table `ai_brain.cadence_tasks` and local state file `/home/ubuntu/apps/ugc-lemonaru/data/doni_daily_jitter.json`:

| Task Key (`ai_brain.cadence_tasks`) | Cron Expression | Target Script & Arguments | Operational Status & Purpose |
| :--- | :--- | :--- | :--- |
| `business.doni_morning_standup` | `30 7,17 * * *` | `/home/ubuntu/tools/doni_working_hours_standup.py` | **ACTIVE** — Runs 2x daily (07:30 & 17:30 WIB) for Mochi telemetry audit, Doni Argon-High evaluation, Luna script drafting, and Obsidian Vault archiving. |
| `business.doni_morning_production` | `*/5 8 * * *` | `/home/ubuntu/tools/doni_production_sprint.py --jitter-window --slot morning` | **ACTIVE** — Polls every 5m during 08:00 hour; fires once at pre-rolled random timestamp (`08:04:07`–`08:55:49 WIB`). |
| `business.doni_midday_serial` | `*/5 12 * * *` | `/home/ubuntu/tools/doni_production_sprint.py --slot midday_serial` | **ACTIVE** — Fires during 12:00 WIB window (`12:04`–`12:25 WIB` jitter) for dedicated multi-part series (*Spook the Kitten Training*). |
| `business.doni_afternoon_production` | `*/5 18 * * *` | `/home/ubuntu/tools/doni_production_sprint.py --jitter-window --slot evening` | **ACTIVE** — Polls every 5m during 18:00 hour; fires once at pre-rolled random timestamp (`18:04:07`–`18:55:49 WIB`). |
| `business.doni_community_replier` | `0 8-22/2 * * *` | `/home/ubuntu/tools/doni_replier_runner.sh` | **ACTIVE** — Runs every 2 hours (08:00–22:00 WIB) to reply to viewer comments via Kak Ceria persona. |
| `business.doni_youtube_autopost` | `*/30 7-22 * * *` | `/home/ubuntu/tools/doni_runner.sh` | **PAUSED** — Legacy 4–5x daily burst runner, superseded by the 3-slot jittered sprint architecture. |

- **Double-Trigger Prevention:** `check_and_consume_jitter_window()` writes `"fired": true` and `"fired_at"` to `data/doni_daily_jitter.json` **immediately before** executing `time.sleep(target_sec)` and rendering, guaranteeing that subsequent `*/5` cron ticks within the same hour cannot double-trigger a build.

---

## 6. HOST & SECURITY HYGIENE AUDIT

### 6.1 Host Environment Profile & Resource Isolation
- **OS & Kernel:** Ubuntu 24.04 LTS (`x86_64`), **2 vCPUs, 4GB Physical RAM**.
- **Containerized Backing Services:** Supabase PostgreSQL (`supabase-db` container accessed via `docker exec -i supabase-db psql -U postgres -d postgres`), housing schema `ai_brain` (`doniesdaily_posts`, `doniesdaily_content_ideas`, `doniesdaily_production_queue`, `doniesdaily_clip_usage`, `doniesdaily_learnings`, `doniesdaily_metrics_history`, `doniesdaily_sniper_logs`, `cadence_tasks`).
- **Observability & Audit Databases:**
  - SQLite Swarm Matrix: `/home/ubuntu/vps-control-center/backend/data/agents_chat.db` (`agent_messages` & `agent_traces` tables powering the VPS Control Center UI).
  - Obsidian Knowledge Vault: `/home/ubuntu/vault/01_Business/doniesdaily/` (`ActiveContext.md`, `Index - doniesdaily.md`, and timestamped meeting devlogs).
- **Display Server:** Headless `Xvfb :99` hosting persistent Google Chrome (`--remote-debugging-port=9222`) for YouTube Studio Advanced Mode scraping (`tools/doni_evaluator.py`), OAuth auto-healing (`tools/doni_oauth_auto_healer.py`), and Google Flow generation (`src/flow_cdp_operator.py`).

### 6.2 Credential Security Evaluation
| Secret / Credential Type | Storage Location / Mechanism | Audit Status & Risk Assessment |
| :--- | :--- | :--- |
| **YouTube OAuth 2.0 Credentials** | `/home/ubuntu/.config/youtube/doniesdaily_oauth.json` | **SECURE (Out-of-Repo)** — Stored outside the application Git repository in `.config`. No Google `client_secret` or `refresh_token` is hardcoded in Python source files. |
| **ElevenLabs API Key** | Environment variable (`.env` / `src/elevenlabs_tts.py`) | **SECURE** — Loaded from environment configuration; not exposed in committed source code. |
| **CLIProxyAPI Key (`:8317`)** | `os.getenv("CPA_API_KEY", "cpa-secret-key-12345")` in `doni_scriptwriter.py` & `doni_working_hours_standup.py` | **LOW RISK (Localhost-Bound) / MINOR HYGIENE FINDING** — While `cpa-secret-key-12345` appears as a default fallback in code, CLIProxyAPI binds strictly to loopback (`127.0.0.1:8317`) and is not exposed to the public interface. Moving the fallback completely into `.env` is recommended. |
| **Telegram Owner Chat ID** | `OWNER_CHAT_ID = "1357517232"` in `doni_production_sprint.py` & `doni_working_hours_standup.py` | **INFORMATIONAL** — Non-secret numeric recipient ID; should be externalized to `.env` for multi-tenant portability. |
| **Chrome Persistent Session** | `/home/ubuntu/apps/ugc-lemonaru/data/chrome_persistent` | **MEDIUM OPERATIONAL SENSITIVITY** — Contains authenticated Google session cookies for `@DoniesDaily`. Protected by host filesystem permissions (`ubuntu` user) and bound to local CDP port `9222`. |

### 6.3 Reusability & Multi-Tenant Portability Assessment
To clone the `@DoniesDaily` architecture for a second autonomous channel or external client tenant, the following coupling points were identified from the codebase:

1. **Highly Portable / Modular Layers (Ready for Multi-Tenant Reuse):**
   - `src/youtube_api_publisher.py`: Accepts arbitrary `oauth_path` in `YouTubeAPIPublisher(oauth_path=...)`.
   - `src/doni_qc_gate.py`: 100% channel-agnostic broadcast inspector (`inspect_video()`, `audit_footage_assembly()`).
   - `remotion/src/DoniOverlay.tsx`: Parameterized via Zod schema (`doniOverlaySchema`), allowing dynamic injection of `hookTitle`, `badgeText`, `captionsFile`, and `storyCardText`.

2. **Hardcoded Single-Tenant Couplings Requiring Parameterization:**
   - **Filesystem Paths:** Absolute paths (`/home/ubuntu/apps/ugc-lemonaru`, `/home/ubuntu/tools`, `/home/ubuntu/vault/01_Business/doniesdaily`) are hardcoded across `doni_production_sprint.py`, `doni_working_hours_standup.py`, and `doni_scriptwriter.py`.
   - **Database Table Names:** SQL queries directly target `ai_brain.doniesdaily_*` tables via `docker exec -i supabase-db psql` rather than filtering by a `channel_id` / `tenant_id` column or reading a tenant prefix from environment variables.
   - **Brand Watermark & CTA Strings:** `@DoniesDaily` is hardcoded inside `remotion/src/DoniOverlay.tsx` (`<span>@DoniesDaily</span>`) and `src/doni_qc_gate.py` (`audit_script_and_outro()` checks for `"doniesdaily"` or `"doni"`).
   - **Legacy Template Defaults:** `HookTitle.tsx` (`badgeText = "🔥 RACUN TIKTOK OOTD"`) and `OutroCTA.tsx` (`headline = "CHECKOUT SEKARANG!"`, `buttonText = "KLIK KERANJANG KUNING"`) retain default prop strings from the parent `ugc-lemonaru` e-commerce template when not overridden by `DoniOverlay` props.

---

## 7. SUMMARY OF INFRASTRUCTURE INVARIANTS & VERIFIED METRICS

| Infrastructure Dimension | Verified Specification / Metric | Governing Rule / Source |
| :--- | :--- | :--- |
| **Host Compute** | Ubuntu 24.04 LTS, 2 vCPUs, 4GB RAM | Host Infrastructure |
| **Video Output Standard** | `1080x1920` (9:16), `30 FPS`, H.264 MP4, `0` Black Frames (`>=0.5s`) | `src/doni_qc_gate.py` / `CLEO_SOUL.md` |
| **Audio Broadcast Standard** | `-14.0` to `-19.0 LUFS` (Operating at `-14.5` to `-16.6 LUFS`), TP `<= -1.0 dBFS` | EBU R128 / `CLEO_SOUL.md` |
| **Master Clock Sync** | `dur_video >= dur_audio - 0.1s` (Max drift tolerance `<= 1.5s` in `doni_qc_gate.py`) | Hukum Besi #3 / The Iron Guard |
| **Subtitle Kinetic Rate** | `SWITCH_CAPTIONS_EVERY_MS = 0` (Strict 1 word per pop-up, `#FFE600` highlight) | Hukum Besi #8 & #15 (`DoniOverlay.tsx`) |
| **Visual Pacing & Variety** | `14–18` unique cuts per 60s video (`3.2s–4.0s` per cut) or sentence-synced beats, `0` loops | Hukum Besi #13 (`MILO_SOUL.md`) |
| **Active Footage Catalog** | `45` total verified clips (`20` authentic `fahru_sent` + `25` AI `google_flow_render`) | `data/cat_assets_catalog.json` |
| **Active SFX Reservoir** | `10` micro-faded viral MP3 sound effects (`0.7s`–`2.7s`) | `sfx_catalog.json` / `src/doni_sfx_helper.py` |
| **Daily Release Cadence** | `3` Shorts/day (`08:04–08:56` Daily #1, `12:04–12:25` Serial, `18:04–18:56` Daily #2) | `ai_brain.cadence_tasks` / `doni_production_sprint.py` |