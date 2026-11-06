# 📦 DELIVERABLE 05: `DEPENDENCY_MANIFEST.md`
## Complete Infrastructure, Runtime & Package Dependencies

**Clone Target:** DONIES VIRGIN (`donies-virgin/`)  
**Operating Environment:** Ubuntu 24.04 LTS (x86_64, Linux Kernel 6.8+)  

---

### 1. Host Infrastructure & System Utilities

| Dependency | Required Version / Spec | Purpose in System | Verification Command |
| :--- | :--- | :--- | :--- |
| **Node.js** | `v22.13.0+` (Installed: `v22.23.4`) | Remotion React video rendering runtime | `node -v` |
| **Python** | `3.10+` (Installed: `3.12.3`) | Multi-agent orchestration, tools, and DB runners | `python3 --version` |
| **FFmpeg** | `6.1+` with `libx264`, `aac` | Video multiplexing, loudness normalization, stream copy | `ffmpeg -version` |
| **ffprobe** | `6.1+` | Deterministic media stream probing, duration assert | `ffprobe -version` |
| **PostgreSQL** | `15+` (Docker: `supabase-db` v17.6) | Primary state queue, post history, and learnings store | `docker exec supabase-db psql --version` |
| **SQLite3** | `3.37+` | Local inter-agent Swarm Matrix (`virgin_agents_chat.db`) | `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"` |
| **Chromium** | Chrome CDP (Port `:9222`) | Autonomous YouTube Studio analytics scraping | `curl -s http://127.0.0.1:9222/json/version` |

---

### 2. Python Package Dependencies (`requirements.txt`)

```txt
requests>=2.31.0
httpx>=0.27.0
aiohttp>=3.9.0
psycopg2-binary>=2.9.9
pydantic>=2.0.0
python-dotenv>=1.0.0
pyyaml>=6.0.1
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
pillow>=10.0.0
imageio>=2.31.0
imageio-ffmpeg>=0.4.9
websockets>=12.0
```

---

### 3. Node.js & Remotion Dependencies (`remotion/package.json`)

```json
{
  "dependencies": {
    "@remotion/animation-utils": "4.0.537",
    "@remotion/cli": "4.0.537",
    "@remotion/layout-utils": "4.0.537",
    "@remotion/media-utils": "4.0.537",
    "@remotion/tailwind-v4": "4.0.537",
    "@remotion/transitions": "^4.0.537",
    "@remotion/zod-types": "4.0.537",
    "react": "19.2.3",
    "react-dom": "19.2.3",
    "remotion": "4.0.537",
    "tailwindcss": "4.0.0",
    "zod": "4.5.4"
  },
  "devDependencies": {
    "@remotion/captions": "4.0.537",
    "@types/react": "19.2.7",
    "typescript": "5.9.3"
  }
}
```

---

### 4. Font & Audio Media Assets

1. **Typography Assets:**
   - `TheBoldFont` (`remotion/public/theboldfont.ttf`): Used for Hook Banner and Outro CTA cards.
   - `Montserrat Bold` (Web font via Google Fonts): Used for Hormozi single-word-by-word kinetic captions.
2. **SFX Audio Arsenal (`remotion/public/sfx/`):**
   - 10 curated viral sound effects: `sfx_vine_boom.mp3`, `sfx_kaching_cash_register.mp3`, `sfx_taco_bell_bong.mp3`, `sfx_anime_wow.mp3`, `sfx_correct_ding.mp3`, `sfx_dry_fart_meme.mp3`, `sfx_akh_groan_fail.mp3`, `sfx_tindeck_toy_squeak.mp3`, `sfx_violin_screech_horror.mp3`, `sfx_yellow_undertale_chime.mp3`.

---

### 5. Local Service Endpoints & Port Binding

| Service Name | Host / Port | Role | Fallback / Behavior |
| :--- | :--- | :--- | :--- |
| **CLIProxyAPI Antigravity** | `http://127.0.0.1:8317` | Multi-model proxy routing to Argon, Sonnet, Opus | Direct API key via provider endpoint |
| **Chrome CDP** | `http://127.0.0.1:9222` | YouTube Studio Advanced Mode scraping | Fallback to official YouTube Analytics API v2 |
| **PostgreSQL** | `127.0.0.1:5432` | State persistence | Docker container `supabase-db` |
