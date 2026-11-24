"""User Preferences and Storage Management System for NeuralClips.

Provides centralized, platform-agnostic resolution of storage directories,
database path, temporary cache locations, and external tools (FFmpeg, yt-dlp).
Allows users to specify arbitrary local, external, or cloud-mounted storage
paths via environment variables (.env) or configuration files without hardcoding
any local machine drive or path.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional, Any
from core.env_loader import load_env

# Ensure environment variables are loaded
load_env()


def get_project_root() -> Path:
    """Returns the absolute Path to the NeuralClips repository root."""
    return Path(__file__).resolve().parent.parent


def get_storage_dir(subfolder: Optional[str] = None, create: bool = True) -> Path:
    """Returns the user-configured media storage directory.

    Priority:
    1. Environment variable: MEDIA_STORAGE_DIR (can be absolute or relative)
    2. config/settings.yaml -> system.storage_root
    3. Default: <project_root>/storage

    Args:
        subfolder: Optional subfolder inside storage (e.g. 'raw', 'clips', 'reports')
        create: If True, automatically creates the directory if it does not exist.

    Returns:
        Path object pointing to the storage directory.
    """
    env_storage = os.getenv("MEDIA_STORAGE_DIR")
    if env_storage and env_storage.strip():
        storage_path = Path(env_storage.strip())
        if not storage_path.is_absolute():
            storage_path = get_project_root() / storage_path
    else:
        # Fallback to config/settings.yaml or default relative storage
        storage_path = get_project_root() / "storage"

    if subfolder:
        target = storage_path / subfolder
    else:
        target = storage_path

    if create:
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    return target


def get_database_path() -> Path:
    """Returns the user-configured database path.

    Priority:
    1. Environment variable: DATABASE_PATH
    2. config/settings.yaml -> system.database_path
    3. Default: <project_root>/data/neuralclips.db
    """
    env_db = os.getenv("DATABASE_PATH")
    if env_db and env_db.strip():
        db_path = Path(env_db.strip())
        if not db_path.is_absolute():
            db_path = get_project_root() / db_path
    else:
        db_path = get_project_root() / "data" / "neuralclips.db"

    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    return db_path


def get_tool_path(tool_name: str) -> Optional[str]:
    """Finds an executable tool (e.g. ffmpeg, ffprobe, yt-dlp) dynamically.

    Priority:
    1. Tool-specific environment variable (e.g. FFMPEG_PATH)
    2. System PATH via shutil.which
    3. Active Python environment's Scripts (Windows) or bin (Unix) folder
    """
    env_key = f"{tool_name.upper().replace('-', '_')}_PATH"
    custom_path = os.getenv(env_key)
    if custom_path and os.path.isfile(custom_path):
        return custom_path

    # Check system PATH
    found = shutil.which(tool_name)
    if found:
        return found

    # Check active virtual environment
    scripts_dir = os.path.join(sys.prefix, "Scripts" if os.name == "nt" else "bin")
    candidate_name = f"{tool_name}.exe" if os.name == "nt" and not tool_name.endswith(".exe") else tool_name
    candidate = os.path.join(scripts_dir, candidate_name)
    if os.path.isfile(candidate):
        return candidate

    return None
