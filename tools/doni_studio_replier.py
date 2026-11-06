#!/usr/bin/env python3
"""
Doni Studio Auto-Replier 💬 — Autonomous Community Engagement for DoniesDaily
Monitors YouTube Studio unresponded comments, automatically:
1. Gives Creator Heart (❤️)
2. Gives Creator Like (👍)
3. Fetches exact video script/CTA context from DB + YouTube Data API v3
4. Drafts warm, witty, context-matched responses via Claude Sonnet / Argon-High as Kak Ceria
5. Submits reply directly to boost algorithm engagement and community loyalty.
"""
import re
import sys
import time
import json
import logging
import argparse
import subprocess
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("doni_studio_replier")

DATA_DIR = Path("/home/ubuntu/apps/ugc-lemonaru/data/seed_views")
DATA_DIR.mkdir(parents=True, exist_ok=True)
CLIPROXY_URL = "http://127.0.0.1:8317/v1/chat/completions"
OAUTH_FILE = Path("/home/ubuntu/.config/youtube/doniesdaily_oauth.json")

UI_NOISE_PATTERNS = [
    r"^\d+\s*repl(y|ies)$",
    r"^reply$",
    r"^balas$",
    r"^\d+\s*balasan$",
    r"^view\s+\d+\s+repl(y|ies)$",
    r"^find similar comments$",
]


def is_ui_noise(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return True
    for pat in UI_NOISE_PATTERNS:
        if re.match(pat, t, re.IGNORECASE):
            return True
    return False


def get_video_context(video_title: str) -> dict:
    """Fetches full script / story_text and hook from ai_brain.doniesdaily_posts or YouTube API."""
    ctx = {"title": video_title, "script": ""}
    if not video_title or video_title in ("Shorts", "Video Shorts"):
        return ctx

    clean_title = video_title.split("#")[0].strip().replace("'", "''")
    if len(clean_title) >= 8:
        sql = (
            f"SELECT title, COALESCE(hook, ''), COALESCE(story_text, '') "
            f"FROM ai_brain.doniesdaily_posts "
            f"WHERE title ILIKE '%{clean_title[:35]}%' "
            f"ORDER BY created_at DESC LIMIT 1;"
        )
        try:
            res = subprocess.run(
                ["docker", "exec", "supabase-db", "psql", "-U", "postgres", "-d", "postgres", "-t", "-A", "-F", "|||", "-c", sql],
                capture_output=True, text=True, timeout=8
            )
            line = res.stdout.strip()
            if line and "|||" in line:
                parts = line.split("|||")
                db_title = parts[0].strip()
                db_hook = parts[1].strip() if len(parts) > 1 else ""
                db_story = parts[2].strip() if len(parts) > 2 else ""
                full_script = f"{db_hook} {db_story}".strip()
                if full_script:
                    ctx["title"] = db_title or video_title
                    ctx["script"] = full_script
                    return ctx
        except Exception as e:
            logger.warning(f"DB context lookup warning: {e}")

    return ctx


def draft_reply(video_title: str, comment_text: str, author: str) -> str:
    """Uses Claude Sonnet / Argon-High to craft a natural, video-specific response in Kak Ceria's voice."""
    clean_text = re.sub(r"\s+", " ", (comment_text or "")).strip()
    if is_ui_noise(clean_text):
        clean_text = ""

    v_ctx = get_video_context(video_title)
    actual_title = v_ctx["title"]
    script_context = v_ctx["script"]

    script_block = f'\nIsi Naskah & Pertanyaan CTA di Video:\n"{script_context}"\n' if script_context else ""

    prompt = f"""Kamu adalah Kak Ceria dari kanal YouTube @DoniesDaily (channel edukasi & fakta unik kucing).
Tugasmu membalas komentar penonton di bawah ini supaya **100% NYAMBUNG dengan topik spesifik di dalam video** dan menjawab langsung maksud komentar penonton.

Judul Video: "{actual_title}"{script_block}
Penonton ({author}) berkomentar: "{clean_text if clean_text else '(memberikan reaksi suka pada video ini)'}"

ATURAN KETAT:
1. WAJIB nyambung langsung dengan isi/topik video di atas dan maksud komentar penonton! (Contoh: jika di akhir video ada pilihan "Tim biarkan atau tim cuci" lalu penonton komen "Di biarkan", pahami bahwa dia memilih "Tim biarkan kucing tidur di baju kotor" dan tanggapi pilihannya dengan seru).
2. DILARANG KERAS membahas jumlah reply/komentar seperti "Sekarang jadi 1 reply", "Udah nggak 0 replies lagi", atau kalimat meta/bot aneh lainnya!
3. Gunakan bahasa Indonesia santai, hangat, akrab sesama pecinta anabul, maksimal 1-2 kalimat pendek (10-18 kata).
4. Sertakan 1-2 emoji yang relevan dengan isi video (😻🐾🧺🐱).
5. Balas HANYA teks balasannya saja tanpa tanda kutip."""

    for model_name in ["claude-sonnet-5-5-high", "gemini-4-argon-high"]:
        try:
            resp = requests.post(
                CLIPROXY_URL,
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.75,
                    "max_tokens": 1024
                },
                headers={"Authorization": "Bearer cpa-secret-key-12345", "Content-Type": "application/json"},
                timeout=25
            )
            if resp.status_code == 200:
                c = (resp.json()["choices"][0]["message"].get("content") or "").strip().strip("\"'")
                if c and "0 replies" not in c.lower() and "1 reply" not in c.lower():
                    return c
        except Exception as e:
            logger.warning(f"LLM reply generation error ({model_name}): {e}")

    return f"Setuju banget kak! Emang tingkah anabul selalu bikin gemes sendiri ya di rumah 😻🐾"


def run_replier(max_replies: int = 15) -> list:
    results = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            page = ctx.new_page()
            page.set_viewport_size({"width": 1280, "height": 900})

            logger.info("Opening YouTube Studio Comments inbox...")
            page.goto(
                "https://studio.youtube.com/channel/UCNPtjF2aB0wvWHI0q7hhcCg/comments/inbox",
                wait_until="domcontentloaded",
                timeout=40000
            )
            time.sleep(5)

            for i in range(max_replies):
                threads = page.locator("ytcp-comment-thread")
                count = threads.count()
                logger.info(f"Iteration {i+1}: Found {count} comment threads displayed.")
                if count == 0:
                    logger.info("No more comments to respond to!")
                    break

                target = threads.first

                # Extract metadata cleanly from ytcp-comment#comment yt-formatted-string#content-text
                info = target.evaluate("""t => {
                    const mainComment = t.querySelector('ytcp-comment#comment') || t.querySelector('ytcp-comment') || t;
                    const authorEl = mainComment.querySelector('a#name, #author-name, .author-name');
                    const contentEl = mainComment.querySelector('yt-formatted-string#content-text, #content-text, span#expander');
                    const videoEl = t.querySelector('#video-title');

                    return {
                        author: authorEl ? authorEl.innerText.trim() : 'Teman Anabul',
                        comment: contentEl ? contentEl.innerText.trim() : '',
                        video: videoEl ? videoEl.innerText.trim() : 'Video Shorts'
                    };
                }""")

                author = info.get("author") or "Teman Anabul"
                comment_text = (info.get("comment") or "").strip()
                video_title = info.get("video") or "Shorts"

                logger.info(f"[{i+1}/{max_replies}] Replying to {author} on '{video_title}': \"{comment_text}\"")

                # 1. Click Heart ❤️
                try:
                    heart = target.locator('ytcp-icon-button[aria-label="Heart"], #creator-heart-button').first
                    if heart.is_visible():
                        heart.click()
                        time.sleep(0.8)
                except Exception as he:
                    logger.warning(f"Heart button click issue: {he}")

                # 2. Click Like 👍
                try:
                    like = target.locator('ytcp-icon-button[aria-label="Like"], ytcp-comment-toggle-button#like-button').first
                    if like.is_visible():
                        like.click()
                        time.sleep(0.8)
                except Exception as le:
                    logger.warning(f"Like button click issue: {le}")

                # 3. Click Reply button
                reply_clicked = False
                try:
                    reply_btn = target.locator('ytcp-comment-button#reply-button, ytcp-button:has-text("Reply")').first
                    if reply_btn.is_visible():
                        reply_btn.click()
                        reply_clicked = True
                        time.sleep(1.5)
                except Exception as re_err:
                    logger.warning(f"Reply button click issue: {re_err}")

                if not reply_clicked:
                    logger.warning("Could not open reply editor, skipping to next.")
                    continue

                # 4. Generate & fill context-aware reply
                reply_msg = draft_reply(video_title, comment_text, author)
                logger.info(f"Drafted reply: \"{reply_msg}\"")

                textarea = target.locator('textarea#textarea').first
                if textarea.is_visible():
                    textarea.fill(reply_msg)
                    time.sleep(1)

                    # 5. Submit reply
                    submit_btn = target.locator('ytcp-comment-button#submit-button, ytcp-button#reply-button').last
                    if submit_btn.is_visible():
                        submit_btn.click()
                        logger.info(f"✅ Submitted reply for {author}!")
                        time.sleep(3.5)

                        results.append({
                            "author": author,
                            "video": video_title,
                            "comment": comment_text,
                            "reply": reply_msg
                        })

                # Refresh page every 4 replies to get fresh list
                if (i + 1) % 4 == 0:
                    logger.info("Refreshing Studio inbox to load updated list...")
                    page.reload(wait_until="domcontentloaded")
                    time.sleep(4)

            final_ss = str(DATA_DIR / "studio_inbox_cleared.png")
            page.screenshot(path=final_ss)
            logger.info(f"All done! Final screenshot saved to: {final_ss}")
            page.close()

        except Exception as e:
            logger.error(f"Error in run_replier: {e}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Doni Studio Auto-Replier")
    parser.add_argument("--limit", type=int, default=15, help="Max comments to reply to")
    args = parser.parse_args()

    res = run_replier(max_replies=args.limit)
    print(json.dumps(res, indent=2, ensure_ascii=False))
