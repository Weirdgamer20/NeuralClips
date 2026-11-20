import sys, subprocess, json

queries = [
    'ytsearch40:GTA 6 gameplay shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA VI official shorts -gta5 -gtav -franklin',
    'ytsearch40:Grand Theft Auto VI shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA 6 trailer shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA 6 leaks shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA 6 graphics shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA 6 vice city shorts -gta5 -gtav -franklin',
    'ytsearch40:GTA 6 details shorts -gta5 -gtav -franklin'
]

results = []
seen = set()

banned = [
    'franklin', 'trevor', 'michael', 'gta 5', 'gta v', 'gta5', 'gtav',
    'fivem', 'panda', 'bullman', 'train', 'bhutiya', 'potty', 'hulk',
    'spiderman', 'dog teach', 'gulli', 'bhoot', 'choot', 'skibidi'
]

for q in queries:
    cmd = [
        sys.executable, '-m', 'yt_dlp',
        q,
        '--dump-json',
        '--no-warnings',
        '--flat-playlist'
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    for line in res.stdout.splitlines():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
            vid_id = d.get('id')
            title = d.get('title', '')
            views = d.get('view_count') or 0
            dur = d.get('duration') or 0
            t_lower = title.lower()

            has_gta6 = ('gta 6' in t_lower or 'gta vi' in t_lower or 'grand theft auto vi' in t_lower or 'grand theft auto 6' in t_lower)
            is_banned = any(b in t_lower for b in banned)

            if has_gta6 and not is_banned and vid_id not in seen:
                seen.add(vid_id)
                results.append({'id': vid_id, 'title': title, 'views': views, 'dur': dur})
        except:
            pass

print(f'Total strictly pure GTA 6 (zero GTA 5/Franklin): {len(results)}')
results.sort(key=lambda x: x['views'], reverse=True)
print('\nTop 15 strictly pure GTA 6:')
for r in results[:15]:
    v = r['views']
    t = r['title'][:60]
    vid = r['id']
    print(f'  {v:,} views | {t} | ID: {vid}')
