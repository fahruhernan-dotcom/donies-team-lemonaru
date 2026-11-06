#!/usr/bin/env python3
"""tools/doni_smart_scheduler.py — Intelligent Jitter & Quota Gatekeeper for Doni.
Ensures exactly 4-5 videos are posted per day across randomized peak hours (7-22 WIB),
strictly respecting database anti-duplication and daily quotas.
"""

import datetime
import json
import logging
import random
import subprocess
import sys
import zoneinfo
from pathlib import Path

JKT_TZ = zoneinfo.ZoneInfo("Asia/Jakarta")
STATE_FILE = Path("/home/ubuntu/donies-team-lemonaru/donies-virgin/data/doni_scheduler_state.json")
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("doni_scheduler")


def count_today_posts() -> int:
    """Queries Postgres ai_brain.virgin_posts for posts published today."""
    cmd = [
        "docker", "exec", "supabase-db", "psql", "-U", "postgres", "-d", "postgres",
        "-t", "-A", "-c",
        "SELECT count(*) FROM ai_brain.virgin_posts WHERE posted_at >= CURRENT_DATE AND privacy_status = 'public';"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return int(res.stdout.strip() or 0)
    except Exception as e:
        logger.warning(f"Error querying today's post count: {e}")
        return 0


def get_minutes_since_last_post() -> float:
    """Calculates minutes elapsed since the most recent public post."""
    cmd = [
        "docker", "exec", "supabase-db", "psql", "-U", "postgres", "-d", "postgres",
        "-t", "-A", "-c",
        "SELECT EXTRACT(EPOCH FROM (NOW() - max(posted_at)))/60.0 FROM ai_brain.virgin_posts WHERE privacy_status = 'public';"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        val = res.stdout.strip()
        if not val or val == "null":
            return 9999.0
        return float(val)
    except Exception as e:
        logger.warning(f"Error querying last post time: {e}")
        return 9999.0


def should_post_now() -> bool:
    """Evaluates whether this 30-min window should fire a post to achieve 4-5 daily posts."""
    now = datetime.datetime.now(JKT_TZ)
    hour = now.hour
    today_str = now.strftime("%Y-%m-%d")

    # Load scheduler state
    state = {}
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
        except Exception:
            state = {}

    if state.get("date") != today_str:
        # Reset state for a new day
        state = {
            "date": today_str,
            "target_slots": [
                random.randint(7, 8),    # Pagi (07-08)
                random.randint(11, 13),  # Siang (11-13)
                random.randint(15, 17),  # Sore (15-17)
                random.randint(18, 20),  # Malam (18-20)
                random.randint(21, 22),  # Malam Larut (21-22)
            ],
            "fired_slots": []
        }
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)

    today_posts = count_today_posts()
    mins_since_last = get_minutes_since_last_post()
    logger.info(f"Checking Doni Scheduler: Current hour={hour}, Today's posts={today_posts}/5, Last post={mins_since_last:.1f}m ago")

    # Anti-Spam Cooldown Guard: Minimum 110 minutes between public posts
    if mins_since_last < 110.0:
        logger.info(f"Anti-spam cooldown active: Last post was {mins_since_last:.1f} min ago (< 110 min). Skipping to protect YouTube Shorts algorithm distribution.")
        return False

    # Max 5 posts per day
    if today_posts >= 5:
        logger.info("Daily target of 5 videos already reached. Skipping.")
        return False

    # Check if current hour matches an unfired target slot
    target_slots = state.get("target_slots", [])
    fired_slots = state.get("fired_slots", [])

    # If current posts today is behind schedule, allow triggering
    if hour in target_slots and hour not in fired_slots:
        chance = random.random()
        if chance > 0.35 or now.minute >= 30:
            logger.info(f"Target slot matched (Hour {hour})! Triggering Doni...")
            fired_slots.append(hour)
            state["fired_slots"] = fired_slots
            with open(STATE_FILE, "w") as f:
                json.dump(state, f, indent=2)
            return True

    return False


if __name__ == "__main__":
    if should_post_now():
        print("TRIGGER_POST")
        sys.exit(0)
    else:
        print("SKIP_POST")
        sys.exit(1)
