"""YouTube OAuth Scope Upgrade Tool.

Allows user to grant the 'https://www.googleapis.com/auth/youtube' scope
required to edit video privacy (unlisting, updates, deletions).
Starts a local listener on http://localhost:8080/ to automatically capture the auth code,
exchanges it for a new refresh token, and updates .env.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

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

auth_code_received = None

class OAuthHandler(BaseHTTPRequestHandler):
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
            <html><body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #4CAF50;">Authorization Successful!</h1>
                <p>The YouTube scope upgrade is complete. You can close this window and return to the terminal.</p>
            </body></html>
            """)
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            err = params.get("error", ["Unknown error"])[0]
            self.wfile.write(f"<html><body><h1>Authorization Failed: {err}</h1></body></html>".encode("utf-8"))

    def log_message(self, format, *args):
        pass  # Suppress default server access logs

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
        print(f"Error: {env_path} not found!")
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
    print(f"Successfully updated YOUTUBE_REFRESH_TOKEN in {env_path}")

def main():
    print("=" * 80)
    print("YOUTUBE OAUTH SCOPE UPGRADE HELPER")
    print("=" * 80)
    print(f"Client ID: {CLIENT_ID}")
    print("Required Scopes:")
    for s in SCOPES:
        print(f"  - {s}")
    print("-" * 80)

    auth_url = get_auth_url()
    print("1. Click or open this authorization URL in your browser:")
    print("\n" + auth_url + "\n")
    print("-" * 80)
    print("2. Waiting for approval on http://localhost:8080/ ...")
    print("   (Or press Ctrl+C if you want to enter the code manually)")

    server = HTTPServer(("localhost", 8080), OAuthHandler)
    server.timeout = 180  # Wait up to 3 minutes

    while not auth_code_received:
        server.handle_request()

    print(f"\nReceived Authorization Code!")
    print("Exchanging authorization code for updated tokens...")
    tokens = exchange_code(auth_code_received)

    new_refresh = tokens.get("refresh_token")
    if not new_refresh:
        print("Notice: No new refresh_token returned (Google may reuse the existing token).")
        print("Checking scopes of returned access_token...")
    else:
        print("New refresh token received! Updating .env...")
        update_env_file(new_refresh)

    # Verify scopes
    acc = tokens.get("access_token")
    if acc:
        info_req = urllib.request.Request(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={acc}")
        with urllib.request.urlopen(info_req) as resp:
            info = json.loads(resp.read().decode())
            print("Verified Active Scopes on new token:")
            print(f"  {info.get('scope')}")

    print("=" * 80)
    print("Upgrade complete! You can now run: python scripts/unlist_low_view_clips.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
