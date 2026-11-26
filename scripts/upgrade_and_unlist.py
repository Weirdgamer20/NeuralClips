"""One-Click YouTube Scope Upgrade & Automated Unlister.

1. Starts a local web receiver on http://localhost:8080/
2. Opens the Google OAuth permission page in the user's default browser
3. As soon as the user clicks 'Allow', captures the code, updates .env with the full 'youtube' scope
4. Immediately unlists all 289 videos with under 3 views with live progress logging
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime, timezone, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.env_loader import load_env
load_env()

CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8080/"

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

IST = timezone(timedelta(hours=5, minutes=30))
ANALYTICS_FILE = BASE_DIR / "storage" / "all_historical_videos_analytics.json"
PROGRESS_FILE = BASE_DIR / "storage" / "unlisted_clips_progress.json"

auth_code_received = None

def log(msg):
    try:
        clean = str(msg).encode("ascii", "replace").decode("ascii")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {clean}", flush=True)
    except Exception:
        pass

class OAuthReceiver(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code_received
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            auth_code_received = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""
            <html><body style="font-family: sans-serif; text-align: center; padding: 60px; background: #0f172a; color: #f8fafc;">
                <h1 style="color: #22c55e; font-size: 32px;">Authorization Successful!</h1>
                <p style="font-size: 18px; color: #94a3b8;">NeuralClips now has video management permission.</p>
                <p style="font-size: 16px; color: #38bdf8;">Unlisting of clips with under 3 views has begun in the terminal!</p>
                <p style="font-size: 14px; color: #64748b;">You can close this tab safely.</p>
            </body></html>
            """)
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            err = params.get("error", ["Unknown error"])[0]
            self.wfile.write(f"<html><body><h1>Authorization Failed: {err}</h1></body></html>".encode("utf-8"))

    def log_message(self, format, *args):
        pass

def get_auth_url() -> str:
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

def exchange_code(code: str) -> dict:
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def update_env_file(new_refresh_token: str):
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    content = env_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("YOUTUBE_REFRESH_TOKEN="):
            lines[i] = f"YOUTUBE_REFRESH_TOKEN={new_refresh_token}"
            updated = True
            break
    if not updated:
        lines.append(f"YOUTUBE_REFRESH_TOKEN={new_refresh_token}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"Updated YOUTUBE_REFRESH_TOKEN in .env")

def unlist_video(video_id: str, title: str, category_id: str, token: str) -> bool:
    update_url = "https://www.googleapis.com/youtube/v3/videos?part=snippet,status"
    payload = {
        "id": video_id,
        "snippet": {
            "title": title,
            "categoryId": category_id or "20"
        },
        "status": {
            "privacyStatus": "unlisted"
        }
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        update_url,
        data=data_bytes,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="PUT"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("status", {}).get("privacyStatus") == "unlisted"

def main():
    log("=" * 80)
    log("ONE-CLICK YOUTUBE SCOPE UPGRADE & AUTOMATED UNLISTER")
    log("=" * 80)

    auth_url = get_auth_url()
    log("\n1. Opening Google Permission page in default browser...")
    log("   (If it doesn't open automatically, click this link:)")
    log(f"   {auth_url}\n")

    try:
        webbrowser.open(auth_url)
    except Exception as e:
        log(f"Notice opening browser: {e}")

    log("2. Waiting for your approval on http://localhost:8080/ ...")
    HTTPServer.allow_reuse_address = True
    server = HTTPServer(("localhost", 8080), OAuthReceiver)
    server.timeout = 1800  # 30 minutes

    start_wait = time.time()
    while not auth_code_received:
        if time.time() - start_wait > 1800:
            log("Timeout waiting for authorization.")
            return
        server.handle_request()

    log("\nAuthorization Code Received! Exchanging for refreshed token...")
    tokens = exchange_code(auth_code_received)
    new_refresh = tokens.get("refresh_token")
    access_token = tokens.get("access_token")

    if new_refresh:
        update_env_file(new_refresh)
    else:
        log("Google reused existing refresh token. Using active access token.")

    # 3. Load candidates from analytics
    if not ANALYTICS_FILE.exists():
        log(f"Error: {ANALYTICS_FILE} not found!")
        return

    with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_videos = data.get("videos", [])
    candidates = [
        v for v in all_videos
        if v.get("privacy") == "public" and int(v.get("views", 0)) < 3
    ]
    log(f"\nTotal public videos with under 3 views: {len(candidates)}")

    # Load progress
    progress = {}
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as pf:
                progress = json.load(pf)
        except Exception:
            progress = {}

    already_done = {k for k, v in progress.items() if v.get("status") == "unlisted"}
    remaining = [c for c in candidates if c["video_id"] not in already_done]
    log(f"Already unlisted: {len(already_done)} | Remaining: {len(remaining)}")

    token = access_token
    success_count = 0

    log("\n" + "=" * 80)
    log("STARTING UNLISTING PROCESS NOW...")
    log("=" * 80)

    for idx, item in enumerate(remaining, 1):
        vid = item["video_id"]
        title = item.get("title", "")
        views = item.get("views", 0)
        pub_ist = item.get("published_at_ist", "")[:10]

        log(f"[{idx}/{len(remaining)}] Unlisting ({views} views, {pub_ist}): '{title[:45]}...'")

        # Refresh token every 30 videos if refresh token exists
        if idx % 30 == 0 and new_refresh:
            try:
                from sources.youtube_source import get_oauth_token
                token = get_oauth_token() or token
            except Exception:
                pass

        try:
            cat_id = item.get("categoryId", "20")
            ok = unlist_video(vid, title, cat_id, token)
            if ok:
                log(f"   -> SUCCESS! Video is now UNLISTED: https://www.youtube.com/shorts/{vid}")
                progress[vid] = {
                    "video_id": vid,
                    "title": title,
                    "views": views,
                    "status": "unlisted",
                    "unlisted_at": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")
                }
                success_count += 1
            else:
                log(f"   -> Failed for {vid}")
                progress[vid] = {"status": "failed", "video_id": vid}

            with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                json.dump(progress, pf, indent=2)

            time.sleep(0.4)

        except urllib.error.HTTPError as he:
            err_b = he.read().decode("utf-8", errors="replace")
            log(f"   HTTP Error {he.code}: {err_b}")
            if "quotaExceeded" in err_b or "dailyLimitExceeded" in err_b:
                log("   Daily YouTube API quota reached! Will resume on next reset.")
                break
        except Exception as e:
            log(f"   Error: {e}")

    log("\n" + "=" * 80)
    log(f"BATCH COMPLETE! Successfully unlisted {success_count} clips in this run.")
    log(f"Total unlisted in progress file: {len([k for k, v in progress.items() if v.get('status') == 'unlisted'])}")
    log("=" * 80)

if __name__ == "__main__":
    main()
