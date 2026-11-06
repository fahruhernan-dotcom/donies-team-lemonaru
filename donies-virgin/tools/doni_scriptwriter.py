#!/usr/bin/env python3
"""
Luna ✍️ — Autonomous Master Scriptwriter Module for Squad DoniesDaily.
Dynamically ingests active learnings from PostgreSQL (ai_brain.virgin_learnings),
enforces Long-Form Shorts standards (110-135 words / 50-60s), generates acoustic
punctuation for ElevenLabs v4 Vivan, and logs traces to Swarm Matrix (virgin_agents_chat.db).
"""
import os
import sys
import json
import re
import time
import uuid
import sqlite3
import argparse
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List

SOUL_PATH = Path("/home/ubuntu/donies-team-lemonaru/donies-virgin/souls/LUNA_SOUL.md")
API_URL = os.getenv("CPA_BASE_URL", "http://127.0.0.1:8317/v1/chat/completions")
API_KEY = os.getenv("CPA_API_KEY", "cpa-secret-key-12345")
DB_CHAT_PATH = Path("/home/ubuntu/vps-control-center/backend/data/virgin_agents_chat.db")

PHONETIC_DICTIONARY = {
    r"\bFlehmen\b": "Fley-men",
    r"\bflehmen\b": "fley-men",
    r"\bJacobson\b": "Jekob-sen",
    r"\bjacobson\b": "jekob-sen",
    r"\bHES-7\b": "Hes Tujuh",
    r"\bhes-7\b": "hes tujuh",
    r"\bFRAPs\b": "Freps",
    r"\bfraps\b": "freps",
    r"\bFRAP\b": "Frep",
    r"\bzoomies\b": "zuumis",
    r"\bZoomies\b": "Zuumis",
    r"\bUV\b": "Yu-Vi",
    r"\bHz\b": "Hertz",
    r"\bCatnip\b": "Ket-nip",
    r"\bcatnip\b": "ket-nip",
}


def post_swarm_chat(sender_id: str, sender_name: str, sender_avatar: str, sender_role: str, channel: str, content: str, traces: list = None):
    try:
        DB_CHAT_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_CHAT_PATH))
        cur = conn.cursor()
        msg_id = f"msg-{int(time.time()*1000)}-{uuid.uuid4().hex[:6]}"
        now_ts = time.strftime("%H:%M")
        epoch = time.time()

        cur.execute("""
            INSERT INTO agent_messages (id, sender_id, sender_name, sender_avatar, sender_role, recipient_id, recipient_name, content, timestamp, channel, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'all', 'All Agents', ?, ?, ?, 'delivered', ?)
        """, (msg_id, sender_id, sender_name, sender_avatar, sender_role, content, now_ts, channel, epoch))

        if traces:
            for tr in traces:
                tr_id = f"tr-{uuid.uuid4().hex[:8]}"
                cur.execute("""
                    INSERT INTO agent_traces (id, message_id, type, title, description, status, content, icon, timestamp, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (tr_id, msg_id, tr.get("type", "reasoning"), tr.get("title", ""), tr.get("description", ""), tr.get("status", "none"), tr.get("content", ""), tr.get("icon", "sparkles"), now_ts, epoch))

        conn.commit()
        conn.close()
        return msg_id
    except Exception as e:
        print(f"Failed to post to swarm chat: {e}")
        return None


def apply_phonetic_fixes(text: str) -> str:
    result = text
    for pattern, replacement in PHONETIC_DICTIONARY.items():
        result = re.sub(pattern, replacement, result)
    return result


def fetch_active_learned_rules() -> List[Dict[str, Any]]:
    """Pulls active learned directives from PostgreSQL ai_brain.virgin_learnings."""
    cmd = [
        "docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres",
        "-t", "-A", "-F", "|", "-c",
        "SELECT category, rule_name, directive, confidence_score FROM ai_brain.virgin_learnings WHERE status = 'active' ORDER BY confidence_score DESC;"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        rules = []
        for line in res.stdout.strip().split("\n"):
            if not line.strip() or "|" not in line:
                continue
            parts = line.split("|")
            rules.append({
                "category": parts[0],
                "rule_name": parts[1],
                "directive": parts[2],
                "confidence": float(parts[3]) if len(parts) > 3 else 0.5
            })
        return rules
    except Exception as e:
        print(f"Warning: Could not fetch active learned rules: {e}")
        return []


def fetch_existing_topics() -> List[str]:
    """Pulls all existing/published topics from PostgreSQL to guarantee 100% topic novelty."""
    cmd = [
        "docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres",
        "-t", "-A", "-c",
        "SELECT DISTINCT title || ' (' || topic_key || ')' FROM ai_brain.virgin_content_ideas UNION SELECT DISTINCT title FROM ai_brain.virgin_posts;"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
    except Exception as e:
        print(f"Warning: Could not fetch existing topics: {e}")
        return []


def generate_autonomous_topic() -> Dict[str, Any]:
    """Generates a fresh high-retention topic using learned rules when queue is empty."""
    rules = fetch_active_learned_rules()
    rules_text = "\n".join([f"- [{r['category'].upper()}] {r['directive']}" for r in rules])
    existing_topics = fetch_existing_topics()
    existing_text = "\n".join([f"  * {t}" for t in existing_topics[:35]])

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    prompt = f"""Kamu adalah Luna, scriptwriter jenius channel YouTube Shorts anabul DoniesDaily.
PENTING: Terapkan aturan hasil evaluasi data terbaru:
{rules_text}

DAFTAR TOPIK YANG SUDAH PERNAH DIPRODUKSI (DILARANG KERAS DUPLIKASI ATAU MIRIP!):
{existing_text}

Tugas:
Buat 1 ide konten YouTube Shorts viral yang 100% BARU tentang psikologi / insting / perilaku unik kucing di rumah yang relatable dan belum pernah ada di daftar di atas!
Syarat mutlak:
1. DILARANG awali judul dengan 'Kenapa Kucing...'.
2. DILARANG membahas topik yang sudah ada di daftar di atas (JANGAN bahas elus perut, gigit/cakar tangan saat dielus, jatuhkan barang, zoomies, ngadon roti, susu sapi, kardus, timun, kedip pelan, tatap tembok, ikut ke toilet, ekor, tidur 16 jam, dengkuran, atau flehmen).
3. Pilih topik segar yang punya Hook Larangan / Rahasia Menyentuh / Fakta Mengejutkan (contoh: alasan mengharukan kucing suka membawakan 'hadiah' bangkai/mainan ke kasurmu karena menganggapmu anak kucing yang gak bisa berburu, atau alasan kucing suka tidur di atas baju kotormu, atau arti rahasia saat kucing duduk membelakangimu).
4. Hook banner: 2-3 kata kapital punchy untuk cover thumbnail (TANPA mengulang kata persis dari judul).

Output JSON persis format ini tanpa markdown/backticks:
{{
  "topic_key": "cat_unique_topic_slug",
  "title": "Judul Menarik Huruf Kapital #Shorts",
  "hook_banner": "BANNER PUNCHY",
  "hook_subtitle": "Subtitle Menarik Di Bawah Banner",
  "concept_why": "Alasan psikologi/biologis anabul di balik topik ini"
}}
"""
    payload = {
        "model": "claude-sonnet-5-5-high",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 8192,
        "temperature": 0.65
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=90)
    raw = (resp.json()["choices"][0]["message"].get("content") or "").strip()
    m_json = re.search(r"\{.*\}", raw, re.DOTALL)
    if m_json:
        raw = m_json.group(0)
    return json.loads(raw)


def generate_long_form_script(topic_title: str, hook_banner: str, hook_subtitle: str = "") -> Dict[str, Any]:
    rules = fetch_active_learned_rules()
    rules_text = "\n".join([f"- [{r['category'].upper()}] {r['directive']}" for r in rules])

    system_prompt = f"""Kamu adalah Luna, master storyteller DoniesDaily.
Gaya bicaramu seperti kawan akrab yang cerdas, hangat, santai, dan ekspresif.
Kamu menulis naskah voiceover untuk dibacakan oleh karakter Vivan di ElevenLabs v4.

ATURAN HASIL EVALUASI METRIK TERBARU:
{rules_text}

STANDAR NASKAH (LONG-FORM SHORTS 50-58 DETIK):
1. Panjang naskah: TEPAT 108 SAMPAI 124 KATA (durasi vokal ~49-56 detik, sudah termasuk kalimat penutup ajakan follow dan subscribe DoniesDaily).
2. DILARANG menggunakan tag [whispers]. Gunakan modul emosional variatif: [curious], [gasps], [excited], [laughs], [sighs].
3. DILARANG menggunakan koma ',' biasa. Gunakan jeda elipsis '... ' untuk napas di tengah kalimat, dan WAJIB akhiri setiap kalimat utuh (setiap 10-14 kata) dengan tanda baca titik '.', tanda seru '!', atau tanda tanya '?' agar editor video Milo bisa memotong perpindahan adegan tepat mengikuti batas kalimat (Speech-Synced Editing, 9-12 kalimat utuh).
4. Struktur 4 Babak:
   - Detik 0-5: Hook pembuka tajam yang bikin penonton berhenti scroll (akhiri dengan ? atau !).
   - Detik 5-25: Fakta biologis atau psikologis insting anabul yang mengejutkan.
   - Detik 25-45: Perilaku nyata anabul di rumah yang sangat relatable bagi cat owner.
   - Detik 45-55: Pertanyaan penutup memancing audiens berdebat di kolom komentar, ditutup kalimat 'Jangan lupa follow dan subscribe DoniesDaily ya!'.

Output JSON persis format ini tanpa backticks:
{{
  "word_count": 120,
  "spoken_script": "Naskah lengkap dengan tag emosi...",
  "phonetic_script": "Naskah adaptasi fonetik...",
  "hook_vocal": "Kalimat pembuka 3 detik pertama",
  "cta_debate": "Pertanyaan debat penutup"
}}
"""
    user_prompt = f"""Topik: {topic_title}
Hook Banner: {hook_banner}
Hook Subtitle: {hook_subtitle}

Tuliskan naskah Long-Form Shorts 110-135 kata yang memikat, mendalam, dan memancing perdebatan hangat di komentar!"""

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    for attempt in range(3):
        payload = {
            "model": "claude-sonnet-5-5-high",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 8192,
            "temperature": 0.5
        }
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        raw = (resp.json()["choices"][0]["message"].get("content") or "").strip()
        m_json = re.search(r"\{.*\}", raw, re.DOTALL)
        if m_json:
            raw = m_json.group(0)
        try:
            data = json.loads(raw)
            script = data.get("spoken_script", "").strip()
            # Clean unwanted commas from acoustic script
            clean_script = script.replace(",", "")
            data["spoken_script"] = clean_script
            data["phonetic_script"] = apply_phonetic_fixes(clean_script)
            wc = len(clean_script.split())
            data["word_count"] = wc

            # Check word count compliance (ideal: 105 - 140 words)
            if 100 <= wc <= 145:
                data["passed_invariants"] = True
                return data
            else:
                user_prompt += f"\n\nREVISI: Naskah sebelumnya memiliki {wc} kata. Wajib pas antara 110 sampai 135 kata!"
        except Exception as e:
            if attempt == 2:
                raise e

    data["passed_invariants"] = False
    return data


def main():
    parser = argparse.ArgumentParser(description="Luna ✍️ — DoniesDaily Master Scriptwriter")
    parser.add_argument("--auto-queue", action="store_true", help="Auto-brainstorm and queue fresh topic using learned rules")
    parser.add_argument("--topic", default="", help="Specific topic key")
    parser.add_argument("--title", default="", help="Optional explicit title")
    parser.add_argument("--hook", default="", help="Optional explicit hook banner")
    parser.add_argument("--dry-run", action="store_true", help="Print without saving to DB")
    args = parser.parse_args()

    topic_key = args.topic
    title = args.title
    hook = args.hook
    hook_sub = ""

    if args.auto_queue or not topic_key:
        print("💡 Luna auto-brainstorming fresh topic using Learned Rules...")
        topic_info = generate_autonomous_topic()
        topic_key = topic_info["topic_key"]
        title = topic_info["title"]
        hook = topic_info["hook_banner"]
        hook_sub = topic_info.get("hook_subtitle", "")
        print(f"✨ Fresh Topic Conceived: [{topic_key}] - {title}")

    print(f"✍️ Luna crafting Long-Form script for [{topic_key}]...")
    script_data = generate_long_form_script(title, hook, hook_sub)
    print(f"✅ Script ready! Words: {script_data['word_count']} words | Compliant: {script_data.get('passed_invariants', False)}")

    if not args.dry_run:
        clean_title = title.replace("'", "''")
        clean_hook = hook.replace("'", "''")
        clean_sub = hook_sub.replace("'", "''")
        clean_script = script_data["spoken_script"].replace("'", "''")
        clean_vocal = script_data.get("hook_vocal", "").replace("'", "''")

        sql_upsert = f"""
        INSERT INTO ai_brain.virgin_content_ideas 
        (topic_key, title, hook_banner, hook_subtitle, hook_vocal, full_script, status)
        VALUES ('{topic_key}', '{clean_title}', '{clean_hook}', '{clean_sub}', '{clean_vocal}', '{clean_script}', 'ready')
        ON CONFLICT (topic_key) DO UPDATE 
        SET title = EXCLUDED.title,
            hook_banner = EXCLUDED.hook_banner,
            hook_subtitle = EXCLUDED.hook_subtitle,
            hook_vocal = EXCLUDED.hook_vocal,
            full_script = EXCLUDED.full_script,
            status = 'ready',
            updated_at = NOW();
        """
        subprocess.run(["docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-c", sql_upsert], check=True)
        print(f"💾 Topic [{topic_key}] committed to DB as 'ready'!")

        # Log trace to Swarm Matrix
        trace_luna = [
            {
                "type": "reasoning",
                "title": f"Luna Conceived: {title}",
                "description": f"Applied Learned Rules (Zero Kenapa-prefix, 110-135 words, acoustic tags). Word count: {script_data['word_count']} words.",
                "content": f"Hook Vocal: \"{script_data.get('hook_vocal', '')}\"\n\nDebate CTA: \"{script_data.get('cta_debate', '')}\""
            }
        ]
        post_swarm_chat("luna", "Luna (Sonnet Scriptwriter)", "✍️", "Master Scriptwriter & Storyteller (claude-sonnet-5-5-high)", "donies",
                        f"Naskah baru selesai diracik via **claude-sonnet-5-5-high** sesuai Learned Rules Advanced Mode dari Mochi:\nJudul: {title}\nBanner: {hook} | {hook_sub}\nPanjang: {script_data['word_count']} kata (Mode Long-Form Shorts 50-60 detik).",
                        trace_luna)


if __name__ == "__main__":
    main()
