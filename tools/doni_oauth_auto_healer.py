#!/usr/bin/env python3
"""
tools/doni_oauth_auto_healer.py
===============================
Autonomous Self-Healing OAuth 2.0 Refresh Token Renewer for @DoniesDaily.
Uses the authenticated persistent Chrome profile on DISPLAY=:99 (CDP :9222)
to re-authorize YouTube Data API v3 whenever Google's 7-day Testing token expires.
"""
import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from playwright.sync_api import sync_playwright

OAUTH_PATH = Path("/home/ubuntu/.config/youtube/doniesdaily_oauth.json")
CHROME_PROFILE = "/home/ubuntu/apps/ugc-lemonaru/data/chrome_persistent"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


def ensure_chrome_cdp() -> None:
    try:
        urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=2)
        return
    except Exception:
        pass

    for lock in Path(CHROME_PROFILE).glob("Singleton*"):
        try:
            lock.unlink()
        except Exception:
            pass

    env = dict(**os.environ, DISPLAY=":99")
    subprocess.Popen(
        [
            "/usr/bin/google-chrome",
            f"--user-data-dir={CHROME_PROFILE}",
            "--remote-debugging-port=9222",
            "--no-sandbox",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=1280,850",
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(4)


def heal_oauth() -> bool:
    cfg = json.loads(OAUTH_PATH.read_text(encoding="utf-8"))
    client_config = {
        "installed": {
            "client_id": cfg["client_id"],
            "client_secret": cfg["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": cfg.get("token_uri", "https://oauth2.googleapis.com/token"),
            "redirect_uris": ["http://localhost:8080/", "http://localhost:8080"],
        }
    }
    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri="http://localhost:8080/",
    )
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    ensure_chrome_cdp()
    captured_urls = []

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.new_page()
        page.on(
            "request",
            lambda req: captured_urls.append(req.url)
            if "localhost:8080" in req.url and "code=" in req.url
            else None,
        )
        page.goto(auth_url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)

        loc = page.locator('[data-identifier="doniesdaily@gmail.com"]')
        if loc.count() > 0:
            loc.first.click()
        else:
            page.get_by_text("doniesdaily@gmail.com").first.click()
        time.sleep(4)

        for _ in range(6):
            if captured_urls or ("localhost:8080" in page.url and "code=" in page.url):
                if "code=" in page.url and page.url not in captured_urls:
                    captured_urls.append(page.url)
                break

            cbs = page.locator('input[type="checkbox"]')
            for i in range(cbs.count()):
                cb = cbs.nth(i)
                if not cb.is_checked():
                    cb.click(force=True)
            time.sleep(1)

            for label in ["Continue", "Allow", "Lanjutkan", "Izinkan"]:
                btn = page.get_by_role("button", name=label)
                if btn.count() > 0 and btn.first.is_visible():
                    btn.first.click()
                    break
            time.sleep(4)

        page.close()

    if not captured_urls:
        return False

    parsed = urllib.parse.urlparse(captured_urls[0])
    code = urllib.parse.parse_qs(parsed.query)["code"][0]
    flow.fetch_token(code=code)
    creds = flow.credentials

    cfg["token"] = creds.token
    cfg["access_token"] = creds.token
    if creds.refresh_token:
        cfg["refresh_token"] = creds.refresh_token
    cfg["scopes"] = creds.scopes or SCOPES
    OAUTH_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return True


if __name__ == "__main__":
    ok = heal_oauth()
    print("OAuth Auto-Healer Result:", ok)
    raise SystemExit(0 if ok else 1)
