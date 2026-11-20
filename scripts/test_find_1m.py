import subprocess
import json
import sys

queries = [
    'ytsearch50:GTA 6 #shorts',
    'ytsearch50:GTA VI #shorts',
    'ytsearch50:Grand Theft Auto VI #shorts',
    'ytsearch50:GTA 6 gameplay #shorts',
    'ytsearch50:GTA 6 trailer #shorts',
    'ytsearch50:GTA 6 graphics #shorts',
    'ytsearch50:GTA 6 details #shorts',
    'ytsearch50:GTA 6 leaks #shorts',
    'ytsearch50:GTA 6 vice city #shorts',
    'ytsearch50:GTA 6 Lucia #shorts',
    'ytsearch50:GTA 6 police #shorts',
    'ytsearch50:GTA 6 map #shorts',
    'ytsearch50:GTA 6 physics #shorts',
    'ytsearch50:GTA 6 realism #shorts',
    'ytsearch50:GTA 6',
    'ytsearch50:GTA VI',
    'ytsearch50:Grand Theft Auto 6',
    'ytsearch50:Grand Theft Auto VI',
    'ytsearch50:GTA 6 gameplay',
    'ytsearch50:GTA 6 trailer',
    'ytsearch50:GTA 6 leaks',
    'ytsearch50:GTA 6 Vice City',
    'ytsearch50:GTA 6 mud club',
    'ytsearch50:GTA 6 twerk',
    'ytsearch50:GTA 6 strip club',
    'ytsearch50:GTA 6 car crash',
    'ytsearch50:GTA 6 water',
    'ytsearch50:GTA 6 alligators',
    'ytsearch50:GTA 6 leonida'
]

banned = [
    'franklin', 'trevor', 'michael', 'fivem', 'panda', 'bullman', 'train',
    'bhutiya', 'potty', 'hulk', 'spiderman', 'dog teach', 'gulli', 'bhoot',
    'choot', 'skibidi', 'dhar mann', 'make money', 'how to make', 'clipping work', 'niches'
]

found = []
seen = set()

for q in queries:
    res = subprocess.run([
        sys.executable, '-m', 'yt_dlp',
        q,
        '--dump-json',
        '--flat-playlist',
        '--no-warnings'
    ], capture_output=True, text=True)
    for line in res.stdout.splitlines():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
            vid = d.get('id')
            title = d.get('title', '')
            dur = d.get('duration') or 0
            views = d.get('view_count') or 0
            t_lower = title.lower()
            if vid in seen:
                continue
            if not (15 <= dur <= 75):
                continue
            has_gta6 = ('gta 6' in t_lower or 'gta vi' in t_lower or 'grand theft auto vi' in t_lower or 'grand theft auto 6' in t_lower)
            if not has_gta6:
                continue
            if any(b in t_lower for b in banned):
                continue
            seen.add(vid)
            found.append({'id': vid, 'title': title, 'views': views, 'dur': dur})
        except:
            pass

found.sort(key=lambda x: x['views'], reverse=True)
print(f"Total qualified pure GTA 6 clips found: {len(found)}")
m_plus = [f for f in found if f['views'] >= 1000000]
print(f"Clips with >= 1,000,000 views: {len(m_plus)}")

with open(r"d:\vidclip\storage\candidates_pure_gta6.json", "w", encoding="utf-8") as f:
    json.dump(found, f, indent=2)

print("Saved candidates to d:\\vidclip\\storage\\candidates_pure_gta6.json")
