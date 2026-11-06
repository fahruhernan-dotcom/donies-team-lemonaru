#!/usr/bin/env python3
"""
Mochi 📊 — Content Strategist & Feedback Engine for DoniesDaily
Reads performance metrics from YouTube Data & DB, discovers viral hooks,
and generates structured video topics for the production backlog.
"""
import os
import sys
import json
import subprocess
import requests
from typing import List, Dict, Any

API_URL = os.getenv("CPA_BASE_URL", "http://127.0.0.1:8317/v1/chat/completions")
API_KEY = os.getenv("CPA_API_KEY", "cpa-secret-key-12345")

STYLE_BIBLE = (
    "photorealistic 8k, vertical 9:16 smartphone aspect ratio, "
    "cinematic lighting, warm vibrant modern indoor living room, "
    "shallow depth of field, adorable expressive ginger tabby cat with white paws, "
    "no humans, no distorted anatomy, smooth fluid natural movement, high frame rate."
)

SOUL_PATH = os.path.expanduser("/home/ubuntu/apps/ugc-lemonaru/souls/MOCHI_SOUL.md")

def load_mochi_soul() -> str:
    if os.path.exists(SOUL_PATH):
        with open(SOUL_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "You are Mochi, Head of Analytics & Audience Psychology for @DoniesDaily."

def run_psql(sql: str) -> str:
    cmd = ["docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-c", sql]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return res.stdout

def get_top_posts(limit: int = 5) -> List[Dict[str, Any]]:
    cmd = [
        "docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres",
        "-t", "-A", "-F", "|", "-c",
        f"SELECT video_id, title, views_count, likes_count FROM ai_brain.doniesdaily_posts ORDER BY views_count DESC LIMIT {limit};"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    posts = []
    for line in res.stdout.strip().split("\n"):
        if line and "|" in line:
            parts = line.split("|")
            posts.append({
                "video_id": parts[0],
                "title": parts[1],
                "views": int(parts[2] or 0),
                "likes": int(parts[3] or 0)
            })
    return posts

def get_existing_topic_keys() -> List[str]:
    cmd = [
        "docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres",
        "-t", "-A", "-c",
        "SELECT topic_key FROM ai_brain.doniesdaily_content_ideas;"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return [k.strip() for k in res.stdout.strip().split("\n") if k.strip()]

def generate_viral_topics(count: int = 3) -> List[Dict[str, Any]]:
    top_posts = get_top_posts(5)
    existing_keys = get_existing_topic_keys()

    prompt = f"""
You are the Executive Content Strategist for @DoniesDaily YouTube Shorts channel (Indonesian cat humor & psychology).
Here are our top performing videos on YouTube Shorts:
{json.dumps(top_posts, indent=2)}

Existing topic keys already in the database (DO NOT DUPLICATE OR OVERLAP):
{json.dumps(existing_keys)}

Task:
Analyze why our top shorts perform well (curiosity gap, relatable cat behaviors, emotional bonding).
Generate EXACTLY {count} NEW, high-probability viral video concepts in Indonesian.
For each concept, produce a full production package:
1. "topic_key": snake_case slug (unique, not in existing keys)
2. "title": catchy YouTube title with emoji & #Shorts (UPPERCASE)
3. "hook_banner": punchy text for 0-3s top banner (UPPERCASE)
4. "hook_vocal": spoken opening line for voiceover Kak Ceria (first 3 seconds)
5. "full_script": complete 40-50 word voiceover script (Indonesian, warm, witty, interactive ending)
6. "scene_breakdown": array of 5 scene objects:
   [{{"scene": 1, "focus": "...", "action": "...", "camera": "...", "seconds": "00:00 - 00:08"}}]
7. "flow_prompts": array of 5 objects for Google Flow video generation:
   [{{"prompt_id": 1, "aspect_ratio": "9:16", "text": "High detail prompt ending with: {STYLE_BIBLE}"}}]

Output MUST be a strict raw JSON array of objects. Do not include markdown or backticks.
"""

    mochi_soul = load_mochi_soul()
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gemini-4-argon-high",
        "messages": [
            {"role": "system", "content": f"{mochi_soul}\nYou are Mochi, a master YouTube Shorts strategist. You return valid raw JSON strictly adhering to schema."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=90)
    if resp.status_code != 200:
        raise RuntimeError(f"Strategist call failed: {resp.status_code} - {resp.text}")

    raw = resp.json()["choices"][0]["message"]["content"].strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

    ideas = json.loads(raw)
    return ideas

def commit_topics_to_db(topics: List[Dict[str, Any]]):
    for t in topics:
        topic_key = t["topic_key"].replace("'", "''")
        title = t["title"].replace("'", "''")
        hook_banner = t["hook_banner"].replace("'", "''")
        hook_vocal = t["hook_vocal"].replace("'", "''")
        full_script = t["full_script"].replace("'", "''")
        scene_json = json.dumps(t["scene_breakdown"]).replace("'", "''")
        flow_json = json.dumps(t["flow_prompts"]).replace("'", "''")

        sql = f"""
        INSERT INTO ai_brain.doniesdaily_content_ideas 
        (topic_key, title, hook_banner, hook_vocal, full_script, scene_breakdown, flow_prompts, status)
        VALUES (
            '{topic_key}',
            '{title}',
            '{hook_banner}',
            '{hook_vocal}',
            '{full_script}',
            '{scene_json}'::jsonb,
            '{flow_json}'::jsonb,
            'ready'
        )
        ON CONFLICT (topic_key) DO UPDATE SET
            title = EXCLUDED.title,
            hook_banner = EXCLUDED.hook_banner,
            full_script = EXCLUDED.full_script,
            updated_at = NOW();
        """
        run_psql(sql)
        print(f"✓ Committed topic: [{topic_key}] {title}")

if __name__ == "__main__":
    commit = "--commit" in sys.argv
    count = 3
    for arg in sys.argv[1:]:
        if arg.startswith("--count="):
            count = int(arg.split("=")[1])

    print(f"Running DoniesDaily Content Strategist (target: {count} topics, commit={commit})...")
    topics = generate_viral_topics(count)
    print(f"\nGenerated {len(topics)} topics:")
    for i, t in enumerate(topics, 1):
        print(f"{i}. [{t['topic_key']}] {t['title']}")
        print(f"   Hook: \"{t['hook_vocal']}\"")
        print(f"   Scenes: {len(t.get('scene_breakdown', []))} | Prompts: {len(t.get('flow_prompts', []))}")

    if commit:
        print("\nCommitting to PostgreSQL VPS `ai_brain.doniesdaily_content_ideas`...")
        commit_topics_to_db(topics)
        print("Done!")
    else:
        print("\n[DRY RUN] Pass --commit to write to database.")
