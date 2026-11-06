#!/usr/bin/env python3
"""
tools/ingest_fahru_footage.py
=============================
Autonomous Multi-Frame Vision Ingestion Engine for Fahru's Authentic Cat Clips.

Workflows:
1. Detects raw/new cat videos (from Telegram upload, drop folder, or CLI argument).
2. Probes exact duration, fps, resolution via ffprobe.
3. Extracts 5-6 evenly spaced frames across the video to capture full behavioral progression.
4. Analyzes multi-frame action & emotions using Gemini Vision (gemini-3.8-flash-high).
5. Generates descriptive snake_case filename, rich semantic tags, and Indonesian description.
6. Renames generic file into clean descriptive format and registers into cat_assets_catalog.json.
7. Logs ingestion trace to SQLite agents_chat.db (#donies).
"""

import os
import sys
import json
import time
import uuid
import base64
import shutil
import sqlite3
import argparse
import tempfile
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

UGC_DIR = Path("/home/ubuntu/apps/ugc-lemonaru")
FAHRU_CLIPS_DIR = UGC_DIR / "assets/cat_videos/fahru_clips"
RAW_INCOMING_DIR = UGC_DIR / "assets/cat_videos/raw_incoming"
CATALOG_PATH = UGC_DIR / "data/cat_assets_catalog.json"
API_URL = "http://127.0.0.1:8317/v1/chat/completions"
API_KEY = "cpa-secret-key-12345"
MODEL = "gemini-3.8-flash-high"

FAHRU_CLIPS_DIR.mkdir(parents=True, exist_ok=True)
RAW_INCOMING_DIR.mkdir(parents=True, exist_ok=True)


def probe_video(video_path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration,r_frame_rate:format=duration",
        "-of", "json",
        str(video_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(res.stdout)
    fmt_dur = float(info.get("format", {}).get("duration", 0.0))
    streams = info.get("streams", [])
    stream_dur = float(streams[0].get("duration", 0.0)) if streams and streams[0].get("duration") else 0.0
    dur = fmt_dur or stream_dur or 10.0
    width = int(streams[0].get("width", 1080)) if streams else 1080
    height = int(streams[0].get("height", 1920)) if streams else 1920
    return {"duration": round(dur, 2), "width": width, "height": height}


def extract_multi_frames(video_path: Path, duration: float, num_frames: int = 10) -> list[str]:
    """Extracts 10 evenly spaced frames as base64 JPEG strings across the full video arc."""
    b64_list = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(num_frames):
            pct = (i + 1) / (num_frames + 1)
            ts = duration * pct
            out_jpg = Path(tmpdir) / f"frame_{i}.jpg"
            cmd = [
                "ffmpeg", "-y", "-ss", f"{ts:.2f}", "-i", str(video_path),
                "-vframes", "1", "-vf", "scale='min(720,iw)':-1", "-q:v", "3", str(out_jpg)
            ]
            subprocess.run(cmd, capture_output=True)
            if out_jpg.exists() and out_jpg.stat().st_size > 0:
                with open(out_jpg, "rb") as f:
                    b64_list.append(base64.b64encode(f.read()).decode("utf-8"))
    return b64_list


def analyze_with_multi_frame_vision(b64_frames: list[str], duration: float) -> dict:
    """Sends 10 frames to Gemini Vision for complete video understanding & naming (LOCKED PROTOCOL)."""
    content_parts = [
        {
            "type": "text",
            "text": f"""Berikut adalah {len(b64_frames)} frame berurutan (kronologis dari detik awal hingga akhir) dari video kucing otentik berdurasi {duration:.1f} detik.
Perhatikan alur tingkah laku kucing secara utuh: kondisi awal -> transisi/aksi gerak -> puncak reaksi/ekspresi -> kondisi akhir.

ATURAN BRIEF & PENAMAAN BAKU (LOCKED SOP):
1. 'slug': Nama file snake_case deskriptif, spesifik, huruf kecil, BOLEH PANJANG (6-12 kata, contoh: 'anak_kucing_calico_menguap_lebar_mengantuk_lalu_membuka_mata_bulat_menatap_kamera'). Tujuannya agar Editor Video (Milo) langsung tahu persis adegan apa yang terjadi tanpa memutar file. DILARANG menggunakan kata generik seperti 'video_kucing' atau 'kucing_lucu'.
2. 'title': Judul singkat deskriptif (Title Case, 4-7 kata).
3. 'description': Deskripsi lengkap 2 kalimat Bahasa Indonesia yang menceritakan urutan kejadian nyata yang terlihat di sepanjang 10 frame.
4. 'tags': 12-18 kata kunci relevan campuran Bahasa Indonesia & English, mencakup:
   - Ciri fisik: warna bulu (oren, calico, hitam, putih, abu, tabby), pola, ras jika tampak (munchkin, siamese, persia).
   - Bagian tubuh & gestur: cakar, ekor, telinga, mata, kumis, mulut_nganga.
   - Objek interaksi: kardus, kasur, bantal, ikan, mangkok, pintu, tali, mainan.
   - Kata kerja aksi: lari, lompat, ngintip, rebahan, cakar, jilat, gigit, bengong, elus.
5. 'emotion': Pilih 1 dominan: 'santai' | 'penasaran' | 'marah' | 'takut' | 'lucu' | 'sedih' | 'berburu' | 'manja'.
6. 'action': Pilih 1 dominan: 'tidur' | 'lari' | 'lompat' | 'makan' | 'gigit' | 'cakar' | 'bengong' | 'elus' | 'kepo'.

Kembalikan HANYA JSON valid murni tanpa format markdown/backticks:
{{
  "slug": "nama_file_snake_case_deskriptif",
  "title": "Judul Deskriptif Singkat",
  "description": "Deskripsi 2 kalimat tentang alur kejadian di video.",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10", "tag11", "tag12"],
  "emotion": "santai|penasaran|marah|takut|lucu|sedih|berburu|manja",
  "action": "tidur|lari|lompat|makan|gigit|cakar|bengong|elus|kepo"
}}"""
        }
    ]

    for b64 in b64_frames:
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
        })

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": content_parts}],
        "max_tokens": 600,
        "temperature": 0.2
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    )

    with urllib.request.urlopen(req, timeout=45) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        raw = res["choices"][0]["message"]["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())


def ingest_file(input_path: Path) -> dict:
    if not input_path.exists():
        raise FileNotFoundError(f"File {input_path} tidak ditemukan!")

    print(f"🎬 [INGEST] Memproses: {input_path.name}...")
    probe = probe_video(input_path)
    dur = probe["duration"]
    print(f"⏱️ Durasi: {dur}s | Resolusi: {probe['width']}x{probe['height']}")

    # Extract 10 frames across video timeline
    print("📸 Mengekstrak 10 frame berurutan untuk analisis multi-frame vision...")
    frames = extract_multi_frames(input_path, dur, num_frames=10)
    if not frames:
        raise RuntimeError("Gagal mengekstrak frame dari video!")

    # Multi-frame vision analysis
    print(f"🧠 Menganalisis aksi & emosi kucing via {MODEL}...")
    meta = analyze_with_multi_frame_vision(frames, dur)
    slug = meta.get("slug", "").strip() or f"kucing_fahru_{int(time.time())}"
    slug = "".join(c if c.isalnum() or c == "_" else "_" for c in slug.lower()).strip("_")
    if not slug.startswith("asli_fahru_"):
        slug = f"asli_fahru_{slug}"

    # Determine final destination
    final_filename = f"{slug}.mp4"
    final_path = FAHRU_CLIPS_DIR / final_filename

    # Handle collision
    if final_path.exists() and final_path.resolve() != input_path.resolve():
        final_filename = f"{slug}_{uuid.uuid4().hex[:4]}.mp4"
        final_path = FAHRU_CLIPS_DIR / final_filename

    # Copy / move to destination
    if input_path.resolve() != final_path.resolve():
        shutil.copy2(str(input_path), str(final_path))
        print(f"📁 Video di-rename & disalin ke: {final_path.name}")
    else:
        print(f"📁 Video sudah berada di: {final_path.name}")

    # Update cat_assets_catalog.json
    catalog = []
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            catalog = json.load(f)

    # Check if entry already exists (by abs_path or id)
    catalog = [c for c in catalog if c.get("id") != slug and c.get("abs_path") != str(final_path)]

    new_entry = {
        "id": slug,
        "cluster": "fahru_clips",
        "stem": slug,
        "rel_path": f"fahru_clips/{final_path.name}",
        "abs_path": str(final_path),
        "duration": dur,
        "category": "fahru_sent",
        "tags": [t.lower().strip() for t in meta.get("tags", [])],
        "description": meta.get("description", ""),
        "emotion": meta.get("emotion", "santai"),
        "action": meta.get("action", "bengong"),
        "ingested_at": datetime.now().isoformat()
    }
    catalog.insert(0, new_entry)

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print("✅ Berhasil didaftarkan ke data/cat_assets_catalog.json!")
    print(f"🏷️ Tags: {', '.join(new_entry['tags'][:8])}")
    print(f"📝 Deskripsi: {new_entry['description']}")

    # Log to agents_chat.db
    try:
        db_chat = Path("/home/ubuntu/vps-control-center/backend/data/agents_chat.db")
        if db_chat.exists():
            conn = sqlite3.connect(str(db_chat))
            cur = conn.cursor()
            mid = f"msg-{int(time.time()*1000)}-{uuid.uuid4().hex[:6]}"
            now_ts = datetime.now().strftime("%H:%M")
            msg_txt = (
                f"📥 **[FOOTAGE INGESTION TUNTAS — FAHRU SENT]**\\n"
                f"• ID/File: `{final_filename}` ({dur}s)\\n"
                f"• Aksi: `{new_entry['action']}` ({new_entry['emotion']})\\n"
                f"• Deskripsi: {new_entry['description']}\\n"
                f"• Tags: `{', '.join(new_entry['tags'][:6])}`\\n"
                f"Klip resmi aktif di katalog dan siap diprioritaskan Milo di sprint berikutnya!"
            )
            cur.execute("""
                INSERT INTO agent_messages (id, sender_id, sender_name, sender_avatar, sender_role, recipient_id, recipient_name, content, timestamp, channel, status, created_at)
                VALUES (?, 'cleo', 'Cleo (QC & Asset Vault)', '🛡️', 'Asset Ingestion & QC', 'all', 'All Agents', ?, ?, 'donies', 'delivered', ?)
            """, (mid, msg_txt, now_ts, time.time()))
            conn.commit()
            conn.close()
    except Exception as e_db:
        print(f"Warning: logging to db failed: {e_db}")

    return new_entry


def scan_and_ingest():
    """Scans raw_incoming and fahru_clips for unindexed MP4 files."""
    if not CATALOG_PATH.exists():
        indexed_paths = set()
    else:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            cat = json.load(f)
        indexed_paths = {c.get("abs_path") for c in cat if c.get("abs_path")}

    candidates = []
    for d in [RAW_INCOMING_DIR, FAHRU_CLIPS_DIR]:
        for f in d.glob("*.*"):
            if f.suffix.lower() in [".mp4", ".mov", ".mkv"]:
                if str(f) not in indexed_paths:
                    candidates.append(f)

    if not candidates:
        print("✨ Tidak ada video baru yang belum terindeks.")
        return []

    print(f"🔍 Ditemukan {len(candidates)} video baru untuk di-ingest!")
    results = []
    for c in candidates:
        try:
            res = ingest_file(c)
            results.append(res)
        except Exception as e:
            print(f"❌ Gagal memproses {c.name}: {e}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Frame Vision Ingestion Engine for Fahru Cat Clips")
    parser.add_argument("--file", type=str, help="Path ke file video tunggal")
    parser.add_argument("--scan", action="store_true", help="Pindai folder incoming & unindexed clips")
    args = parser.parse_args()

    if args.file:
        ingest_file(Path(args.file))
    elif args.scan:
        scan_and_ingest()
    else:
        scan_and_ingest()
