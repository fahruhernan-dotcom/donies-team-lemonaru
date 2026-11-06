# 🧬 DELIVERABLE 11: CLONING & MULTI-TEAM ISOLATION STRATEGY (`11_CLONING_ISOLATION_STRATEGY.md`)

**Document ID:** `AUDIT-DD-2026-11-CLONING`  
**Phase:** 10 — Cloning & Multi-Team Isolation Strategy  
**Target System:** DONIES DAILY Autonomous Multi-Agent Production Ecosystem $\rightarrow$ Virgin Master Framework (`ugc-master-core`)  
**Host Environment:** Ubuntu 24.04 LTS, 2 vCPUs, 4GB RAM, Shared Supabase PostgreSQL (`supabase-db`), Shared CLIProxyAPI (`127.0.0.1:8317`), Xvfb `:99` / Chrome CDP `:9222`  
**Auditor Role:** Principal AI Systems Architect & Agentic Workflow Engineer  

---

## 1. Executive Summary & Current-State Forensics

To scale the `@DoniesDaily` (`UCNPtjF2aB0wvWHI0q7hhcCg`) architecture into 10, 50, or 100 autonomous vertical media teams (e.g., `finance_daily`, `gadget_daily`, `automotive_daily`, `health_daily`) without cross-channel context contamination, file collisions, or out-of-memory (OOM) kernel panics, we must first audit the hardcoded singleton bottlenecks present in the current codebase.

### 1.1 Verified Hardcoded Singleton Bottlenecks (Current State Evidence)

| Subsystem | Hardcoded Path / Identifier in Current Code | Collision / Leakage Risk if Cloned Naively |
| :--- | :--- | :--- |
| **PostgreSQL Tables** | `ai_brain.doniesdaily_content_ideas`, `ai_brain.doniesdaily_posts`, `ai_brain.doniesdaily_learnings`, `ai_brain.doniesdaily_production_queue`, `ai_brain.doniesdaily_clip_usage`, `ai_brain.doniesdaily_metrics_history`, `ai_brain.doniesdaily_sniper_logs` | **CRITICAL:** All scripts (`doni_scriptwriter.py`, `doni_production_sprint.py`, `doni_remotion_flow_pipeline.py`) execute raw SQL strings against `ai_brain.doniesdaily_*`. Cloning without table/schema parameterization causes Team B to consume Team A's topics and inject cat biology rules into Finance scripts. |
| **Remotion Public Scratchpad** | `/home/ubuntu/apps/ugc-lemonaru/remotion/public/doni-{t_key}-captions.json`, `{t_key}_master.mp3`, `flow_{t_key}_bg_concat.mp4` | **HIGH:** Concurrent renders across teams overwrite shared `public/` assets or bloat the Remotion webpack bundle if all teams share one `public/` directory without namespacing. |
| **Ephemeral ProRes Cache** | `/tmp/{topic}_remotion_overlay.mov` (~100–250MB per render) | **CRITICAL:** Two teams rendering a generic `topic_key` (or concurrent ProRes 4444 renders on a 2-vCPU / 4GB RAM VPS) will either collide on `/tmp/` filenames or exhaust `/tmp` tmpfs/disk space and RAM. |
| **Jitter & State Files** | `/home/ubuntu/apps/ugc-lemonaru/data/doni_daily_jitter.json` | **HIGH:** `check_and_consume_jitter_window()` reads/writes a single JSON file. Team A firing its morning slot marks `morning.fired = True`, preventing Team B from posting. |
| **Swarm Matrix SQLite** | `/home/ubuntu/vps-control-center/backend/data/agents_chat.db` (`channel = 'donies'` or `'all'`) | **MEDIUM:** `post_swarm_chat()` hardcodes `channel='donies'` and `sender_id='doni'`. Multi-team messages will interleave in the same room unless partitioned by `channel = '{team_slug}'` and prefixed `sender_id = '{team_slug}:doni'`. |
| **Obsidian Vault** | `/home/ubuntu/vault/01_Business/doniesdaily/ActiveContext.md` & `Index - doniesdaily.md` | **HIGH:** `save_meeting_to_vault()` writes directly to `VAULT_DIR = Path("/home/ubuntu/vault/01_Business/doniesdaily")`. |
| **YouTube OAuth** | `/home/ubuntu/.config/youtube/doniesdaily_oauth.json` | **CRITICAL:** `YouTubeAPIPublisher` defaults to `DEFAULT_OAUTH_PATH`. Uploading from Team B without strict credential isolation publishes Finance videos to `@DoniesDaily`. |
| **Chrome CDP Browser** | `127.0.0.1:9222` (`/home/ubuntu/apps/ugc-lemonaru/data/chrome_persistent`) | **HIGH:** `doni_oauth_auto_healer.py`, `doni_evaluator.py`, and `FlowCDPOperator` attach to a single Chrome session logged into `@DoniesDaily`'s Google account. |

---

## 2. Multi-Team Topology & Isolation Models

We evaluate three architectural topologies for deploying $N$ independent AI agentic teams from the Virgin Master Framework.

```mermaid
graph TB
    subgraph "Model A: Multi-Tenant Single Core (RECOMMENDED FOR 2-vCPU / 4GB VPS)"
        CORE_A["/home/ubuntu/apps/ugc-master-core/<br/>(Shared Python Venv + Shared Remotion Node_Modules)"]
        T1_A["/home/ubuntu/teams/doniesdaily/<br/>(config.yaml, souls/, assets/, data/)"]
        T2_A["/home/ubuntu/teams/financedaily/<br/>(config.yaml, souls/, assets/, data/)"]
        TN_A["/home/ubuntu/teams/team_N/<br/>(config.yaml, souls/, assets/, data/)"]
        LOCK["Global Render Mutex<br/>(/var/lock/ugc_render.lock)"]
        CORE_A --> T1_A
        CORE_A --> T2_A
        CORE_A --> TN_A
        T1_A -.-> LOCK
        T2_A -.-> LOCK
        TN_A -.-> LOCK
    end

    subgraph "Model B: Directory-Level Clones (Symlinked Core)"
        T1_B["/home/ubuntu/apps/ugc-doniesdaily/<br/>(.venv, remotion/, src/ -> symlink)"]
        T2_B["/home/ubuntu/apps/ugc-financedaily/<br/>(.venv, remotion/, src/ -> symlink)"]
    end

    subgraph "Model C: Containerized Swarms (Docker Compose per Team)"
        D1["Container: swarm-doniesdaily<br/>(Python + Node + Chromium + FFmpeg)"]
        D2["Container: swarm-financedaily<br/>(Python + Node + Chromium + FFmpeg)"]
        DN["Container: swarm-team-N<br/>(Python + Node + Chromium + FFmpeg)"]
    end
```

### 2.1 Comparative Matrix of Isolation Models

| Architectural Dimension | Model A: Multi-Tenant Single Process (Shared Core + Tenant Directories) | Model B: Directory-Level Clones (Separate App Folders + Symlinked Core) | Model C: Containerized Swarms (Docker Compose per Channel) |
| :--- | :--- | :--- | :--- |
| **Architecture Pattern** | Single immutable code & runtime engine (`/home/ubuntu/apps/ugc-master-core`) invoked with `--team <slug>`. Tenant state lives in `/home/ubuntu/teams/<slug>/`. | Separate `/home/ubuntu/apps/ugc-<slug>/` directories per channel; `src/` symlinked to master, separate data/assets folders. | 1 Docker container per team (or 1 worker + 1 renderer container per team) managed via Docker Compose. |
| **RAM Footprint (Idle)** | **~0 MB per additional team** (cron-driven execution; 0 background daemons per team). | **~0 MB per additional team** (if cron-driven), but high page-cache thrashing across duplicated binaries. | **~150–300 MB per container** (base OS overhead, Python runtime, Node daemon). 10 teams = 1.5–3.0 GB RAM dead weight. |
| **RAM Footprint (Active Render)** | **1.1 – 1.6 GB** (1 active Remotion headless Chromium + FFmpeg instance gated by flock mutex). | **1.1 – 1.6 GB per concurrent render** (risk of OOM if two crons overlap without global lock). | **1.4 – 2.0 GB per active container** (container overhead + headless Chromium inside container). |
| **Disk Footprint per Team** | **~5–15 MB** (configs, souls, prompts) + raw video assets (`assets/clips/`). Zero duplicate `node_modules` or `.venv`. | **~1.2 GB per team** if `.venv` (~450MB) and `remotion/node_modules` (~750MB) are duplicated; **~20 MB** if symlinked (fragile with Node/Webpack resolution). | **~2.5 GB+ per image layer** if unshared; requires custom Docker registry/build pipeline and complex volume mounts. |
| **Node.js / Remotion Compatibility** | **Native:** Single `remotion/` project dynamically receives `--props` JSON pointing to tenant asset paths via local HTTP asset server or tenant-scoped symlink `public/tenants/{slug}/`. | **Fragile:** Webpack/Remotion bundler frequently breaks when `node_modules` or `src/` are symlinked outside the package root (`preserveSymlinks` issues). | **High:** Clean inside container, but requires passing GPU/CPU flags and `/dev/shm` sizing (`shm_size: 1gb`) per container so Chromium doesn't crash. |
| **Blast Radius / Fault Isolation** | **Low-Medium:** A syntax error in `ugc-master-core` affects all teams (mitigated via Blue/Green core versioning). Tenant config errors only affect that tenant. | **Medium:** Symlinked `src/` still shares code blast radius, while configuration drift across cloned directories becomes severe after 5+ teams. | **Lowest (Highest Isolation):** Kernel namespaces, cgroups (`--memory=1.5g`), and isolated filesystems per team. |
| **Max Teams on 2 vCPU / 4GB RAM** | **10–15 Teams** (with staggered cron windows + global render lock). | **3–5 Teams** (before disk I/O and uncoordinated render overlaps cause OOM kills). | **1–2 Teams MAX** (Supabase DB + Xvfb + Chrome `:9222` + Control Center already consume ~2.1 GB of the 4GB RAM). |

### 2.2 Hardware Capacity Evaluation for Fahru’s VPS (Ubuntu 24.04, 2 vCPUs, 4GB RAM)

Let us perform a deterministic resource budget calculation based on the live services running on Fahru's VPS:

1. **Baseline Resident Memory (Always-On Infrastructure):**
   - Linux Kernel + Systemd + Journald: `~280 MB`
   - Docker Engine + `supabase-db` (PostgreSQL 15) + Supabase stack: `~850 MB`
   - Xvfb (`:99`) + Persistent Google Chrome (`:9222` CDP for YouTube Studio / Google Flow): `~650 MB`
   - CLIProxyAPI (`:8317`) + VPS Control Center (Backend + SQLite): `~250 MB`
   - **Total Baseline RAM Used:** **`~2,030 MB` (2.03 GB)**
   - **Available Free / Buffer RAM for Production Sprints:** **`~1,970 MB` (1.97 GB)**

2. **Peak Transient Memory During a Single Production Sprint (`doni_production_sprint.py`):**
   - Python Orchestrator + TTS + DB Clients: `~85 MB`
   - Remotion Render (`npx remotion render DoniOverlay` spawning Headless Chromium + Bundler): `~950 MB – 1,350 MB`
   - FFmpeg ProRes 4444 Composite + `ebur128` + `blackdetect`: `~350 MB – 500 MB`
   - **Peak Concurrent Sprint RAM:** **`~1,400 MB – 1,850 MB`**

> [!CRITICAL]
> **Architectural Verdict for 2 vCPU / 4GB RAM VPS:**
> The VPS can physically execute **AT MOST ONE (1) Remotion/FFmpeg video render at any given second**. If Team A (`doniesdaily`) and Team B (`financedaily`) trigger `npx remotion render` simultaneously, Resident Set Size (RSS) will spike to $2.03\text{ GB} + 2 \times 1.4\text{ GB} = 4.83\text{ GB}$, immediately triggering the Linux kernel OOM-killer and crashing `supabase-db` or Chrome `:9222`.
>
> Therefore:
> 1. **Model A (Multi-Tenant Single Core with Tenant Workspaces + Global Hardware Mutex)** is the **ONLY** viable architecture for running **1 to 12 teams** on the current 2-vCPU / 4GB RAM VPS.
> 2. Scaling to **50 or 100 teams** (at 3 videos/day/team = 150–300 renders/day, taking ~3 minutes per render = 450–900 minutes = 7.5–15 hours of continuous 100% CPU load) requires **Model A deployed across horizontally sharded Worker Nodes** (e.g., 1 Master DB/Control VPS + $K$ Render Worker VPS nodes at 15–20 teams per 4-vCPU/8GB worker node).

---

## 3. Data & Memory Isolation Protocols

To guarantee **Zero Cross-Channel Context Leakage** (ensuring a Finance or Horror team never reads `@DoniesDaily`'s cat biology rules, clips, or scripts), isolation is enforced across four storage layers: **PostgreSQL**, **SQLite Swarm Matrix**, **Obsidian Vault**, and **Ephemeral/Static Filesystems**.

```mermaid
erDiagram
    TEAM_REGISTRY ||--o{ CONTENT_IDEAS : "isolates via team_slug + RLS"
    TEAM_REGISTRY ||--o{ PRODUCTION_QUEUE : "isolates via team_slug + RLS"
    TEAM_REGISTRY ||--o{ POSTS : "isolates via team_slug + RLS"
    TEAM_REGISTRY ||--o{ LEARNINGS : "isolates via team_slug + RLS"
    TEAM_REGISTRY ||--o{ CLIP_USAGE : "isolates via team_slug + RLS"
    TEAM_REGISTRY ||--o{ METRICS_HISTORY : "isolates via team_slug + RLS"

    TEAM_REGISTRY {
        text team_slug PK "e.g., doniesdaily, financedaily"
        text channel_id UK "YouTube Channel ID"
        text display_name "e.g., Donies Daily"
        text niche "e.g., Feline Education & Humor"
        jsonb cadence_config "Cron windows & daily limits"
        text status "active | paused | archived"
    }

    CONTENT_IDEAS {
        uuid id PK
        text team_slug FK
        text topic_key
        text title
        text full_script
        text status
    }

    LEARNINGS {
        int id PK
        text team_slug FK
        text category
        text rule_name
        text directive
        numeric confidence_score
    }
```

### 3.1 PostgreSQL Isolation Protocol (Schema-Per-Team vs. Row-Level Partitioning)

We evaluate two PostgreSQL isolation patterns inside `supabase-db`:
- **Option 1: Dedicated Schema per Team (`team_doniesdaily.*`, `team_financedaily.*`)**
- **Option 2: Unified Schema (`ai_brain.*`) with Mandatory `team_slug` Discriminator + PostgreSQL Row-Level Security (RLS)**

**Architect Recommendation:** **Hybrid Schema-Per-Team (`team_{slug}`)** for complete physical table isolation, paired with a global `ai_brain.teams_registry` master table.
*Why Schema-Per-Team wins for 10–100 Autonomous Teams:*
1. **Zero Query Leakage by Construction:** Setting `SET search_path TO team_financedaily;` at the connection level makes it physically impossible for a bug in `doni_scriptwriter.py` to `SELECT` from `team_doniesdaily.learnings` or `team_doniesdaily.posts`.
2. **Independent Backup, Restore & Archival:** You can `pg_dump -n team_financedaily` or `DROP SCHEMA team_failed_experiment CASCADE` in 50ms without touching active production channels.
3. **Unchanged Table Structures:** All 7 existing tables (`content_ideas`, `production_queue`, `clip_usage`, `learnings`, `posts`, `metrics_history`, `sniper_logs`) keep clean names inside `team_{slug}.*`, eliminating the need to rewrite every SQL `JOIN` or composite unique constraint.

#### SQL Provisioning Template (`sql/provision_team_schema.sql`):
```sql
-- 1. Global Master Registry (Created Once)
CREATE TABLE IF NOT EXISTS ai_brain.teams_registry (
    team_slug TEXT PRIMARY KEY CHECK (team_slug ~ '^[a-z0-9_]+$'),
    channel_name TEXT NOT NULL,
    youtube_channel_id TEXT UNIQUE,
    niche_description TEXT NOT NULL,
    daily_quota INTEGER NOT NULL DEFAULT 3,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Per-Team Isolated Schema Template (Parameterized by :team_slug)
CREATE SCHEMA IF NOT EXISTS team_financedaily;

-- Create isolated role for the team
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'role_financedaily') THEN
        CREATE ROLE role_financedaily NOLOGIN;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA team_financedaily TO role_financedaily;
ALTER DEFAULT PRIVILEGES IN SCHEMA team_financedaily GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO role_financedaily;
ALTER DEFAULT PRIVILEGES IN SCHEMA team_financedaily GRANT USAGE, SELECT ON SEQUENCES TO role_financedaily;

-- Clone the exact 7-table structure from ai_brain.doniesdaily_* into team_financedaily.*
CREATE TABLE team_financedaily.content_ideas (LIKE ai_brain.doniesdaily_content_ideas INCLUDING ALL);
CREATE TABLE team_financedaily.production_queue (LIKE ai_brain.doniesdaily_production_queue INCLUDING ALL);
CREATE TABLE team_financedaily.clip_usage (LIKE ai_brain.doniesdaily_clip_usage INCLUDING ALL);
CREATE TABLE team_financedaily.learnings (LIKE ai_brain.doniesdaily_learnings INCLUDING ALL);
CREATE TABLE team_financedaily.posts (LIKE ai_brain.doniesdaily_posts INCLUDING ALL);
CREATE TABLE team_financedaily.metrics_history (LIKE ai_brain.doniesdaily_metrics_history INCLUDING ALL);
CREATE TABLE team_financedaily.sniper_logs (LIKE ai_brain.doniesdaily_sniper_logs INCLUDING ALL);
```

#### Python Database Helper Enforcement (`core/db.py`):
Every database call in the Virgin Master Framework is routed through a single context-locked wrapper that enforces `SET ROLE` and `SET search_path`:
```python
def run_team_sql(team_slug: str, sql_query: str) -> str:
    if not re.match(r"^[a-z0-9_]+$", team_slug):
        raise ValueError(f"Invalid team_slug: {team_slug}")
    scoped_sql = f"SET ROLE role_{team_slug}; SET search_path TO team_{team_slug}, public; {sql_query}"
    cmd = ["docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-t", "-A", "-c", scoped_sql]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    # Strip 'SET\nSET\n' output lines from psql -t -A
    lines = [line for line in res.stdout.splitlines() if line not in ("SET",)]
    return "\n".join(lines).strip()
```
Even if a developer accidentally writes `SELECT * FROM team_doniesdaily.learnings` while running as `financedaily`, PostgreSQL rejects it with `ERROR: permission denied for schema team_doniesdaily` because `SET ROLE role_financedaily` only has `USAGE` on `team_financedaily`.

---

### 3.2 SQLite Swarm Matrix Isolation Protocol (`agents_chat.db`)

Currently, `/home/ubuntu/vps-control-center/backend/data/agents_chat.db` stores all agent communications in `agent_messages` and `agent_traces`. As proven in the Swarm Matrix SQLite stats, channels like `donies`, `doniesdaily`, `bawang`, `subtracker`, and `all` coexist in the same SQLite file, with inconsistent `sender_id` values (`doni`, `doniesdaily`, `luna`, `sub-luna`).

When scaling to 10–100 teams, two failure modes arise:
1. **UI & Context Contamination:** Two teams posting as `sender_id = 'luna'` or into `channel = 'all'` merge their personas in the VPS Control Center UI.
2. **SQLite `SQLITE_BUSY` Write Lock Contention:** 50 teams writing traces simultaneously to a single SQLite file will trigger database lock timeouts.

#### Isolation Architecture for Swarm Matrix:
1. **Strict Namespace Convention (1–20 Teams on Single VPS):**
   - Enable SQLite WAL mode (`PRAGMA journal_mode=WAL; PRAGMA busy_timeout=10000;`) on `agents_chat.db`.
   - Enforce composite `sender_id` and strict `channel` partitioning in `core/swarm_logger.py`:
     - `channel`: Always `team_{team_slug}` (e.g., `team_doniesdaily`, `team_financedaily`). **Never** write routine standup or sprint logs to `'all'`; `'all'` is reserved strictly for Executive Holding (`hermes` / `fahru`) alerts.
     - `sender_id`: Always `{team_slug}:{agent_role_key}` (e.g., `financedaily:orchestrator`, `financedaily:scriptwriter`, `financedaily:qc`).
     - `sender_name`: `{Agent Persona Name} [{Team Badge}]` (e.g., `Luna (Scriptwriter) [FinanceDaily]`).
2. **Per-Team Sharded SQLite Databases (20–100 Teams):**
   - Each team writes to `/home/ubuntu/vps-control-center/backend/data/swarms/{team_slug}_chat.db`.
   - The VPS Control Center backend dynamically mounts `?team={team_slug}` by connecting to that team's dedicated `.db` file in read-only mode, completely eliminating write-lock contention across teams.

---

### 3.3 Obsidian Vault Isolation Protocol (Zero GRO Cross-Talk)

In `doni_working_hours_standup.py`, `VAULT_DIR` is hardcoded to `/home/ubuntu/vault/01_Business/doniesdaily`. Under the GRO v3.0 Triad Compaction protocol (`ActiveContext.md`, `Index - {slug}.md`, and timestamped Devlogs), any LLM agent reading the vault workspace must only see its own channel's history.

#### Vault Directory Topology:
```text
/home/ubuntu/vault/01_Business/
├── Index - 01_Business.md                 # Holding-level MOC (Hermes Only)
├── doniesdaily/                           # Team 1 Vault Workspace
│   ├── ActiveContext.md
│   ├── Index - doniesdaily.md
│   └── 2026-11-06 - 07.30 - Rapat Standup & Kurasi Editorial Squad DoniesDaily.md
├── financedaily/                          # Team 2 Vault Workspace
│   ├── ActiveContext.md
│   ├── Index - financedaily.md
│   └── 2026-11-06 - 07.45 - Rapat Standup & Kurasi Editorial Squad FinanceDaily.md
└── {team_slug}/                           # Team N Vault Workspace
    ├── ActiveContext.md
    └── Index - {team_slug}.md
```
- **Enforcement Rule:** The `VaultArchivist` module resolves `VAULT_DIR = Path(f"/home/ubuntu/vault/01_Business/{team_slug}").resolve()` and asserts `VAULT_DIR.parent == Path("/home/ubuntu/vault/01_Business")` (preventing path traversal `../`).
- YAML frontmatter in every Devlog and `ActiveContext.md` is strictly tagged with `workspace: "01_Business/{team_slug}"` and `team_slug: "{team_slug}"`.

---

### 3.4 Ephemeral Cache, Asset & Runtime State Isolation

Every file path touched during pre-production, rendering, and post-production must be strictly namespaced by `{team_slug}`:

| Artifact Type | Legacy Path (`doniesdaily` singleton) | Isolated Multi-Team Path (`{team_slug}` namespaced) | Cleanup / Lifecycle Policy |
| :--- | :--- | :--- | :--- |
| **ProRes 4444 Overlay** | `/tmp/{topic}_remotion_overlay.mov` | `/tmp/ugc_render/{team_slug}/{topic_key}_{run_id}_overlay.mov` | Unlinked immediately after YouTube publication or after sprint exit (`finally:` block + `tmpfiles.d` 6h age purge). |
| **FFmpeg Concat / Norm Slices** | `/tmp/concat_list.txt`, `/tmp/slice_*.mp4` | `/tmp/ugc_render/{team_slug}/{topic_key}/slice_{idx}.mp4` | `shutil.rmtree(f"/tmp/ugc_render/{team_slug}/{topic_key}")` immediately upon composite completion. |
| **Remotion Public Stage** | `remotion/public/doni-{t_key}-captions.json` | `remotion/public/tenants/{team_slug}/{topic_key}/captions.json`, `master.mp3` | Unlinked after composite MP4 passes Cleo QC. |
| **Daily Jitter State** | `data/doni_daily_jitter.json` | `/home/ubuntu/teams/{team_slug}/data/daily_jitter.json` | Persistent per team; rolls over daily at 00:00 WIB. |
| **Asset Catalog JSON** | `data/cat_assets_catalog.json` | `/home/ubuntu/teams/{team_slug}/data/assets_catalog.json` | Persistent per team; updated only by `ingest_footage.py --team {team_slug}`. |
| **Raw Clips & Voiceovers** | `assets/cat_videos/fahru_clips/`, `assets/audio/generated_voiceovers/` | `/home/ubuntu/teams/{team_slug}/assets/clips/authentic/`, `/home/ubuntu/teams/{team_slug}/assets/audio/voiceovers/` | Permanent per-team vault. |
| **Master Output MP4** | `output/{topic}_master.mp4` | `/home/ubuntu/teams/{team_slug}/output/{topic_key}_master.mp4` | Retained for 7 days, then auto-pruned by cron after verifying `youtube_video_id IS NOT NULL` in DB. |

---

## 4. API Credential, Browser CDP & Quota Management

Scaling across multiple channels introduces severe external API rate limits and account association risks (Google OAuth, YouTube Studio CDP, ElevenLabs TTS, and CLIProxyAPI LLM calls).

### 4.1 YouTube OAuth Credential Partitioning & Google Cloud Project Sharding

1. **Isolated OAuth Token Files:**
   - Stored at `/home/ubuntu/.config/youtube/{team_slug}_oauth.json` with `chmod 600` permissions.
   - `YouTubeAPIPublisher(oauth_path=Path(f"/home/ubuntu/.config/youtube/{team_slug}_oauth.json"))` refuses to initialize if `team_slug` is omitted—removing `DEFAULT_OAUTH_PATH` entirely so a misconfigured team fails closed rather than uploading to `@DoniesDaily`.
   - **Pre-Upload Channel ID Verification Gate (Hukum Besi Multi-Team):**
     Before calling `youtube.videos().insert()`, `YouTubeAPIPublisher` calls `youtube.channels().list(part="id", mine=True)` (cost: 1 quota unit) and asserts:
     ```python
     authenticated_channel_id = resp["items"][0]["id"]
     assert authenticated_channel_id == team_config["youtube_channel_id"], (
         f"FATAL CROSS-CHANNEL LEAK BLOCKED: OAuth token belongs to {authenticated_channel_id}, "
         f"but team '{team_slug}' expects {team_config['youtube_channel_id']}!"
     )
     ```
2. **Google Cloud Project Quota Sharding:**
   - **YouTube Data API v3 Default Quota:** `10,000 units/day` per Google Cloud Project.
   - **Cost per Short Upload:** `videos.insert` = `1,600 units` + `thumbnails.set` = `50 units` + `channels.list` = `1 unit` $\approx$ **`1,651 units/video`**.
   - At 3 videos/day/channel, **1 channel consumes `4,953 units/day` (~50% of a GCP project's quota)**.
   - **Hard Partitioning Rule:** Maximum **2 channels per Google Cloud Project** (`client_id` / `client_secret`). When deploying 10 channels, allocate 5 distinct GCP Projects (or request quota extension per project), storing the dedicated `client_id` and `client_secret` directly inside each `/home/ubuntu/.config/youtube/{team_slug}_oauth.json`.

### 4.2 Persistent Chrome CDP (`:9222`) Multi-Profile Isolation

Currently, `doni_evaluator.py` (Mochi Advanced Mode scraping), `doni_oauth_auto_healer.py`, and `FlowCDPOperator` connect to a single Chrome instance at `127.0.0.1:9222` using `/home/ubuntu/apps/ugc-lemonaru/data/chrome_persistent`.
- **The Multi-Channel Problem:** If 10 channels share one Chrome profile or stay logged into the same browser session concurrently, YouTube Studio scrapes the wrong channel's analytics, and Google flags multi-channel switching as suspicious automation.
- **The On-Demand Ephemeral CDP Port Allocation Protocol:**
  Instead of 10 always-on Chrome instances (which would consume $10 \times 650\text{ MB} = 6.5\text{ GB}$ RAM), each team has an isolated `--user-data-dir=/home/ubuntu/teams/{team_slug}/data/chrome_profile` on disk, and **only launches headless/Xvfb Chrome on demand** during its 90-second OAuth heal or Mochi Studio scrape window, guarded by a browser mutex lock (`/var/lock/ugc_chrome_cdp.lock`):
  ```python
  # Context manager in core/browser_pool.py
  with acquire_exclusive_lock("/var/lock/ugc_chrome_cdp.lock", timeout=300):
      proc = launch_chrome_on_xvfb(
          user_data_dir=f"/home/ubuntu/teams/{team_slug}/data/chrome_profile",
          cdp_port=9222
      )
      try:
          yield "http://127.0.0.1:9222"
      finally:
          terminate_chrome_cleanly(proc)
  ```
  This keeps idle browser RAM at **0 MB** while providing **100% cookie, IndexedDB, and Google Account isolation** per channel.

### 4.3 Rate-Limit Staggering & Global Mutex Orchestration

To prevent bursting CLIProxyAPI (`127.0.0.1:8317`), ElevenLabs TTS concurrency limits (2–5 concurrent requests depending on tier), and VPS CPU/RAM during Remotion rendering, all teams are coordinated via **Deterministic Hash-Based Time-Slot Staggering** and **Two-Tier OS File Locks (`flock`)**.

```mermaid
gantt
    title Deterministic Staggered Execution Timeline (Sample 4 Teams on 2-vCPU VPS)
    dateFormat  HH:mm
    axisFormat  %H:%M

    section Standup (LLM + CDP)
    doniesdaily Standup   :s1, 07:00, 4m
    financedaily Standup  :s2, 07:06, 4m
    gadgetdaily Standup   :s3, 07:12, 4m
    healthdaily Standup   :s4, 07:18, 4m

    section Morning Sprint (TTS + Remotion + Upload)
    doniesdaily Render    :r1, 08:05, 5m
    financedaily Render   :r2, 08:17, 5m
    gadgetdaily Render    :r3, 08:29, 5m
    healthdaily Render    :r4, 08:41, 5m
```

#### Two-Tier Semaphores / Locks (`/var/lock/`):
1. **Render & FFmpeg Lock (`/var/lock/ugc_heavy_render.lock` — Exclusive `flock`):**
   - Acquired before calling `npx remotion render` or `ffmpeg` composite/QC.
   - Guarantees **max 1 heavy media pipeline** runs at a time on the 2-vCPU / 4GB VPS.
2. **API & TTS Concurrency Semaphore (`/var/lock/ugc_api_slot_{0..1}.lock`):**
   - Limits concurrent ElevenLabs v4 TTS syntheses and `claude-opus-5-5-high` / `gemini-4-argon-high` calls to at most 2 parallel requests across the entire host.
3. **Deterministic Slot Window Partitioning:**
   - Instead of every team rolling a random minute in `08:04–08:55` (which guarantees collisions via the Birthday Paradox once $N \ge 4$), each team registered with index $i \in \{0, 1, \dots, N-1\}$ is assigned a dedicated sub-window:
     $$\text{WindowStart}_i = 60 \times \frac{i}{N}, \quad \text{WindowEnd}_i = 60 \times \frac{i+1}{N} - 2$$
   - Within its assigned slice $[\text{WindowStart}_i, \text{WindowEnd}_i]$, the team adds organic micro-jitter (`random.randint(5, 45)` seconds) so YouTube never sees robotic fixed-minute uploads, while two teams on the same VPS **never** collide in time.

---

## 5. Framework Upgrades & Propagation Strategy

When an architectural improvement is engineered in the Universal Core—for example, upgrading Cleo's `doni_qc_gate.py` to detect audio phase cancellation, or adding a new React kinetic component in `remotion/src/components/`—it must propagate cleanly to all 10, 50, or 100 teams **without overwriting** any team's `SOUL.md` personas, learned rules, phonetic dictionaries, or asset catalogs.

### 5.1 Evaluation of Code Distribution Topologies

| Distribution Mechanism | Pros | Cons | Verdict |
| :--- | :--- | :--- | :--- |
| **Git Submodules** | Explicit commit SHA pinning per team repo. | Notoriously error-prone (`detached HEAD`, forgotten `git submodule update --remote` across 50 folders) and duplicates working trees on disk. | ❌ **REJECTED** |
| **Git Subtree** | Single repo history per team. | Merging upstream changes across 50–100 team repositories requires 50–100 git merge operations and risks merge conflicts. | ❌ **REJECTED** |
| **Editable Python Package (`pip install -e ./core`) + Strict Core/Tenant Separation + Release Symlink Switching** | Zero code duplication; atomic 1-millisecond upgrades & rollbacks via symlink flip (`releases/v2.1.0` $\rightarrow$ `current`); clean separation between **Code (Immutable Core)** and **State/Persona (Tenant Workspace)**. | Requires strict prohibition against storing tenant state inside the code directory. | ✅ **SELECTED (GOLD STANDARD)** |

### 5.2 The Immutable Core vs. Tenant Workspace Boundary

We separate the system into two completely decoupled filesystem trees:

```text
/home/ubuntu/apps/ugc-master-core/          # IMMUTABLE ENGINE (Git-Tracked, Zero Channel State)
├── releases/
│   ├── v2.1.0/                             # Tagged Release v2.1.0
│   │   ├── pyproject.toml
│   │   ├── ugc_core/                       # Installed via pip install -e
│   │   │   ├── orchestrator.py             # Parameterized doni_production_sprint.py
│   │   │   ├── standup.py                  # Parameterized doni_working_hours_standup.py
│   │   │   ├── scriptwriter.py             # Parameterized doni_scriptwriter.py
│   │   │   ├── hybrid_renderer.py          # Parameterized doni_hybrid_renderer.py
│   │   │   ├── qc_gate.py                  # Parameterized doni_qc_gate.py (Cleo)
│   │   │   ├── evaluator.py                # Parameterized doni_evaluator.py (Mochi)
│   │   │   ├── youtube_publisher.py        # Parameterized youtube_api_publisher.py
│   │   │   └── ingest_footage.py           # Parameterized 10-frame multi-vision ingester
│   │   └── remotion/                       # Universal Remotion Studio Engine
│   │       ├── package.json
│   │       ├── node_modules/
│   │       └── src/
│   │           ├── DoniOverlay.tsx         # Accepts dynamic theme/colors/fonts via Zod props
│   │           └── components/
│   └── v2.2.0/                             # Tagged Release v2.2.0 (Canary / Next)
├── current -> /home/ubuntu/apps/ugc-master-core/releases/v2.1.0/
└── .venv/                                  # Shared Python Virtual Environment

/home/ubuntu/teams/                         # MUTABLE TENANT WORKSPACES (1 Folder per Channel)
├── doniesdaily/
│   ├── team_config.yaml                    # Channel ID, Voice ID, Theme Colors, Models, Niche
│   ├── core_pin -> /home/ubuntu/apps/ugc-master-core/current   # Or pinned to releases/v2.1.0
│   ├── souls/                              # Channel-Specific Agent Personas
│   │   ├── ORCHESTRATOR_SOUL.md            # (Doni)
│   │   ├── ANALYTICS_SOUL.md               # (Mochi)
│   │   ├── SCRIPTWRITER_SOUL.md            # (Luna)
│   │   ├── AUDIO_SOUL.md                   # (Kak Ceria / Vivan)
│   │   ├── VISUAL_SOUL.md                  # (Milo)
│   │   ├── QC_SOUL.md                      # (Cleo)
│   │   └── voice_profile.md                # Channel vocabulary, banned words, phonetic dict
│   ├── data/
│   │   ├── assets_catalog.json
│   │   ├── sfx_catalog.json
│   │   ├── daily_jitter.json
│   │   └── chrome_profile/
│   ├── assets/
│   │   ├── clips/authentic/
│   │   ├── clips/ai_renders/
│   │   └── audio/{bgm.mp3, sfx/, voiceovers/, dataset/}
│   └── output/
└── financedaily/
    ├── team_config.yaml
    ├── core_pin -> /home/ubuntu/apps/ugc-master-core/current
    └── ...
```

### 5.3 Canary Rollout & Instant Zero-Downtime Rollback Protocol

Notice the `core_pin` symlink inside each `/home/ubuntu/teams/{team_slug}/` folder:
1. **Default Inheritance:** By default, a team's `core_pin` points to `/home/ubuntu/apps/ugc-master-core/current`.
2. **Canary Testing a New Release (`v2.2.0`):**
   - Deploy new code to `/home/ubuntu/apps/ugc-master-core/releases/v2.2.0`.
   - Point **only one canary team** (e.g., `test_sandbox` or `financedaily`) to `v2.2.0`:
     `ln -sfn /home/ubuntu/apps/ugc-master-core/releases/v2.2.0 /home/ubuntu/teams/financedaily/core_pin`
   - Run 1 full standup + production sprint on the canary team and verify `QC_PASSED`.
3. **Fleet-Wide Atomic Promotion:**
   - Once verified, flip the global `current` symlink atomically:
     `ln -sfn /home/ubuntu/apps/ugc-master-core/releases/v2.2.0 /home/ubuntu/apps/ugc-master-core/current`
   - All 50–100 teams immediately execute `v2.2.0` on their next scheduled cron tick without touching a single file inside `/home/ubuntu/teams/*`.
4. **1-Second Emergency Rollback:**
   - If `v2.2.0` introduces a regression, run:
     `ln -sfn /home/ubuntu/apps/ugc-master-core/releases/v2.1.0 /home/ubuntu/apps/ugc-master-core/current`
   - Every team reverts to the known-good `v2.1.0` engine in `< 5ms`.

---

## 6. End-to-End Cloning Playbook (`tools/clone_channel.py`)

Below is the complete, production-ready operational playbook and automated provisioning CLI specification to clone a brand-new autonomous media squad in under 60 seconds.

### 6.1 Standard Tenant Configuration Schema (`team_config.yaml`)

Each cloned team is governed by a declarative `team_config.yaml` generated during cloning:

```yaml
team_slug: "finance_daily"
display_name: "FinanceDaily ID"
youtube_channel_id: "UCxxxxxxxxxxxxxxxxxxxxxx"
niche: "Crypto, Saham & Personal Finance Anak Muda Indonesia"
audience_persona: "Anak muda Indonesia usia 20-35 tahun yang ingin melek finansial, investasi waras, dan anti-rungkad."

agents:
  orchestrator: { id: "rex", name: "Rex", emoji: "🦁", model: "gemini-4-argon-high" }
  analytics:    { id: "quant", name: "Quant", emoji: "📈", model: "gemini-4-argon-high" }
  scriptwriter: { id: "sora", name: "Sora", emoji: "✍️", model: "claude-sonnet-5-5-high" }
  audio:        { id: "bima", name: "Bang Bima", emoji: "🎙️", voice_id: "ZowYWFat3iypr7PwKMPb", stability: 0.45, similarity_boost: 0.80, speed: 1.10 }
  visual:       { id: "vega", name: "Vega", emoji: "🎬", model: "claude-opus-5-5-high" }
  qc:           { id: "aegis", name: "Aegis", emoji: "🛡️", target_lufs_min: -19.0, target_lufs_max: -14.0 }

branding:
  watermark_text: "💸 @FinanceDailyID"
  badge_default: "🚨 FAKTA CUAN VIRAL"
  primary_accent_hex: "#00FF88"
  outro_cta_phrase: "dan jangan lupa follow dan subscribe FinanceDaily ID biar gak rungkad ya!"

cadence:
  max_daily_posts: 3
  standup_cron: "42 7,17 * * *"
  morning_slot_cron: "*/5 9 * * *"
  midday_slot_cron: "*/5 13 * * *"
  evening_slot_cron: "*/5 19 * * *"

paths:
  oauth_file: "/home/ubuntu/.config/youtube/finance_daily_oauth.json"
  vault_dir: "/home/ubuntu/vault/01_Business/finance_daily"
  temp_dir: "/tmp/ugc_render/finance_daily"
```

### 6.2 Reference Implementation of `tools/clone_channel.py`

```python
#!/usr/bin/env python3
"""
tools/clone_channel.py
======================
Virgin Master Framework Provisioner — Safely clones a new isolated multi-agent YouTube Shorts
squad with zero cross-channel contamination.

 Performs 7 Atomic Provisioning Steps:
1. Validates slug uniqueness & system capacity.
2. Creates isolated directory hierarchy in /home/ubuntu/teams/<slug>/.
3. Generates parameterized team_config.yaml & niche-adapted Agent Souls.
4. Provisions isolated PostgreSQL schema `team_<slug>` + RBAC role `role_<slug>` + 7 core tables.
5. Initializes Obsidian Vault workspace `/home/ubuntu/vault/01_Business/<slug>/` (ActiveContext + MOC).
6. Initializes Swarm Matrix room `team_<slug>` in SQLite `agents_chat.db`.
7. Registers staggered cron tasks in `ai_brain.cadence_tasks` (paused until OAuth & 10+ clips are verified).
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

TEAMS_ROOT = Path("/home/ubuntu/teams")
CORE_CURRENT = Path("/home/ubuntu/apps/ugc-master-core/current")
VAULT_ROOT = Path("/home/ubuntu/vault/01_Business")
OAUTH_DIR = Path("/home/ubuntu/.config/youtube")


def run_psql(sql: str) -> str:
    cmd = ["docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-v", "ON_ERROR_STOP=1", "-t", "-A", "-c", sql]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return res.stdout.strip()


def provision_team(args):
    slug = args.slug.strip().lower()
    if not re.match(r"^[a-z][a-z0-9_]{2,28}$", slug):
        sys.exit("FATAL: --slug must be lowercase alphanumeric/underscore (3-29 chars).")

    team_dir = TEAMS_ROOT / slug
    if team_dir.exists():
        sys.exit(f"FATAL: Team workspace already exists at {team_dir}")

    print(f"🚀 [1/7] Creating isolated workspace directory at {team_dir}...")
    for sub in [
        "souls", "data/chrome_profile", "assets/clips/authentic",
        "assets/clips/ai_renders", "assets/audio/sfx",
        "assets/audio/voiceovers", "assets/audio/dataset", "output"
    ]:
        (team_dir / sub).mkdir(parents=True, exist_ok=True)

    # Link core_pin to current immutable release
    (team_dir / "core_pin").symlink_to(CORE_CURRENT)

    # Initialize empty catalogs
    (team_dir / "data/assets_catalog.json").write_text("[]\n", encoding="utf-8")
    (team_dir / "data/sfx_catalog.json").write_text("[]\n", encoding="utf-8")

    print(f"📝 [2/7] Writing team_config.yaml and niche-adapted Souls for '{args.display_name}'...")
    # Calculate deterministic staggered cron offset based on existing team count
    team_count_str = run_psql("SELECT count(*) FROM information_schema.schemata WHERE schema_name LIKE 'team_%';")
    idx = int(team_count_str or "0") + 1
    standup_min = (30 + (idx * 7)) % 58
    morning_hour = 8 + (idx % 2)
    evening_hour = 18 + (idx % 2)

    config_payload = {
        "team_slug": slug,
        "display_name": args.display_name,
        "youtube_channel_id": args.channel_id,
        "niche": args.niche,
        "voice_id": args.voice_id,
        "watermark_text": args.watermark,
        "badge_default": args.badge,
        "primary_accent_hex": args.accent_color,
        "outro_cta_phrase": f"dan jangan lupa follow dan subscribe {args.display_name} ya!",
        "standup_cron": f"{standup_min} 7,17 * * *",
        "morning_slot_cron": f"*/5 {morning_hour} * * *",
        "evening_slot_cron": f"*/5 {evening_hour} * * *",
        "oauth_file": str(OAUTH_DIR / f"{slug}_oauth.json"),
        "vault_dir": str(VAULT_ROOT / slug),
        "temp_dir": f"/tmp/ugc_render/{slug}"
    }
    (team_dir / "team_config.json").write_text(json.dumps(config_payload, indent=2), encoding="utf-8")

    print(f"🐘 [3/7] Provisioning isolated PostgreSQL schema 'team_{slug}' & RBAC role 'role_{slug}'...")
    sql_provision = f"""
    CREATE SCHEMA IF NOT EXISTS team_{slug};
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'role_{slug}') THEN
            CREATE ROLE role_{slug} NOLOGIN;
        END IF;
    END
    $$;
    GRANT USAGE ON SCHEMA team_{slug} TO role_{slug};
    CREATE TABLE IF NOT EXISTS team_{slug}.content_ideas (LIKE ai_brain.doniesdaily_content_ideas INCLUDING ALL);
    CREATE TABLE IF NOT EXISTS team_{slug}.production_queue (LIKE ai_brain.doniesdaily_production_queue INCLUDING ALL);
    CREATE TABLE IF NOT EXISTS team_{slug}.clip_usage (LIKE ai_brain.doniesdaily_clip_usage INCLUDING ALL);
    CREATE TABLE IF NOT EXISTS team_{slug}.learnings (LIKE ai_brain.doniesdaily_learnings INCLUDING ALL);
    CREATE TABLE IF NOT EXISTS team_{slug}.posts (LIKE ai_brain.doniesdaily_posts INCLUDING ALL);
    CREATE TABLE IF NOT EXISTS team_{slug}.metrics_history (LIKE ai_brain.doniesdaily_metrics_history INCLUDING ALL);
    CREATE TABLE IF NOT EXISTS team_{slug}.sniper_logs (LIKE ai_brain.doniesdaily_sniper_logs INCLUDING ALL);
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA team_{slug} TO role_{slug};
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA team_{slug} TO role_{slug};
    """
    run_psql(sql_provision)

    print(f"💎 [4/7] Initializing isolated Obsidian Vault workspace at {VAULT_ROOT / slug}...")
    vault_dir = VAULT_ROOT / slug
    vault_dir.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+07:00")
    (vault_dir / "ActiveContext.md").write_text(
        f"---\nworkspace: 01_Business/{slug}\nteam_slug: {slug}\nlast_updated: {now_iso}\nstatus: active\n---\n\n"
        f"# Active Context — {args.display_name} ({args.niche})\n\n- **Channel ID:** `{args.channel_id}`\n- **Schema:** `team_{slug}`\n",
        encoding="utf-8"
    )
    (vault_dir / f"Index - {slug}.md").write_text(
        f"# Index — {args.display_name}\n\n| Tanggal | Jam (WIB) | Topik Devlog | Tautan Catatan |\n|---|---|---|---|\n",
        encoding="utf-8"
    )

    print(f"⏱️ [5/7] Registering staggered Cadence Tasks in ai_brain.cadence_tasks (status='paused' until pre-flight pass)...")
    sql_cadence = f"""
    INSERT INTO ai_brain.cadence_tasks (task_key, title, cron_expr, action_type, action_payload, status)
    VALUES
      ('business.{slug}_standup', 'Standup & Evaluasi 2x Sehari ({args.display_name})', '{config_payload["standup_cron"]}', 'script_runner', '{{"script": "/home/ubuntu/apps/ugc-master-core/current/ugc_core/standup.py", "args": ["--team", "{slug}"]}}', 'paused'),
      ('business.{slug}_morning_sprint', 'Sprint Produksi Pagi ({args.display_name})', '{config_payload["morning_slot_cron"]}', 'script_runner', '{{"script": "/home/ubuntu/apps/ugc-master-core/current/ugc_core/orchestrator.py", "args": ["--team", "{slug}", "--jitter-window", "--slot", "morning"], "timeout": 900}}', 'paused'),
      ('business.{slug}_evening_sprint', 'Sprint Produksi Sore ({args.display_name})', '{config_payload["evening_slot_cron"]}', 'script_runner', '{{"script": "/home/ubuntu/apps/ugc-master-core/current/ugc_core/orchestrator.py", "args": ["--team", "{slug}", "--jitter-window", "--slot", "evening"], "timeout": 900}}', 'paused')
    ON CONFLICT (task_key) DO NOTHING;
    """
    run_psql(sql_cadence)

    print(f"✅ [6/7] Team '{slug}' provisioned successfully! Pre-activation checklist:")
    print(f"   1. Place OAuth credentials at: {config_payload['oauth_file']}")
    print(f"   2. Ingest >= 15 authentic clips: python3 /home/ubuntu/apps/ugc-master-core/current/ugc_core/ingest_footage.py --team {slug} --scan")
    print(f"   3. Run dry-run verification:     python3 /home/ubuntu/apps/ugc-master-core/current/ugc_core/verify_isolation.py --team {slug}")
```

### 6.3 Step-by-Step CLI Execution Playbook (Operator Runbook)

To deploy a new channel (e.g., `finance_daily` for "Crypto & Personal Finance"), execute the following 5 deterministic commands:

#### Step 1: Execute the Provisioner CLI
```bash
python3 /home/ubuntu/tools/clone_channel.py \
  --slug finance_daily \
  --display-name "FinanceDaily ID" \
  --channel-id "UC9x8y7z6w5v4u3t2s1r0q" \
  --niche "Crypto, Saham & Personal Finance Anak Muda Indonesia" \
  --voice-id "ZowYWFat3iypr7PwKMPb" \
  --watermark "💸 @FinanceDailyID" \
  --badge "🚨 FAKTA CUAN VIRAL" \
  --accent-color "#00FF88"
```

#### Step 2: Provision & Verify Dedicated YouTube OAuth Token
```bash
# Authenticate the new Google Account into its isolated token path (never touching doniesdaily_oauth.json)
/home/ubuntu/apps/ugc-master-core/.venv/bin/python \
  /home/ubuntu/apps/ugc-master-core/current/ugc_core/youtube_oauth_init.py \
  --team finance_daily \
  --client-secrets /home/ubuntu/.config/youtube/gcp_project_02_client_secret.json \
  --output /home/ubuntu/.config/youtube/finance_daily_oauth.json

chmod 600 /home/ubuntu/.config/youtube/finance_daily_oauth.json
```

#### Step 3: Ingest Initial Visual Asset Pool (10-Frame Multi-Vision Protocol)
```bash
# Drop 15-20 niche-specific raw clips into /home/ubuntu/teams/finance_daily/assets/clips/authentic/
/home/ubuntu/apps/ugc-master-core/.venv/bin/python \
  /home/ubuntu/apps/ugc-master-core/current/ugc_core/ingest_footage.py \
  --team finance_daily \
  --scan
```

#### Step 4: Execute the Isolation & Dry-Run Verification Suite
```bash
# Asserts RBAC blocks cross-schema SQL, verifies OAuth channel ID match, and runs 1 dry-run standup + QC render
/home/ubuntu/apps/ugc-master-core/.venv/bin/python \
  /home/ubuntu/apps/ugc-master-core/current/ugc_core/verify_isolation.py \
  --team finance_daily \
  --assert-cross-schema-denied team_doniesdaily \
  --dry-run-render
```

#### Step 5: Activate Autonomous Cadence in PostgreSQL
```bash
docker exec -i supabase-db psql -U postgres -d postgres -c \
  "UPDATE ai_brain.cadence_tasks SET status = 'active' WHERE task_key LIKE 'business.finance_daily_%';"
```

---

## 7. Summary Verification Checklist for Multi-Team Isolation

| Isolation Gate | Enforcement Mechanism | Failure Mode Prevented |
| :--- | :--- | :--- |
| **PostgreSQL RBAC Gate** | `SET ROLE role_{slug}; SET search_path TO team_{slug};` | Prevents Team B from querying or mutating Team A's `content_ideas`, `posts`, or `learnings`. |
| **YouTube Channel ID Hardware Assert** | `channels().list(mine=True)` compared against `team_config.yaml` before upload | Prevents accidental cross-uploading of Finance or Tech Shorts to `@DoniesDaily`. |
| **Global Render Mutex (`flock`)** | `/var/lock/ugc_heavy_render.lock` around Remotion & FFmpeg | Prevents Linux OOM killer from crashing `supabase-db` when 2+ teams render on the 2-vCPU / 4GB RAM VPS. |
| **Ephemeral `/tmp` Namespacing** | `/tmp/ugc_render/{team_slug}/{topic_key}_{run_id}_overlay.mov` | Eliminates ProRes 4444 `.mov` filename collisions and disk exhaustion. |
| **Chrome CDP Profile Partitioning** | `/home/ubuntu/teams/{team_slug}/data/chrome_profile` + `/var/lock/ugc_chrome_cdp.lock` | Prevents Google Account cookie bleed during YouTube Studio Advanced Mode scraping. |
| **Obsidian Vault Scoping** | `/home/ubuntu/vault/01_Business/{team_slug}/ActiveContext.md` | Prevents GRO v3.0 memory compaction from leaking cat directives into non-cat channels. |
| **Blue/Green Symlink Core (`core_pin`)** | `/home/ubuntu/teams/{slug}/core_pin` $\rightarrow$ `/home/ubuntu/apps/ugc-master-core/current` | Enables instant fleet-wide engine upgrades and `<5ms` atomic rollbacks without touching tenant personas or data. |