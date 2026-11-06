"""
DONIES VIRGIN — Configuration Loader
Loads team_config.yaml, channel_config.yaml, and environment variables.
Provides single-source-of-truth configuration for all agents, database queries, and tools.
"""

import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "config"

# Load local .env if present
env_path = CONFIG_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

class VirginConfig:
    def __init__(self):
        self.team = load_yaml(CONFIG_DIR / "team_config.yaml")
        self.channel = load_yaml(CONFIG_DIR / "channel_config.yaml")
        
        # Database Table Names (Namespaced)
        pg_conf = self.channel.get("persistence", {}).get("postgres", {})
        self.schema = pg_conf.get("schema", "ai_brain")
        self.prefix = pg_conf.get("table_prefix", "virgin_")
        tables = pg_conf.get("tables", {})
        
        self.TABLE_POSTS = f"{self.schema}.{tables.get('posts', self.prefix + 'posts')}"
        self.TABLE_IDEAS = f"{self.schema}.{tables.get('ideas', self.prefix + 'content_ideas')}"
        self.TABLE_QUEUE = f"{self.schema}.{tables.get('queue', self.prefix + 'production_queue')}"
        self.TABLE_LEARNINGS = f"{self.schema}.{tables.get('learnings', self.prefix + 'learnings')}"
        self.TABLE_METRICS = f"{self.schema}.{tables.get('metrics', self.prefix + 'metrics_history')}"
        self.TABLE_CLIP_USAGE = f"{self.schema}.{tables.get('clip_usage', self.prefix + 'clip_usage')}"
        self.TABLE_SNIPER_LOGS = f"{self.schema}.{tables.get('sniper_logs', self.prefix + 'sniper_logs')}"
        
        # SQLite Swarm Matrix
        sq_conf = self.channel.get("persistence", {}).get("sqlite", {})
        self.SWARM_DB_PATH = str(BASE_DIR / sq_conf.get("swarm_db", "data/virgin_virgin_agents_chat.db"))
        self.SWARM_CHANNEL = sq_conf.get("channel", "virgin_studio")
        
        # Paths
        self.CATALOG_PATH = str(BASE_DIR / self.channel.get("integrations", {}).get("storage", {}).get("catalog_path", "data/assets_catalog.json"))
        self.OVERLAY_CACHE_DIR = self.channel.get("integrations", {}).get("storage", {}).get("cache_overlay_dir", "/tmp/virgin_overlays")
        self.OUTPUT_DIR = str(BASE_DIR / self.channel.get("integrations", {}).get("storage", {}).get("output_dir", "output/master_renders"))
        
        # YouTube Credentials
        yt_conf = self.channel.get("integrations", {}).get("youtube_oauth", {})
        self.YOUTUBE_CLIENT_SECRETS = str(BASE_DIR / yt_conf.get("client_secrets_path", "config/virgin_client_secrets.json"))
        self.YOUTUBE_OAUTH_TOKEN = str(BASE_DIR / yt_conf.get("oauth_token_path", "config/virgin_oauth_token.json"))
        self.CHANNEL_ID = self.channel.get("channel", {}).get("id", "")
        
        # Voice Settings
        v_conf = self.channel.get("voice_identity", {})
        self.VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", v_conf.get("voice_id", "21m00Tcm4TlvDq8ikWAM"))
        self.VOICE_MODEL = v_conf.get("model_id", "eleven_multilingual_v2")
        self.TARGET_LUFS = v_conf.get("loudness_target_lufs", -14.5)
        
        # Content & CTA Rules
        c_rules = self.channel.get("content_rules", {})
        self.MIN_WORDS = c_rules.get("script", {}).get("min_words", 108)
        self.MAX_WORDS = c_rules.get("script", {}).get("max_words", 124)
        self.MAX_DURATION = c_rules.get("script", {}).get("max_duration_sec", 58.5)
        self.CTA_VERBAL = c_rules.get("cta", {}).get("verbal", "Jangan lupa follow dan subscribe ya!")
        self.CTA_TITLE = c_rules.get("cta", {}).get("visual_title", "SUBSCRIBE")
        self.CTA_SUBTITLE = c_rules.get("cta", {}).get("visual_subtitle", "Dapatkan info seru setiap hari!")

# Global singleton instance
cfg = VirginConfig()
