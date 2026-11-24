import shutil
import subprocess
import json
import sys

queries = [
    ("carryislive", "ytsearch3:CarryisLive GTA V funny moments"),
    ("techno_gamerz", "ytsearch3:Techno Gamerz GTA 5 high speed police chase"),
    ("live_insaan", "ytsearch3:Live Insaan GTA 5 funny moments rage")
]

results = {}

for creator, q in queries:
    cmd = [
        (shutil.which("yt-dlp") or str(Path(sys.prefix) / "Scripts" / "yt-dlp.exe")),
        "--dump-json",
        "--flat-playlist",
        q
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        creator_vids = []
        for line in lines:
            try:
                item = json.loads(line)
                creator_vids.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "duration": item.get("duration"),
                    "url": f"https://www.youtube.com/watch?v={item.get('id')}"
                })
            except Exception:
                continue
        results[creator] = creator_vids
    except Exception as e:
        results[creator] = str(e)

print(json.dumps(results, indent=2))
