# 🛡️ DELIVERABLE 12: MASTER RISK & GAP ANALYSIS (`12_RISK_GAP_ANALYSIS.md`)

**Document Classification:** Technical Audit — Phase 11 (Severity-Rated Vulnerability, Technical Debt & Architectural Gap Analysis)  
**Target Ecosystem:** `@DoniesDaily` Autonomous Multi-Agent YouTube Shorts Production Engine  
**Canonical Workspace:** `/home/ubuntu/apps/ugc-lemonaru/` & `/home/ubuntu/tools/`  
**Audit Date:** 2026-11-06  
**Audit Status:** READ-ONLY VERIFIED  

---

## 1. Risk Classification Framework

To evaluate the operational stability, security posture, and template portability of the `@DoniesDaily` autonomous production engine, all findings are categorized using a deterministic 5-tier severity rating framework grounded in CVSS-aligned impact and likelihood metrics:

| Severity Level | SLA / Remediation Priority | Operational & Architectural Definition |
| :--- | :--- | :--- |
| 🔴 **CRITICAL** | **Immediate (P0)** — Blocks production or Virgin Template cloning | Systemic failure vector capable of causing total pipeline paralysis, kernel-level Out-Of-Memory (OOM) crashes, unrecoverable credential exposure, or severe compliance/brand contamination across channels. |
| 🟠 **HIGH** | **Urgent (P1)** — Mitigate within 24–72 hours | High-probability single points of failure (SPOF), API quota exhaustion vectors, or severe specification-to-code drift that silently degrades broadcast quality or halts daily publishing cadences. |
| 🟡 **MEDIUM** | **Scheduled (P2)** — Mitigate within 1–2 sprints | Technical debt, legacy code entanglement, state machine stalls, or conflicting rule injections in PostgreSQL that require manual operator intervention or cause non-fatal retry loops. |
| 🔵 **LOW** | **Backlog (P3)** — Mitigate during routine maintenance | Minor inconsistencies in logging schemas, non-blocking UI/metadata artifacts, or suboptimal disk cache lifecycles that do not immediately threaten uptime. |
| ⚪ **INFORMATIONAL** | **Observation (P4)** — Document for architectural awareness | Architectural observations, future scalability considerations (e.g., voice dataset harvesting progress), or external platform constraints outside direct code control. |

### Master Risk Matrix Overview

```mermaid
quadrantChart
    title DoniesDaily Ecosystem Risk Assessment Matrix (Impact vs. Likelihood)
    x-axis Low Likelihood --> High Likelihood
    y-axis Low Impact --> High Impact
    quadrant-1 CRITICAL (Immediate Action)
    quadrant-2 HIGH (Architectural Hardening)
    quadrant-3 LOW / INFO (Routine Maintenance)
    quadrant-4 MEDIUM (Technical Debt Cleanup)
    "R4: VPS Hardware/OOM Choke": [0.85, 0.92]
    "R2: CLIProxyAPI (:8317) SPOF": [0.78, 0.90]
    "R8: Spec-to-Code & DB Drift": [0.92, 0.78]
    "R9: Credential Hygiene & SQLi": [0.68, 0.88]
    "R1: Legacy E-Com Entanglement": [0.95, 0.65]
    "R3: Chrome CDP (:9222) Fragility": [0.72, 0.75]
    "R6: YouTube API Quota Ceiling": [0.60, 0.80]
    "R5: ElevenLabs Credit Drain": [0.55, 0.70]
    "R7: Cross-Channel Contamination": [0.80, 0.62]
    "R10: State Machine Deadlocks": [0.62, 0.58]
```

---

## 2. Comprehensive Risk & Gap Assessment

### 🔴 RISK 1: Legacy Code Entanglement & E-Commerce Artifact Contamination
* **Severity:** **HIGH** (Escalates to **CRITICAL** if `OutroCTA` renders with default props or when cloning to a Virgin Template)
* **Category:** Technical Debt / Visual Broadcast Compliance / Repo Bloat
* **Affected Components:**
  * `/home/ubuntu/apps/ugc-lemonaru/remotion/src/components/HookTitle.tsx`
  * `/home/ubuntu/apps/ugc-lemonaru/remotion/src/components/OutroCTA.tsx`
  * `/home/ubuntu/apps/ugc-lemonaru/` (Root repository naming and legacy UGC TikTok Shop structure)

#### Forensic Evidence
The `@DoniesDaily` codebase lives inside `/home/ubuntu/apps/ugc-lemonaru/`, a repository originally built for an Indonesian TikTok Shop / e-commerce affiliate UGC automation tool ("Lemonaru" / "Velora AI"). While the Python orchestration layer was adapted for feline educational Shorts, **hardcoded e-commerce defaults remain active inside the React Remotion visual components**:

1. **In `/home/ubuntu/apps/ugc-lemonaru/remotion/src/components/HookTitle.tsx` (Line 13):**
   ```tsx
   export const HookTitle: React.FC<HookTitleProps> = ({
     title,
     subtitle,
     badgeText = "🔥 RACUN TIKTOK OOTD",
   }) => {
   ```
2. **In `/home/ubuntu/apps/ugc-lemonaru/remotion/src/components/OutroCTA.tsx` (Lines 12–17):**
   ```tsx
   export const OutroCTA: React.FC<OutroCTAProps> = ({
     headline = "CHECKOUT SEKARANG!",
     subheadline = "⚡ Diskon Terbatas Hari Ini Saja",
     buttonText = "KLIK KERANJANG KUNING",
     startFromEndFrames = 100,
   }) => {
   ```
3. **In `/home/ubuntu/apps/ugc-lemonaru/remotion/src/DoniOverlay.tsx` (Line 17 & 26):**
   `DoniOverlay.tsx` imports `OutroCTA` and exposes `showOutroCTA: z.boolean().default(true)`. If `OutroCTA` is invoked without explicitly overriding `headline`, `subheadline`, and `buttonText`, the rendered cat video will display **"CHECKOUT SEKARANG! ⚡ Diskon Terbatas Hari Ini Saja — KLIK KERANJANG KUNING 👇"** in the final 3.3 seconds, directly violating **Hukum Besi #15** (*"Penutup Wajib CTA: Follow & Subscribe DoniesDaily"*).

#### Impact Analysis
* **Brand & Compliance Failure:** Any render invocation that omits explicit `OutroCTA` prop overrides injects TikTok Shop hard-sell e-commerce banners into an educational pet channel.
* **Cognitive & Tooling Confusion:** Autonomous agents inspecting the workspace directory structure (`ugc-lemonaru`) or reading default component schemas encounter conflicting domain contexts (OOTD fashion/affiliate vs. feline psychology).

---

### 🔴 RISK 2: Single Point of Failure (SPOF) on Local CLIProxyAPI (`:8317`) & Host Containers
* **Severity:** **CRITICAL**
* **Category:** Infrastructure Resilience / Network SPOF
* **Affected Components:**
  * `/home/ubuntu/tools/doni_working_hours_standup.py`
  * `/home/ubuntu/tools/doni_scriptwriter.py`
  * `/home/ubuntu/tools/doni_production_sprint.py`
  * `/home/ubuntu/tools/ingest_fahru_footage.py`
  * Docker container `supabase-db`

#### Forensic Evidence
Every cognitive agent across the squad relies on a single unclustered local reverse-proxy endpoint (`http://127.0.0.1:8317/v1/chat/completions`) routing to frontier models (`gemini-4-argon-high`, `claude-opus-5-5-high`, `claude-sonnet-5-5-high`, `gemini-3.8-flash-high`):

1. **In `/home/ubuntu/tools/doni_scriptwriter.py` (Lines 23–24, 151–157):**
   ```python
   API_URL = os.getenv("CPA_BASE_URL", "http://127.0.0.1:8317/v1/chat/completions")
   API_KEY = os.getenv("CPA_API_KEY", "cpa-secret-key-12345")
   ...
   resp = requests.post(API_URL, headers=headers, json=payload, timeout=90)
   raw = (resp.json()["choices"][0]["message"].get("content") or "").strip()
   ```
   *Note:* Unlike `doni_working_hours_standup.py` (which wraps `call_argon_high` in a `try/except` with a static `fallback_text`), `generate_autonomous_topic()` in `doni_scriptwriter.py` has **zero exception handling, zero exponential backoff, and zero fallback model routing**. If `:8317` returns a `502 Bad Gateway`, `429 Too Many Requests`, or times out, `resp.json()["choices"]` raises an unhandled `KeyError` or `requests.exceptions.ConnectionError`, crashing the entire sprint.
2. **Hardcoded Subprocess Docker Dependency:**
   Database queries across `doni_production_sprint.py`, `doni_scriptwriter.py`, and `doni_remotion_flow_pipeline.py` do not use a pooled Python PostgreSQL driver (`psycopg2` or `asyncpg`) with connection retries. Instead, they spawn raw OS shells via `docker exec -i supabase-db psql ...`:
   ```python
   cmd = ["docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-t", "-A", "-c", sql]
   ```

#### Impact Analysis
* If the local CLIProxyAPI daemon (`:8317`) hangs, restarts, or experiences upstream token rotation issues during the `08:04–08:56` or `18:04–18:56` sprint windows, Luna's script generation and Milo's Opus scene-cutting (`claude-opus-5-5-high`) crash immediately.
* Because `check_and_consume_jitter_window()` in `doni_production_sprint.py` (Lines 147–151) **marks the daily slot as `"fired": True` and writes it to `doni_daily_jitter.json` BEFORE executing the pipeline**, an unhandled crash in `:8317` or `supabase-db` permanently consumes the slot for that day, causing a **silent missed upload** despite the subsequent `*/5` cron ticks.

---

### 🟠 RISK 3: Chrome CDP Session Fragility (`:9222`) & Unattended UI Automation
* **Severity:** **HIGH**
* **Category:** Browser Automation / Authentication Persistence
* **Affected Components:**
  * `/home/ubuntu/apps/ugc-lemonaru/src/youtube_api_publisher.py` (`/home/ubuntu/tools/doni_oauth_auto_healer.py`)
  * `/home/ubuntu/apps/ugc-lemonaru/src/doni_remotion_flow_pipeline.py` (`src/flow_cdp_operator.py`)
  * `/home/ubuntu/tools/doni_evaluator.py` (Mochi YouTube Studio Advanced Mode scraper)
  * Persistent Profile: `/home/ubuntu/apps/ugc-lemonaru/data/chrome_persistent` on Xvfb `:99`

#### Forensic Evidence
The architecture relies on a single persistent Google Chrome instance running headless/Xvfb (`:99`) with Remote Debugging enabled on port `:9222` for three critical operations:
1. **OAuth Auto-Healing (`youtube_api_publisher.py`, Lines 48–51):**
   ```python
   except Exception as e:
       logger.warning(f"Standard token refresh failed ({e}). Running OAuth Auto-Healer via CDP...")
       import subprocess
       subprocess.run([sys.executable, "/home/ubuntu/tools/doni_oauth_auto_healer.py"], check=True)
   ```
2. **Google Flow AI Video Rendering (`doni_remotion_flow_pipeline.py`, Line 157):**
   ```python
   downloaded_clips = await self.flow_operator.generate_scenes(prompts, out_dir)
   ```
3. **YouTube Studio Advanced Mode Telemetry (`ActiveContext.md`):**
   Mochi scrapes `Stayed to watch %`, `Average View Duration`, and `Average Percentage Viewed %` directly from the YouTube Studio web UI via CDP `:9222`.

#### Impact Analysis
* **CDP Port Contention & Target Collisions:** If Mochi's analytics scraper (`doni_evaluator.py`), Milo's `FlowCDPOperator`, or `doni_oauth_auto_healer.py` attach to `:9222` concurrently, page navigation or tab closures in one script can sever the WebSocket target of another.
* **Google Session Invalidation & 2FA Challenges:** Google periodically invalidates persistent browser cookies or injects "Verify it's you" / 2FA prompts or CAPTCHAs on datacenter/VPS IP addresses. If the Chrome session expires, `doni_oauth_auto_healer.py` fails with `CalledProcessError`, and Mochi's Studio Advanced Mode scraping returns empty/null metrics.
* **Stale Fallback Pool in `doni_remotion_flow_pipeline.py` (Lines 163–165):**
   When `FlowCDPOperator` fails, `prepare_flow_scenes` falls back to hardcoded filenames:
   ```python
   stock_names = ["clip8_stock.mp4", "clip6_stock.mp4", "clip1_fight.mp4", "clip2_ball.mp4", "clip14_yawning.mp4"]
   ```
   However, per `ActiveContext.md` and **Hukum Besi #14**, the entire asset catalog was renamed to descriptive `asli_fahru_*` and `ai_gen_{cluster}_*` slugs! Falling back to `clip8_stock.mp4` either fails with file-not-found or violates the semantic naming and anti-repetition rules.

---

### 🔴 RISK 4: Hardware & Concurrency Choke on VPS (CPU / RAM / Ephemeral Disk Exhaustion)
* **Severity:** **CRITICAL**
* **Category:** Infrastructure Capacity / Resource Contention
* **Affected Components:**
  * Host VPS (2 vCPUs, 4GB RAM)
  * Persistent Chrome on Xvfb (`:99`) + Remotion Headless Chromium Bundler + Multi-input FFmpeg Filtergraphs + Supabase PostgreSQL Docker Stack + `/tmp/` ProRes 4444 Cache

#### Forensic Evidence
The VPS simultaneously hosts:
1. **Supabase Docker Stack** (`supabase-db` PostgreSQL + supporting containers).
2. **Persistent Google Chrome (`:9222`)** on Xvfb (`:99`) holding heavy DOM trees (YouTube Studio & Google Flow).
3. **Remotion React Renderer (`npx remotion render`):** Spawns its own headless Chromium instance and Node.js bundler to render 1,500–1,800 frames (50–60s @ 30fps) at `1080x1920` resolution with alpha-channel transparency (`ProRes 4444 .mov`).
4. **FFmpeg Multi-Stream Compositor:** Decodes 14–18 unique 1080p H.264 clips, applies `setpts` time-stretching, mixes 3 audio layers (Voiceover + Original/SFX + BGM with `dynaudnorm` and `ebur128`), and overlays the massive ProRes 4444 `.mov`.
5. **Delayed Ephemeral Purge Conflict (`ActiveContext.md` vs. PRD Rule #5):**
   * **PRD Rule #5 (Disk Hygiene):** *"File render overlay raksasa ProRes 4444 (`.mov` ~100-250MB) wajib langsung di-unlink dari `/tmp/` seketika render komposit MP4 tuntas."*
   * **`ActiveContext.md` (2026-11-06):** *"File ProRes 4444 (`/tmp/{topic}_remotion_overlay.mov`) di-cache saat render pertama... dan hanya dihapus otomatis dari disk setelah video terkonfirmasi live di YouTube Data API."*
   * If a video fails QC 3 times across multiple topics (the 3x retry loop in `doni_production_sprint.py`), multiple 250MB ProRes `.mov` files accumulate in `/tmp/` (which on many Ubuntu configurations is mounted on `tmpfs` backed by RAM/swap or a small root partition).
6. **Subprocess Timeout Ceiling (`ai_brain.cadence_tasks`):**
   ```json
   {"args": ["--jitter-window", "--slot", "morning"], "script": "/home/ubuntu/tools/doni_production_sprint.py", "timeout": 900}
   ```
   The cadence runner enforces a hard `900s` (15-minute) timeout on `doni_production_sprint.py`. However, `check_and_consume_jitter_window()` sleeps up to `49s` for micro-jitter, and if the 3x self-healing retry loop triggers across 2–3 topics on a throttled 2-vCPU machine, execution easily exceeds 15 minutes, causing the cadence runner to `SIGKILL` the sprint mid-render.

#### Impact Analysis
* **Linux Kernel OOM-Killer Invocation:** Running persistent Chrome (`~600–900MB`), Remotion's headless Chromium (`~800–1,200MB`), FFmpeg 1080p compositing (`~500MB`), and PostgreSQL (`~400MB`) simultaneously on a 4GB RAM machine pushes memory utilization past 100%, triggering the Linux OOM killer to abruptly terminate either Chromium, FFmpeg, or `supabase-db`.

---

### 🟠 RISK 5: ElevenLabs v4 API Cost & Character Quota Exhaustion
* **Severity:** **HIGH**
* **Category:** Third-Party API Cost / Financial & Operational Continuity
* **Affected Components:**
  * `/home/ubuntu/apps/ugc-lemonaru/src/doni_remotion_flow_pipeline.py` (`synthesize_audio_and_captions`)
  * `/home/ubuntu/apps/ugc-lemonaru/src/elevenlabs_tts.py`
  * `/home/ubuntu/apps/ugc-lemonaru/src/vivan_dataset_harvester.py`

#### Forensic Evidence
1. **Scale of Daily Consumption:**
   With the cadence expanded to **3 Long-Form Shorts per day** (`morning`, `midday_serial`, `evening`), each script contains 110–135 words (~800–1,000 characters including ElevenLabs v4 emotional tags `[curious]`, `[gasps]`, `[excited]`, plus the mandatory CTA suffix). That equates to ~3,000 characters/day (~90,000 characters/month) under zero-failure conditions.
2. **Topic Fallback Multiplier:**
   While `synthesize_audio_and_captions()` caches audio by `topic_key` (`if master_audio_path.exists() and captions_path.exists(): return ...`), `ActiveContext.md` notes that `doni_production_sprint.py` *"otomatis beralih ke topik berikutnya jika mentok"* (switches to a new topic if QC fails 3 times) and `doni_working_hours_standup.py` runs **twice daily** (`30 7,17 * * *`) generating new topics. Every new topic switch triggers a fresh ElevenLabs v4 API call.
3. **Unfinished Local Voice Sovereignty (`VIVAN_SOUL.md`):**
   `VIVAN_SOUL.md` documents the mitigation strategy: `src/vivan_dataset_harvester.py` slices 3–10s 24kHz mono WAVs + `.lab` transcripts into `assets/audio/vivan_dataset/` until reaching 150–200 clips (~20 minutes) for independent fine-tuning. Until that threshold is reached and deployed, if ElevenLabs returns `quota_exceeded` or `401/402 Payment Required`, there is **no automatic runtime failover** in `doni_remotion_flow_pipeline.py` to a local/secondary TTS engine.

#### Impact Analysis
* Exhausting the ElevenLabs character quota mid-month immediately halts all new video production across all 3 daily slots until manual billing top-up or local RVC/GPT-SoVITS/F5-TTS model cutover occurs.

---

### 🟠 RISK 6: YouTube Data API v3 Quota Ceiling & Cadence Contradictions
* **Severity:** **HIGH**
* **Category:** External API Rate Limits / Governance Drift
* **Affected Components:**
  * `/home/ubuntu/apps/ugc-lemonaru/src/youtube_api_publisher.py`
  * `/home/ubuntu/tools/doni_production_sprint.py`
  * `ai_brain.doniesdaily_learnings` (Rule ID #3)

#### Forensic Evidence
1. **YouTube Data API v3 Unit Math:**
   Google allocates a default quota of **10,000 units per day** (resets midnight Pacific Time) per Google Cloud Project:
   * `videos.insert` (`upload_short`): **1,600 units** per call.
   * `thumbnails.set` (`set_thumbnail`): **50 units** per call.
   * `commentThreads.list` / `comments.insert` (`doni_community_replier` running every 2 hours via `0 8-22/2 * * *` + `doniesdaily_sniper_logs`): **1 to 50 units** per call.
   * `search.list` (if used by comment sniper): **100 units** per call.
   * At 3 uploads/day (`3 * 1650 = 4,950 units`) plus 8 daily community replier/sniper runs and Mochi's analytics pulls, daily consumption sits at ~5,500–7,000 units. Any retry upload or manual re-upload (`doniesdaily_posts` shows multiple tests/uploads) pushes consumption dangerously close to the 10,000-unit cliff (hard cap of max 6 video uploads/day).
2. **Missing `uploadLimitExceeded` Catch in `doni_remotion_flow_pipeline.py` / `youtube_api_publisher.py`:**
   * `DONI_SOUL.md` (Section 2.2) states: *"Jika kuota habis (`uploadLimitExceeded`), Doni mengunci status ke `BLOCKED_QUOTA` (tunda 24 jam) tanpa menandai video sebagai cacat/failed."*
   * However, inspecting `youtube_api_publisher.py` (Lines 107–113) reveals **zero `try/except HttpError` handling around `request.next_chunk()`**! If YouTube throws a `403 quotaExceeded` or `uploadLimitExceeded` `HttpError`, `upload_short()` crashes with an uncaught exception rather than returning a structured `BLOCKED_QUOTA` state.

---

### 🟠 RISK 7: Cross-Channel Memory & Identity Contamination
* **Severity:** **HIGH**
* **Category:** Multi-Tenant Isolation / Brand Safety
* **Affected Components:**
  * `/home/ubuntu/vps-control-center/backend/data/agents_chat.db` (`agent_messages` & `agent_traces`)
  * `/home/ubuntu/tools/doni_working_hours_standup.py` (`post_swarm_chat`)
  * `/home/ubuntu/tools/doni_scriptwriter.py` (`post_swarm_chat`)

#### Forensic Evidence
1. **Shared SQLite Swarm Database Across Unrelated Holding Ventures:**
   The SQLite database `/home/ubuntu/vps-control-center/backend/data/agents_chat.db` is shared globally across all business units owned by Mas Fahru. The verified `SWARM MATRIX SQLITE CHAT STATS` dump confirms that agents from completely separate businesses read and write to the `all` channel in the same table:
   * `juragan-bawang` (*"B2B Pitch Specialist"*, *"Lead B2B Outreach & Retail Ops"*) -> `channel: "all"` and `"bawang"`.
   * `subtracker` (*"SubTracker Guard"*, *"SaaS Reseller & Billing Audit"*, *"Anomaly Detector"*) -> `channel: "all"` and `"subtracker"`.
   * `doniesdaily` (*"Doni"*, *"Luna"*, *"Milo"*, *"Cleo"*, *"Kak Ceria"*) -> `channel: "all"`, `"donies"`, and `"doniesdaily"`.
2. **Hardcoded `recipient_id = 'all'` Broadcasts:**
   In `doni_working_hours_standup.py` (Line 47) and `doni_scriptwriter.py` (Line 49):
   ```sql
   INSERT INTO agent_messages (id, sender_id, sender_name, sender_avatar, sender_role, recipient_id, recipient_name, content, timestamp, channel, status, created_at)
   VALUES (?, ?, ?, ?, ?, 'all', 'All Agents', ?, ?, ?, 'delivered', ?)
   ```
   Furthermore, the chat stats show `doniesdaily` subagents (`Luna`, `Milo`, `Kak Ceria`, `Cleo`, `Doni`) have posted **35+ messages directly into `channel = "all"`**, mixing cat litter/flehmen/belly-trap prompts with `juragan-bawang` B2B commodity outreach and `subtracker` SaaS billing audits.
3. **Hardcoded Personal & Channel Artifacts:**
   `OWNER_CHAT_ID = "1357517232"`, `asli_fahru_*` clip prefixes, and prompts referencing "Mas Fahru" are hardcoded across `/home/ubuntu/tools/doni_*.py`. If any global summarizer or cross-channel agent queries `WHERE channel = 'all'` or `WHERE recipient_id = 'all'`, feline slang ("Anabul", "Babu kucing") leaks directly into executive B2B contexts.

---

### 🔴 RISK 8: Severe Specification-to-Code & Database Rule Drift (Brain Split-Horizon)
* **Severity:** **CRITICAL**
* **Category:** Cognitive Coherence / Quality Control Integrity
* **Affected Components:**
  * `ai_brain.doniesdaily_learnings` (13 Active Rules)
  * `PRD_DONIESDAILY_MASTER_SPEC.md` vs. `CLEO_SOUL.md` vs. `/home/ubuntu/apps/ugc-lemonaru/src/doni_qc_gate.py`
  * `LUNA_SOUL.md` vs. `voice.md` vs. `/home/ubuntu/tools/doni_scriptwriter.py`

#### Forensic Evidence
An exhaustive cross-examination of the PostgreSQL learning ledger, agent Souls, PRD specifications, and Python enforcement gates reveals **severe internal contradictions** currently active in production:

#### Contradiction Matrix A: `ai_brain.doniesdaily_learnings` Append-Only Rule Collisions
In `doni_scriptwriter.py` (Lines 95–96), Luna fetches **all** `status = 'active'` rules from `ai_brain.doniesdaily_learnings` and injects all 13 of them simultaneously into a single LLM prompt (`rules_text = "\n".join(...)`). Because Mochi's daily standup appends new rules without deprecating superseded ones, **Luna is simultaneously commanded to obey mutually exclusive constraints**:

| Conflict Dimension | Active Rule A in PostgreSQL (`status = 'active'`) | Active Rule B in PostgreSQL / Code (`status = 'active'`) | Resulting Cognitive / Pipeline Failure |
| :--- | :--- | :--- | :--- |
| **Release Cadence** | **Rule #3 (`cadence_interval_gate`, conf 0.95):** *"Jeda rilis antar-video WAJIB minimal 20-24 jam (maksimal 1 video terkurasi per hari). Tolak upload jika video sebelumnya baru berumur < 20 jam."* | **`doni_production_sprint.py` (`MAX_DAILY_POSTS = 3`):** Runs 3 slots/day (`08:00`, `12:00`, `18:00` WIB — intervals of 4 to 6 hours). | Direct contradiction between DB learning ledger and active cron scheduler. |
| **Target Video Duration** | **Rule #5 (conf 0.98):** *"durasi optimal 55-63 detik"*<br>**Rule #2 & #12:** *"48-55 detik"* | **Rule #7 (conf 0.96):** *"Batasi total naskah maksimal 35-38 detik"*<br>**Rule #9 (conf 0.96):** *"Kunci durasi naskah di sweet-spot 30-38 detik (jangan lebih dari 45 detik)"*<br>**`doni_qc_gate.py` (Line 73):** Rejects `duration > 59.9s`! | Luna receives 5 different duration mandates (30–38s, 35–38s, 42–48s, 48–55s, 55–63s) in the same prompt. Worse: if Milo obeys Rule #5 (60–63s), **Cleo's `doni_qc_gate.py` hard-fails the video (`duration > 59.9`)**! |
| **Outro / CTA Structure** | **Rule #6 (conf 0.96):** *"potong semua kalimat kesimpulan/outro di 5 detik terakhir... tanpa layar penutup"*<br>**Rule #13 (conf 0.97):** *"potong habis outro statis di akhir video."* | **Hukum Besi #15 & `doni_qc_gate.py` (`audit_script_and_outro`, Line 154):** *"HUKUM BESI #15 VIOLATION: Naskah wajib menyertakan CTA penutup Follow/Subscribe DoniesDaily!"*<br>**`voice.md` (Line 23):** Bans *"Jangan lupa like, comment, and subscribe ya!"* | If Luna obeys Rule #6/#13 and cuts the outro, `doni_qc_gate.py` (`audit_script_and_outro`) **rejects the script as `QC_FAILED`**, or `doni_remotion_flow_pipeline.py` (Line 77) forcibly appends *"Jangan lupa follow dan subscribe DoniesDaily ya!"* anyway. |
| **Visual Cut Pacing** | **Rule #4 (`dynamic_semantic_cuts`, conf 0.80):** *"mengganti sudut pandang footage tiap 6-8 detik (minimal 4-6 klip per video)."* | **Hukum Besi #13 (`PRD` & `MILO_SOUL.md`):** *"Setiap cut visual wajib berganti setiap 3.2 – 4.0 detik... 14–17 adegan unik."* | Milo receives conflicting scene-cut pacing directives (6–8s vs. 3.2–4.0s). |

#### Contradiction Matrix B: Specification vs. Python Code Enforcement (`doni_qc_gate.py`)

| Parameter | Specification (`PRD` / `CLEO_SOUL.md`) | Actual Code (`src/doni_qc_gate.py`) | Gap / Vulnerability |
| :--- | :--- | :--- | :--- |
| **Audio-Video Sync Drift** | **PRD Section 4:** `assert dur_video >= dur_audio - 0.1`<br>**`CLEO_SOUL.md`:** Max drift `<= 0.5 detik`. | **Line 87:** `if delta > 1.5: report["passed"] = False` | Python gate allows up to **1.5 seconds** of audio cutoff or desync (3x looser than `CLEO_SOUL.md` and 15x looser than PRD Iron Guard). |
| **EBU R128 Integrated Loudness** | **`CLEO_SOUL.md`:** Mandatory **-14 LUFS to -19 LUFS** (`QC_FAILED` outside range). | **Lines 125–128:** Only logs a non-blocking `warning` if `il < -26.0` or `il > -8.0` (`report["passed"]` stays `True`!). | A video with heavily distorted `-8.5 LUFS` or barely audible `-25.0 LUFS` audio **passes `doni_qc_gate.py` with `passed: True`**. |
| **True Peak Clipping** | **`CLEO_SOUL.md`:** True Peak must not exceed **-1.0 dBFS**. | **Not implemented** in `doni_qc_gate.py` (regex only parses `I: ... LUFS`). | Audio clipping above `-1.0 dBFS` goes completely undetected. |
| **Cluster Deduplication (Hukum Besi #13)** | **PRD Rule #13:** Prohibited from selecting >1 scene from the same AI cluster folder (`cat_belly_trap_scratch/scene_1` and `scene_2`). | **`audit_footage_assembly()` (Lines 165–176):** Only checks exact file path string uniqueness (`set(clip_strs)`). | Two different files from the exact same AI render cluster pass `audit_footage_assembly()` without error. |

---

### 🔴 RISK 9: Credential Hygiene, Hardcoded Secrets & SQL Injection Vectors
* **Severity:** **CRITICAL**
* **Category:** Security / Access Control / Injection Vulnerability
* **Affected Components:**
  * `/home/ubuntu/tools/doni_working_hours_standup.py` (Line 147)
  * `/home/ubuntu/tools/doni_scriptwriter.py` (Line 24)
  * `/home/ubuntu/apps/ugc-lemonaru/src/doni_remotion_flow_pipeline.py` (Lines 56–60)
  * `/home/ubuntu/.config/youtube/doniesdaily_oauth.json`

#### Forensic Evidence
1. **Hardcoded Bearer Tokens & Personal Chat IDs in Source Code:**
   * `doni_working_hours_standup.py` (Line 147):
     ```python
     headers={"Content-Type": "application/json", "Authorization": "Bearer cpa-secret-key-12345"}
     ```
   * `doni_scriptwriter.py` (Line 24):
     ```python
     API_KEY = os.getenv("CPA_API_KEY", "cpa-secret-key-12345")
     ```
   * `OWNER_CHAT_ID = "1357517232"` is hardcoded in both `doni_production_sprint.py` (Line 34) and `doni_working_hours_standup.py` (Line 34).
2. **Unparameterized SQL String Interpolation (SQL Injection / Broken Query Vector):**
   In `doni_remotion_flow_pipeline.py` (Line 56):
   ```python
   sql = f"SELECT json_agg(t) FROM (SELECT topic_key, title, hook_banner, hook_subtitle, hook_vocal, full_script, flow_prompts, scene_breakdown, status FROM ai_brain.doniesdaily_content_ideas WHERE topic_key = '{topic_key}') t;"
   ```
   And across the pipeline when inserting LLM-generated Indonesian scripts, titles, or hook banners into PostgreSQL via `docker exec -i supabase-db psql -c "..."`: any unescaped single quote (`'`) in an LLM-generated string (or a malformed `topic_key`) breaks the SQL syntax or permits arbitrary SQL execution inside the `postgres` superuser context.
3. **Plaintext OAuth Token Storage (`doniesdaily_oauth.json`):**
   `/home/ubuntu/.config/youtube/doniesdaily_oauth.json` stores `client_id`, `client_secret`, `token`, and `refresh_token` in plaintext JSON on disk, and `doni_oauth_auto_healer.py` rewrites it automatically. Without strict `chmod 600` file permissions and `.gitignore` enforcement, cloning the workspace risks leaking full YouTube channel write/upload privileges.

---

### 🟡 RISK 10: State Machine Deadlocks, Split-Brain Tables & Race Conditions
* **Severity:** **MEDIUM** (Escalates to **HIGH** during unattended crash recovery)
* **Category:** State Management / Concurrency Control
* **Affected Components:**
  * `ai_brain.doniesdaily_content_ideas` vs. `ai_brain.doniesdaily_production_queue`
  * `/home/ubuntu/apps/ugc-lemonaru/data/doni_daily_jitter.json`
  * `/home/ubuntu/tools/doni_production_sprint.py`

#### Forensic Evidence
1. **Split-Brain State Machine (Two Competing Queue Tables):**
   * `DONI_SOUL.md` mandates managing state transitions in `ai_brain.doniesdaily_production_queue` (`IDEA_SELECTED` ➔ `SCRIPT_READY` ➔ `AUDIO_READY` ➔ `VISUAL_READY` ➔ `RENDER_READY` ➔ `QC_PASSED` ➔ `PUBLISHED`), and this table exists in PostgreSQL with `current_stage` and `retry_count`.
   * However, `doni_production_sprint.py` and `doni_remotion_flow_pipeline.py` (`fetch_next_topic`) **completely ignore `doniesdaily_production_queue`** and instead poll `ai_brain.doniesdaily_content_ideas WHERE status = 'ready' ORDER BY created_at ASC LIMIT 1`!
2. **Poison-Pill Head-of-Line Blocking (`ORDER BY created_at ASC LIMIT 1`):**
   Because `fetch_next_topic()` selects the oldest `'ready'` topic (`ORDER BY created_at ASC LIMIT 1`) without locking (`FOR UPDATE SKIP LOCKED`) or incrementing a `retry_count` column on `doniesdaily_content_ideas`:
   * If the oldest `'ready'` topic has a corrupted script, invalid characters, or fails after the sprint script exits, it **remains `status = 'ready'` at the very top of `ORDER BY created_at ASC`**.
   * On the next scheduled sprint slot (e.g., Evening 18:00 WIB), the pipeline fetches the exact same broken head-of-line topic first, wasting render cycles again.
3. **Premature Jitter State Consumption (`doni_production_sprint.py`, Lines 147–156):**
   ```python
   # Mark fired immediately before sleeping/rendering to prevent double-trigger across 5m ticks
   slot_cfg["fired"] = True
   slot_cfg["fired_at"] = now_jkt.strftime("%Y-%m-%d %H:%M:%S")
   state["slots"][slot_key] = slot_cfg
   JITTER_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
   ...
   time.sleep(target_sec)
   return True
   ```
   Because `fired = True` is persisted to disk **before** `time.sleep(target_sec)` and **before** the render/upload pipeline executes, if the process is killed during the sleep or crashes during Remotion rendering, the `*/5` cron job sees `fired == True` on subsequent ticks and refuses to retry, resulting in an unrecovered empty slot.

---

## 3. Mandatory Blockers for Virgin Master Template Cloning

Before attempting to extract and package this ecosystem into a clean, reusable **Virgin Master Template** (Deliverable 13) for deployment to new channels or niches, the following **5 Hard Blockers** MUST be resolved. Cloning the system in its current state will propagate broken defaults, hardcoded persona leaks, and contradictory database rules.

| Blocker ID | Linked Risk | Why It Blocks Virgin Template Cloning | Required Pre-Clone Resolution |
| :--- | :--- | :--- | :--- |
| **BLOCKER-1** | **Risk 1 (Legacy E-Commerce Defaults)** | `HookTitle.tsx` (`"🔥 RACUN TIKTOK OOTD"`) and `OutroCTA.tsx` (`"CHECKOUT SEKARANG!"`, `"KLIK KERANJANG KUNING"`) will inject TikTok Shop affiliate text into any new channel that uses default Remotion props. | Scrub all e-commerce strings from `remotion/src/components/*.tsx` and bind default props to a centralized `channel_brand_config.json`. |
| **BLOCKER-2** | **Risk 7 (Hardcoded Persona & Cross-Channel Leaks)** | Hardcoded strings (`@DoniesDaily`, `asli_fahru_*`, `OWNER_CHAT_ID = "1357517232"`, cat phonetic dictionaries, and global `channel = 'all'` SQLite writes) tightly couple the code to Mas Fahru's cat channel. | Extract all channel identity, niche vocabulary, phonetic maps, and Telegram/Matrix routing into environment-driven tenant configuration files; enforce strict `channel_id` scoping in `agents_chat.db`. |
| **BLOCKER-3** | **Risk 8 (Contradictory DB Rules & Spec Drift)** | Cloning the current `ai_brain.doniesdaily_learnings` seed data or `doni_qc_gate.py` transfers 13 mutually exclusive prompt rules (35s vs 60s, no-outro vs mandatory-CTA) and broken LUFS/drift assertions. | Reconcile `doni_qc_gate.py` with `CLEO_SOUL.md` (-14..-19 LUFS hard gate, <=0.5s drift, cluster dedup check) and implement category-keyed UPSERT (1 active rule per category) in the learning ledger. |
| **BLOCKER-4** | **Risk 9 (Hardcoded Secrets & Raw SQL Interpolation)** | Hardcoded `"Bearer cpa-secret-key-12345"`, hardcoded VPS paths (`/home/ubuntu/...`), and raw string-interpolated `docker exec psql` queries create severe security and portability failures on any new host. | Externalize all paths and secrets to `.env.example` / `pydantic-settings` and replace raw `psql` string interpolation with parameterized `psycopg2` queries. |
| **BLOCKER-5** | **Risk 10 (Split-Brain Queue & Non-Atomic Jitter Lock)** | Having both `doniesdaily_content_ideas` and an unused `doniesdaily_production_queue`, plus a non-atomic `fired = True` lock in `doni_daily_jitter.json`, guarantees silent dropped uploads on any crash. | Unify state tracking into a transactional state machine (`SELECT ... FOR UPDATE SKIP LOCKED`) with atomic lock acquisition (`LOCKED_RENDERING` ➔ `PUBLISHED` or `FAILED_RETRYABLE`). |

---

## 4. Concrete Mitigation & Hardening Blueprint

Below is the actionable, engineering-grade remediation blueprint for every identified risk, complete with architectural patterns and drop-in code specifications.

### 4.1 Remediating Risk 1 & Risk 7: Decoupling Legacy E-Commerce & Channel Identity
1. **Sanitize Remotion Components (`HookTitle.tsx` & `OutroCTA.tsx`):**
   Replace legacy TikTok Shop defaults in `/home/ubuntu/apps/ugc-lemonaru/remotion/src/components/OutroCTA.tsx` and `HookTitle.tsx` with neutral, brand-driven props:
   ```tsx
   // remotion/src/components/OutroCTA.tsx
   export const OutroCTA: React.FC<OutroCTAProps> = ({
     headline = "JANGAN LUPA SUBSCRIBE!",
     subheadline = "🐾 Fakta Unik Anabul Setiap Hari",
     buttonText = "FOLLOW & SUBSCRIBE @DONIESDAILY",
     startFromEndFrames = 100,
   }) => { ... }
   ```
2. **Enforce Tenant Isolation in `agents_chat.db`:**
   Update `post_swarm_chat()` across all `/home/ubuntu/tools/doni_*.py` scripts to forbid writing to `channel = 'all'` unless explicitly flagging a holding-level executive alert. Enforce `channel = os.getenv("SWARM_CHANNEL_ID", "donies")`.

### 4.2 Remediating Risk 2 & Risk 9: Resilient LLM Gateway Client & Parameterized DB Layer
1. **Centralized LLM Client with Exponential Backoff & Multi-Model Fallback:**
   Create `/home/ubuntu/apps/ugc-lemonaru/src/llm_client.py` and remove all hardcoded `"Bearer cpa-secret-key-12345"` strings:
   ```python
   import os, time, requests
   from typing import List, Dict, Any

   CPA_BASE_URL = os.environ["CPA_BASE_URL"]  # Fail fast if .env is missing
   CPA_API_KEY = os.environ["CPA_API_KEY"]

   def call_llm_resilient(
       messages: List[Dict[str, str]],
       primary_model: str = "claude-sonnet-5-5-high",
       fallback_models: List[str] = ["gemini-4-argon-high", "gemini-3.8-flash-high"],
       temperature: float = 0.5,
       timeout: int = 60,
   ) -> str:
       models_to_try = [primary_model] + [m for m in fallback_models if m != primary_model]
       headers = {"Authorization": f"Bearer {CPA_API_KEY}", "Content-Type": "application/json"}
       last_err = None

       for model in models_to_try:
           for attempt in range(1, 3):
               try:
                   resp = requests.post(
                       CPA_BASE_URL,
                       headers=headers,
                       json={"model": model, "messages": messages, "temperature": temperature},
                       timeout=timeout,
                   )
                   resp.raise_for_status()
                   content = resp.json()["choices"][0]["message"]["content"].strip()
                   if content:
                       return content
               except Exception as exc:
                   last_err = exc
                   time.sleep(2 ** attempt)
       raise RuntimeError(f"All LLM endpoints/fallbacks exhausted ({models_to_try}): {last_err}")
   ```
2. **Replace `docker exec psql` String Interpolation with Parameterized `psycopg2`:**
   Connect directly to PostgreSQL over localhost/Unix socket using parameterized queries (`cursor.execute("SELECT ... WHERE topic_key = %s", (topic_key,))`), eliminating SQL injection and subprocess spawn overhead.
3. **Lock Down Credential Permissions:**
   ```bash
   chmod 600 /home/ubuntu/.config/youtube/doniesdaily_oauth.json
   chmod 600 /home/ubuntu/apps/ugc-lemonaru/.env
   ```

### 4.3 Remediating Risk 3 & Risk 4: VPS Resource Serialization & Swap/Tmpfs Hardening
1. **Process-Level Mutex for Heavy Media & CDP Operations:**
   Use `fcntl.flock` on `/tmp/doni_media_render.lock` and `/tmp/doni_cdp_9222.lock` so that:
   * Mochi's CDP scraper (`doni_evaluator.py`) and Milo's `FlowCDPOperator` never manipulate Chrome `:9222` tabs simultaneously.
   * Remotion (`npx remotion render --concurrency=1`) runs with `--concurrency=1` (limiting headless Chromium render threads to 1 core on the 2-vCPU VPS) and suspends/minimizes background Chrome tabs before spawning.
2. **Disk & Memory Hygiene for ProRes 4444 Cache:**
   * Move cached ProRes 4444 `.mov` files out of `/tmp/` (if `/tmp` is `tmpfs` RAM-backed) into `/home/ubuntu/apps/ugc-lemonaru/output/.cache/` on the NVMe/SSD block device.
   * Enforce a strict TTL / max-count eviction policy: keep at most **1 cached `.mov` file** on disk (`rm -f output/.cache/*_remotion_overlay.mov` whenever a new topic begins rendering or immediately upon upload completion).
   * Ensure an 8GB Linux swapfile (`/swapfile`) is active with `vm.swappiness=10` to absorb transient Chromium + FFmpeg memory spikes without triggering the kernel OOM killer.

### 4.4 Remediating Risk 5 & Risk 6: Quota Circuit Breakers (ElevenLabs & YouTube API)
1. **YouTube `uploadLimitExceeded` / `quotaExceeded` Circuit Breaker (`youtube_api_publisher.py`):**
   Wrap `request.next_chunk()` in `googleapiclient.errors.HttpError` handling:
   ```python
   from googleapiclient.errors import HttpError

   try:
       while response is None:
           status, response = request.next_chunk()
   except HttpError as e:
       if e.resp.status in (400, 403) and ("quotaExceeded" in str(e) or "uploadLimitExceeded" in str(e)):
           logger.error("YouTube API Quota/Upload limit reached! Transitioning topic to BLOCKED_QUOTA.")
           return {"success": False, "error_code": "BLOCKED_QUOTA", "error": str(e)}
       raise
   ```
   When `doni_production_sprint.py` receives `error_code == "BLOCKED_QUOTA"`, it preserves the rendered `.mp4` master on disk, updates the queue state to `BLOCKED_QUOTA`, and halts further retries for 24 hours (satisfying `DONI_SOUL.md` Section 2.2).
2. **ElevenLabs Pre-Flight Quota Check & Vivan Dataset Cutover Readiness:**
   Query `GET https://api.elevenlabs.io/v1/user/subscription` before synthesis to check `character_count` vs. `character_limit`. If remaining characters `< 2,500`, alert Mas Fahru on Telegram immediately and switch to the local Vivan fine-tuned model (`src/custom_vivan_tts.py`).

### 4.5 Remediating Risk 8: Reconciling `doni_qc_gate.py` & Pruning Contradictory DB Learnings
1. **Deduplicate & Categorically Lock `ai_brain.doniesdaily_learnings`:**
   Instead of accumulating 8 conflicting `script_structure` rules (`id` 6 through 13) in `status = 'active'`, enforce a **Single Active Rule per Sub-Slot/Category** policy:
   ```sql
   -- Archive superseded conflicting rules so Luna only receives 1 coherent set of directives
   UPDATE ai_brain.doniesdaily_learnings
   SET status = 'superseded', updated_at = NOW()
   WHERE id IN (3, 4, 6, 7, 8, 9, 10, 11, 12);
   ```
   Modify Mochi's learning updater (`doni_evaluator.py`) to `UPDATE` or mark prior rules in the same `category` as `'superseded'` whenever a higher-confidence rule is committed, and validate that any new rule does not violate immutable **Hukum Besi #1–#15** (e.g., reject any learned rule that attempts to ban the mandatory Follow/Subscribe CTA or exceed 58 seconds).
2. **Harden `src/doni_qc_gate.py` to Match `CLEO_SOUL.md` & PRD Iron Guards:**
   * **Audio-Video Drift Tolerance:** Tighten `if delta > 1.5:` on Line 87 to `if delta > 0.5:` and enforce `if duration < raw_a_duration - 0.1: report["passed"] = False` (PRD Section 4 Anti-Cutoff Iron Guard).
   * **EBU R128 Loudness Gate:** Change Lines 125–128 from passive warnings to strict enforcement (`if not (-19.5 <= il <= -13.5): report["passed"] = False`) and parse `True peak: ... Peak: (-?[\d\.]+) dBFS` to enforce `peak <= -1.0`.
   * **Cluster-Level Deduplication (`audit_footage_assembly`):** Parse the cluster identifier from each clip path (`ai_gen_{cluster}_*` or parent folder) and fail QC if any two clips in a single video share the same AI generation cluster.

### 4.6 Remediating Risk 10: Atomic State Machine & Two-Phase Jitter Commit
1. **Two-Phase Jitter State Commit (`doni_production_sprint.py`):**
   Do not mark `slot_cfg["fired"] = True` permanently before rendering. Instead:
   * Set `slot_cfg["status"] = "IN_PROGRESS"` with `locked_at = time.time()` during execution so concurrent 5-minute cron ticks skip while the render is actively running.
   * Only set `slot_cfg["fired"] = True` **after** the video is confirmed `published` (or `BLOCKED_QUOTA`).
   * If `status == "IN_PROGRESS"` is older than `900s` (stale crash lock), allow the next 5-minute cron tick within the hour to automatically recover and complete the slot.
2. **Unify Queue State Tracking:**
   Add `retry_count INT DEFAULT 0` and `last_error TEXT` to `ai_brain.doniesdaily_content_ideas` (or route all sprints through `ai_brain.doniesdaily_production_queue`), selecting topics via:
   ```sql
   SELECT * FROM ai_brain.doniesdaily_content_ideas
   WHERE status = 'ready' AND COALESCE(retry_count, 0) < 3
   ORDER BY retry_count ASC, created_at ASC
   LIMIT 1
   FOR UPDATE SKIP LOCKED;
   ```
   This guarantees poison-pill topics are automatically demoted after 3 failures and never block subsequent daily sprints.

---

## 5. Summary Audit Ledger of Identified Risks

| Risk ID | Risk Title | Severity | Primary Evidence Location | Virgin Template Blocker? |
| :--- | :--- | :--- | :--- | :--- |
| **RISK-01** | Legacy Code Entanglement (`ugc-lemonaru` / TikTok Shop props) | 🔴 **CRITICAL** / **HIGH** | `remotion/src/components/OutroCTA.tsx`, `HookTitle.tsx` | **YES (BLOCKER-1)** |
| **RISK-02** | SPOF on Local CLIProxyAPI (`:8317`) & Unhandled LLM Timeouts | 🔴 **CRITICAL** | `tools/doni_scriptwriter.py:23`, `doni_working_hours_standup.py:147` | No (Infra Hardening) |
| **RISK-03** | Chrome CDP (`:9222`) Session Fragility & Stale Stock Fallback | 🟠 **HIGH** | `src/youtube_api_publisher.py:48`, `src/doni_remotion_flow_pipeline.py:164` | No (Runtime Hardening) |
| **RISK-04** | VPS Hardware (2 vCPU / 4GB RAM) OOM Choke & `/tmp` ProRes Bloat | 🔴 **CRITICAL** | `ActiveContext.md` (ProRes cache), `cadence_tasks` (`timeout: 900`) | No (Infra Hardening) |
| **RISK-05** | ElevenLabs v4 Character Quota Drain & Unfinished Local Fallback | 🟠 **HIGH** | `src/doni_remotion_flow_pipeline.py:95`, `souls/VIVAN_SOUL.md` | No (Cost Guard) |
| **RISK-06** | YouTube Data API Quota Ceiling & Missing `HttpError` Catch | 🟠 **HIGH** | `src/youtube_api_publisher.py:107`, `souls/DONI_SOUL.md` | No (API Guard) |
| **RISK-07** | Cross-Channel Memory & Identity Contamination in `agents_chat.db` | 🟠 **HIGH** | `agents_chat.db` (`channel='all'`), `tools/doni_working_hours_standup.py:47` | **YES (BLOCKER-2)** |
| **RISK-08** | Spec-to-Code Drift (`doni_qc_gate.py`) & 13 Conflicting DB Rules | 🔴 **CRITICAL** | `ai_brain.doniesdaily_learnings`, `src/doni_qc_gate.py:87,125` | **YES (BLOCKER-3)** |
| **RISK-09** | Hardcoded Bearer Tokens, Plaintext OAuth & Raw SQL Interpolation | 🔴 **CRITICAL** | `src/doni_remotion_flow_pipeline.py:56`, `tools/doni_scriptwriter.py:24` | **YES (BLOCKER-4)** |
| **RISK-10** | Split-Brain Queue Tables, Head-of-Line Blocking & Premature Jitter Lock | 🟡 **MEDIUM** | `tools/doni_production_sprint.py:147`, `doniesdaily_production_queue` | **YES (BLOCKER-5)** |