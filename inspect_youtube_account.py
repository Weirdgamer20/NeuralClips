"""Inspect YouTube Channel Details via Official Data API v3."""

import json
import os
import sys
import urllib.parse
import urllib.request

# Ensure workspace root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core.env_loader


def get_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    """Exchanges refresh token for access token using standard library HTTP."""
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            return res_data.get("access_token")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[ERROR] Failed to refresh token: HTTP {e.code} - {error_body}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to connect to OAuth endpoint: {e}")
        sys.exit(1)


def fetch_channel_info(access_token: str, channel_id: str = None) -> dict:
    """Fetches channel metadata and statistics."""
    base_url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet,contentDetails,statistics,status",
    }
    if channel_id:
        params["id"] = channel_id
    else:
        params["mine"] = "true"

    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("items", [])
            if not items and not channel_id:
                # If mine=true returned nothing, fallback to channel_id if configured
                cid = os.getenv("YOUTUBE_CHANNEL_ID")
                if cid:
                    return fetch_channel_info(access_token, channel_id=cid)
            return items[0] if items else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[ERROR] YouTube API channels query failed: HTTP {e.code} - {error_body}")
        sys.exit(1)


def fetch_recent_videos(access_token: str, uploads_playlist_id: str, max_results: int = 5) -> list:
    """Fetches most recent uploads from channel uploads playlist."""
    if not uploads_playlist_id:
        return []

    url = "https://www.googleapis.com/youtube/v3/playlistItems?" + urllib.parse.urlencode({
        "part": "snippet",
        "playlistId": uploads_playlist_id,
        "maxResults": max_results,
    })
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", [])
    except Exception as e:
        print(f"[WARNING] Could not fetch recent uploads: {e}")
        return []


def main():
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")

    if not client_id or not client_secret or not refresh_token:
        print("[ERROR] Missing required YouTube credentials in .env")
        sys.exit(1)

    print("Authenticating with Google OAuth2...")
    access_token = get_access_token(client_id, client_secret, refresh_token)
    if not access_token:
        print("[ERROR] No access token received.")
        sys.exit(1)

    print("Fetching channel metadata from YouTube Data API v3...")
    channel = fetch_channel_info(access_token, channel_id)

    if not channel:
        print("[WARNING] No channel details returned. The account might not have a channel created yet.")
        sys.exit(0)

    snippet = channel.get("snippet", {})
    stats = channel.get("statistics", {})
    content = channel.get("contentDetails", {})
    uploads_id = content.get("relatedPlaylists", {}).get("uploads")

    print("\n" + "=" * 60)
    print("YOUTUBE ACCOUNT / CHANNEL INSPECTION REPORT")
    print("=" * 60)
    print(f"Channel Title:       {snippet.get('title')}")
    print(f"Custom URL / Handle: {snippet.get('customUrl', 'N/A')}")
    print(f"Channel ID:          {channel.get('id')}")
    print(f"Created Date:        {snippet.get('publishedAt')}")
    print(f"Country:             {snippet.get('country', 'N/A')}")
    print(f"Subscribers:         {stats.get('subscriberCount', 'Hidden')}")
    print(f"Total Video Count:   {stats.get('videoCount', '0')}")
    print(f"Total Views:         {stats.get('viewCount', '0')}")
    print(f"Description:         {snippet.get('description', '').strip() or 'None'}")
    print("-" * 60)

    if uploads_id:
        videos = fetch_recent_videos(access_token, uploads_id, max_results=5)
        print(f"Recent Uploads ({len(videos)}):")
        for v in videos:
            snip = v.get("snippet", {})
            v_id = snip.get("resourceId", {}).get("videoId")
            v_title = snip.get("title")
            v_date = snip.get("publishedAt")
            print(f"  - [{v_date}] {v_title} (https://youtu.be/{v_id})")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
