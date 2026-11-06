# 🏛️ Donies Team Lemonaru — Canonical Autonomous Production Studio

Welcome to the authoritative source repository for the **Donies Daily** multi-agent autonomous YouTube content studio and its independent logical clone instances.

---

## 🌿 Repository Structure & Branches

This repository is maintained in two primary branches:

1. **`main`**: The canonical reference baseline snapshot of the active Donies Daily production studio. Contains the original souls, engines, Remotion components, tools, database DDLs, and the 14 forensic audit reports (`docs/audit/`).
2. **`feature/donies-virgin-clone`**: The isolated working branch containing **Project Donies Virgin** (`donies-virgin/`) — a clean, faithful logical duplicate of the Donies team with separated channel context, isolated persistence, and the 10 required audit & duplication deliverables.

---

## 📑 Project Donies Virgin Deliverables Index

All 10 required deliverables for the Virgin Clone are located in this branch:

| # | Deliverable File | Description |
| :-: | :--- | :--- |
| **01** | [`01_VIRGIN_CLONE.md`](01_VIRGIN_CLONE.md) / [`donies-virgin/`](donies-virgin/) | Complete, working, independent codebase of Donies Virgin. |
| **02** | [`02_CLONE_MAPPING.md`](02_CLONE_MAPPING.md) | Full 42-component traceability matrix from original to Virgin counterpart. |
| **03** | [`03_PRESERVED_LOGIC.md`](03_PRESERVED_LOGIC.md) | Record of preserved agent intelligence, 15 Hukum Besi, and model routing. |
| **04** | [`04_CHANNEL_CONTEXT_SEPARATION.md`](04_CHANNEL_CONTEXT_SEPARATION.md) | Demarcation of Reusable Intelligence vs Channel Identity. |
| **05** | [`05_DEPENDENCY_MANIFEST.md`](05_DEPENDENCY_MANIFEST.md) | Comprehensive runtime, system, Python, and Node.js dependency manifest. |
| **06** | [`06_MEMORY_ISOLATION.md`](06_MEMORY_ISOLATION.md) | 6-tier database, queue, telemetry, and memory separation strategy. |
| **07** | [`07_VALIDATION_REPORT.md`](07_VALIDATION_REPORT.md) | Automated parity and isolation test results (**5 of 5 tests passed**). |
| **08** | [`08_SETUP_GUIDE.md`](08_SETUP_GUIDE.md) | Step-by-step onboarding guide for deploying a new YouTube channel (< 15 min). |
| **09** | [`09_KNOWN_LIMITATIONS.md`](09_KNOWN_LIMITATIONS.md) | Transparent disclosure of boundaries, concurrency limits, and setup steps. |
| **10** | [`10_ORIGINAL_VS_VIRGIN_DIFF.md`](10_ORIGINAL_VS_VIRGIN_DIFF.md) | Granular code and architectural diff between original and Virgin. |

---

## ⚡ Quick Start: Deploying Donies Virgin

To spin up an independent instance of the Donies team for a new channel:

```bash
# 1. Switch to the clone directory
cd donies-virgin

# 2. Run the one-click automated setup
./setup_env.sh

# 3. Configure your new channel
nano config/channel_config.yaml

# 4. Add API credentials
nano config/.env

# 5. Verify parity and isolation
python3 tests/test_virgin_parity.py

# 6. Run autonomous production sprint
python3 tools/doni_production_sprint.py
```

---

## 👥 The Autonomous Squad

```
                     👑 KETUA DONI
             (gemini-4-argon-high | Lead)
                          │
         ┌────────────────┼────────────────┐
         │                                 │
     📊 MOCHI                          ✍️ LUNA
(gemini-4-argon-high)            (claude-sonnet-5-5-high)
  Retention Forensics              Script & Hook Engineer
         │                                 │
         │                         🎙️ KAK CERIA / VIVAN
         │                         (ElevenLabs v2 / v4)
         │                         Audio & Voice Director
         │                                 │
         └────────────────┬────────────────┘
                          │
                       🎬 MILO
               (claude-opus-5-5-high)
             Visual Director & Remotion
                          │
                       🛡️ CLEO
                (0-Token Deterministic)
              Broadcast Quality Control
                          │
                     🚀 PUBLISH
               (Official YouTube API)
```

---

## 🛡️ Zero-Leakage Data Isolation Guarantee

Donies Virgin operates on dedicated PostgreSQL tables (`ai_brain.virgin_*`) and a segregated SQLite database (`data/virgin_agents_chat.db`). Writing, modifying, or testing the Virgin instance **cannot alter or collide with Donies Daily production data**.

---

## 📖 Detailed Documentation

For in-depth technical documentation, refer to:
- [`donies-virgin/README.md`](donies-virgin/README.md) — Clone usage, CLI commands, and project architecture.
- [`docs/audit/`](docs/audit/) — The 14 reverse-engineering system audit reports.
- [`PRD_DONIESDAILY_MASTER_SPEC.md`](PRD_DONIESDAILY_MASTER_SPEC.md) — Master product specification.
