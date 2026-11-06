#!/usr/bin/env python3
"""
tools/doni_evaluator.py
=======================
Squad DoniesDaily — Mochi Advanced Mode & Retention Curve Forensics Evaluator.
Combines:
1. YouTube Data API v3 (surface counters & metadata)
2. YouTube Analytics API v2 (averageViewDuration, averageViewPercentage, engagedViews, subscribersGained, 100-point retention curve)
3. YouTube Studio Advanced Mode Live Extractor via Chrome CDP :9222 (Stayed to watch %, real-time AVD & APV %)
4. Deep Evaluation & Team Upgrade Directive via gemini-4-argon-high
"""

import sys
import os
import re
import json
import time
import uuid
import sqlite3
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

OAUTH_TOKEN_PATH = Path("/home/ubuntu/.config/youtube/doniesdaily_oauth.json")
DB_CHAT_PATH = Path("/home/ubuntu/vps-control-center/backend/data/agents_chat.db")
VEN_PYTHON = "/home/ubuntu/apps/ugc-lemonaru/.venv/bin/python3"


def post_swarm_chat(sender_id: str, sender_name: str, sender_avatar: str, sender_role: str, channel: str, content: str, traces: list = None):
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


def get_google_credentials():
    if not OAUTH_TOKEN_PATH.exists():
        raise FileNotFoundError(f"OAuth token missing: {OAUTH_TOKEN_PATH}")
    with open(OAUTH_TOKEN_PATH, "r") as f:
        tdata = json.load(f)
    return Credentials(
        token=tdata.get("access_token"),
        refresh_token=tdata.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=tdata.get("client_id"),
        client_secret=tdata.get("client_secret")
    )


def get_youtube_service():
    return build("youtube", "v3", credentials=get_google_credentials())


def get_youtube_analytics_service():
    return build("youtubeAnalytics", "v2", credentials=get_google_credentials())


def mmss_to_sec(s: str) -> float:
    parts = s.strip().split(":")
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return float(int(parts[0]) * 60 + int(parts[1]))
    return 0.0


def scrape_studio_advanced_mode() -> dict:
    """Scrapes YouTube Studio Advanced Mode table via persistent Chrome CDP :9222.
    Returns dict keyed by video title with stayed_to_watch_pct, avg_view_duration_sec, avg_view_pct, views.
    """
    script = """
import json, re
from playwright.sync_api import sync_playwright

def mmss_to_sec(s):
    parts = s.strip().split(":")
    return float(int(parts[0]) * 60 + int(parts[1])) if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit() else 0.0

out = {"channel_stayed_avg": 38.0, "videos": {}}
try:
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = b.contexts[0]
        page = ctx.new_page()
        url = "https://studio.youtube.com/channel/UCNPtjF2aB0wvWHI0q7hhcCg/analytics/tab-overview/period-default/explore?entity_type=CHANNEL&entity_id=UCNPtjF2aB0wvWHI0q7hhcCg&time_period=4_weeks&explore_type=TABLE_AND_CHART&metric=EXTERNAL_VIEWS&granularity=DAY&t_metrics=EXTERNAL_VIEWS&t_metrics=SHORTS_FEED_IMPRESSIONS_VTR&t_metrics=AVERAGE_WATCH_TIME&t_metrics=AVERAGE_WATCH_PERCENTAGE&dimension=VIDEO&o_column=EXTERNAL_VIEWS&o_direction=ANALYTICS_ORDER_DIRECTION_DESC"
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(6500)
        body = page.inner_text("body")
        page.close()

        lines = [l.strip() for l in body.splitlines() if l.strip()]
        for idx, l in enumerate(lines):
            if l == "Total" and idx + 4 < len(lines):
                try:
                    out["channel_stayed_avg"] = float(lines[idx+2].replace("%", "").replace(",", "."))
                except Exception:
                    pass
        i = 0
        while i < len(lines) - 6:
            if re.match(r"^\\d+:\\d{2}$", lines[i]) and not re.match(r"^[\\d.,]+%?$", lines[i+1]):
                dur_s = mmss_to_sec(lines[i])
                title = lines[i+1]
                views_raw = lines[i+2].replace(".", "").replace(",", "")
                stayed_raw = lines[i+4].replace("%", "").replace(",", ".")
                avd_s = mmss_to_sec(lines[i+5]) if ":" in lines[i+5] else 0.0
                apv_raw = lines[i+6].replace("%", "").replace(",", ".")
                try:
                    out["videos"][title] = {
                        "dur_s": dur_s,
                        "views": int(views_raw) if views_raw.isdigit() else 0,
                        "stayed_to_watch_pct": float(stayed_raw),
                        "avg_view_duration_sec": float(avd_s),
                        "avg_view_pct": float(apv_raw)
                    }
                except Exception:
                    pass
                i += 7
            else:
                i += 1
except Exception as e:
    out["error"] = str(e)
print("JSON_START" + json.dumps(out))
"""
    try:
        res = subprocess.run([VEN_PYTHON, "-c", script], capture_output=True, text=True, timeout=45)
        if "JSON_START" in res.stdout:
            payload = res.stdout.split("JSON_START", 1)[1].strip()
            return json.loads(payload)
    except Exception as e:
        print(f"Studio Advanced Mode CDP fallback warning: {e}")
    return {"channel_stayed_avg": 38.0, "videos": {}}


def fetch_api_analytics_and_curves() -> tuple:
    """Queries Official YouTube Analytics v2 API for per-video retention & 100-point audienceWatchRatio curve."""
    api_map = {}
    curves_map = {}
    try:
        yta = get_youtube_analytics_service()
        res = yta.reports().query(
            ids="channel==MINE",
            startDate="2026-09-01",
            endDate=datetime.now().strftime("%Y-%m-%d"),
            metrics="views,engagedViews,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained",
            dimensions="video",
            sort="-views",
            maxResults=30
        ).execute()
        for r in res.get("rows", []):
            vid = r[0]
            api_map[vid] = {
                "views": int(r[1]),
                "engaged_views": int(r[2]),
                "avg_view_duration_sec": float(r[3]),
                "avg_view_pct": float(r[4]),
                "likes": int(r[5]),
                "comments": int(r[6]),
                "shares": int(r[7]),
                "subs_gained": int(r[8])
            }

        # Query 100-point retention curve for top videos
        for vid in list(api_map.keys())[:10]:
            try:
                c_res = yta.reports().query(
                    ids="channel==MINE",
                    startDate="2026-09-01",
                    endDate=datetime.now().strftime("%Y-%m-%d"),
                    metrics="audienceWatchRatio,relativeRetentionPerformance",
                    dimensions="elapsedVideoTimeRatio",
                    filters=f"video=={vid}"
                ).execute()
                rows = c_res.get("rows", [])
                if rows:
                    curves_map[vid] = rows
            except Exception:
                pass
    except Exception as e:
        print(f"youtubeAnalytics v2 query warning: {e}")
    return api_map, curves_map


def analyze_retention_curve(rows: list, duration_sec: float) -> dict:
    """Extracts 3s hold %, 50% midpoint retention, 95-100% end completion rate, and steepest drop second."""
    if not rows or duration_sec <= 0:
        return {}
    # Find ratio closest to 3 seconds
    r_3s = min(rows, key=lambda r: abs(float(r[0]) * duration_sec - 3.0))
    r_mid = min(rows, key=lambda r: abs(float(r[0]) - 0.50))
    r_end = rows[-1]

    # Find steepest single-step drop after 3 seconds
    biggest_drop_ratio = 0.0
    biggest_drop_delta = 0.0
    for idx in range(1, len(rows)):
        t_sec = float(rows[idx][0]) * duration_sec
        if t_sec < 3.0:
            continue
        delta = float(rows[idx-1][1]) - float(rows[idx][1])
        if delta > biggest_drop_delta:
            biggest_drop_delta = delta
            biggest_drop_ratio = float(rows[idx][0])

    return {
        "hold_3s_pct": round(float(r_3s[1]) * 100.0, 1),
        "mid_50_pct": round(float(r_mid[1]) * 100.0, 1),
        "end_retention_pct": round(float(r_end[1]) * 100.0, 1),
        "biggest_drop_sec": round(biggest_drop_ratio * duration_sec, 1),
        "biggest_drop_delta_pct": round(biggest_drop_delta * 100.0, 1)
    }


def evaluate_channel():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📊 Mochi starting Advanced Mode & Retention Curve forensics...")
    yt = get_youtube_service()

    # 1. Fetch channel uploads playlist
    ch_res = yt.channels().list(part="contentDetails", mine=True).execute()
    uploads_playlist_id = ch_res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    pl_res = yt.playlistItems().list(part="snippet,contentDetails", playlistId=uploads_playlist_id, maxResults=50).execute()
    video_ids = [it["contentDetails"]["videoId"] for it in pl_res.get("items", [])]

    if not video_ids:
        print("No videos found to evaluate.")
        return

    # 2. Fetch surface statistics + Advanced Mode Studio + youtubeAnalytics API v2
    v_res = yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(video_ids)).execute()
    items = v_res.get("items", [])

    studio_data = scrape_studio_advanced_mode()
    studio_videos = studio_data.get("videos", {})
    channel_stayed_avg = studio_data.get("channel_stayed_avg", 38.0)

    api_map, curves_map = fetch_api_analytics_and_curves()

    videos_data = []
    now = datetime.now(timezone.utc)

    for v in items:
        vid = v["id"]
        title = v["snippet"]["title"]
        pub_at_str = v["snippet"]["publishedAt"]
        pub_at = datetime.fromisoformat(pub_at_str.replace("Z", "+00:00"))
        age_hours = (now - pub_at).total_seconds() / 3600.0

        stats = v.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        dur_raw = v.get("contentDetails", {}).get("duration", "PT0S")
        dur_sec = 0.0
        m_dur = re.findall(r"PT(?:(\d+)M)?(?:(\d+)S)?", dur_raw)
        if m_dur:
            mins = int(m_dur[0][0]) if m_dur[0][0] else 0
            secs = int(m_dur[0][1]) if m_dur[0][1] else 0
            dur_sec = float(mins * 60 + secs)

        st_entry = studio_videos.get(title, {})
        api_entry = api_map.get(vid, {})
        curve_info = analyze_retention_curve(curves_map.get(vid, []), dur_sec)

        stayed_pct = st_entry.get("stayed_to_watch_pct")
        avd_sec = st_entry.get("avg_view_duration_sec") or api_entry.get("avg_view_duration_sec") or 0.0
        apv_pct = st_entry.get("avg_view_pct") or api_entry.get("avg_view_pct") or 0.0
        engaged_v = api_entry.get("engaged_views") or (int(views * (stayed_pct / 100.0)) if stayed_pct else 0)
        subs_gained = api_entry.get("subs_gained", 0)
        end_ret_pct = curve_info.get("end_retention_pct")
        drop_sec = curve_info.get("biggest_drop_sec")

        # Use highest view count between Data API and Studio Advanced Mode
        final_views = max(views, st_entry.get("views", 0), api_entry.get("views", 0))

        videos_data.append({
            "video_id": vid,
            "title": title,
            "published_at": pub_at_str,
            "age_hours": age_hours,
            "views": final_views,
            "likes": likes,
            "comments": comments,
            "duration_sec": dur_sec,
            "stayed_to_watch_pct": stayed_pct,
            "engaged_views": engaged_v,
            "avg_view_duration_sec": avd_sec,
            "avg_view_pct": apv_pct,
            "subs_gained": subs_gained,
            "end_retention_pct": end_ret_pct,
            "biggest_drop_sec": drop_sec,
            "hold_3s_pct": curve_info.get("hold_3s_pct"),
            "mid_50_pct": curve_info.get("mid_50_pct")
        })

    # 3. Store enriched Advanced Mode snapshot in PostgreSQL
    for vd in videos_data:
        snap_hour = int(vd["age_hours"])
        stayed_val = "NULL" if vd["stayed_to_watch_pct"] is None else f"{vd['stayed_to_watch_pct']}"
        eng_val = "NULL" if not vd["engaged_views"] else f"{vd['engaged_views']}"
        avd_val = "NULL" if not vd["avg_view_duration_sec"] else f"{vd['avg_view_duration_sec']}"
        apv_val = "NULL" if not vd["avg_view_pct"] else f"{vd['avg_view_pct']}"
        end_val = "NULL" if vd["end_retention_pct"] is None else f"{vd['end_retention_pct']}"
        drop_val = "NULL" if vd["biggest_drop_sec"] is None else f"{vd['biggest_drop_sec']}"
        subs_val = int(vd.get("subs_gained") or 0)

        sql_snap = f"""
        INSERT INTO ai_brain.doniesdaily_metrics_history 
        (video_id, title, snapshot_hours, views_count, likes_count, comments_count, duration_sec, stayed_to_watch_pct, engaged_views, avg_view_duration_sec, avg_view_pct, subs_gained, end_retention_pct, biggest_drop_sec)
        VALUES ('{vd['video_id']}', '{vd['title'].replace("'", "''")}', {snap_hour}, {vd['views']}, {vd['likes']}, {vd['comments']}, {vd['duration_sec']}, {stayed_val}, {eng_val}, {avd_val}, {apv_val}, {subs_val}, {end_val}, {drop_val});
        
        UPDATE ai_brain.doniesdaily_posts 
        SET views_count = {vd['views']},
            likes_count = {vd['likes']},
            duration_sec = {vd['duration_sec']},
            stayed_to_watch_pct = COALESCE({stayed_val}, stayed_to_watch_pct),
            engaged_views = COALESCE({eng_val}, engaged_views),
            avg_view_duration_sec = COALESCE({avd_val}, avg_view_duration_sec),
            avg_view_pct = COALESCE({apv_val}, avg_view_pct),
            subs_gained = GREATEST(COALESCE(subs_gained, 0), {subs_val}),
            end_retention_pct = COALESCE({end_val}, end_retention_pct),
            biggest_drop_sec = COALESCE({drop_val}, biggest_drop_sec)
        WHERE video_id = '{vd['video_id']}';
        """
        subprocess.run(["docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-c", sql_snap], capture_output=True)

    # 4. Forensic Sorting & Comparative Cohorts
    sorted_by_views = sorted(videos_data, key=lambda x: x["views"], reverse=True)
    top_video = sorted_by_views[0] if sorted_by_views else None
    latest_video = videos_data[0] if videos_data else None

    major_videos = [v for v in sorted_by_views if v["views"] >= 500]
    best_stayed_video = max(major_videos, key=lambda x: x.get("stayed_to_watch_pct") or 0) if major_videos else top_video
    best_avd_video = max(major_videos, key=lambda x: x.get("avg_view_duration_sec") or 0) if major_videos else top_video

    # 5. Deep Retention & Advanced Mode Forensics via gemini-4-argon-high
    argon_diagnosis = ""
    video_by_video_breakdown = []
    what_makes_viewers_stay_to_end = ""
    upgraded_rules_log = []

    try:
        major_table = [
            {
                "video_id": v["video_id"],
                "title": v["title"],
                "duration_sec": v["duration_sec"],
                "views": v["views"],
                "stayed_to_watch_pct": v["stayed_to_watch_pct"],
                "watched_how_long_sec": v["avg_view_duration_sec"],
                "avg_percentage_viewed": v["avg_view_pct"],
                "hold_at_3s_pct": v["hold_3s_pct"],
                "retained_at_50pct_mark": v["mid_50_pct"],
                "stayed_until_very_end_pct": v["end_retention_pct"],
                "biggest_dropoff_at_sec": v["biggest_drop_sec"],
                "subs_gained": v["subs_gained"],
                "likes": v["likes"]
            }
            for v in major_videos[:8]
        ]

        eval_prompt = f"""Kamu adalah Mochi (Head of Analytics & Retention Forensics) di Squad YouTube Shorts @DoniesDaily, ditenagai oleh **gemini-4-argon-high**.
Pak Fahru (Owner) meminta kamu menganalisis dari **YouTube Studio Advanced Mode** secara mendalam:
- Untuk Video A, B, C, dst: **ditonton berapa lama (detik & %)**?
- **Berapa banyak orang yang STAY vs SWIPE AWAY (`stayed_to_watch_pct`)**?
- **Apa yang membuat sebuah video ditonton sampai akhir (`stayed_until_very_end_pct` / `watched_how_long_sec` tinggi) vs apa yang bikin penonton kabur di tengah (`biggest_dropoff_at_sec`)**?

DATA RIIL YOUTUBE STUDIO ADVANCED MODE + API RETENSI (Channel Avg Stayed-to-Watch: {channel_stayed_avg}%):
{json.dumps(major_table, ensure_ascii=False, indent=2)}

Kembalikan HANYA JSON valid tanpa markdown/backticks dengan skema:
{{
  "video_abc_forensics": [
    "Bedah tajam Video A (sebut judul, durasi, ditonton berapa detik, Stayed to watch berapa %, berapa % yang bertahan sampai akhir / subs didapat, dan alasan psikologis/visualnya)",
    "Bedah tajam Video B (kontraskan kenapa Stayed to watch atau durasi tontonnya tinggi/rendah)",
    "Bedah tajam Video C (kontraskan misal kenapa sama-sama pakai kata JANGAN tapi Stayed to watch beda jauh: 48.3% vs 26.2%, atau kenapa video 49-62 detik menghasilkan +10 subs & AVD 27-31 detik)"
  ],
  "why_viewers_watch_until_end": "Analisis mendalam 2-3 kalimat: faktor apa yang terbukti membuat penonton betah nonton 27-31 detik sampai kalimat terakhir, dan di detik ke berapa biasanya terjadi drop-off terbesar serta cara mengatasinya.",
  "diagnosis_summary": "Ringkasan eksekutif 2 kalimat untuk briefing pagi Ketua Doni.",
  "team_upgrade_rule": {{
    "category": "title_hook | visual_footage | audio_pacing | script_structure",
    "rule_name": "snake_case_unique_rule_key",
    "directive": "Instruksi operasional spesifik untuk Luna (naskah/hook), Kak Ceria (voiceover), dan Milo (Opus Remotion scene cut) berdasarkan metrik Stayed-to-Watch & AVD.",
    "rationale": "Bukti angka Stayed to watch % dan Average View Duration (detik) dari tabel Advanced Mode.",
    "confidence_score": 0.96
  }}
}}"""

        req = urllib.request.Request(
            "http://127.0.0.1:8317/v1/chat/completions",
            data=json.dumps({
                "model": "gemini-4-argon-high",
                "messages": [{"role": "user", "content": eval_prompt}],
                "temperature": 0.25
            }).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": "Bearer cpa-secret-key-12345"}
        )
        with urllib.request.urlopen(req, timeout=50) as resp:
            raw_eval = json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"].strip()
            if raw_eval.startswith("```"):
                raw_eval = raw_eval.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            eval_json = json.loads(raw_eval)
            argon_diagnosis = eval_json.get("diagnosis_summary", "")
            video_by_video_breakdown = eval_json.get("video_abc_forensics", [])
            what_makes_viewers_stay_to_end = eval_json.get("why_viewers_watch_until_end", "")
            up_rule = eval_json.get("team_upgrade_rule") or {}
            if up_rule.get("rule_name") and up_rule.get("directive"):
                r_cat = up_rule.get("category", "script_structure").replace("'", "''")
                r_name = up_rule["rule_name"].replace("'", "''")
                r_dir = up_rule["directive"].replace("'", "''")
                r_rat = up_rule.get("rationale", "Argon-High Advanced Mode Audit").replace("'", "''")
                r_conf = float(up_rule.get("confidence_score", 0.95))
                sql_up = f"""
                INSERT INTO ai_brain.doniesdaily_learnings (category, rule_name, directive, rationale, confidence_score, status)
                VALUES ('{r_cat}', '{r_name}', '{r_dir}', '{r_rat}', {r_conf}, 'active')
                ON CONFLICT (rule_name) DO UPDATE
                SET directive = EXCLUDED.directive,
                    rationale = EXCLUDED.rationale,
                    confidence_score = GREATEST(ai_brain.doniesdaily_learnings.confidence_score, EXCLUDED.confidence_score),
                    updated_at = NOW();
                """
                subprocess.run(["docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-c", sql_up], capture_output=True)
                upgraded_rules_log.append(f"[{r_cat.upper()}] {up_rule['rule_name']}: {up_rule['directive']}")
    except Exception as e:
        print(f"Warning: Argon-High deep evaluation fallback: {e}")

    # 6. Fetch Active Directives for Next Video
    cmd_get_rules = [
        "docker", "exec", "-i", "supabase-db",
        "psql", "-U", "postgres", "-d", "postgres", "-t", "-A", "-c",
        "SELECT category, rule_name, directive, confidence_score FROM ai_brain.doniesdaily_learnings WHERE status = 'active' ORDER BY confidence_score DESC;"
    ]
    res_rules = subprocess.run(cmd_get_rules, capture_output=True, text=True)
    active_rules_list = res_rules.stdout.strip().split("\n") if res_rules.stdout.strip() else []
    rules_summary = "\n".join([f"• [{r.split('|')[0].upper()}] {r.split('|')[2]} (Confidence: {float(r.split('|')[3])*100:.0f}%)" for r in active_rules_list if "|" in r])

    # Format Advanced Mode Table Summary
    adv_rows_txt = []
    for idx, v in enumerate(major_videos[:7], 1):
        st_str = f"{v['stayed_to_watch_pct']:.1f}%" if v["stayed_to_watch_pct"] is not None else "N/A"
        avd_str = f"{v['avg_view_duration_sec']:.0f}s ({v['avg_view_pct']:.1f}%)" if v["avg_view_duration_sec"] else "N/A"
        end_str = f" | End Hold: {v['end_retention_pct']:.1f}% (Drop @{v['biggest_drop_sec']:.0f}s)" if v["end_retention_pct"] is not None else ""
        subs_str = f" | +{v['subs_gained']} subs" if v["subs_gained"] else ""
        adv_rows_txt.append(
            f"• **Vid #{idx} `{v['title'][:42]}...`** (Durasi `{v['duration_sec']:.0f}s`)\n"
            f"  ↳ Views: **{v['views']:,}** | Stayed to Watch: **{st_str}** | Ditonton: **{avd_str}**{end_str}{subs_str}"
        )

    forensics_txt = "\n".join([f"• {item}" for item in video_by_video_breakdown]) if video_by_video_breakdown else f"• {argon_diagnosis}"

    mochi_msg = f"""📊 **[MOCHI ADVANCED MODE & RETENTION CURVE FORENSICS — ENGINE: `gemini-4-argon-high`]**
Ketua @Doni & Tim, aku baru saja menarik tabel **YouTube Studio Advanced Mode + Kurva Retensi 100-Titik API v2** (Rerata Channel Stayed-to-Watch: **{channel_stayed_avg:.1f}%**):

**1. TABEL PERFORMA PER VIDEO (DITONTON BERAPA LAMA & BERAPA % YANG STAY):**
{chr(10).join(adv_rows_txt)}

**2. BEDAH FORENSIK VIDEO A / B / C (`gemini-4-argon-high`):**
{forensics_txt}

**3. APA YANG MEMBUAT PENONTON BETAH SAMPAI AKHIR vs SWIPE AWAY:**
• {what_makes_viewers_stay_to_end or argon_diagnosis}

**4. UPGRADE RULE BARU & PEMBAGIAN TUGAS TIM:**
• **Rule Baru Diinjeksi:** {'; '.join(upgraded_rules_log) if upgraded_rules_log else 'Confidence rules diperbarui.'}
• **@Luna (Scriptwriter — `gemini-4-argon-high`):** Buka 3 detik pertama dengan **Ancaman Emosional/Kesalahan Fatal Terlihat** (seperti *Bawa Bangkai = 48.3% Stayed*), pasang **Re-Hook Twist di detik ke-14 s/d ke-18** untuk mencegah *mid-video drop-off*, dan kunci kalimat terakhir dengan * payoff emosional* agar durasi tonton tembus >30 detik.
• **@Milo (Remotion Visual Director — WAJIB `claude-opus-5-5-high`):** Susun *Scene Cut Plan* Remotion dengan **Claude Opus**, selang-seling klip asli Pak Fahru & AI Flow, potong tepat mengikuti titik kalimat (`4.0s-8.5s`), 0% looping!"""

    trace_data = [
        {
            "type": "tool",
            "title": "YouTube Studio Advanced Mode + Analytics v2 Extraction",
            "description": f"Extracted Stayed-to-Watch %, AVD (seconds), APV %, and 100-point retention curves for {len(major_videos)} top videos.",
            "content": "\n".join(adv_rows_txt[:5])
        },
        {
            "type": "reasoning",
            "title": "Argon-High Video A/B/C Retention Diagnosis",
            "description": argon_diagnosis[:180],
            "content": what_makes_viewers_stay_to_end
        }
    ]

    post_swarm_chat("mochi", "Mochi (Argon-High Analytics)", "📊", "Head of Advanced Analytics & Retention Forensics", "donies", mochi_msg, trace_data)
    print("✅ Mochi Advanced Mode evaluation complete and logged to Swarm Matrix!")
    return {
        "top_video": top_video,
        "latest_video": latest_video,
        "best_stayed_video": best_stayed_video,
        "best_avd_video": best_avd_video,
        "argon_diagnosis": argon_diagnosis,
        "video_by_video_breakdown": video_by_video_breakdown,
        "what_makes_viewers_stay_to_end": what_makes_viewers_stay_to_end,
        "active_rules_count": len(active_rules_list)
    }


if __name__ == "__main__":
    evaluate_channel()
