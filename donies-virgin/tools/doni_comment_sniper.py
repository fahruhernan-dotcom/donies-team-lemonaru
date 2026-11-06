#!/usr/bin/env python3
"""
Doni Comment Sniper 🎯 — Autonomous High-Engagement Tactical Commenter for @DoniesDaily
Searches trending/recent Indonesian cat Shorts and leaves witty, highly-relatable cat-lover comments
to drive organic profile traffic and subscriber conversion.
"""
import os
import sys
import json
import random
import requests
import argparse
from pathlib import Path
from datetime import datetime, timezone
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

OAUTH_FILE = Path("/home/ubuntu/.config/youtube/virgin_oauth_token.json")
MY_CHANNEL_ID = "UC_VIRGIN_CHANNEL_ID_PLACEHOLDER"
CLIPROXY_URL = "http://127.0.0.1:8317/v1/chat/completions"

SEARCH_QUERIES = [
    "kucing lucu shorts",
    "tingkah anabul shorts",
    "kucing oren bar bar shorts",
    "lucunya anabul shorts",
    "kucing ngambek shorts",
    "fakta anabul shorts",
    "kucing gemoy shorts"
]

def get_youtube_client():
    if not OAUTH_FILE.exists():
        raise FileNotFoundError(f"OAuth file not found: {OAUTH_FILE}")
    with open(OAUTH_FILE, "r") as f:
        data = json.load(f)
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes")
    )
    return build("youtube", "v3", credentials=creds)

def get_already_commented_video_ids():
    import subprocess
    cmd = [
        "docker", "exec", "-i", "supabase-db",
        "psql", "-U", "postgres", "-d", "postgres", "-t", "-A",
        "-c", "SELECT video_id FROM ai_brain.virgin_sniper_logs;"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return set(line.strip() for line in res.stdout.splitlines() if line.strip())
    except Exception as e:
        print(f"Warning: could not query DB for logs: {e}")
        return set()

def record_comment_log(video_id, video_title, channel_title, comment_text, comment_id):
    import subprocess
    clean_title = video_title.replace("'", "''")
    clean_channel = channel_title.replace("'", "''")
    clean_text = comment_text.replace("'", "''")
    sql = f"""
    INSERT INTO ai_brain.virgin_sniper_logs (video_id, video_title, channel_title, comment_text, comment_id)
    VALUES ('{video_id}', '{clean_title}', '{clean_channel}', '{clean_text}', '{comment_id}')
    ON CONFLICT (video_id) DO NOTHING;
    """
    subprocess.run([
        "docker", "exec", "-i", "supabase-db",
        "psql", "-U", "postgres", "-d", "postgres", "-c", sql
    ], capture_output=True, text=True)

def generate_witty_comment(video_title: str, channel_title: str) -> str:
    """Uses LLM to craft a witty, natural, highly-upvotable cat-lover comment."""
    prompt = f"""Kamu adalah persona Doni dari kanal YouTube DoniesDaily (seorang pecinta anabul kocak, pinter, dan sangat relate sama kelakuan kucing).
Tulis 1 komentar pendek (1-2 kalimat saja, maks 20 kata) berbahasa Indonesia gaul santai untuk video Shorts berikut:
Judul Video: "{video_title}"
Nama Channel: "{channel_title}"

ATURAN MUTLAK:
- JANGAN PERNAH minta subscribe atau promosi channel secara langsung (dilarang bilang 'mampir ya', 'sub balik', 'cek channelku')!
- Komentar harus bikin penonton lain ngakak, tersenyum, atau merasa "fix bener banget!", sehingga komentar ini di-upvote banyak orang dan di-pin oleh kreator.
- Boleh sisipkan fakta anabul super mini atau jokes relate babu kucing.
- Gunakan 1-2 emoji kucing/tawa yang pas (contoh: 😭, 🐾, 😹, 🐱).
- Balas HANYA teks komentarnya saja, tanpa tanda kutip pembuka/penutup."""

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer cpa-secret-key-12345"
    }
    payload = {
        "model": "gemini-4-argon-high",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 100
    }
    try:
        resp = requests.post(CLIPROXY_URL, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"].strip()
            # Bersihkan tanda kutip
            content = content.strip("\"'")
            if content:
                return content
    except Exception as e:
        print(f"LLM comment gen error: {e}")

    # Fallback pool jika LLM tidak merespons
    fallbacks = [
        "Definisi sebenarnya dari penguasa rumah tangga, kita babu cuma bisa pasrah 😭🐾",
        "Tatapannya itu lho, kayak lagi nge-judge seluruh keputusan hidup kita 😹",
        "Anabul kalau udah mode begini gak ada obatnya, gemoy banget tapi bikin elus dada 🐱✨",
        "Fix, di kepalanya cuma ada rencana menguasai dunia dan camilan basah 😭🐾",
        "Muka tanpa dosa tapi kelakuan di luar nalar, khas anabul kesayangan 😹"
    ]
    return random.choice(fallbacks)

def run_sniper(target_count: int = 3, dry_run: bool = False):
    print("=" * 60)
    print("🎯 DONI COMMENT SNIPER — GUERILLA SUBSCRIBER GROWTH ENGINE")
    print(f"Target comments: {target_count} | Dry-run: {dry_run}")
    print("=" * 60)

    yt = get_youtube_client()
    already_done = get_already_commented_video_ids()
    print(f"Found {len(already_done)} already commented videos in database.")

    query = random.choice(SEARCH_QUERIES)
    print(f"Searching YouTube Shorts for query: '{query}'...")

    search_resp = yt.search().list(
        q=query,
        part="snippet",
        type="video",
        videoDuration="short",
        order="relevance",
        maxResults=20
    ).execute()

    items = search_resp.get("items", [])
    print(f"Retrieved {len(items)} videos from YouTube search.")

    success_count = 0
    for item in items:
        if success_count >= target_count:
            break

        v_id = item["id"]["videoId"]
        snippet = item["snippet"]
        v_title = snippet["title"]
        ch_title = snippet["channelTitle"]
        ch_id = snippet["channelId"]

        if ch_id == MY_CHANNEL_ID:
            continue
        if v_id in already_done:
            continue

        print(f"\n🎯 [Target Found] {v_title} (by {ch_title})")
        comment_text = generate_witty_comment(v_title, ch_title)
        print(f"💬 Generated Comment: \"{comment_text}\"")

        if dry_run:
            print("   [DRY-RUN] Comment not submitted.")
            success_count += 1
            continue

        try:
            insert_resp = yt.commentThreads().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": v_id,
                        "topLevelComment": {
                            "snippet": {
                                "textOriginal": comment_text
                            }
                        }
                    }
                }
            ).execute()
            c_id = insert_resp.get("id", "")
            print(f"   ✅ Comment posted successfully! Comment ID: {c_id}")
            record_comment_log(v_id, v_title, ch_title, comment_text, c_id)
            already_done.add(v_id)
            success_count += 1
        except Exception as e:
            print(f"   ❌ Failed to post comment on video {v_id}: {e}")

    print("\n" + "=" * 60)
    print(f"🏁 Sniper run complete! Successfully posted {success_count}/{target_count} comments.")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Doni Comment Sniper")
    parser.add_argument("--count", type=int, default=3, help="Number of comments to post")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without posting")
    args = parser.parse_args()

    run_sniper(target_count=args.count, dry_run=args.dry_run)
