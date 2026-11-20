import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "neuralclips.db")
conn = sqlite3.connect(db_path)

c_pub = conn.execute("SELECT COUNT(pub_id) FROM youtube_publications WHERE status = 'PUBLISHED'").fetchone()[0]
c_fail = conn.execute("SELECT COUNT(pub_id) FROM youtube_publications WHERE status = 'FAILED'").fetchone()[0]

print(f"Total Published Shorts: {c_pub}")
print(f"Total Failed / Rate-Limited: {c_fail}")

rows = conn.execute("SELECT title, status, youtube_video_id, error_message, created_at FROM youtube_publications ORDER BY created_at DESC LIMIT 8").fetchall()
print("\nRecent 8 Publishing Attempts:")
for r in rows:
    title, status, vid, err, dt = r
    if status == 'PUBLISHED':
        print(f"[OK] {title} -> https://youtube.com/shorts/{vid} ({dt})")
    else:
        print(f"[FAILED] {title} -> Error: {err} ({dt})")

conn.close()
