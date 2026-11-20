"""Environment variable loader supporting .env and .env.txt."""

import os
from typing import Optional


def load_env(env_path: Optional[str] = None) -> bool:
    """Loads key-value pairs from .env or .env.txt into os.environ."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    candidates = [
        env_path,
        os.path.join(base_dir, ".env"),
        os.path.join(base_dir, ".env.txt"),
    ]

    target_file = None
    for p in candidates:
        if p and os.path.isfile(p):
            target_file = p
            break

    if not target_file:
        return False

    try:
        with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = val
        return True
    except Exception:
        return False


# Auto-load on import
load_env()

# Ensure virtualenv Scripts directory is on PATH so ffmpeg and yt-dlp are universally discoverable
import sys
_scripts_dir = os.path.dirname(sys.executable)
if _scripts_dir and _scripts_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _scripts_dir + os.pathsep + os.environ.get("PATH", "")

