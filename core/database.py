"""Database connection and schema initialization for NeuralClips.

Implements all 16 required logical entities with transactional WAL mode.
"""

import os
import sqlite3
from typing import Optional

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- 1. Daily Batches
CREATE TABLE IF NOT EXISTS daily_batches (
    batch_id TEXT PRIMARY KEY,
    batch_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('CREATED', 'PROCESSING', 'COMPLETED', 'PARTIALLY_COMPLETED', 'FAILED')),
    total_sources INTEGER NOT NULL DEFAULT 5,
    valid_sources INTEGER NOT NULL DEFAULT 0,
    clips_produced INTEGER NOT NULL DEFAULT 0,
    youtube_published INTEGER NOT NULL DEFAULT 0,
    instagram_published INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Source Permissions
CREATE TABLE IF NOT EXISTS source_permissions (
    creator_id TEXT PRIMARY KEY,
    creator_name TEXT NOT NULL,
    channel_id TEXT NOT NULL UNIQUE,
    channel_url TEXT NOT NULL,
    permission_status TEXT NOT NULL CHECK(permission_status IN ('AUTHORIZED', 'PENDING', 'EXPIRED', 'REVOKED', 'DENIED')),
    permission_evidence TEXT,
    recording_permitted INTEGER NOT NULL DEFAULT 0,
    editing_permitted INTEGER NOT NULL DEFAULT 0,
    redistribution_permitted INTEGER NOT NULL DEFAULT 0,
    commercial_use_permitted INTEGER NOT NULL DEFAULT 0,
    authorized_destinations TEXT NOT NULL DEFAULT '["YOUTUBE", "INSTAGRAM"]',
    expiration_date TEXT,
    revoked INTEGER NOT NULL DEFAULT 0,
    crop_profile TEXT DEFAULT 'default_fallback',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Source Streams
CREATE TABLE IF NOT EXISTS source_streams (
    source_id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL,
    original_url TEXT NOT NULL,
    canonical_video_id TEXT,
    channel_id TEXT,
    title TEXT,
    source_type TEXT NOT NULL CHECK(source_type IN (
        'COMPLETED_VOD', 'ACTIVE_LIVESTREAM', 'SCHEDULED_LIVESTREAM',
        'UNAVAILABLE', 'ACCESS_DENIED', 'PERMISSION_REQUIRED', 'PROCESSING', 'COMPLETED', 'FAILED'
    )),
    duration_seconds REAL,
    fps REAL,
    resolution TEXT,
    permission_verified INTEGER NOT NULL DEFAULT 0,
    scheduled_start_time TEXT,
    actual_start_time TEXT,
    stream_ended INTEGER NOT NULL DEFAULT 0,
    crop_profile TEXT DEFAULT 'default_fallback',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(batch_id) REFERENCES daily_batches(batch_id) ON DELETE CASCADE
);

-- 4. Capture Jobs
CREATE TABLE IF NOT EXISTS capture_jobs (
    capture_job_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    worker_id TEXT,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'ACTIVE', 'PAUSED', 'COMPLETED', 'TERMINATED', 'FAILED')),
    last_captured_timestamp REAL NOT NULL DEFAULT 0.0,
    total_segments_captured INTEGER NOT NULL DEFAULT 0,
    stream_url TEXT,
    lease_expires_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_id) REFERENCES source_streams(source_id) ON DELETE CASCADE
);

-- 5. Media Segments
CREATE TABLE IF NOT EXISTS media_segments (
    segment_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    segment_index INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    duration REAL NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    analyzed INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_id) REFERENCES source_streams(source_id) ON DELETE CASCADE,
    UNIQUE(source_id, segment_index)
);

-- 6. Highlight Candidates
CREATE TABLE IF NOT EXISTS highlight_candidates (
    candidate_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    segment_id TEXT,
    start_timestamp REAL NOT NULL,
    end_timestamp REAL NOT NULL,
    duration REAL NOT NULL,
    category TEXT NOT NULL,
    score REAL NOT NULL,
    confidence REAL NOT NULL,
    reason TEXT NOT NULL,
    transcript TEXT,
    suggested_duration INTEGER NOT NULL,
    suggested_title TEXT,
    evaluated INTEGER NOT NULL DEFAULT 0,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_id) REFERENCES source_streams(source_id) ON DELETE CASCADE
);

-- 7. Approved Highlights
CREATE TABLE IF NOT EXISTS approved_highlights (
    highlight_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL UNIQUE,
    source_id TEXT NOT NULL,
    start_timestamp REAL NOT NULL,
    end_timestamp REAL NOT NULL,
    duration REAL NOT NULL,
    score REAL NOT NULL,
    rank_order INTEGER,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    transcript TEXT,
    status TEXT NOT NULL CHECK(status IN ('APPROVED', 'QUEUED', 'RENDERING', 'RENDERED', 'FAILED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(candidate_id) REFERENCES highlight_candidates(candidate_id),
    FOREIGN KEY(source_id) REFERENCES source_streams(source_id)
);

-- 8. Rendered Clips
CREATE TABLE IF NOT EXISTS rendered_clips (
    clip_id TEXT PRIMARY KEY,
    highlight_id TEXT NOT NULL UNIQUE,
    source_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    duration REAL NOT NULL,
    width INTEGER NOT NULL DEFAULT 1080,
    height INTEGER NOT NULL DEFAULT 1920,
    aspect_ratio TEXT NOT NULL DEFAULT '9:16',
    video_codec TEXT NOT NULL DEFAULT 'h264',
    audio_codec TEXT NOT NULL DEFAULT 'aac',
    has_audio INTEGER NOT NULL DEFAULT 1,
    has_captions INTEGER NOT NULL DEFAULT 1,
    file_size_bytes INTEGER NOT NULL,
    validated INTEGER NOT NULL DEFAULT 0,
    validation_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(highlight_id) REFERENCES approved_highlights(highlight_id),
    FOREIGN KEY(source_id) REFERENCES source_streams(source_id)
);

-- 9. YouTube Publications
CREATE TABLE IF NOT EXISTS youtube_publications (
    pub_id TEXT PRIMARY KEY,
    clip_id TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN (
        'PENDING', 'PROCESSING', 'UPLOADING', 'PUBLISHED', 'RETRY_REQUIRED', 'FAILED', 'RATE_LIMITED', 'PERMISSION_BLOCKED'
    )),
    upload_attempts INTEGER NOT NULL DEFAULT 0,
    youtube_video_id TEXT,
    youtube_url TEXT,
    title TEXT NOT NULL,
    description TEXT,
    hashtags TEXT,
    error_message TEXT,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(clip_id) REFERENCES rendered_clips(clip_id)
);

-- 10. Instagram Publications
CREATE TABLE IF NOT EXISTS instagram_publications (
    pub_id TEXT PRIMARY KEY,
    clip_id TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN (
        'PENDING', 'PROCESSING', 'UPLOADING', 'PUBLISHED', 'RETRY_REQUIRED', 'FAILED', 'RATE_LIMITED', 'PERMISSION_BLOCKED'
    )),
    upload_attempts INTEGER NOT NULL DEFAULT 0,
    container_id TEXT,
    instagram_media_id TEXT,
    instagram_reel_url TEXT,
    caption TEXT NOT NULL,
    hashtags TEXT,
    error_message TEXT,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(clip_id) REFERENCES rendered_clips(clip_id)
);

-- 11. Upload History
CREATE TABLE IF NOT EXISTS upload_history (
    history_id TEXT PRIMARY KEY,
    clip_id TEXT NOT NULL,
    platform TEXT NOT NULL CHECK(platform IN ('YOUTUBE', 'INSTAGRAM')),
    platform_video_id TEXT NOT NULL,
    platform_url TEXT,
    status TEXT NOT NULL,
    response_payload TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(clip_id) REFERENCES rendered_clips(clip_id)
);

-- 12. API Quota Usage
CREATE TABLE IF NOT EXISTS api_quota_usage (
    usage_date TEXT NOT NULL,
    platform TEXT NOT NULL CHECK(platform IN ('YOUTUBE', 'INSTAGRAM', 'GEMINI')),
    units_used INTEGER NOT NULL DEFAULT 0,
    units_limit INTEGER NOT NULL,
    last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(usage_date, platform)
);

-- 13. Worker Status
CREATE TABLE IF NOT EXISTS worker_status (
    worker_id TEXT PRIMARY KEY,
    worker_type TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('IDLE', 'BUSY', 'HEARTBEAT', 'DEAD', 'STOPPED')),
    current_job_id TEXT,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    host_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. Job Locks
CREATE TABLE IF NOT EXISTS job_locks (
    lock_name TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

-- 15. Retry Records
CREATE TABLE IF NOT EXISTS retry_records (
    retry_id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL,
    job_id TEXT NOT NULL,
    attempt INTEGER NOT NULL DEFAULT 1,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    error_type TEXT NOT NULL CHECK(error_type IN ('TRANSIENT', 'PERMANENT')),
    last_error TEXT,
    next_retry_at TIMESTAMP NOT NULL,
    resolved INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. Error Logs
CREATE TABLE IF NOT EXISTS error_logs (
    log_id TEXT PRIMARY KEY,
    subsystem TEXT NOT NULL,
    error_code TEXT,
    message TEXT NOT NULL,
    stack_trace TEXT,
    context_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_source_streams_batch ON source_streams(batch_id);
CREATE INDEX IF NOT EXISTS idx_media_segments_source ON media_segments(source_id);
CREATE INDEX IF NOT EXISTS idx_highlight_candidates_source ON highlight_candidates(source_id);
CREATE INDEX IF NOT EXISTS idx_approved_highlights_status ON approved_highlights(status);
CREATE INDEX IF NOT EXISTS idx_rendered_clips_highlight ON rendered_clips(highlight_id);
CREATE INDEX IF NOT EXISTS idx_youtube_publications_status ON youtube_publications(status);
CREATE INDEX IF NOT EXISTS idx_instagram_publications_status ON instagram_publications(status);
CREATE INDEX IF NOT EXISTS idx_retry_records_pending ON retry_records(resolved, next_retry_at);
"""


def get_db_path(custom_path: Optional[str] = None) -> str:
    """Returns absolute path to database, respecting custom path or env."""
    if custom_path:
        path = custom_path
    elif os.getenv("DATABASE_PATH"):
        path = os.getenv("DATABASE_PATH")
    else:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "neuralclips.db")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    return path


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Returns a SQLite connection with row factory and WAL mode enabled."""
    path = get_db_path(db_path)
    conn = sqlite3.connect(path, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_database(db_path: Optional[str] = None) -> None:
    """Initializes the database schema."""
    conn = get_connection(db_path)
    with conn:
        conn.executescript(SCHEMA_SQL)
    conn.close()
