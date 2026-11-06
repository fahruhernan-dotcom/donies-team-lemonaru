# ✂️ DELIVERABLE 04: `CHANNEL_CONTEXT_SEPARATION.md`
## Demarcation of Reusable Intelligence vs Channel Identity

**Clone Instance:** DONIES VIRGIN (`donies-virgin/`)  
**Core Axiom:** COPY THE BRAIN. PRESERVE THE LOGIC. CLEAN THE CHANNEL CONTEXT.  

---

### 1. Architectural Demarcation Framework

The cloning process strictly separates the operational system into two distinct domains:

```
┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│        TEAM INTELLIGENCE (PRESERVED)         │         CHANNEL IDENTITY (SEPARATED)         │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ • Agent Identities (Doni, Mochi, Luna, Milo, │ • YouTube Channel ID (UCNPtjF2aB0wvWHI0q7hh) │
│   Ceria, Vivan, Cleo)                        │ • Channel Handle (@DoniesDaily)              │
│ • Cognitive Model Routing (Argon, Sonnet,    │ • Channel Niche (Cats, Anabul, Feline Sci)   │
│   Opus, Flash)                               │ • Target Audience (Cat owners, Pawrents)     │
│ • Speech-Beat Scene Cut Algorithm            │ • Specific Voice ID (ElevenLabs Vivan Voice) │
│ • 10-Frame Temporal Vision Ingestion SOP     │ • Historical Posts Archive (32 Shorts)       │
│ • 14-Cut Anti-Fatigue Rules                  │ • Historical Metrics (100-pt retention curves│
│ • Hybrid Remotion + FFmpeg Compositing Engine│ • 13 Donies Daily Dynamic Learning Rules     │
│ • Cleo QC Broadcast Enforcement Rules        │ • Cat Asset B-Roll Footage (45 clips)        │
│ • Jitter Window Cadence Governor             │ • Feline Phonetic Regex Dictionary           │
│ • Standup 9-Step Deliberation Protocol       │ • Outro CTA Text ("SUBSCRIBE @DoniesDaily")  │
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

---

### 2. Granular Inventory of Separated Components

#### A. YouTube Channel Credentials & Identifiers
- **Original:** `UCNPtjF2aB0wvWHI0q7hhcCg` (`@DoniesDaily`), tokens stored in `/home/ubuntu/.config/youtube/doniesdaily_oauth.json`.
- **Virgin Separation:** Parameterized via `donies-virgin/config/channel_config.yaml` (`channel.id`, `channel.handle`) and independent credentials file path `config/virgin_oauth_token.json`. Original YouTube OAuth credentials were **never copied**.

#### B. Voice Identity & Synthesis Parameters
- **Original:** Vivan male voice ID hardcoded in `elevenlabs_tts.py` and `voice.md`.
- **Virgin Separation:** Extracted into `channel_config.yaml` (`voice_identity.voice_id`) with environment override `ELEVENLABS_VOICE_ID`. The Virgin team can bind to any ElevenLabs voice ID (e.g. female, British, authoritative, energetic) without touching the synthesis code.

#### C. Content Niche & Target Audience
- **Original:** Exclusively domestic cat biology, feline behavior, and Indonesian "pawrents" vernacular.
- **Virgin Separation:** Niche definition extracted into `channel_config.yaml` (`niche.primary_topic`, `niche.target_audience`, `niche.slang_register`). The Virgin instance can be configured for tech, finance, motivation, or history while retaining the high-tempo conversational register.

#### D. Verbal & Visual Call-to-Action (CTA)
- **Original:** Hardcoded in `DoniOverlay.tsx` lines 152–156 (`"SUBSCRIBE @DoniesDaily"`, `"Follow Buat Fakta Anabul Tiap Hari! 🐾"`).
- **Virgin Separation:** `DoniOverlay.tsx` was parameterized to accept `outroHeadline`, `outroSubheadline`, and `outroButtonText` as reactive props, falling back to clean channel defaults.

#### E. Historical Production Records & Learning State
- **Original:** 32 published posts in `ai_brain.doniesdaily_posts`, 13 duration and topic rules in `ai_brain.doniesdaily_learnings`, and 45 cat clips in `data/cat_assets_catalog.json`.
- **Virgin Separation:** Re-routed to `ai_brain.virgin_posts` (0 rows), `ai_brain.virgin_learnings` (0 rows), and `data/assets_catalog.json` (clean starter template). Zero historical data was copied over, preventing memory contamination.

---

### 3. Proof of Non-Exposure of Secrets
A cryptographic inspection of `donies-virgin/` verifies:
- Zero raw API keys (no ElevenLabs keys, no Groq keys, no YouTube client secrets).
- `.env.example` provides only variable names and descriptive placeholder strings.
- All credential paths reference independent file locations.
