"""YouTube URL parsing and validation."""

import re
from typing import Optional, Tuple
from urllib.parse import parse_qs, urlparse

YOUTUBE_DOMAINS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "youtube-nocookie.com",
}


def extract_video_id(url: str) -> Optional[str]:
    """Extracts 11-character canonical YouTube video ID from supported URL formats."""
    if not url or not isinstance(url, str):
        return None

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception:
        return None

    domain = parsed.netloc.lower()
    if domain not in YOUTUBE_DOMAINS:
        return None

    # youtu.be/<id>
    if domain == "youtu.be":
        path_parts = parsed.path.strip("/").split("/")
        if path_parts and len(path_parts[0]) == 11 and re.match(r"^[0-9A-Za-z_-]{11}$", path_parts[0]):
            return path_parts[0]

    # youtube.com/watch?v=<id>
    if parsed.path == "/watch":
        query = parse_qs(parsed.query)
        v_list = query.get("v")
        if v_list and len(v_list[0]) == 11 and re.match(r"^[0-9A-Za-z_-]{11}$", v_list[0]):
            return v_list[0]

    # youtube.com/live/<id> or /shorts/<id>
    for prefix in ["/live/", "/shorts/", "/v/", "/embed/"]:
        if parsed.path.startswith(prefix):
            vid_id = parsed.path[len(prefix):].split("/")[0].split("?")[0]
            if len(vid_id) == 11 and re.match(r"^[0-9A-Za-z_-]{11}$", vid_id):
                return vid_id

    return None


def validate_youtube_url(url: str) -> Tuple[bool, Optional[str], str]:
    """Validates URL syntax and returns (is_valid, video_id, error_message)."""
    vid_id = extract_video_id(url)
    if not vid_id:
        return False, None, f"Invalid YouTube URL syntax: '{url}'"
    return True, vid_id, "Valid YouTube URL"
