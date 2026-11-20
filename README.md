# NEURALCLIPS
## Autonomous Gaming Livestream → AI Highlights → YouTube Shorts + Instagram Reels

NeuralClips is an autonomous gaming content production and distribution pipeline running in the Google Antigravity environment. Every morning, five YouTube livestream or VOD URLs are submitted. NeuralClips verifies creator redistribution rights, extracts gameplay highlights using Gemini AI (score >= 75/100), renders 1080x1920 vertical split-screen videos (facecam top 40%, gameplay bottom 60%) with animated synchronized captions, validates each render, and publishes approved videos independently to YouTube Shorts and Instagram Reels respecting daily quotas.

---

## 1. Environment Audit & Capabilities Report

| Capability | Status | Implementation Details |
|---|---|---|
| **Python** | ✅ Available | Python 3.13.14 (`d:\vidclip\.venv`) |
| **Persistent Storage** | ✅ Verified | Drive `D:\vidclip` (53.6 GB free), SQLite WAL database |
| **Scheduled Tasks** | ✅ Supported | Antigravity `schedule` Cron (`* * * * *`, `*/5 * * * *`) & Windows `schtasks` |
| **Persistent Workers** | ✅ Supported | `IsDaemon: true` / Background worker processes |
| **FFmpeg Execution** | ⚠️ Configurable | Configured via `FFMPEG_PATH` & `FFPROBE_PATH` in `.env` (fallback simulator active) |
| **Network & Sandboxing** | ⚠️ Governed | Host / BypassSandbox required for external YouTube / Gemini / Meta HTTP calls |
| **Gemini AI Access** | ✅ Integrated | `AI_PROVIDER=agent` (Antigravity Assistant performs all AI work; NO Gemini API key required) or `AI_PROVIDER=gemini` |
| **YouTube Data API v3** | ✅ Integrated | OAuth2 with refresh token; enforces 1,600 units/upload quota cap |
| **Meta Instagram API** | ✅ Integrated | Two-step Reels container creation & publication workflow; rolling daily limits |
| **Media Hosting** | ⚠️ External Required | Public HTTPS URL (S3 / R2 / GCS) required for Instagram Reels video ingestion |

---

## 2. Directory Architecture

```
d:\vidclip\
├── config/
│   ├── settings.yaml            # Pipeline thresholds, video specs, and scheduling crons
│   ├── creators.yaml            # Rights authorization registry (channels, permissions, crop profiles)
│   ├── routing.yaml             # Game genre routing and hashtag templates
│   └── crop_profiles.yaml       # Facecam (top 40%) & gameplay (bottom 60%) coordinates
├── core/
│   ├── database.py              # SQLite schema with WAL mode (all 16 logical entities)
│   ├── state_store.py           # Data access objects with transactional integrity
│   ├── locks.py                 # Distributed database lease locking
│   ├── job_manager.py           # Worker leases, atomic job claiming, state transitions
│   ├── retry.py                 # Transient vs permanent classification & jittered backoff
│   ├── quota_manager.py         # YouTube quota (1600 units/upload) & Instagram rate limiting
│   ├── logging_config.py        # Structured logging with secret sanitization
│   └── scheduler.py             # End-to-end pipeline coordinator & CLI entrypoint
├── sources/
│   ├── url_validator.py         # YouTube URL parsing and 11-char video ID validation
│   ├── youtube_source.py        # YouTube Data API v3 live status & metadata inspection
│   ├── source_detector.py       # 9-status classifier enforcing rights verification
│   ├── vod_processor.py         # Completed VOD downloader and 60s overlapping segmenter
│   ├── live_capture.py          # Persistent capture worker coordinator for active streams
│   └── segment_manager.py       # Disk segment indexing and deduplication
├── permissions/
│   ├── permission_registry.py   # Creator permission loader and channel lookup
│   └── rights_validator.py      # Strict rights verification (recording, editing, redistribution)
├── ai/
│   ├── gemini_client.py         # Gemini Flash/Pro client with structured JSON output
│   ├── video_analyzer.py        # Multimodal segment dispatcher
│   ├── highlight_detector.py    # 15 gaming categories highlight detector
│   ├── highlight_ranker.py      # Global scoring (>=75/100), deduplication & ranking
│   └── transcript_engine.py     # Word-level speech timing alignment
├── rendering/
│   ├── crop_detector.py         # Facecam and gameplay crop coordinate resolver
│   ├── layout_engine.py         # FFmpeg filtergraph: Facecam top 40% + Gameplay bottom 60%
│   ├── caption_engine.py        # Animated ASS subtitle generator (yellow active word emphasis)
│   ├── ffmpeg_renderer.py       # FFmpeg video encoding execution engine
│   ├── render_validator.py      # Quality assurance: 1080x1920, 30-60s, audio presence, h264/aac
│   └── clip_extractor.py        # Full clip production and publishing queue registration
├── publishing/
│   ├── metadata_generator.py    # Platform-specific titles, descriptions, and hashtags
│   ├── youtube_auth.py          # YouTube OAuth2 refresh token authenticator
│   ├── youtube_publisher.py     # YouTube Shorts publisher with resumable upload
│   ├── instagram_auth.py        # Meta Graph API token manager for Professional accounts
│   ├── instagram_publisher.py   # Two-step Reels container workflow & status polling
│   └── publishing_queue.py      # Decoupled dual-platform publishing runner
├── monitoring/
│   ├── health_check.py          # Storage, database, workers, and API diagnostic monitor
│   ├── recovery.py              # Crash recovery: resets stale leases and stranded jobs
│   └── daily_report.py          # Truthful consolidated daily report generator
├── jobs/
│   ├── daily_intake.py          # JOB A: 5 URLs intake and batch initialization
│   ├── monitor_sources.py       # JOB B: Stream status monitor (every 1 min)
│   ├── process_media.py         # JOB C: Media segmenter (every 5 min)
│   ├── analyze_highlights.py    # JOB D: Gemini highlight analyzer (every 5 min)
│   ├── render_clips.py          # JOB E: Video renderer (every 5 min)
│   ├── publish_youtube.py       # JOB F: YouTube publisher (every 5 min)
│   ├── publish_instagram.py     # JOB G: Instagram publisher (every 5 min)
│   └── daily_maintenance.py     # JOB H & I: Health, crash recovery, and daily report (every 15 min)
├── tests/                       # 14 Unit and Integration Tests (100% passing)
├── storage/
│   ├── segments/                # Raw 60s media segments
│   ├── clips/                   # Rendered 1080x1920 MP4 vertical videos
│   └── reports/                 # Daily consolidated report text files
└── data/
    └── neuralclips.db           # SQLite WAL persistent state database
```

---

## 3. Daily User Workflow

### Step 1: Submit 5 Daily URLs
Every morning, run the intake job with five YouTube livestream or VOD URLs:
```bash
d:\vidclip\.venv\Scripts\python.exe jobs/daily_intake.py \
  "https://www.youtube.com/watch?v=VIDEO_ID_1" \
  "https://www.youtube.com/watch?v=VIDEO_ID_2" \
  "https://www.youtube.com/watch?v=VIDEO_ID_3" \
  "https://www.youtube.com/watch?v=VIDEO_ID_4" \
  "https://www.youtube.com/watch?v=VIDEO_ID_5"
```
The system will:
1. Validate syntax and extract canonical 11-char video IDs.
2. Verify rights authorization in `config/creators.yaml`.
3. Create daily batch ID `NC-YYYY-MMDD-XXXX`.
4. Allow valid sources to proceed while logging reasons for any rejected sources.

### Step 2: Automated Pipeline Execution
The scheduled background jobs autonomously take over:
- **`monitor_sources.py`**: Watches active/scheduled streams and attaches capture workers.
- **`process_media.py`**: Chunks footage into 60-second analysis windows with 10-second overlap.
- **`analyze_highlights.py`**: Antigravity AI Agent analyzes segments, ranks highlights globally, and approves items scoring ≥ 75/100 (up to 100 clips). No Gemini API key is needed.
- **`render_clips.py`**: Renders 1080x1920 vertical videos with facecam top 40% and gameplay bottom 60% plus animated captions.
- **`publish_youtube.py`**: Uploads Shorts to authorized channel, deducting 1,600 quota units per upload.
- **`publish_instagram.py`**: Creates Reels containers on Meta Graph API and publishes them.
- **`daily_maintenance.py`**: Recovers any interrupted tasks and compiles the final truthful daily report.

### Optional: Interactive Agent AI Review Tool
To interact directly with the agent review queue or export segments:
```bash
# Automatically analyze all pending segments using Antigravity Agent AI
d:\vidclip\.venv\Scripts\python.exe jobs/agent_ai_review.py --auto

# Or export pending segments for interactive agent inspection:
d:\vidclip\.venv\Scripts\python.exe jobs/agent_ai_review.py --export
```

---

## 4. Production Deployment & Task Scheduling

To run automated scheduled execution on Windows, configure Windows Task Scheduler commands:

```cmd
schtasks /Create /SC MINUTE /MO 1  /TN "NeuralClips_MonitorSources"    /TR "d:\vidclip\.venv\Scripts\python.exe -m jobs.monitor_sources" /F
schtasks /Create /SC MINUTE /MO 5  /TN "NeuralClips_ProcessMedia"      /TR "d:\vidclip\.venv\Scripts\python.exe -m jobs.process_media" /F
schtasks /Create /SC MINUTE /MO 5  /TN "NeuralClips_AnalyzeHighlights" /TR "d:\vidclip\.venv\Scripts\python.exe -m jobs.analyze_highlights" /F
schtasks /Create /SC MINUTE /MO 5  /TN "NeuralClips_RenderClips"       /TR "d:\vidclip\.venv\Scripts\python.exe -m jobs.render_clips" /F
schtasks /Create /SC MINUTE /MO 5  /TN "NeuralClips_PublishYouTube"    /TR "d:\vidclip\.venv\Scripts\python.exe -m jobs.publish_youtube" /F
schtasks /Create /SC MINUTE /MO 5  /TN "NeuralClips_PublishInstagram"  /TR "d:\vidclip\.venv\Scripts\python.exe -m jobs.publish_instagram" /F
schtasks /Create /SC MINUTE /MO 15 /TN "NeuralClips_DailyMaintenance"  /TR "d:\vidclip\.venv\Scripts\python.exe -m jobs.daily_maintenance" /F
```

---

## 5. Verification & Test Suite

Run the full automated test suite anytime:
```bash
d:\vidclip\.venv\Scripts\python.exe tests/run_tests.py
```
All 14 tests verify:
- 5-source intake validation and canonical video ID parsing
- Source classification (VOD, Active, Scheduled, Unavailable)
- Mandatory rights validation (recording, editing, redistribution, expiration, revocation)
- Gemini scoring threshold (≥ 75/100), duration filtering (30-60s), and deduplication
- 1080x1920 vertical split-screen rendering (facecam top 40%, gameplay bottom 60%)
- Animated ASS subtitle timing and karaoke-style highlight tags
- YouTube quota accounting (1,600 units) and upload verification
- Instagram Reels container creation and 2-step publishing workflow
- Platform failure isolation (YouTube success / Instagram failure independence)
- Crash recovery and truthful daily reporting
