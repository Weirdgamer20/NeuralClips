"""State Store Data Access Object (DAO) for NeuralClips.

Handles all persistence, state transitions, idempotency checks, and batch queries.
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from core.database import get_connection


def now_utc_iso() -> str:
    """Returns current UTC timestamp in ISO 8601 string format."""
    return datetime.now(timezone.utc).isoformat()


class StateStore:
    """Manages transactional database operations for the NeuralClips pipeline."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)

    # -------------------------------------------------------------------------
    # Daily Batches
    # -------------------------------------------------------------------------
    def create_batch(self, batch_id: str, total_sources: int = 5) -> Dict[str, Any]:
        """Creates a new daily batch record."""
        batch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        now = now_utc_iso()
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO daily_batches (batch_id, batch_date, status, total_sources, created_at, updated_at)
                VALUES (?, ?, 'CREATED', ?, ?, ?)
                ON CONFLICT(batch_id) DO UPDATE SET updated_at = excluded.updated_at
                """,
                (batch_id, batch_date, total_sources, now, now),
            )
        return self.get_batch(batch_id)

    def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a batch by its ID."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM daily_batches WHERE batch_id = ?", (batch_id,)
            ).fetchone()
            return dict(row) if row else None

    def update_batch_status(self, batch_id: str, status: str, **kwargs) -> None:
        """Updates batch status and stats."""
        now = now_utc_iso()
        set_clauses = ["status = ?", "updated_at = ?"]
        params = [status, now]

        for k, v in kwargs.items():
            set_clauses.append(f"{k} = ?")
            params.append(v)
        params.append(batch_id)

        query = f"UPDATE daily_batches SET {', '.join(set_clauses)} WHERE batch_id = ?"
        with self._get_conn() as conn:
            conn.execute(query, params)

    # -------------------------------------------------------------------------
    # Source Streams
    # -------------------------------------------------------------------------
    def create_source_stream(
        self,
        source_id: str,
        batch_id: str,
        original_url: str,
        canonical_video_id: Optional[str] = None,
        source_type: str = "COMPLETED_VOD",
        channel_id: Optional[str] = None,
        title: Optional[str] = None,
        crop_profile: str = "default_fallback",
        permission_verified: bool = False,
    ) -> Dict[str, Any]:
        """Registers a source stream under a batch."""
        now = now_utc_iso()
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO source_streams (
                    source_id, batch_id, original_url, canonical_video_id,
                    channel_id, title, source_type, crop_profile, permission_verified,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_id,
                    batch_id,
                    original_url,
                    canonical_video_id,
                    channel_id,
                    title,
                    source_type,
                    crop_profile,
                    1 if permission_verified else 0,
                    now,
                    now,
                ),
            )
        return self.get_source_stream(source_id)

    def get_source_stream(self, source_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM source_streams WHERE source_id = ?", (source_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_sources_by_batch(self, batch_id: str) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM source_streams WHERE batch_id = ?", (batch_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def find_previous_source(self, canonical_video_id: str) -> Optional[Dict[str, Any]]:
        """Checks if a video was previously submitted and processed."""
        if not canonical_video_id:
            return None
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM source_streams WHERE canonical_video_id = ? ORDER BY created_at DESC LIMIT 1",
                (canonical_video_id,),
            ).fetchone()
            return dict(row) if row else None

    def update_source_status(self, source_id: str, source_type: str, **kwargs) -> None:
        now = now_utc_iso()
        set_clauses = ["source_type = ?", "updated_at = ?"]
        params = [source_type, now]
        for k, v in kwargs.items():
            set_clauses.append(f"{k} = ?")
            params.append(v)
        params.append(source_id)
        query = f"UPDATE source_streams SET {', '.join(set_clauses)} WHERE source_id = ?"
        with self._get_conn() as conn:
            conn.execute(query, params)

    # -------------------------------------------------------------------------
    # Permissions Registry
    # -------------------------------------------------------------------------
    def upsert_permission(self, perm: Dict[str, Any]) -> None:
        dest = json.dumps(perm.get("authorized_destinations", ["YOUTUBE", "INSTAGRAM"]))
        now = now_utc_iso()
        creator_name = perm.get("creator_name") or perm.get("name") or "Unknown Creator"
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO source_permissions (
                    creator_id, creator_name, channel_id, channel_url,
                    permission_status, permission_evidence, recording_permitted,
                    editing_permitted, redistribution_permitted, commercial_use_permitted,
                    authorized_destinations, expiration_date, revoked, crop_profile,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(creator_id) DO UPDATE SET
                    creator_name = excluded.creator_name,
                    channel_id = excluded.channel_id,
                    channel_url = excluded.channel_url,
                    permission_status = excluded.permission_status,
                    permission_evidence = excluded.permission_evidence,
                    recording_permitted = excluded.recording_permitted,
                    editing_permitted = excluded.editing_permitted,
                    redistribution_permitted = excluded.redistribution_permitted,
                    commercial_use_permitted = excluded.commercial_use_permitted,
                    authorized_destinations = excluded.authorized_destinations,
                    expiration_date = excluded.expiration_date,
                    revoked = excluded.revoked,
                    crop_profile = excluded.crop_profile,
                    updated_at = excluded.updated_at
                """,
                (
                    perm["creator_id"],
                    creator_name,
                    perm["channel_id"],
                    perm["channel_url"],
                    perm["permission_status"],
                    perm.get("permission_evidence"),
                    1 if perm.get("recording_permitted") else 0,
                    1 if perm.get("editing_permitted") else 0,
                    1 if perm.get("redistribution_permitted") else 0,
                    1 if perm.get("commercial_use_permitted") else 0,
                    dest,
                    perm.get("expiration_date"),
                    1 if perm.get("revoked") else 0,
                    perm.get("crop_profile", "default_fallback"),
                    now,
                    now,
                ),
            )

    def get_permission_by_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM source_permissions WHERE channel_id = ?", (channel_id,)
            ).fetchone()
            if row:
                d = dict(row)
                d["authorized_destinations"] = json.loads(d["authorized_destinations"])
                return d
            return None

    # -------------------------------------------------------------------------
    # Media Segments
    # -------------------------------------------------------------------------
    def add_segment(
        self,
        segment_id: str,
        source_id: str,
        segment_index: int,
        file_path: str,
        start_time: float,
        end_time: float,
        file_size_bytes: int,
    ) -> None:
        duration = round(end_time - start_time, 2)
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO media_segments (
                    segment_id, source_id, segment_index, file_path,
                    start_time, end_time, duration, file_size_bytes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, segment_index) DO NOTHING
                """,
                (
                    segment_id,
                    source_id,
                    segment_index,
                    file_path,
                    start_time,
                    end_time,
                    duration,
                    file_size_bytes,
                ),
            )

    def get_unanalyzed_segments(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM media_segments WHERE analyzed = 0 ORDER BY source_id, segment_index ASC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def mark_segment_analyzed(self, segment_id: str) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE media_segments SET analyzed = 1 WHERE segment_id = ?",
                (segment_id,),
            )

    # -------------------------------------------------------------------------
    # Highlights & Candidates
    # -------------------------------------------------------------------------
    def add_highlight_candidate(self, candidate: Dict[str, Any]) -> str:
        cand_id = candidate.get("candidate_id", str(uuid.uuid4()))
        duration = round(candidate["end_timestamp"] - candidate["start_timestamp"], 2)
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO highlight_candidates (
                    candidate_id, source_id, segment_id, start_timestamp, end_timestamp,
                    duration, category, score, confidence, reason, transcript,
                    suggested_duration, suggested_title
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cand_id,
                    candidate["source_id"],
                    candidate.get("segment_id"),
                    candidate["start_timestamp"],
                    candidate["end_timestamp"],
                    duration,
                    candidate["category"],
                    candidate["score"],
                    candidate.get("confidence", 1.0),
                    candidate["reason"],
                    candidate.get("transcript", ""),
                    candidate.get("suggested_duration", 45),
                    candidate.get("suggested_title", "Epic Moment"),
                ),
            )
        return cand_id

    def get_unapproved_candidates(self, min_score: float = 75.0) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM highlight_candidates
                WHERE evaluated = 0 AND score >= ?
                ORDER BY score DESC
                """,
                (min_score,),
            ).fetchall()
            return [dict(r) for r in rows]

    def approve_highlight(
        self,
        highlight_id: str,
        candidate_id: str,
        source_id: str,
        start_ts: float,
        end_ts: float,
        score: float,
        category: str,
        title: str,
        transcript: str = "",
        rank_order: Optional[int] = None,
    ) -> None:
        duration = round(end_ts - start_ts, 2)
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO approved_highlights (
                    highlight_id, candidate_id, source_id, start_timestamp, end_timestamp,
                    duration, score, rank_order, category, title, transcript, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'APPROVED')
                """,
                (
                    highlight_id,
                    candidate_id,
                    source_id,
                    start_ts,
                    end_ts,
                    duration,
                    score,
                    rank_order,
                    category,
                    title,
                    transcript,
                ),
            )
            conn.execute(
                "UPDATE highlight_candidates SET evaluated = 1 WHERE candidate_id = ?",
                (candidate_id,),
            )

    def get_highlights_for_rendering(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT h.*, s.original_url, s.crop_profile as source_crop_profile
                FROM approved_highlights h
                JOIN source_streams s ON h.source_id = s.source_id
                WHERE h.status IN ('APPROVED', 'QUEUED')
                ORDER BY h.score DESC LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def update_highlight_status(self, highlight_id: str, status: str) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE approved_highlights SET status = ? WHERE highlight_id = ?",
                (status, highlight_id),
            )

    # -------------------------------------------------------------------------
    # Rendered Clips & Publishing Records
    # -------------------------------------------------------------------------
    def register_rendered_clip(self, clip: Dict[str, Any]) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO rendered_clips (
                    clip_id, highlight_id, source_id, file_path, duration,
                    width, height, aspect_ratio, video_codec, audio_codec,
                    has_audio, has_captions, file_size_bytes, validated, validation_error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(highlight_id) DO UPDATE SET
                    clip_id = excluded.clip_id,
                    file_path = excluded.file_path,
                    duration = excluded.duration,
                    file_size_bytes = excluded.file_size_bytes,
                    validated = excluded.validated,
                    validation_error = excluded.validation_error
                """,
                (
                    clip["clip_id"],
                    clip["highlight_id"],
                    clip["source_id"],
                    clip["file_path"],
                    clip["duration"],
                    clip.get("width", 1080),
                    clip.get("height", 1920),
                    clip.get("aspect_ratio", "9:16"),
                    clip.get("video_codec", "h264"),
                    clip.get("audio_codec", "aac"),
                    1 if clip.get("has_audio", True) else 0,
                    1 if clip.get("has_captions", True) else 0,
                    clip["file_size_bytes"],
                    1 if clip.get("validated", True) else 0,
                    clip.get("validation_error"),
                ),
            )
            # Create or update YouTube & Instagram publication entries
            conn.execute(
                """
                INSERT INTO youtube_publications (
                    pub_id, clip_id, status, title, description, hashtags
                ) VALUES (?, ?, 'PENDING', ?, ?, ?)
                ON CONFLICT(clip_id) DO UPDATE SET
                    status = 'PENDING',
                    title = excluded.title,
                    description = excluded.description,
                    hashtags = excluded.hashtags,
                    error_message = NULL
                """,
                (
                    str(uuid.uuid4()),
                    clip["clip_id"],
                    clip.get("youtube_title", "Epic Gaming Moment #Shorts"),
                    clip.get("youtube_description", "Best gaming highlights"),
                    clip.get("youtube_hashtags", "#Shorts #gaming"),
                ),
            )
            conn.execute(
                """
                INSERT INTO instagram_publications (
                    pub_id, clip_id, status, caption, hashtags
                ) VALUES (?, ?, 'PENDING', ?, ?)
                ON CONFLICT(clip_id) DO UPDATE SET
                    status = 'PENDING',
                    caption = excluded.caption,
                    hashtags = excluded.hashtags
                """,
                (
                    str(uuid.uuid4()),
                    clip["clip_id"],
                    clip.get("instagram_caption", "Insane gameplay moment! Drop a like if you enjoyed 🔥"),
                    clip.get("instagram_hashtags", "#reels #gaming #gamer"),
                ),
            )
            # Mark approved highlight as RENDERED
            conn.execute(
                "UPDATE approved_highlights SET status = 'RENDERED' WHERE highlight_id = ?",
                (clip["highlight_id"],),
            )

    def get_pending_publications(self, platform: str, limit: int = 10) -> List[Dict[str, Any]]:
        table = "youtube_publications" if platform.upper() == "YOUTUBE" else "instagram_publications"
        with self._get_conn() as conn:
            rows = conn.execute(
                f"""
                SELECT p.*, c.file_path, c.duration, c.validated
                FROM {table} p
                JOIN rendered_clips c ON p.clip_id = c.clip_id
                WHERE p.status IN ('PENDING', 'RETRY_REQUIRED') AND c.validated = 1
                ORDER BY p.upload_attempts ASC, p.created_at ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def update_publication_status(
        self,
        platform: str,
        pub_id: str,
        status: str,
        video_id: Optional[str] = None,
        url: Optional[str] = None,
        error_msg: Optional[str] = None,
    ) -> None:
        now = now_utc_iso()
        table = "youtube_publications" if platform.upper() == "YOUTUBE" else "instagram_publications"
        id_col = "youtube_video_id" if platform.upper() == "YOUTUBE" else "instagram_media_id"
        url_col = "youtube_url" if platform.upper() == "YOUTUBE" else "instagram_reel_url"

        query = f"""
            UPDATE {table}
            SET status = ?,
                upload_attempts = upload_attempts + 1,
                {id_col} = COALESCE(?, {id_col}),
                {url_col} = COALESCE(?, {url_col}),
                error_message = ?,
                published_at = CASE WHEN ? = 'PUBLISHED' THEN ? ELSE published_at END,
                updated_at = ?
            WHERE pub_id = ?
        """
        with self._get_conn() as conn:
            conn.execute(query, (status, video_id, url, error_msg, status, now, now, pub_id))

    # -------------------------------------------------------------------------
    # Quota & Rates
    # -------------------------------------------------------------------------
    def get_quota_used(self, platform: str, date_str: Optional[str] = None) -> int:
        d = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT units_used FROM api_quota_usage WHERE usage_date = ? AND platform = ?",
                (d, platform.upper()),
            ).fetchone()
            return int(row["units_used"]) if row else 0

    def increment_quota(self, platform: str, units: int, limit: int) -> None:
        d = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        now = now_utc_iso()
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO api_quota_usage (usage_date, platform, units_used, units_limit, last_reset)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(usage_date, platform) DO UPDATE SET
                    units_used = units_used + excluded.units_used,
                    last_reset = excluded.last_reset
                """,
                (d, platform.upper(), units, limit, now),
            )

    # -------------------------------------------------------------------------
    # Diagnostics & Logs
    # -------------------------------------------------------------------------
    def log_error(
        self,
        subsystem: str,
        message: str,
        error_code: Optional[str] = None,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        log_id = str(uuid.uuid4())
        ctx_str = json.dumps(context) if context else None
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO error_logs (log_id, subsystem, error_code, message, stack_trace, context_data)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (log_id, subsystem, error_code, message, stack_trace, ctx_str),
            )
