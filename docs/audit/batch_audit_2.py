import sys
import time
from pathlib import Path
from audit_context import get_complete_knowledge_context
from generate_audit_doc import call_argon

AUDIT_DIR = Path("/home/ubuntu/donies_daily_master_audit")

PROMPTS = {
    "06_PROMPT_MEMORY_AUDIT.md": """
Produce Deliverable 06: `06_PROMPT_MEMORY_AUDIT.md`
Phase 5: PROMPT, MEMORY & KNOWLEDGE AUDIT (CRITICAL ANALYSIS)

Exhaustively audit how information, context, and knowledge are stored, retrieved, and isolated:
1. Prompt Architecture Audit:
   - Deep structural inspection of all 8 SOUL.md files (DONI, MOCHI, LUNA, MILO, KAK_CERIA, VIVAN, CLEO, voice.md).
   - Prompt inheritance vs duplication patterns across agents.
   - Channel-specific assumptions hardcoded into universal agent prompts (e.g. cat biology, pawrents slang, Solo/Boyolali cultural nuances, specific ElevenLabs voice IDs).
   - Conflicting instructions between agent souls (e.g. Luna wanting creative pacing vs Cleo strict duration limits vs Mochi data rules).
2. Memory Architecture & Persistence Tiers:
   - Tier 1: Ephemeral Turn Context (Claude/Gemini API message history, per-turn prompt injection).
   - Tier 2: Short-Term Swarm Communication (SQLite agents_chat.db: agent_messages & agent_traces).
   - Tier 3: Mid-Term State & Queue (PostgreSQL ai_brain.doniesdaily_production_queue & doniesdaily_content_ideas).
   - Tier 4: Long-Term Quantitative Telemetry (ai_brain.doniesdaily_posts, doniesdaily_metrics_history, doniesdaily_clip_usage).
   - Tier 5: Evolving Strategic Memory (ai_brain.doniesdaily_learnings with 13 active rules, confidence scores).
   - Tier 6: Architectural Executive Knowledge (Obsidian Vault GRO v3.0: ActiveContext.md, devlogs, sub-MOC).
3. Cross-Channel Context Leakage & Memory Contamination Risks:
   - Identify every data point, prompt directive, or database record that would poison a second channel (e.g. YouTube Team B in finance or tech) if inherited directly.
   - What MUST remain isolated per channel?
   - What CAN safely be shared in a universal multi-channel framework?
   - Strict boundaries between Holding Orchestrator memory vs Channel production memory.
4. Prompt & Memory Refactoring Recommendations:
   - Blueprint for parameterizing SOUL files with dynamic jinja/mustache variables ({{CHANNEL_NICHE}}, {{AUDIENCE_DEMOGRAPHIC}}, {{VOICE_STYLE}}, {{AVATAR_NAME}}).
""",

    "07_TOOLS_INFRASTRUCTURE.md": """
Produce Deliverable 07: `07_TOOLS_INFRASTRUCTURE.md`
Phase 6: TOOLS, MODELS & INFRASTRUCTURE AUDIT

Provide a complete, verified technical catalog of all models, tools, scripts, APIs, and host infrastructure:
1. Model Routing & AI Providers:
   - CLIProxyAPI (:8317) multi-account load balancer (support.ternakos & anakbawangstore).
   - Detailed mapping:
     * gemini-4-argon-high -> Used by Doni (Standup & Evaluation) & Mochi (Analytics Forensics).
     * claude-sonnet-5-5-high -> Used by Luna (Scriptwriting).
     * claude-opus-5-5-high -> Used by Milo (Remotion cut planning).
     * gemini-3.8-flash-high -> Daily Hermes holding operations, vision ingestion.
     * ElevenLabs Multilingual v2 / v4 Turbo -> Vivan voice synthesis.
     * 0-Token Deterministic Workers -> Cleo QC Gate, FFmpeg muxing, Jitter scheduler.
   - Token economics, rate limits, latency profiles, and cost implications observed.
2. Rendering & Video Engineering Infrastructure:
   - React Remotion engine (/home/ubuntu/apps/ugc-lemonaru/remotion):
     * Components: DoniOverlay.tsx, DoniShort/index.tsx, HookTitle.tsx, OutroCTA.tsx, StoryCoverCard.tsx, SubtitlePage.tsx.
     * Font assets: theboldfont.ttf, Montserrat Bold.
     * Remotion composition render -> ProRes 4444 (.mov with alpha channel) -> FFmpeg composite with raw background video.
     * Why hybrid rendering was implemented (VPS 2-core / 4GB RAM CPU bottleneck vs browser OOM).
3. Audio, Voice & SFX Infrastructure:
   - ElevenLabs API integration (elevenlabs_tts.py).
   - Vivan fine-tuning dataset harvester (assets/audio/vivan_dataset/ 24kHz mono slices).
   - Audio normalization: FFmpeg loudnorm filter (target -14.5 to -16.6 LUFS, TP -1.0, LRA 9/11).
   - SFX Arsenal (doni_sfx_helper.py, sfx_catalog.json, 10 curated viral sound effects).
4. Visual Footage Sourcing Infrastructure:
   - Google Flow / Veo2 AI generation via persistent Chrome CDP (:9222 / flow_cdp_operator.py).
   - Authentic owner footage ingestion pipeline (ingest_fahru_footage.py, 10-frame multi-vision extraction).
   - Asset catalog architecture (cat_assets_catalog.json, 45 active clips, anti-fatigue tracking).
5. Publishing & Channel Automation:
   - YouTube Data API v3 OAuth 2.0 (youtube_api_publisher.py, /home/ubuntu/.config/youtube/doniesdaily_oauth.json).
   - OAuth auto-healing via Chrome CDP (doni_oauth_auto_healer.py).
   - Scheduled task triggers (ai_brain.cadence_tasks, system crontab, Jitter window).
6. Host & Security Hygiene Audit:
   - Host environment: Ubuntu 24.04 LTS (x86_64, 2 vCPUs, 4GB RAM).
   - Credential security evaluation (location of tokens, .env files, no hardcoded secrets in code).
   - Reusability & Multi-Tenant Portability Assessment.
""",

    "08_QA_RELIABILITY_AUDIT.md": """
Produce Deliverable 08: `08_QA_RELIABILITY_AUDIT.md`
Phase 7: QUALITY CONTROL & RELIABILITY AUDIT

Evaluate the technical enforcement, robustness, and reliability of the quality control mechanisms:
1. Cleo QC Gatekeeper Deep Dive (src/doni_qc_gate.py):
   - Inspection criteria:
     * File existence & size check (> 1.0 MB)
     * ffprobe stream validation (video h264/yuv420p, audio aac/stereo)
     * Resolution assertion (exact 1080x1920, 9:16 aspect ratio)
     * Duration compliance (Shorts limit: >= 10.0s and <= 59.9s)
     * Audio-Video drift & sync check (delta <= 1.5s in code / 0.5s in soul)
     * Black frame detection (ffmpeg blackdetect=d=0.5:pix_th=0.10)
     * Integrated Loudness audit (ebur128 filter, target -14.0 to -19.0 LUFS)
     * The Iron Guard duration assert: video duration >= audio duration (anti-cutoff)
2. Script Quality & Content Compliance Gates:
   - Luna script length checks (110–135 words for 50-60s Shorts).
   - Outro CTA audit (audit_script_and_outro regex for follow & subscribe verbal + visual).
   - Deduplication query on ai_brain.doniesdaily_posts before script lock.
3. In-Place Self-Healing Revision Loop Audit:
   - Implementation in doni_production_sprint.py & doni_remotion_flow_pipeline.py.
   - Retry logic: up to 3 revision attempts per topic.
   - Remotion overlay caching: caching ProRes 4444 overlay to avoid re-rendering graphics during footage swaps.
   - Emergency force-fit audio stretch guard (setpts factor <= 1.5x).
4. Reality Gap Analysis (Intended vs Actually Enforced):
   - Gaps where prompt descriptions promise enforcement but code relies on heuristics or fallbacks.
   - Inconsistencies between SOUL.md files and actual Python scripts.
   - Stress test failure modes (what happens when API fails, quota exhausted, or rendering hangs).
5. Reliability Scorecards:
   - Individual reliability score (0-100%) for each agent (Doni, Mochi, Luna, Milo, Kak Ceria, Vivan, Cleo).
   - Overall system reliability rating and mean time between failure (MTBF) estimation.
""",

    "09_UNIVERSALIZATION_MATRIX.md": """
Produce Deliverable 09: `09_UNIVERSALIZATION_MATRIX.md`
Phase 8: UNIVERSALIZATION ANALYSIS & 3-LAYER CLASSIFICATION MATRIX

Systematically dissect the entire Donies Daily system into 3 clean architectural layers:
1. Theoretical Framework:
   - LAYER 1: UNIVERSAL CORE (Channel-Agnostic Engine, Reusable by 100% of future teams).
   - LAYER 2: TEAM CONFIGURATION (Pluggable Settings, Personas, Models & Schedules per team).
   - LAYER 3: CHANNEL IDENTITY (Isolated Brand, Niche, Voice, Content History & Audience Assets).
2. Comprehensive Component Classification Matrix:
   - Map EVERY script, soul, table, component, configuration, and asset into Layer 1, 2, or 3.
   - Columns: Component Name, Type, Path, Current Role in Donies Daily, Assigned Layer, Technical Justification, Extraction / Decoupling Effort (Low/Med/High).
   - Components to classify:
     * Orchestration scripts (doni_production_sprint.py, doni_working_hours_standup.py, doni_smart_scheduler.py)
     * Content generation (doni_scriptwriter.py, doni_content_strategist.py)
     * Voice & Audio (elevenlabs_tts.py, custom_vivan_tts.py, vivan_dataset_harvester.py, doni_sfx_helper.py)
     * Visual & Video (doni_remotion_flow_pipeline.py, doni_hybrid_renderer.py, doni_visual_director.py, flow_cdp_operator.py)
     * Quality Control (doni_qc_gate.py)
     * Publishing & Engagement (youtube_api_publisher.py, doni_studio_replier.py, doni_comment_sniper.py)
     * Remotion Components (DoniOverlay, HookTitle, OutroCTA, StoryCoverCard, SubtitlePage)
     * Database Schemas (the 7 ai_brain tables, SQLite agents_chat.db)
     * Souls & Prompts (the 8 SOUL.md files)
     * Legacy Velora AI / TikTok Shop files (affiliate_pipeline.py, scoring.py, etc.)
3. Analysis of Non-Generalizable Elements:
   - What components are so tightly coupled to cat humor or Donies Daily that they cannot be abstracted?
   - What must be completely rewritten or isolated?
4. Decoupling Action Items:
   - Clear guidelines on how to extract Layer 1 without breaking the live Donies Daily channel.
"""
}

def run_batch(doc_names):
    print("Loading verified system context...")
    ctx = get_complete_knowledge_context()
    print(f"Context loaded ({len(ctx)} chars). Starting document generation...\n")

    for doc_name in doc_names:
        out_path = AUDIT_DIR / doc_name
        if out_path.exists() and out_path.stat().st_size > 1000:
            print(f"⏭️ Skipping {doc_name} (already exists, {out_path.stat().st_size} bytes)")
            continue

        prompt = PROMPTS.get(doc_name)
        if not prompt:
            print(f"❌ No prompt defined for {doc_name}")
            continue

        print(f"🚀 Generating {doc_name} via gemini-4-argon-high...")
        t0 = time.time()
        try:
            content = call_argon(prompt, ctx)
            out_path.write_text(content, encoding="utf-8")
            elapsed = time.time() - t0
            print(f"✅ Generated {doc_name} ({len(content)} chars, {out_path.stat().st_size} bytes) in {elapsed:.1f}s\n")
        except Exception as e:
            print(f"❌ Failed to generate {doc_name}: {e}\n", file=sys.stderr)

if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(PROMPTS.keys())
    run_batch(targets)
