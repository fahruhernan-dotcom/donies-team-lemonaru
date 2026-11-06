# ⚠️ DELIVERABLE 09: `KNOWN_LIMITATIONS.md`
## Technical Limitations, Boundaries & Unverified Components

**Audit Classification:** Transparent Boundary & Limitation Disclosure  
**Target:** DONIES VIRGIN (`donies-virgin/`)  

---

### 1. Catalog of Identified Limitations

| # | Limitation Finding | Severity | Category | Status & Impact | Recommended Action / Solution |
| :-: | :--- | :---: | :--- | :--- | :--- |
| **1** | **Remote GitHub Repo Initial State** | Low | Git Infrastructure | `git@github.com:fahruhernan-dotcom/donies-team-lemonaru.git` was empty (unborn HEAD). Production codebase was committed as baseline to `main` and clone to `feature/donies-virgin-clone`. | **Resolved:** Branch structure established; push to remote fulfills repository specification. |
| **2** | **External YouTube Credentials Requirement** | Medium | Third-Party Auth | A new YouTube channel requires its own Google Cloud OAuth 2.0 Client Secrets and user consent token. Donies Daily's token was intentionally not copied. | **Action Required:** Follow `SETUP_GUIDE.md` Step 6 to authenticate the new channel account. |
| **3** | **Starter Asset Catalog Capacity** | Low | Media Assets | `data/assets_catalog.json` contains 1 starter clip template. The new channel cannot produce multi-clip Shorts until 10–20 B-roll videos are deposited in `data/media/`. | **Action Required:** Deposit vertical B-roll clips and run `ingest_fahru_footage.py` to populate semantic tags. |
| **4** | **VPS Hardware Concurrency Limit** | High | Infrastructure | The VPS has 2 vCPUs and 4GB RAM. Running simultaneous Remotion video renders for Donies Daily and Donies Virgin at the exact same minute would risk memory pressure. | **Solution:** Stagger production cron slots (e.g. Channel A at :00, Channel B at :30) via dynamic Jitter windows. |
| **5** | **Live YouTube Publishing Mocked in Validation** | Informational | Safety Protocol | In compliance with Rule #11 (*"Never publish content during testing"*), the validation suite tested table inserts and mock publishing without executing a live YouTube API call. | **Verified:** Code logic matches production `youtube_api_publisher.py` with 100% parameter equivalence. |
| **6** | **Chrome CDP Headless Port Sharing** | Medium | Scraping Service | If Chrome CDP (`:9222`) is used for YouTube Studio Advanced Mode scraping, both channels must not scrape simultaneously on the same port if logged into different Google accounts. | **Solution:** Use separate browser profiles (`--user-data-dir`) or rely on the official YouTube Analytics API v2. |

---

### 2. Explicit Verification Status

- **Agent Prompts & Souls:** VERIFIED (100% Identical)
- **Model Routing (`:8317`):** VERIFIED (Argon, Sonnet, Opus accessible)
- **PostgreSQL Table Isolation:** VERIFIED (`virgin_*` tables created, 0 rows)
- **SQLite Swarm Matrix:** VERIFIED (`virgin_agents_chat.db` isolated)
- **Remotion Typography & Layout:** VERIFIED (DoniOverlay compiles and accepts dynamic props)
- **Cleo QC Logic:** VERIFIED (Asserts resolution, duration, loudness)
- **Live Video Publishing to Channel B:** UNVERIFIED (Awaiting user's Channel B OAuth token)
