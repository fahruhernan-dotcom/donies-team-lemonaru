# 📦 DELIVERABLE 01: `VIRGIN_CLONE`
## Canonical Directory Pointer to Donies Virgin System

The complete, operational, independent codebase of **Donies Virgin** is located at:

📁 **Directory:** `/home/ubuntu/donies-team-lemonaru/donies-virgin/`  
🌿 **Branch:** `feature/donies-virgin-clone`  

### Directory Architecture

```text
donies-virgin/
├── config/
│   ├── team_config.yaml          # Agent definitions, hierarchy, and model routing
│   ├── channel_config.yaml       # Channel identity, niche, CTA, and table namespaces
│   └── .env.example              # Safe credentials template
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
└── tests/
    └── test_virgin_parity.py     # Automated parity & isolation test suite
```
