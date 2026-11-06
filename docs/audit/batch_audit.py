import sys
import time
from pathlib import Path
from audit_context import get_complete_knowledge_context
from generate_audit_doc import call_argon

AUDIT_DIR = Path("/home/ubuntu/donies_daily_master_audit")

PROMPTS = {
    "02_AGENT_INVENTORY.md": """
Produce Deliverable 02: `02_AGENT_INVENTORY.md`
Phase 1 & 2: COMPLETE AGENT AND SUB-AGENT INVENTORY

Contents to cover thoroughly:
1. Executive Inventory Summary: Scope of all autonomous entities within Donies Daily.
2. Master Agent Inventory Table:
   - Agent Name & Avatar Emoji
   - Formal Role & Sub-role
   - Position in Hierarchy (Tier 1 Executive, Tier 2 Creative/Analytical Specialist, Tier 3 Technical Worker)
   - Assigned Engine Model (exact model string from proxy :8317 or external provider)
   - Model Provider, Endpoint, Context Window & Temperature Configuration
   - Token Cost Profile (Heavy LLM vs Fast vs 0-Token Deterministic)
   - Primary Tools & Python Scripts Accessed
   - Database / State Persistence Tables Read and Written
   - Communication Channel in Swarm Matrix (#donies, #executive-board, all)
3. Granular Analysis of Discovered Entities:
   - Doni (Executive Producer & Squad Chairman)
   - Mochi (Head of Analytics & Retention Forensics)
   - Luna (Master Scriptwriter & Cat Storyteller)
   - Kak Ceria (Senior Voice Director & Community Lead)
   - Vivan (Sub-Unit Voice Synthesis & Dataset Harvester)
   - Milo (Visual Director, AI Cinematographer & Opus Remotion Editor)
   - Cleo (Broadcast QC Gatekeeper & EBU R128 Inspector)
   - Hermes Agent (Holding Co-Pilot & Security Gatekeeper)
   - Fahru (Human Owner, Strategic Authority & Authentic Footage Source)
   - Supporting Entities / Bots / Background Workers (e.g., Vault Archivist / GRO, Jitter Scheduler, Comment Sniper)
4. Model Routing & Assignment Architecture:
   - Why Argon-High for Doni & Mochi?
   - Why Sonnet 5.5 for Luna?
   - Why Opus 5.5 for Milo?
   - Why 0-Token Deterministic for Cleo and Vivan?
5. Agent Hierarchy & RACI Responsibility Matrix:
   - Accountable, Responsible, Consulted, Informed for each phase of production.
6. Summary of Active vs Deprecated Agents (identifying any legacy Velora AI agents).

Ensure zero hallucination. Ground everything in the provided souls, scripts, and logs.
""",

    "03_AGENT_REVERSE_ENGINEERING.md": """
Produce Deliverable 03: `03_AGENT_REVERSE_ENGINEERING.md`
Phase 2: AGENT-BY-AGENT REVERSE ENGINEERING (DEEP AUDIT)

For EACH of the core agents:
1. Doni (@doni)
2. Mochi (@mochi)
3. Luna (@luna)
4. Kak Ceria (@ceria)
5. Vivan (@vivan)
6. Milo (@milo)
7. Cleo (@cleo)

And the auxiliary bridge:
8. Hermes & Owner Bridge

Provide an exhaustive, structured analysis covering all 6 mandatory dimensions:
A. Identity:
   - Name, handle, role, secondary duties, hierarchy tier, model assignment & configuration.
B. Intelligence:
   - Full system prompt architecture (from SOUL.md), core philosophies, behavioral directives, reasoning rules, task boundaries, internal rules (e.g. Luna's Acoustic Punctuation, Milo's 14-cut rule), emotional constraints, personality and communication style.
C. Operational Logic:
   - Task reception mechanism, request interpretation, decision trees, tool invocation, inter-agent messaging, incomplete information handling, self-healing & error recovery, completion definition.
D. Dependencies:
   - Upstream agents, downstream agents, scripts called, tools accessed, DB tables read/written, shared memory, external APIs (ElevenLabs, Google Flow, YouTube Data API), configuration files.
E. Output:
   - Concrete output format/schema, validation checks, quality gates, handoff mechanism, downstream consumers.
F. Reusability Assessment:
   - Formal classification into: UNIVERSAL CORE, CONFIGURABLE, CHANNEL-SPECIFIC, DONIES-SPECIFIC, or LEGACY/UNCLEAR.
   - Comprehensive technical justification for each classification.

Write in extensive detail with concrete code/prompt snippets and precise table references.
""",

    "04_ORCHESTRATION_ARCHITECTURE.md": """
Produce Deliverable 04: `04_ORCHESTRATION_ARCHITECTURE.md`
Phase 3: TEAM ORCHESTRATION & COMMUNICATION AUDIT

Contents to cover thoroughly:
1. Executive Orchestration Overview:
   - How the team collaborates without human intervention.
   - Orchestration paradigm (Centralized Leader vs Distributed Swarm vs Hybrid State Machine).
2. The Dual-Cadence Production Engines:
   - A. Daily Standup & Learning Loop (09:00 WIB / doni_working_hours_standup.py): 9-step workflow from Mochi telemetry to Doni Stage 1 & 2 reviews, Luna concession, Milo planning, Cleo checklist, and Vault persistence.
   - B. Autonomous Production & Release Sprint (doni_production_sprint.py & doni_remotion_flow_pipeline.py): Randomized Jitter window, in-place revision loop (up to 3 retries), Remotion ProRes caching.
   - C. Community Engagement Engine (doni_studio_replier.py & doni_comment_sniper.py).
3. Communication & Message Bus Architecture:
   - SQLite Swarm Matrix (agents_chat.db: agent_messages & agent_traces). Schema, indexing, channel segregation (#donies, #doniesdaily, #all).
   - PostgreSQL State Queue (ai_brain.doniesdaily_production_queue): enum production_stage, transition rules.
4. Comprehensive Mermaid Diagrams:
   - Diagram 1: Full Daily Standup & Learning Feedback Cycle (Mermaid Sequence Diagram).
   - Diagram 2: Production Sprint & In-Place Self-Healing Loop (Mermaid Flowchart).
   - Diagram 3: Multi-Agent Message Bus & Swarm Matrix Flow (Mermaid Graph).
5. Conflict Resolution, Authority & Consensus:
   - Who has veto power? (Doni on editorial, Cleo on broadcast physics, Fahru on strategy).
   - How conflicts between creative aspirations (Luna/Milo) and QC physics (Cleo) are resolved.
6. Fault Tolerance, Anti-Spam & Concurrency Protection:
   - Jitter gatekeeping, cooldown guards (minimum 110 min between posts), max daily post enforcement.
   - Recovery from API timeouts (ElevenLabs, YouTube OAuth CDP auto-healer).
7. Bottlenecks & Single Points of Failure (SPOF) Analysis.
""",

    "05_CONTENT_PIPELINE.md": """
Produce Deliverable 05: `05_CONTENT_PIPELINE.md`
Phase 4: YOUTUBE CONTENT PRODUCTION PIPELINE (END-TO-END LIFECYCLE)

Exhaustively analyze the 18 stages of the content lifecycle in Donies Daily:
1. Content Research & Brainstorming
2. Trend Discovery & Telemetry Ingestion
3. Topic Selection & Anti-Duplication Gate
4. Content Strategy & Hook Formulation
5. Idea Validation & Standup Deliberation
6. Scriptwriting & Acoustic Punctuation Engineering
7. Storytelling Pacing & 5-Second Open-Loop Re-hook
8. Voice Synthesis & Dynamic Parameter Tuning (ElevenLabs v4 Vivan)
9. Audio Engineering, Ducking & LUFS Loudness Normalization
10. Visual Asset Ingestion, 10-Frame Multi-Vision & B-Roll Cataloging
11. Scene Cut Planning & Speech-Beats Synchronized Alignment (14-18 unique cuts)
12. Kinetic Remotion Typography & Overlay Rendering (DoniOverlay, HookTitle, SubtitlePage)
13. Subtitle Generation (Hormozi single-word-by-word highlight)
14. Automated Broadcast Quality Control (Cleo QC Gate: EBU R128, drift, black frames, duration assert)
15. Remotion High-CTR Thumbnail & Cover Poster Injection
16. YouTube Publishing (Data API v3 with OAuth 2.0 auto-healing)
17. Automated Community Engagement (Studio Replier & Comment Sniper)
18. Performance Telemetry, Retention Autopsy & Continuous Learning Feedback

For EACH stage, provide:
- Status: IMPLEMENTED / PARTIALLY IMPLEMENTED / PLANNED / NOT IMPLEMENTED / UNKNOWN
- Responsible Agent & Model
- Required Inputs & Source
- Processing Logic & Algorithms
- Tools, Libraries & Scripts Invoked
- Concrete Outputs & File Formats
- Validation & Assertion Gates
- Downstream Destination
- Failure Modes & Fallback Procedures

Provide a master end-to-end pipeline summary matrix and timeline.
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
