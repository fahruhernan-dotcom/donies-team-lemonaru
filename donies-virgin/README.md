# 🎬 Donies Virgin — Autonomous Multi-Agent YouTube Shorts Studio

> **"Copy the Brain. Preserve the Logic. Clean the Channel Context. Create an Independent Team."**

**Donies Virgin** is an exact, uncoupled, logical duplicate of the **Donies Daily** autonomous production ecosystem. It preserves 100% of the original agent intelligence, cognitive models, media engineering, and self-healing quality control gates while cleanly separating the YouTube channel identity, niche, voice, and database persistence.

---

## ⚡ Quick Start (Under 5 Minutes)

### 1. One-Click Environment Setup
Run the automated initialization script from inside `donies-virgin/`:
```bash
cd donies-virgin
./setup_env.sh
```
This script will:
- Create Python `.venv` and install all dependencies from `requirements.txt`.
- Install Node.js Remotion packages in `remotion/`.
- Generate `config/.env` from `.env.example`.
- Initialize isolated PostgreSQL tables (`ai_brain.virgin_*`) and SQLite Swarm Matrix.
- Execute the 5-module automated parity verification suite.

### 2. Configure Your Channel Identity
Open `config/channel_config.yaml` and set your channel parameters:
```yaml
channel:
  id: "UC_YOUR_NEW_CHANNEL_ID"
  handle: "@YourChannelHandle"
  name: "Your Channel Name"

niche:
  primary_topic: "Tech & AI Innovations" # Any niche: Finance, Motivation, Stoicism, etc.
  target_audience: "Tech enthusiasts and creators (18-35)"
  language: "id-ID"

content_rules:
  cta:
    verbal: "Follow dan subscribe buat update AI tercepat!"
    visual_title: "SUBSCRIBE"
    visual_subtitle: "Update AI Setiap Hari!"

voice_identity:
  voice_id: "YOUR_ELEVENLABS_VOICE_ID"
```

### 3. Add Credentials to `config/.env`
```bash
nano config/.env
```
Provide your `ELEVENLABS_API_KEY` and path to your YouTube Data API v3 OAuth token.

### 4. Verify Parity & State Isolation
```bash
python3 tests/test_virgin_parity.py
```
Expected output: `🎉 ALL 5 PARITY & ISOLATION TESTS PASSED WITH 100% SUCCESS!`

### 5. Trigger Autonomous Production
```bash
python3 tools/doni_production_sprint.py
```

---

## 👥 The Autonomous Agent Squad

| Agent Persona | Assigned Engine | Role & Operational Responsibility |
| :--- | :--- | :--- |
| **👑 Ketua Doni** | `gemini-4-argon-high` | **Squad Chairman & Lead Producer:** Runs daily standups (07:30 & 17:30 WIB), manages 3-slot daily jitter windows, executes Stage 1 pre-sprint and Stage 2 editorial sign-offs. |
| **📊 Mochi** | `gemini-4-argon-high` | **Analytics & Retention Forensics:** Queries YouTube Analytics API v2 for 100-point retention curves (`audienceWatchRatio`), identifies drop-offs, and updates active learning rules in SQL. |
| **✍️ Luna** | `claude-sonnet-5-5-high` | **Master Scriptwriter:** Crafts 108–124 word high-retention Indonesian scripts with 4.5s second-hook open loops, acoustic punctuation, and channel-specific CTAs. |
| **🎬 Milo** | `claude-opus-5-5-high` | **Visual Director & Remotion Cut Planner:** Maps speech-beats to B-roll footage, plans 14–18 fast cuts, prevents viewer clip fatigue, and triggers sound effects. |
| **🎙️ Kak Ceria** | `ElevenLabs v2/v4` | **Senior Voice Director & Community Lead:** Supervises emotional pitch and automates audience community engagement. |
| **🗣️ Vivan** | `0-Token Worker` | **Voice Synthesizer Sub-Unit:** Synthesizes voiceover stems, extracts word-level JSON timestamps, and harvests 24kHz mono slices for dataset fine-tuning. |
| **🛡️ Cleo** | `0-Token Deterministic` | **Broadcast QC Gatekeeper:** Strictly asserts 1080x1920 (9:16) resolution, duration limits (10.0s - 59.9s), EBU R128 loudness (-14.5 LUFS), black frame detection, and audio-visual sync. |

---

## 📁 Directory Architecture

```text
donies-virgin/
├── config/
│   ├── team_config.yaml          # Agent definitions, hierarchy, and model routing
│   ├── channel_config.yaml       # Channel identity, niche, CTA, and table namespaces
│   ├── .env.example              # Safe credentials template
│   └── .env                      # Local runtime environment (gitignored)
├── souls/                        # 100% Preserved Agent Prompts
│   ├── DONI_SOUL.md
│   ├── MOCHI_SOUL.md
│   ├── LUNA_SOUL.md
│   ├── MILO_SOUL.md
│   ├── KAK_CERIA_SOUL.md
│   ├── VIVAN_SOUL.md
│   ├── CLEO_SOUL.md
│   └── voice.md
├── src/                          # Core Execution & Rendering Modules
│   ├── config_loader.py          # Unified config & table resolver
│   ├── doni_engine.py            # Squad engine & event loop
│   ├── doni_qc_gate.py           # Cleo QC broadcast inspector
│   ├── doni_remotion_flow_pipeline.py
│   ├── doni_hybrid_renderer.py   # Hybrid ProRes 4444 + FFmpeg compositor
│   ├── doni_visual_director.py   # Milo speech-beat cut planner (Opus)
│   ├── doni_sfx_helper.py        # Sound effect injector
│   ├── elevenlabs_tts.py         # Dynamic voice synthesis adapter
│   ├── youtube_api_publisher.py  # Multi-tenant YouTube publisher
│   └── media_muxer.py            # FFmpeg audio ducking & loudnorm
├── tools/                        # Production & Telemetry Runners
│   ├── doni_production_sprint.py # Autonomous sprint & 3x self-healing retry
│   ├── doni_working_hours_standup.py # 07:30 & 17:30 WIB standup runner
│   ├── doni_smart_scheduler.py   # Jitter window governor
│   ├── doni_evaluator.py         # Retention forensics (100-pt curve)
│   ├── doni_scriptwriter.py      # Luna scriptwriter & deduplication check
│   ├── doni_comment_sniper.py    # Organic community engagement
│   ├── doni_studio_replier.py    # Auto-replier
│   └── yt_agent_tools/           # Algorithmic scoring toolset
├── remotion/                     # Parametric React Remotion Engine
│   ├── package.json
│   ├── remotion.config.ts
│   ├── src/
│   │   ├── DoniOverlay.tsx       # Parametric kinetic overlay
│   │   ├── components/           # HookTitle, OutroCTA, StoryCoverCard
│   │   └── CaptionedVideo/       # Hormozi kinetic word-by-word captions
│   └── public/                   # TheBoldFont, SFX arsenal
├── database/                     # Isolated Persistence DDL & Initializers
│   ├── virgin_schema.sql         # Clean PostgreSQL tables (ai_brain.virgin_*)
│   ├── init_virgin_db.py         # One-click isolated DB initializer
│   └── agents_chat_schema.sql    # SQLite Swarm Matrix schema
├── data/                         # Isolated Operational State
│   ├── assets_catalog.json       # Clean footage catalog template
│   ├── doni_daily_jitter.json    # Fresh 3-slot jitter schedule
│   ├── doni_scheduler_state.json # Clean daily post counter
│   └── virgin_agents_chat.db     # Isolated Swarm Matrix database
├── tests/
│   └── test_virgin_parity.py     # Automated parity & isolation test suite
├── requirements.txt              # Complete Python package requirements
└── setup_env.sh                  # One-click automated setup script
```

---

## 🛡️ Database & State Isolation Guarantee

Donies Virgin uses isolated database namespaces to guarantee **zero cross-channel data pollution**:

```
┌──────────────────────────────────────┬──────────────────────────────────────┐
│ Donies Daily (Production)            │ Donies Virgin (Isolated Instance)    │
├──────────────────────────────────────┼──────────────────────────────────────┤
│ ai_brain.doniesdaily_posts           │ ai_brain.virgin_posts                │
│ ai_brain.doniesdaily_content_ideas   │ ai_brain.virgin_content_ideas        │
│ ai_brain.doniesdaily_production_queue│ ai_brain.virgin_production_queue     │
│ ai_brain.doniesdaily_learnings       │ ai_brain.virgin_learnings            │
│ ai_brain.doniesdaily_metrics_history │ ai_brain.virgin_metrics_history      │
│ ai_brain.doniesdaily_clip_usage      │ ai_brain.virgin_clip_usage           │
│ ai_brain.doniesdaily_sniper_logs     │ ai_brain.virgin_sniper_logs          │
│ data/agents_chat.db (#donies)        │ data/virgin_agents_chat.db (#virgin) │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 🛠️ Operational CLI Commands

| Action | Command | Description |
| :--- | :--- | :--- |
| **Run Daily Standup** | `python3 tools/doni_working_hours_standup.py` | Evaluates telemetry, updates learning rules, signs off on topics |
| **Run Production Sprint** | `python3 tools/doni_production_sprint.py` | Full autonomous pipeline: script -> voice -> render -> QC -> upload |
| **Run Cleo QC Manually** | `python3 -c "import doni_qc_gate; print(doni_qc_gate.inspect_video('path/to/video.mp4'))"` | Verifies resolution, duration, LUFS loudness, black frames |
| **Run Parity Tests** | `python3 tests/test_virgin_parity.py` | 5-module verification of agent parity and DB isolation |
| **Re-initialize DB** | `python3 database/init_virgin_db.py` | Idempotently creates or validates Virgin PostgreSQL & SQLite tables |

---

## 📜 Preserved Engineering Principles (15 Hukum Besi)

1. **Shorts Duration:** Strict limit between `10.0s` and `59.9s`.
2. **Broadcast Geometry:** Vertical `1080x1920` (`9:16`).
3. **Audio-First Clock:** Video length is governed by the narration audio stem duration.
4. **Speech-Beat Cuts:** 14–18 fast dynamic cuts mapped to spoken phrases.
5. **Hybrid Rendering:** Transparent ProRes 4444 `.mov` rendered in Remotion, then composited over footage via FFmpeg to prevent VPS CPU choke.
6. **Kinetic Captions:** Alex Hormozi single-word-by-word highlight with `TheBoldFont`.
7. **EBU R128 Loudness:** Final audio normalized to `-14.5 LUFS`.
8. **In-Place Self-Healing:** Up to 3 automatic retries if QC fails before topic fallback.
