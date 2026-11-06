import sys
import time
from pathlib import Path
from audit_context import get_complete_knowledge_context
from generate_audit_doc import call_argon

AUDIT_DIR = Path("/home/ubuntu/donies_daily_master_audit")

PROMPTS = {
    "10_VIRGIN_MASTER_BLUEPRINT.md": """
Produce Deliverable 10: `10_VIRGIN_MASTER_BLUEPRINT.md`
Phase 9: VIRGIN MASTER TEMPLATE DESIGN (ARCHITECTURAL PROPOSAL)

Design the clean, uncoupled, reusable master framework (e.g., `OMNI_CHANNEL_AI_STUDIO` / `DONIES_MASTER`) that preserves the proven agentic capabilities while completely stripping out Donies Daily's channel identity:
1. Architectural Core Principles:
   - Zero hardcoded assumptions (no hardcoded cats, pawrents, specific voice IDs, or channel IDs).
   - Strict Separation of Concerns (Core Orchestration vs Team Manifest vs Channel Identity).
   - Pluggable Engine Architecture (Swappable TTS providers, swappable video generators, swappable LLM models).
2. Proposed Directory & File Architecture:
   - Complete, professional ASCII tree diagram showing:
     * CORE/ (orchestration, state machine, QC engine, media muxer, publishing gateway, SQLite event bus)
     * AGENT_TEMPLATES/ (creative_lead, analytics, scriptwriter, visual_director, audio_director, voice_synthesizer, broadcast_qc)
     * CONFIG_SCHEMAS/ (team_manifest.schema.json, channel_identity.schema.json, style_bible.schema.json)
     * REMOTION_MASTER/ (Universal parametric Remotion overlay engine: parameterized hook banners, dynamic typography, kinetic word-by-word captions, outro cards)
     * DATABASE/ (clean migration SQL scripts, multi-tenant or schema-isolated tables)
     * SCRIPTS/ (team_generator.py, clone_channel.py, audit_runner.py)
3. Universal Configuration Schema Specifications:
   - Full YAML/JSON schema for `team_manifest.yaml` (agents, assigned models, temperatures, API credentials pointers, cron expressions).
   - Full YAML/JSON schema for `channel_identity.yaml` (channel_id, niche, target_audience, language, emotional_tones, banned_words, voice_clone_id, visual_style, hashtags).
4. Parametric Remotion React Engine Blueprint:
   - How to refactor DoniOverlay into UniversalOverlay.tsx accepting dynamic themes (colors, fonts, badge styles, CTA text, positioning).
5. Database Universalization Schema:
   - Generic table designs (`channel_posts`, `channel_content_ideas`, `channel_production_queue`, `channel_learnings`, `channel_clip_usage`).
   - How tenant_id or schema prefix (`ch_donies`, `ch_tech`, `ch_finance`) isolates data.
""",

    "11_CLONING_ISOLATION_STRATEGY.md": """
Produce Deliverable 11: `11_CLONING_ISOLATION_STRATEGY.md`
Phase 10: CLONING & MULTI-TEAM ISOLATION STRATEGY

Design how to safely deploy 10, 50, or 100 independent AI agentic teams from the Virgin Master Framework without cross-channel context leakage:
1. Multi-Team Topology & Isolation Models:
   - Comparison of:
     * Model A: Multi-Tenant Single Process (Shared VPS, isolated DB schemas, isolated folders) -> Highest resource efficiency for 2-core VPS.
     * Model B: Directory-Level Clones (Separate folders per channel, shared core symlink).
     * Model C: Containerized Swarms (Docker compose per channel) -> High isolation, heavier memory.
   - Evaluation of the optimal model for Fahru's VPS environment (Ubuntu 24.04, 2 vCPUs, 4GB RAM).
2. Data & Memory Isolation Protocols:
   - PostgreSQL schema/row isolation: ensuring Channel B cannot query Channel A's posts or learnings.
   - SQLite Swarm Matrix isolation: separate SQLite databases or strict channel room isolation (`ch_{slug}_messages`).
   - Obsidian Vault isolation: separate vault workspaces (`vault/01_Business/channel_a/` vs `channel_b/`) to prevent GRO cross-talk.
   - Ephemeral cache isolation (`/tmp/` namespacing with channel prefixes to prevent ProRes overlay collisions).
3. API Credential & Quota Management:
   - YouTube OAuth credential partitioning: separate OAuth client secrets & tokens per channel (/home/ubuntu/.config/youtube/{channel_slug}_oauth.json).
   - Rate limit management: staggering cron release windows across channels to avoid bursting CLIProxyAPI (:8317) or ElevenLabs.
   - Shared model proxy routing vs dedicated accounts.
4. Framework Upgrades & Propagation Strategy:
   - How improvements in the Universal Core (e.g. Cleo QC upgrades or Remotion rendering optimizations) propagate to all teams without overwriting channel-specific prompts, learnings, or custom configs.
   - Git submodule vs Python package (`pip install -e ./core`) vs Git subtree approach.
   - Rollback strategy if an upgrade introduces regressions.
5. End-to-End Cloning Playbook:
   - Step-by-step CLI commands (`python3 tools/clone_channel.py --slug finance_daily --niche "Crypto & Personal Finance" ...`).
""",

    "12_RISK_GAP_ANALYSIS.md": """
Produce Deliverable 12: `12_RISK_GAP_ANALYSIS.md`
Phase 11: RISK & GAP ANALYSIS (SEVERITY-RATED AUDIT)

Provide an exhaustive, evidence-backed evaluation of all vulnerabilities, technical debt, and architectural risks:
1. Risk Classification Framework:
   - Rating scale: CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL.
2. Comprehensive Risk Assessment:
   - Risk 1: Legacy Code Entanglement (Velora AI / TikTok Shop remnants in ugc-lemonaru bloating repo, stale dependencies, confusing MCP tools).
   - Risk 2: Single Point of Failure (SPOF) on CLIProxyAPI (:8317) and Local Host Services (if Antigravity proxy fails, all LLM reasoning collapses).
   - Risk 3: Chrome CDP Session Fragility (:9222 for Google Flow & YouTube OAuth auto-healer: session expiry, Google re-auth blocks).
   - Risk 4: Hardware & Concurrency Choke on VPS (2 vCPUs, 4GB RAM: simultaneous Remotion render + Chromium + FFmpeg can cause kernel OOM killer to strike).
   - Risk 5: ElevenLabs API Cost & Quota Exhaustion (uncontrolled retries could drain characters rapidly; need fallback to local/cheaper TTS).
   - Risk 6: YouTube Data API Quota Consumption (upload cost is 1600 units per video; daily quota is 10,000 units = max 6 uploads/day across all channels).
   - Risk 7: Cross-Channel Memory Contamination (prompts referencing cats, Doni, or Fahru's personal life leaking into B2B or corporate channels).
   - Risk 8: Inconsistent QC Thresholds between Souls and Code (e.g. drift tolerance 0.5s in soul vs 1.5s in python gate).
   - Risk 9: Credential Hygiene in Local Configs (.env file access, permissions on OAuth JSON files).
   - Risk 10: State Machine Deadlocks in PostgreSQL (topics stuck in 'ready' or queue items stuck in 'RENDERING' after process crashes).
3. Blockers for Virgin Master Template:
   - Exactly which of these risks MUST be resolved before attempting to clone the system.
4. Concrete Mitigation & Hardening Blueprint for every identified risk.
""",

    "13_IMPLEMENTATION_ROADMAP.md": """
Produce Deliverable 13: `13_IMPLEMENTATION_ROADMAP.md`
RECOMMENDED IMPLEMENTATION PHASES & DEPENDENCY BLUEPRINT

Formulate a disciplined, low-risk, phase-by-phase roadmap to transform Donies Daily into the Virgin Master Architecture:
1. Guiding Axiom: ZERO DOWNTIME FOR LIVE DONIES DAILY.
   - Donies Daily MUST continue releasing 3 Shorts per day uninterrupted throughout all refactoring.
2. Phase Breakdown:
   - Phase 0: Freeze, Snapshot & Baseline Verification (Creating isolated branch, golden test suite, verifying current production metrics).
   - Phase 1: Surgical Cleansing & Decoupling of Legacy Velora AI (Pruning inactive TikTok Shop code, isolating shared utilities, establishing clean import boundaries).
   - Phase 2: Core Abstraction & Parameterization (Extracting Universal Core into `omni_studio_core/`, parameterizing Remotion React engine, implementing configuration loaders).
   - Phase 3: Team Configuration & Templating Engine (Building `team_manifest.yaml` and `channel_identity.yaml` parsers, dynamic SOUL prompt synthesizer).
   - Phase 4: Multi-Tenant Database & State Isolation (Migrating PostgreSQL tables to multi-tenant or schema-scoped structure with backwards-compatible views for Donies).
   - Phase 5: Pilot Clone Deployment (Instantiating Channel B — e.g. Tech/AI News or Stoic Motivation — to validate zero-leakage, independent publishing, and independent analytics).
   - Phase 6: Telemetry Aggregation & Multi-Channel Fleet Dashboard.
3. Detailed Gantt / Timeline Matrix with Dependencies, Deliverables & Success Criteria for each phase.
4. Pre-Flight Checklist & Rollback Playbook.
""",

    "14_MASTER_AUDIT_SUMMARY.md": """
Produce Deliverable 14: `14_MASTER_AUDIT_SUMMARY.md`
EXECUTIVE SUMMARY & MASTER TRUTH DISCOVERY

Provide the definitive executive synthesis answering all the fundamental questions for Fahru:
1. Executive Verdict & System Maturity Score:
   - Overview of the audit findings.
   - Maturity assessment across 6 axes: Autonomous Intelligence, Media Engineering, Infrastructure Reliability, Self-Healing & QC, Data & Telemetry Closed-Loop, Reusability & Clonability.
2. Definitive Answers to the 12 Fundamental Architectural Questions:
   - 1. What exactly makes Donies Daily work?
   - 2. What does every agent actually do?
   - 3. How do the agents communicate and collaborate?
   - 4. Which prompts, tools, models, and workflows are essential?
   - 5. Which parts are genuinely reusable?
   - 6. Which parts are tightly coupled to Donies Daily / cats?
   - 7. What must be removed from a clean clone?
   - 8. What must be preserved?
   - 9. How do we create the Virgin Master Template?
   - 10. How can we deploy 10, 50, or 100 independent AI agentic teams without cross-channel contamination?
   - 11. What architecture changes are genuinely necessary vs premature optimization?
   - 12. What is the safest implementation sequence?
3. The Three Golden Insights Discovered in the Audit:
   - The Hybrid Render Breakthrough (ProRes overlay + FFmpeg stream copy solving VPS CPU choke).
   - The Closed-Loop Telemetry Engine (100-point retention curve feeding Mochi & Luna's 5s re-hook).
   - The 15 Iron Laws (Hukum Besi) as the deterministic backbone preventing LLM drift.
4. Executive Sign-Off & Next Steps.
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
