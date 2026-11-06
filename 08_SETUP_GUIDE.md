# 🚀 DELIVERABLE 08: `SETUP_GUIDE.md`
## Onboarding & Setup Guide for a New Independent YouTube Channel

This guide explains how to take **Donies Virgin** and connect it to a completely new YouTube channel (e.g. Tech/AI, Finance, Stoic Philosophy, Gaming, or Fitness) in under 15 minutes.

---

### Step 1: Navigate to the Virgin Environment

```bash
cd /home/ubuntu/donies-team-lemonaru/donies-virgin
```

---

### Step 2: Configure Channel Identity (`config/channel_config.yaml`)

Open `config/channel_config.yaml` and customize the identity parameters:

```yaml
channel:
  id: "UC_YOUR_NEW_CHANNEL_ID"
  handle: "@YourChannelHandle"
  name: "Your Channel Name"
  url: "https://www.youtube.com/@YourChannelHandle"
  description: "High-retention Shorts powered by Donies Agentic Studio."

niche:
  primary_topic: "AI News & Future Tech" # Example new niche
  sub_topics:
    - "Autonomous AI Agents"
    - "Robotics Breakthroughs"
    - "Silicon Valley Leaks"
  target_audience: "Tech enthusiasts, developers, entrepreneurs (20-40)"
  language: "id-ID"
  slang_register: "Tech savvy, santai, to-the-point"

content_rules:
  cta:
    verbal: "Follow dan subscribe buat update AI tercepat!"
    visual_title: "SUBSCRIBE"
    visual_subtitle: "Update AI Setiap Hari!"

voice_identity:
  voice_id: "YOUR_ELEVENLABS_VOICE_ID" # Custom ElevenLabs voice
  loudness_target_lufs: -14.5
```

---

### Step 3: Configure Environment Variables

Copy the example environment file and add the required credentials:

```bash
cp config/.env.example config/.env
nano config/.env
```

Set:
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key.
- `VIRGIN_YOUTUBE_CLIENT_SECRETS`: Path to Google Cloud OAuth client secrets JSON.
- `VIRGIN_YOUTUBE_OAUTH_TOKEN`: Destination path for saved user token.

---

### Step 4: Initialize Isolated Database Tables

Run the automated initializer:

```bash
python3 database/init_virgin_db.py
```

This creates the isolated tables:
- `ai_brain.virgin_posts`
- `ai_brain.virgin_content_ideas`
- `ai_brain.virgin_production_queue`
- `ai_brain.virgin_learnings`
- `ai_brain.virgin_metrics_history`
- `ai_brain.virgin_clip_usage`
- `ai_brain.virgin_sniper_logs`
- `data/virgin_agents_chat.db`

---

### Step 5: Populate B-Roll Footage Catalog

1. Deposit vertical (9:16) video clips into `data/media/`.
2. Add entries to `data/assets_catalog.json` describing each clip:
```json
[
  {
    "filename": "robot_walking_lab.mp4",
    "video_path": "data/media/robot_walking_lab.mp4",
    "source_type": "channel_authentic",
    "duration_sec": 8.5,
    "dimensions": [1080, 1920],
    "description": "Humanoid robot walking in lab setting.",
    "energy_level": "high",
    "camera_movement": "tracking",
    "tags": ["robot", "ai", "hardware", "lab"],
    "usage_count": 0,
    "last_used_at": null
  }
]
```

---

### Step 6: Authenticate YouTube Data API v3

Generate the OAuth token for the new YouTube channel:

```bash
python3 -c "
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(
    'config/virgin_client_secrets.json',
    scopes=['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly']
)
creds = flow.run_local_server(port=0)
with open('config/virgin_oauth_token.json', 'w') as f:
    f.write(creds.to_json())
print('✅ YouTube OAuth token generated successfully!')
"
```

---

### Step 7: Run Parity & Isolation Verification

Run the automated test suite to ensure all gates and databases are operational:

```bash
python3 tests/test_virgin_parity.py
```

Expected result: `🎉 ALL 5 PARITY & ISOLATION TESTS PASSED WITH 100% SUCCESS!`

---

### Step 8: Trigger Production

To run an autonomous sprint for the new channel:

```bash
python3 tools/doni_production_sprint.py
```

The system will:
1. Consult `ai_brain.virgin_learnings` and `virgin_content_ideas`.
2. Luna writes a script with your new niche's CTA.
3. Vivan synthesizes audio via your custom voice.
4. Milo cuts B-roll from your `assets_catalog.json`.
5. Remotion renders the kinetic overlay.
6. Cleo audits resolution, duration, and LUFS.
7. YouTubeAPIPublisher uploads to your new channel.
8. Telemetry logs to `ai_brain.virgin_posts`.
