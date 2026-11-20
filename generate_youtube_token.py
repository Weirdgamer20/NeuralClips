"""Automated YouTube OAuth 2.0 Token Receiver and Channel Inspector."""

import json
import os
import sys
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core.env_loader

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]

PORT = 8088
REDIRECT_URI = f"http://localhost:{PORT}/"


def generate_auth_url(client_id: str) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"


def exchange_code_for_tokens(client_id: str, client_secret: str, code: str) -> dict:
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        print(f"\n[ERROR] Token exchange failed: HTTP {e.code} - {err}")
        return {}


def update_env_file(key: str, value: str) -> None:
    env_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env.txt"),
    ]
    for p in env_paths:
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        found = False
        for line in lines:
            if line.strip().startswith(f"{key}=") or line.strip().startswith(f"{key} ="):
                new_lines.append(f"{key}={value}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"{key}={value}\n")
        with open(p, "w", encoding="utf-8") as f:
            f.writelines(new_lines)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    client_id = ""
    client_secret = ""

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)

        if "code" in query:
            code = query["code"][0]
            tokens = exchange_code_for_tokens(self.client_id, self.client_secret, code)
            refresh_token = tokens.get("refresh_token")
            access_token = tokens.get("access_token")

            if refresh_token:
                update_env_file("YOUTUBE_REFRESH_TOKEN", refresh_token)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                html = """
                <html>
                <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #2e7d32;">Authorization Successful!</h1>
                    <p>Your real YouTube Refresh Token has been acquired and saved to <code>.env</code>.</p>
                    <p>You can close this browser tab now.</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode("utf-8"))
                print("\n[SUCCESS] Captured authorization code and saved real YOUTUBE_REFRESH_TOKEN to .env!")

                # Query channel details immediately
                try:
                    import inspect_youtube_account
                    print("\nFetching authorized channel details...")
                    ch = inspect_youtube_account.fetch_channel_info(access_token)
                    if ch:
                        cid = ch.get("id")
                        title = ch.get("snippet", {}).get("title")
                        update_env_file("YOUTUBE_CHANNEL_ID", cid)
                        print(f"Connected YouTube Channel: {title} (ID: {cid})")
                except Exception as e:
                    print(f"Note: {e}")

            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Failed to obtain refresh token. Please check Google Cloud settings.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No authorization code received.")


def listen_for_callback(client_id: str, client_secret: str, timeout: int = 120):
    OAuthCallbackHandler.client_id = client_id
    OAuthCallbackHandler.client_secret = client_secret
    server = HTTPServer(("localhost", PORT), OAuthCallbackHandler)
    server.timeout = timeout
    print(f"Waiting for authorization callback on http://localhost:{PORT}/ (timeout: {timeout}s)...")
    server.handle_request()
    server.server_close()


if __name__ == "__main__":
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")

    if not client_id or client_id.startswith("your_"):
        print("[ERROR] Please set your real YOUTUBE_CLIENT_ID in .env")
        sys.exit(1)

    auth_url = generate_auth_url(client_id)
    print("\n" + "=" * 60)
    print("YOUTUBE AUTHORIZATION")
    print("=" * 60)
    print("Please open this link in your browser to authorize access to your YouTube channel:\n")
    print(auth_url)
    print("\n" + "=" * 60)

    # If code passed as argument:
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        code = sys.argv[1].strip()
        tokens = exchange_code_for_tokens(client_id, client_secret, code)
        rt = tokens.get("refresh_token")
        if rt:
            update_env_file("YOUTUBE_REFRESH_TOKEN", rt)
            print("[SUCCESS] Real YOUTUBE_REFRESH_TOKEN acquired and saved to .env!")
        else:
            print("[ERROR] Could not exchange code for refresh token.")
    elif "--listen" in sys.argv:
        listen_for_callback(client_id, client_secret)
